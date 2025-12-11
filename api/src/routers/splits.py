"""
Split calculation router for handling bill splitting and sharing.
"""

import base64
import hashlib
import json

# Import logger after other imports
import logging
import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# Import core modules
from ..core.config import settings
from ..core.security import get_api_key
from ..models.schemas import (
    CalculateSplitRequest,
    CalculateSplitResponse,
    ItemAssignment,
    SharedSplitDataResponse,
)
from ..services.minio_utils import (
    get_metadata_from_minio,
    upload_image_to_minio,
    upload_metadata_to_minio,
)

# Import services using relative imports
from ..services.split_logic import calculate_split

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/splits", tags=["splits"])


# Pydantic models (simplified versions for now)
class ReceiptUploadResponse(BaseModel):
    parsed_data: Dict[str, Any]
    processed_image_bytes_base64: Optional[str] = None
    extracted_subtotal_from_gemini: float
    extracted_total_discount: float


def load_shared_split_data(split_id: str) -> Optional[Dict[str, Any]]:
    """Load shared split data from MinIO."""
    metadata = get_metadata_from_minio(split_id)
    if metadata:
        return metadata
    return None


@router.post("/calculate", response_model=CalculateSplitResponse)
async def calculate_split_endpoint(
    request: CalculateSplitRequest, api_key: str = Depends(get_api_key)
):
    """
    Calculate bill split and generate shareable link.

    Args:
        request: Split calculation request with person names, items, tax, tip, etc.

    Returns:
        Split calculation results with share link and split ID
    """
    final_assignments_for_calc = request.item_assignments

    # Validate request
    if (
        not request.split_evenly
        and not final_assignments_for_calc
        and (request.tax_amount_input == 0 and request.tip_amount_input == 0)
    ):
        raise HTTPException(
            status_code=400, detail="Please assign items or enter tax/tip."
        )

    # Generate idempotency key for content-based split ID
    idempotency_key_material = {
        "image_bytes_hash": (
            hashlib.sha256(
                base64.b64decode(request.processed_image_bytes_for_minio_base64 or "")
            ).hexdigest()
            if request.processed_image_bytes_for_minio_base64
            else ""
        ),
        "people": sorted(request.person_names),
        "assignments": (
            sorted(
                [
                    {
                        "item_desc": a.item_details.get("item", ""),
                        "item_qty": a.item_details.get("qty", ""),
                        "item_price": a.item_details.get("price", ""),
                        "assigned_to": sorted(a.assigned_to),
                    }
                    for a in final_assignments_for_calc
                ],
                key=lambda x: x["item_desc"],
            )
            if not request.split_evenly
            else "SPLIT_EVENLY"
        ),
        "tax": request.tax_amount_input,
        "tip": request.tip_amount_input,
        "split_evenly": request.split_evenly,
        "extracted_subtotal": request.extracted_subtotal_from_gemini or 0.0,
        "extracted_discount": request.extracted_total_discount,
        "notes_text": request.notes_text,
        "payment_details": (
            request.payment_details.dict() if request.payment_details else None
        ),
    }

    id_hasher = hashlib.sha256()
    id_hasher.update(
        json.dumps(idempotency_key_material, sort_keys=True).encode("utf-8")
    )
    split_id = id_hasher.hexdigest()[:12]

    # Check for existing split
    existing_metadata = get_metadata_from_minio(split_id)
    if existing_metadata and existing_metadata.get("share_link"):
        return CalculateSplitResponse(
            split_results=existing_metadata.get("calculated_split_results"),
            share_link=existing_metadata["share_link"],
            split_id=split_id,
        )

    # Calculate split
    subtotal_for_even_split = (
        request.extracted_subtotal_from_gemini if request.split_evenly else 0.0
    ) or 0.0  # Ensure it's always a float, never None
    calculated_split = calculate_split(
        final_assignments_for_calc,
        str(request.tax_amount_input),
        str(request.tip_amount_input),
        request.person_names,
        split_evenly_flag=request.split_evenly,
        overall_subtotal_for_even_split=subtotal_for_even_split,
        total_discount_amount=request.extracted_total_discount,
    )

    if "Error" in calculated_split:
        raise HTTPException(
            status_code=500, detail=f"Calculation error: {calculated_split['Error']}"
        )

    # Upload image if provided
    minio_image_object_name = None
    if request.processed_image_bytes_for_minio_base64:
        try:
            processed_image_bytes = base64.b64decode(
                request.processed_image_bytes_for_minio_base64
            )
            base_image_name = f"{split_id}.jpg"
            full_image_obj_name = upload_image_to_minio(
                processed_image_bytes, base_image_name, "image/jpeg"
            )
            if full_image_obj_name:
                minio_image_object_name = full_image_obj_name
        except Exception as e:
            logger.error(f"Failed to save receipt image to cloud: {e}")

    # Generate share link
    app_base_url = settings.APP_BASE_URL
    current_share_link = f"{app_base_url}/view-split/{split_id}"

    # Save metadata
    metadata_to_save = {
        "split_id": split_id,
        "original_parsed_data": request.original_parsed_data,
        "person_names": request.person_names,
        "item_assignments": [a.dict() for a in final_assignments_for_calc],
        "split_evenly_choice": request.split_evenly,
        "total_discount_applied": request.extracted_total_discount,
        "user_adjusted_tax": request.tax_amount_input,
        "user_adjusted_tip": request.tip_amount_input,
        "calculated_split_results": calculated_split,
        "minio_image_object_name": minio_image_object_name,
        "share_link": current_share_link,
        "creation_timestamp": time.time(),
        "notes_text": request.notes_text or "",
        "payment_details": (
            request.payment_details.dict() if request.payment_details else {}
        ),
    }

    meta_upload_obj_name = upload_metadata_to_minio(metadata_to_save, split_id)
    if not meta_upload_obj_name:
        logger.error(f"Failed to save split metadata for {split_id}.")

    return CalculateSplitResponse(
        split_results=calculated_split, share_link=current_share_link, split_id=split_id
    )


@router.get("/view/{split_id}", response_model=SharedSplitDataResponse)
async def view_split(split_id: str, api_key: str = Depends(get_api_key)):
    """
    Retrieve shared split data by ID.

    Args:
        split_id: Unique split identifier

    Returns:
        Shared split data including results, participants, and image

    Raises:
        HTTPException: If split data not found
    """
    loaded_data_dict = load_shared_split_data(split_id)
    if not loaded_data_dict:
        raise HTTPException(
            status_code=404, detail=f"Split data for ID '{split_id}' not found."
        )

    # Convert item_assignments to proper format
    item_assignments_converted = [
        ItemAssignment(**item) for item in loaded_data_dict.get("item_assignments", [])
    ]

    # Handle payment details compatibility
    payment_details = loaded_data_dict.get("payment_details")
    if payment_details is None:
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
        image_bytes_for_display_base64=None,  # Can be added later if needed
        notes_text=loaded_data_dict.get("notes_text", ""),
        payment_details=payment_details,
    )
