# gemini_ocr.py
import google.generativeai as genai
import PIL.Image # For type hinting if needed, and opening image
import io
import os
import json
import time
from typing import Any # For dict type hint

# --- Configure Gemini API ---
try:
    GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
    print("Gemini API Key configured from environment variable.")
except KeyError:
    print("ERROR: GEMINI_API_KEY environment variable not set.")
    GEMINI_API_KEY = None 

# --- Model Configuration ---
# Check Google AI Studio for the latest appropriate model names supporting vision.
# "gemini-1.5-flash-latest" is good for speed/cost.
# "gemini-1.5-pro-latest" is more powerful but slower/more expensive.
MODEL_NAME = os.environ.get("GEMINI_MODEL_NAME", "gemini-2.0-flash")


def generate_gemini_prompt_with_discounts():
    """Generates the prompt for Gemini, asking for discount extraction."""
    prompt = """You are an expert receipt processing assistant. Your task is to analyze the provided receipt image and extract key information.
Return the extracted information ONLY as a valid JSON object. Do not include any explanatory text before or after the JSON.

The JSON object should have the following structure:
{
  "store_name": "string | null",
  "transaction_date": "string (YYYY-MM-DD if possible, otherwise as is) | null",
  "transaction_time": "string (HH:MM if possible) | null",
  "line_items": [
    {
      "item_description": "string (full description of the item)",
      "quantity": "number (default to 1.0 if not specified or ambiguous)",
      "item_total_price": "number (total price for the given quantity of this item line, BEFORE any item-specific discount if separately listed, or after item-specific discount if the price shown is already discounted)"
    }
  ],
  "subtotal": "number | null (This should typically be the sum of all line_items' item_total_price. If the receipt shows a subtotal that differs, try to use the one that seems to be the sum of items before overall bill discounts.)",
  "discounts": [
    {
      "description": "string (e.g., 'VOUCHER', '10% OFF TOTAL', 'LOYALTY DISCOUNT')",
      "amount": "number (POSITIVE value representing the discount amount. If it's a percentage discount on the subtotal, calculate the actual discount amount and provide that numeric value.)"
    }
  ],
  "tax_details": [
    {
      "tax_label": "string (e.g., 'VAT', 'SVC CHG', 'PBI 10%', 'PPN 11%')",
      "tax_amount": "number"
    }
  ],
  "total_amount": "number (the final grand total paid) | null",
  "tip_amount": "number | null (if explicitly stated as tip or gratuity on the receipt)"
}

Guidelines for extraction:
- If a value is not clearly present or cannot be confidently extracted, use null for that field or an empty array for list fields like line_items, discounts, tax_details.
- All monetary amounts must be extracted as numbers (float or integer), without currency symbols or commas (e.g., 165000 not "165,000 IDR").
- For line_items:
    - 'item_description' should be as complete as possible.
    - 'quantity' should be a number; default to 1.0 if not specified.
    - 'item_total_price' is the total price for that line entry. If a unit price and quantity are given, calculate this total.
- For 'subtotal': If a subtotal is explicitly printed before overall discounts, use that. Otherwise, it can be inferred as the sum of 'item_total_price' from 'line_items'.
- For 'discounts': List any overall bill discounts. The 'amount' should always be a positive number representing the value of the discount. If a percentage discount is applied to the subtotal, calculate and provide the numeric discount amount.
- For 'tax_details': Tax is typically calculated on the subtotal *after* any 'discounts' have been applied. Extract the 'tax_label' (e.g., "PBI 10%") and the final numeric 'tax_amount'.
- The output must be only the JSON object, starting with '{' and ending with '}'. Do not add any other text.
"""
    return prompt

