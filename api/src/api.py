import io
import json
import os
import hashlib
import base64
import time
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables first
dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path)

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # Import for Bearer token
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from PIL import Image as PILImage, UnidentifiedImageError

from . import gemini_ocr
from . import minio_utils 
from . import split_logic

# Constants
MAX_IMAGE_SIZE_MB = 2
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024

# --- API Key Authentication Configuration ---
API_KEY = os.getenv("API_KEY") # Get API key from environment variable
if not API_KEY:
    raise ValueError("API_KEY environment variable is not set in .env file")

# If API_KEY is not set, raise an error on startup
if not API_KEY:
    raise ValueError("API_KEY environment variable is not set. Please set it to secure your API.")

security_scheme = HTTPBearer()

async def get_api_key(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    # Expecting a Bearer token that matches the API_KEY
    if credentials.scheme != "Bearer" or credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials # Return the API key (token) itself

# --- FastAPI App Instance ---
app = FastAPI(
    title="Bill Splitter API",
    description="API for uploading receipts, extracting data, and calculating bill splits.",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# --- CORS Configuration ---
# Allow requests from any origin (React front-end, Streamlit, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Accept requests from every domain
    allow_credentials=True,
    allow_methods=["*"],       # Accept all HTTP methods
    allow_headers=["*"],       # Accept all request headers
)

# Helper functions (moved from main.py, adapted for API)
def compress_image(image_bytes: bytes, target_size_bytes: int = MAX_IMAGE_SIZE_BYTES, quality: int = 90, min_quality: int = 70) -> bytes | None:
    # Ensure quality and min_quality are integers (handle unexpected list type)
    if isinstance(quality, list):
        quality = int(quality[0]) if quality else 90
    else:
        quality = int(quality)
    if isinstance(min_quality, list):
        min_quality = int(min_quality[0]) if min_quality else 70
    else:
        min_quality = int(min_quality)

    try:
        img = PILImage.open(io.BytesIO(image_bytes))
        if img.mode not in ('RGB', 'L'): img = img.convert('RGB')
        compressed_bytes = None 
        for q in range(quality, min_quality -1 , -5):
            buffer = io.BytesIO(); img.save(buffer, format="JPEG", quality=q, optimize=True)
            compressed_bytes = buffer.getvalue()
            if len(compressed_bytes) <= target_size_bytes:
                print(f"Image compressed to {len(compressed_bytes)/1024:.2f} KB with quality {q}.")
                return compressed_bytes
        if compressed_bytes and len(compressed_bytes) > target_size_bytes:
            ratio = (target_size_bytes / len(compressed_bytes))**0.5 
            new_width = int(img.width * ratio); new_height = int(img.height * ratio)
            if new_width > 0 and new_height > 0:
                img_resized = img.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
                buffer = io.BytesIO(); img_resized.save(buffer, format="JPEG", quality=min_quality, optimize=True)
                compressed_bytes = buffer.getvalue()
                print(f"Resized/compressed image size: {len(compressed_bytes)/1024:.2f} KB.")
                return compressed_bytes
        return compressed_bytes
    except UnidentifiedImageError: raise HTTPException(status_code=400, detail="Cannot identify image file.")
    except Exception as e: raise HTTPException(status_code=500, detail=f"Image compression error: {e}")

def load_shared_split_data(split_id: str) -> dict[str, Any] | None:
    metadata = minio_utils.get_metadata_from_minio(split_id)
    if metadata:
        image_bytes_for_display = None
        minio_img_obj_name = metadata.get("minio_image_object_name")
        if minio_img_obj_name:
            base_img_name = minio_img_obj_name.replace(minio_utils.IMAGE_PREFIX, "", 1)
            image_bytes_for_display = minio_utils.get_image_from_minio(base_img_name)
        metadata['image_bytes_for_display'] = image_bytes_for_display if image_bytes_for_display else None
        return metadata
    else: return None

# Pydantic models for request/response bodies (kept the same)
class ReceiptUploadResponse(BaseModel):
    parsed_data: Dict[str, Any]
    processed_image_bytes_base64: str | None = None # Base64 encoded image for display
    minio_image_object_name: str | None = None
    extracted_subtotal_from_gemini: float
    extracted_total_discount: float

class ItemAssignment(BaseModel):
    item_details: Dict[str, Any]
    assigned_to: List[str]

class CalculateSplitRequest(BaseModel):
    person_names: List[str]
    item_assignments: List[ItemAssignment]
    tax_amount_input: float
    tip_amount_input: float
    split_evenly: bool
    extracted_subtotal_from_gemini: float | None = None
    extracted_total_discount: float
    processed_image_bytes_for_minio_base64: str | None = None # Base64 encoded image for MinIO upload
    original_parsed_data: Dict[str, Any]
    notes_text: str | None = None
    payment_details: Dict[str, Any] | None = None

class CalculateSplitResponse(BaseModel):
    split_results: Dict[str, Any]
    share_link: str
    split_id: str

class SharedSplitDataResponse(BaseModel):
    split_id: str
    original_parsed_data: Dict[str, Any]
    person_names: List[str]
    item_assignments: List[ItemAssignment]
    split_evenly_choice: bool
    total_discount_applied: float
    user_adjusted_tax: float
    user_adjusted_tip: float
    calculated_split_results: Dict[str, Any]
    minio_image_object_name: str | None
    share_link: str
    creation_timestamp: float
    image_bytes_for_display_base64: str | None = None # Base64 encoded image for display
    notes_text: str
    payment_details: Dict[str, Any] = Field(default_factory=dict)

# --- API Endpoints ---

@app.post("/upload-receipt", response_model=ReceiptUploadResponse)
async def upload_receipt(file: UploadFile = File(...), api_key: str = Depends(get_api_key)): # Secured with API Key
    if file.size > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail=f"Image too large ({file.size / (1024*1024):.2f} MB). Max {MAX_IMAGE_SIZE_MB} MB.")
    
    raw_image_bytes = await file.read()
    
    # Added: Check if image is a valid receipt using classifier
    if not gemini_ocr.classify_image_as_receipt(raw_image_bytes):
        raise HTTPException(status_code=400, detail="The uploaded image does not appear to be a receipt. Please upload a valid receipt image.")

    processed_image_bytes = compress_image(raw_image_bytes)
    if not processed_image_bytes:
        raise HTTPException(status_code=500, detail="Image processing failed.")

    parsed_data_dict = gemini_ocr.extract_receipt_data_with_gemini(processed_image_bytes)

    # Updated: Removed "NOT_A_RECEIPT" check since we classify upfront
    if "Error" in parsed_data_dict:
        raise HTTPException(status_code=500, detail=f"Processing error: {parsed_data_dict['Error']}")
    elif not parsed_data_dict.get('line_items') and not parsed_data_dict.get('total_amount'):
        raise HTTPException(status_code=400, detail="Could not extract details from receipt. Please ensure it's a clear receipt image.")
    
    subtotal_from_gemini = parsed_data_dict.get("subtotal", 0.0)
    extracted_subtotal_from_gemini = split_logic.clean_and_convert_number(subtotal_from_gemini) or 0.0
    
    total_discount = 0.0
    if isinstance(parsed_data_dict.get("discounts"), list):
        for disc in parsed_data_dict.get("discounts", []):
            total_discount += (split_logic.clean_and_convert_number(disc.get("amount")) or 0.0)
    extracted_total_discount = total_discount

    processed_image_bytes_base64 = base64.b64encode(processed_image_bytes).decode('utf-8') if processed_image_bytes else None

    return ReceiptUploadResponse(
        parsed_data=parsed_data_dict,
        processed_image_bytes_base64=processed_image_bytes_base64,
        extracted_subtotal_from_gemini=extracted_subtotal_from_gemini,
        extracted_total_discount=extracted_total_discount
    )

