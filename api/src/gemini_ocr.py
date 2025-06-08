# filename: src/gemini_ocr.py
import os
import json
import time
import io
from typing import Any, Optional, List

# Correct Imports
from google import genai  # Main genai module
from google.genai import types  # For type definitions like Tool, GenerateContentConfig
import PIL.Image
from pydantic import BaseModel, Field
from loguru import logger

# --- API Key Environment Variable ---

# --- Pydantic Models ---
class LineItem(BaseModel):
    item_description: str = Field(description="Full description of the item")
    quantity: float = Field(default=1.0, description="Quantity of the item")
    item_total_price: float = Field(description="Total price for the item line")

class Discount(BaseModel):
    description: str = Field(description="Description of the discount")
    amount: float = Field(description="Positive numeric value of the discount")

class TaxDetail(BaseModel):
    tax_label: str = Field(description="Label for the tax or charge")
    tax_amount: float = Field(description="Amount of the tax or charge")

class ReceiptData(BaseModel):
    store_name: Optional[str] = Field(default=None, description="Name of the store")
    transaction_date: Optional[str] = Field(default=None, description="Transaction date (YYYY-MM-DD)")
    transaction_time: Optional[str] = Field(default=None, description="Transaction time (HH:MM)")
    line_items: List[LineItem] = Field(default_factory=list)
    discounts: List[Discount] = Field(default_factory=list)
    tax_details: List[TaxDetail] = Field(default_factory=list)
    subtotal: Optional[float] = Field(default=None, description="Subtotal before taxes/discounts")
    total_amount: Optional[float] = Field(default=None, description="The final grand total paid")
    tip_amount: Optional[float] = Field(default=None, description="Tip or gratuity amount")

def create_flattened_schema():
    """
    Create a flattened JSON schema compatible with Gemini API.
    This removes $ref and $defs that cause validation errors.
    """
    return {
        "type": "object",
        "properties": {
            "store_name": {
                "type": "string",
                "description": "Name of the store",
                "default": None
            },
            "transaction_date": {
                "type": "string",
                "description": "Transaction date (YYYY-MM-DD)",
                "default": None
            },
            "transaction_time": {
                "type": "string",
                "description": "Transaction time (HH:MM)",
                "default": None
            },
            "line_items": {
                "type": "array",
                "description": "List of items purchased",
                "items": {
                    "type": "object",
                    "properties": {
                        "item_description": {
                            "type": "string",
                            "description": "Full description of the item"
                        },
                        "quantity": {
                            "type": "number",
                            "description": "Quantity of the item",
                            "default": 1.0
                        },
                        "item_total_price": {
                            "type": "number",
                            "description": "Total price for the item line"
                        }
                    },
                    "required": ["item_description", "item_total_price"]
                }
            },
            "discounts": {
                "type": "array",
                "description": "List of discounts applied",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Description of the discount"
                        },
                        "amount": {
                            "type": "number",
                            "description": "Positive numeric value of the discount"
                        }
                    },
                    "required": ["description", "amount"]
                }
            },
            "tax_details": {
                "type": "array",
                "description": "List of taxes and charges",
                "items": {
                    "type": "object",
                    "properties": {
                        "tax_label": {
                            "type": "string",
                            "description": "Label for the tax or charge"
                        },
                        "tax_amount": {
                            "type": "number",
                            "description": "Amount of the tax or charge"
                        }
                    },
                    "required": ["tax_label", "tax_amount"]
                }
            },
            "subtotal": {
                "type": "number",
                "description": "Subtotal before taxes/discounts",
                "default": None
            },
            "total_amount": {
                "type": "number",
                "description": "The final grand total paid",
                "default": None
            },
            "tip_amount": {
                "type": "number",
                "description": "Tip or gratuity amount",
                "default": None
            }
        }
    }

def generate_gemini_prompt_with_guidelines():
    return """You are an expert receipt processing assistant. Your task is to analyze the provided receipt image and extract key information by calling the `extract_receipt_data` function.

Follow these guidelines for extraction accuracy:
- For 'discounts': If a percentage discount is shown, calculate the final numeric discount amount.
- For 'subtotal': If not explicitly printed, infer it as the sum of all line items.
- If a value is not clearly present, use null or an empty list.
"""