def extract_receipt_data_with_gemini(image_bytes: bytes, api_key: str | None = None) -> dict[str, Any]:
    """Extracts receipt data from an image using the Gemini API."""
    start_time = time.time()
    
    current_api_key = api_key or GEMINI_API_KEY
    if not current_api_key:
        return {"Error": "Gemini API Key not configured."}
    
    # Ensure genai is configured with the potentially overridden key for this call
    # This is only necessary if you allow api_key to be passed per call and it differs from the global config
    if api_key and api_key != genai. अभीकृत_api_key: # Fictitious attribute, real check might be more complex or just reconfigure
         genai.configure(api_key=api_key)


    try:
        print(f"Initializing Gemini model: {MODEL_NAME}")
        # Safety settings can be adjusted if content is being filtered unexpectedly
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        model = genai.GenerativeModel(MODEL_NAME, safety_settings=safety_settings)

        img = PIL.Image.open(io.BytesIO(image_bytes))
        prompt_text = generate_gemini_prompt_with_discounts()
        contents = [prompt_text, img]

        print("Sending request to Gemini API...")
        generation_config = genai.types.GenerationConfig(
            temperature=0.1, # Low temperature for factual extraction
            max_output_tokens=4096,
            # response_mime_type="application/json" # Enable if your Gemini model version supports it for strict JSON output
        )

        response = model.generate_content(contents, generation_config=generation_config)
        
        print(f"Gemini API response received in {time.time() - start_time:.2f} seconds.")

        if not response.candidates or not response.candidates[0].content.parts:
             print("Error: Gemini response is empty or malformed."); print("Full response:", response)
             return {"Error": "Gemini response was empty or malformed."}

        raw_json_text = response.text
        print("\n--- Raw Gemini Response Text (Discount Prompt) ---"); print(raw_json_text); print("--------------------------------\n")

        if raw_json_text.startswith("```json"): raw_json_text = raw_json_text[7:]
        if raw_json_text.endswith("```"): raw_json_text = raw_json_text[:-3]
        raw_json_text = raw_json_text.strip()

        try:
            parsed_data = json.loads(raw_json_text)
            
            # Basic type conversion for numeric fields
            for item in parsed_data.get("line_items", []):
                if isinstance(item, dict):
                    item["quantity"] = float(item.get("quantity", 1.0)) if item.get("quantity") is not None else 1.0
                    item["item_total_price"] = float(item.get("item_total_price", 0.0)) if item.get("item_total_price") is not None else 0.0
            
            for tax_item in parsed_data.get("tax_details", []):
                if isinstance(tax_item, dict):
                    tax_item["tax_amount"] = float(tax_item.get("tax_amount", 0.0)) if tax_item.get("tax_amount") is not None else 0.0

            for disc_item in parsed_data.get("discounts", []):
                if isinstance(disc_item, dict):
                    disc_item["amount"] = float(disc_item.get("amount", 0.0)) if disc_item.get("amount") is not None else 0.0
            
            for key in ["subtotal", "total_amount", "tip_amount"]:
                if key in parsed_data and parsed_data[key] is not None:
                    try: parsed_data[key] = float(parsed_data[key])
                    except (ValueError, TypeError): parsed_data[key] = None # Or 0.0 if preferred for missing numeric
                elif key in parsed_data and parsed_data[key] is None:
                    pass # Keep it None
                else: # Key not present, ensure it's None or 0.0 for consistency if needed later
                    parsed_data[key] = None


            return parsed_data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}. Raw text: {raw_json_text[:500]}...")
            return {"Error": f"Failed to parse JSON from Gemini: {e}."}
    except Exception as e:
        print(f"An error occurred calling Gemini API: {e}")
        # import traceback; traceback.print_exc() # For more detailed error
        return {"Error": f"Gemini API call failed: {str(e)}"}

if __name__ == '__main__':
    # ... (your test block remains the same, ensure GEMINI_API_KEY is set for testing)
    if not GEMINI_API_KEY: print("Skipping direct test: GEMINI_API_KEY not set.")
    else:
        test_image_path = "path/to/your/sample_receipt_with_discount.png" # Use a relevant image
        if not os.path.exists(test_image_path): print(f"Test image not found: {test_image_path}")
        else:
            print(f"Testing with image: {test_image_path}")
            with open(test_image_path, "rb") as f: img_bytes = f.read()
            data = extract_receipt_data_with_gemini(img_bytes)
            print("\n--- Processed Data (with discount prompt) ---")
            if "Error" in data: print(f"Error: {data['Error']}")
            else: print(json.dumps(data, indent=2))