@app.post("/calculate-split", response_model=CalculateSplitResponse)
async def calculate_split_endpoint(request: CalculateSplitRequest, api_key: str = Depends(get_api_key)): # Secured with API Key
    final_assignments_for_calc = request.item_assignments
    
    if not request.split_evenly and not final_assignments_for_calc and (request.tax_amount_input == 0 and request.tip_amount_input == 0):
        raise HTTPException(status_code=400, detail="Please assign items or enter tax/tip.")

    idempotency_key_material = {
        "image_bytes_hash": hashlib.sha256(base64.b64decode(request.processed_image_bytes_for_minio_base64) or b"").hexdigest() if request.processed_image_bytes_for_minio_base64 else "",
        "people": sorted(request.person_names),
        "assignments": sorted(
            [{"item_desc": a.item_details.get("item", ""), "item_qty": a.item_details.get("qty", ""), "item_price": a.item_details.get("price", ""), "assigned_to": sorted(a.assigned_to)} for a in final_assignments_for_calc],
            key=lambda x: x["item_desc"]
        ) if not request.split_evenly else "SPLIT_EVENLY",
        "tax": request.tax_amount_input,
        "tip": request.tip_amount_input,
        "split_evenly": request.split_evenly,
        "extracted_subtotal": request.extracted_subtotal_from_gemini,
        "extracted_discount": request.extracted_total_discount,
        "notes_text": request.notes_text,
        "payment_details": request.payment_details
    }
    id_hasher = hashlib.sha256(); id_hasher.update(json.dumps(idempotency_key_material, sort_keys=True).encode('utf-8'))
    split_id = id_hasher.hexdigest()[:12]
    print(f"Generated content-based split_id: {split_id}")
    
    existing_metadata = minio_utils.get_metadata_from_minio(split_id)
    if existing_metadata and existing_metadata.get("share_link"):
        print(f"Using existing share link for split_id {split_id}: {existing_metadata['share_link']}")
        return CalculateSplitResponse(
            split_results=existing_metadata.get("calculated_split_results"),
            share_link=existing_metadata["share_link"],
            split_id=split_id
        )
    else:
        print(f"New split or metadata not found for {split_id}. Proceeding.")
        subtotal_for_even_split = request.extracted_subtotal_from_gemini if request.split_evenly else 0.0
        calculated_split = split_logic.calculate_split(
            final_assignments_for_calc, 
            str(request.tax_amount_input), 
            str(request.tip_amount_input), 
            request.person_names, 
            split_evenly_flag=request.split_evenly, 
            overall_subtotal_for_even_split=subtotal_for_even_split, 
            total_discount_amount=request.extracted_total_discount
        )

        if "Error" in calculated_split:
            raise HTTPException(status_code=500, detail=f"Calculation error: {calculated_split['Error']}")

        minio_image_object_name = None
        if request.processed_image_bytes_for_minio_base64:
            processed_image_bytes = base64.b64decode(request.processed_image_bytes_for_minio_base64)
            base_image_name = f"{split_id}.jpg"
            full_image_obj_name = minio_utils.upload_image_to_minio(processed_image_bytes, base_image_name, "image/jpeg")
            if full_image_obj_name: minio_image_object_name = full_image_obj_name
            else: print("Failed to save receipt image to cloud.") # Log, but don't fail the whole request

        app_base_url = os.environ.get("APP_BASE_URL", "http://localhost:8000") # Default for FastAPI
        current_share_link = f"{app_base_url}/view-split/{split_id}"

        metadata_to_save = {
            "split_id": split_id, 
            "original_parsed_data": request.original_parsed_data, 
            "person_names": request.person_names, 
            "item_assignments": [a.model_dump() for a in final_assignments_for_calc], # Convert Pydantic models to dicts
            "split_evenly_choice": request.split_evenly, 
            "total_discount_applied": request.extracted_total_discount, 
            "user_adjusted_tax": request.tax_amount_input, 
            "user_adjusted_tip": request.tip_amount_input, 
            "calculated_split_results": calculated_split, 
            "minio_image_object_name": minio_image_object_name, 
            "share_link": current_share_link, 
            "creation_timestamp": time.time(),
            "notes_text": request.notes_text,
            "payment_details": request.payment_details
        }
        meta_upload_obj_name = minio_utils.upload_metadata_to_minio(metadata_to_save, split_id)
        if not meta_upload_obj_name:
            print(f"Failed to save split metadata for {split_id}.") # Log, but don't fail the whole request

        return CalculateSplitResponse(
            split_results=calculated_split,
            share_link=current_share_link,
            split_id=split_id
        )