def get_gemini_config():
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set. This key is required for genai.Client().")
    MODEL_NAME = os.environ.get("GEMINI_MODEL_NAME", "gemini-1.5-flash")
    return GEMINI_API_KEY, MODEL_NAME

def classify_image_as_receipt(image_bytes: bytes) -> bool:
    try:
        start_time = time.time()
        GEMINI_API_KEY, MODEL_NAME = get_gemini_config()
        client = genai.Client(api_key=GEMINI_API_KEY)

        img = PIL.Image.open(io.BytesIO(image_bytes))
        prompt = "Is this image a retail receipt or bill? Answer only 'YES' or 'NO'."

        config_obj = types.GenerateContentConfig(
            temperature=0.0,
            max_output_tokens=10
        )

        logger.info("Sending classification request to Gemini API...")
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt, img],
            config=config_obj,
        )

        classification_result = response.text.strip().upper()
        elapsed = time.time() - start_time
        logger.info(f"Gemini classification result: {classification_result} (took {elapsed:.2f} seconds)")
        return classification_result == "YES"
    except Exception as e:
        logger.error(f"An error occurred during Gemini image classification: {e}")
        import traceback; traceback.print_exc()
        return False

def extract_receipt_data_with_gemini(image_bytes: bytes) -> dict[str, Any]:
    start_time = time.time()
    logger.info(f"Starting receipt data extraction at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    GEMINI_API_KEY, MODEL_NAME = get_gemini_config()

    if not classify_image_as_receipt(image_bytes):
        return {"Error": "NOT_A_RECEIPT", "message": "The uploaded image does not appear to be a receipt."}

    try:
        logger.info(f"Initializing Gemini for OCR with function calling: {MODEL_NAME}")
        client = genai.Client(api_key=GEMINI_API_KEY)

        img = PIL.Image.open(io.BytesIO(image_bytes))
        prompt_text = generate_gemini_prompt_with_guidelines()

        # Use flattened schema instead of Pydantic model_json_schema()
        receipt_extraction_function = {
            "name": "extract_receipt_data",
            "description": "Extracts all structured data from a receipt image based on the provided schema.",
            "parameters": create_flattened_schema()
        }

        tools_obj = types.Tool(function_declarations=[receipt_extraction_function])

        config_obj = types.GenerateContentConfig(
            tools=[tools_obj],
            temperature=0.1
        )

        logger.info("Sending OCR request to Gemini API...")
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt_text, img],
            config=config_obj,
        )
        logger.info(f"Gemini API response received in {time.time() - start_time:.2f} seconds.")

        if not response.candidates or not response.candidates[0].content.parts or \
           not response.candidates[0].content.parts[0].function_call:
            logger.error("Error: Model did not return a valid function call.")
            logger.error("Full response object:", response)
            try:
                if hasattr(response, 'text') and response.text:
                    logger.error("Response text:", response.text)
                elif response.candidates and response.candidates[0].content.parts:
                     logger.error("Response parts text:", [part.text for part in response.candidates[0].content.parts if hasattr(part, 'text')])
            except Exception as pe:
                logger.error(f"Could not extract text from response: {pe}")
            return {"Error": "Model did not return the expected function call structure."}

        function_call = response.candidates[0].content.parts[0].function_call

        if function_call.name == 'extract_receipt_data':
            extracted_data = dict(function_call.args)
            logger.info("\n--- Successfully Parsed Data via Function Call ---")
            logger.info(json.dumps(extracted_data, indent=2))
            # Optional: Validate the extracted data against your Pydantic model
            try:
                validated_data = ReceiptData(**extracted_data)
                logger.info("Data validation successful!")
                elapsed_time = time.time() - start_time
                logger.info(f"Receipt data extraction completed in {elapsed_time:.2f} seconds")
                return validated_data.model_dump()
            except Exception as validation_error:
                logger.warning(f"Pydantic validation warning: {validation_error}")
                logger.info("Returning raw extracted data...")
                return extracted_data

        else:
            return {"Error": f"Unexpected function call '{function_call.name}'."}

    except Exception as e:
        logger.error(f"An error occurred calling Gemini API: {e}")
        import traceback; traceback.print_exc()
        return {"Error": f"Gemini API call failed: {str(e)}"}