@app.get("/view-split/{split_id}", response_model=SharedSplitDataResponse)
async def view_split(split_id: str, api_key: str = Depends(get_api_key)): # Secured with API Key
    loaded_data_dict = load_shared_split_data(split_id)
    if not loaded_data_dict:
        raise HTTPException(status_code=404, detail=f"Split data for ID '{split_id}' not found.")
    
    # Encode image bytes for display if available
    image_bytes_for_display_base64 = None
    if loaded_data_dict.get('image_bytes_for_display'):
        image_bytes_for_display_base64 = base64.b64encode(loaded_data_dict['image_bytes_for_display']).decode('utf-8')
    
    # Ensure item_assignments are in the correct format for the Pydantic model
    # They might be dicts from MinIO, need to convert to ItemAssignment models
    item_assignments_converted = [ItemAssignment(**item) for item in loaded_data_dict.get("item_assignments", [])]
 
    # Handle backward compatibility for payment_details vs payment_option
    payment_details = loaded_data_dict.get("payment_details")
    if payment_details is None:
        # Fall back to payment_option for old metadata
        payment_option_value = loaded_data_dict.get("payment_option", "Cash")
        payment_details = {"method": payment_option_value}
 
    return SharedSplitDataResponse(
        split_id=loaded_data_dict["split_id"],
        original_parsed_data=loaded_data_dict.get("original_parsed_data", {}),
        person_names=loaded_data_dict.get("person_names", []),
        item_assignments=item_assignments_converted,
        split_evenly_choice=loaded_data_dict.get("split_evenly_choice", False),
        total_discount_applied=loaded_data_dict.get("total_discount_applied", 0.0),
        user_adjusted_tax=loaded_data_dict.get("user_adjusted_tax", 0.0),
        user_adjusted_tip=loaded_data_dict.get("user_adjusted_tip", 0.0),
        calculated_split_results=loaded_data_dict.get("calculated_split_results", {}),
        minio_image_object_name=loaded_data_dict.get("minio_image_object_name"),
        share_link=loaded_data_dict.get("share_link"),
        creation_timestamp=loaded_data_dict.get("creation_timestamp", 0.0),
        image_bytes_for_display_base64=image_bytes_for_display_base64,
        notes_text=loaded_data_dict.get("notes_text", ""),
        payment_details=payment_details
    )
 
# Add a root endpoint for health check or basic info
@app.get("/")
async def read_root():
    return {"message": "Bill Splitter API is running"}
