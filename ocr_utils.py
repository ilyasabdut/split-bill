import easyocr
import re
import cv2
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Optional, Union # Keep imports from split_logic summary
import split_logic # Import split_logic for number cleaning

# Pre-compile regex patterns outside the function for efficiency
# Price pattern: number (with optional comma/dot) potentially with currency, entire line
_price_pattern = re.compile(r"^\s*([\d,]+(?:[\.,]\d+)?)\s*$", re.IGNORECASE)
# Quantity pattern: number (with optional comma/dot), optionally with "x" prefix, entire line
_quantity_pattern = re.compile(r"^\s*(\d+)\s*x\s*$", re.IGNORECASE)
# Item name pattern: contains at least two letters
_item_name_pattern = re.compile(r"[A-Za-z]{2,}", re.IGNORECASE)
# Non-item line pattern: contains only digits and special characters
_non_item_line_pattern = re.compile(r"^[\d\s:\/\-]+$")

# New patterns for single-line items
# Pattern 1: Qty Item Price (e.g., 1.0 PORK BELLY SAMBAL MATA 165,000)
_qty_item_price_pattern = re.compile(r"^\s*(\d+\.?\d*)\s+(.+?)\s+([\d,]+(?:[\.,]\d+)?)\s*$", re.IGNORECASE)
# Pattern 2: Item Qty Price (e.g., Item Name 1.0 120,000) - less common on this receipt but useful
_item_qty_price_pattern = re.compile(r"^\s*(.+?)\s+(\d+\.?\d*)\s+([\d,]+(?:[\.,]\d+)?)\s*$", re.IGNORECASE)


# Keywords for tax detection - Added "PBI"
_tax_keywords = ["SVC CHG", "PB1", "PBI", "PPH", "PPN"]
# Keywords for tip detection (add more as needed)
_tip_keywords = ["TIP", "GRATUITY"]
# Keywords that should NOT be parsed as items (excluding tax/tip keywords handled separately)
_non_item_keywords = ["SUBTTL", "TOTAL"] # Removed SVC CHG, PB1, PBI, PPH, PPN as they are handled in tax/tip logic

# Helper function to clean number strings (price/quantity/tax/tip) - Basic cleaning kept, but will use split_logic for conversion
def clean_number_string_basic(num_str):
    """Removes spaces, keeps commas and dots, returns cleaned string."""
    if not isinstance(num_str, str):
        return "0.0"
    return num_str.strip()

def preprocess_image(image_bytes):
    """Clean and enhance the image before OCR"""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    thresh = cv2.resize(thresh, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)
    return Image.fromarray(thresh)

    for line in lines:
        if any(char.isdigit() for char in line) and "x" not in line:
            # Likely a quantity/price line
            current_item += f" {line}"
            grouped_items.append(current_item.strip())
            current_item = ""
        else:
            # Likely item name or description
            current_item += f" {line}"

    # Add any remaining item text
    if current_item:
        grouped_items.append(current_item.strip())

    return grouped_items


# Modified to accept the reader object
def extract_text_from_image(reader, uploaded_file, progress_callback=None):
    """
    Extracts text from an uploaded image file using enhanced OCR pipeline.

    Args:
        reader: An initialized EasyOCR reader instance.
        uploaded_file: The file uploaded via Streamlit.
        progress_callback: A function to call with progress updates (0-100).

    Returns:
        str: The extracted text, joined by newlines.
    """
    image_bytes = uploaded_file.getvalue()

    # Preprocess image
    processed_img = preprocess_image(image_bytes)

    # OCR with optimized settings and progress updates
    import time
    start_time = time.time()

    if progress_callback:
        progress_callback(10)
    print("Running EasyOCR readtext...")

    # Use the reader object passed to the function, request detailed output
    ocr_result = reader.readtext(
        np.array(processed_img),
        detail=1,  # Returns list of (bbox, text, conf)
        paragraph=False,
        batch_size=4  # Smaller batches for progress updates
    )
    print(f"EasyOCR readtext took {time.time() - start_time:.2f} seconds")

    if progress_callback:
        progress_callback(80)

    # The lines list already contains one string per detected line.
    print("OCR Result:\n", ocr_result)  # Print the OCR result
    return ocr_result


def parse_receipt_text(text):
    import time
    print("Starting parse_receipt_text")
    start_time = time.time()

    if not text:
        print("Empty text received")
        return {"store_name": None, "date": None, "time": None, "items": [], "total_tax": "0.0", "total_tip": "0.0"}

    # Debug the content of OCR result
    print("OCR Result Sample:", text[:5])  # Show a few lines for verification

    # Initialize variables for store name, date, and time
    store_name = None
    date = None
    time = None

    items = []
    total_tax_amount = 0.0 # Use float for summing tax
    total_tip_amount = 0.0 # Use float for summing tip
    # detected_total_str = "0.0" # Optional: for validation

    # Regex patterns are pre-compiled globally

    try:
        i = 0
        print(f"Starting to parse {len(text)} lines of text...")
        while i < len(text):
            bbox, line, confidence = text[i]
            line = line.strip()
            # Avoid printing potentially very long lines
            print(f"Processing line {i+1}/{len(text)}: {line[:100]}{'...' if len(line) > 100 else ''}")

        line_upper = line.upper()

        # --- Attempt to extract store name, date, and time ---
        if store_name is None:
            # Look for store name in the first few lines
            if i < 5 and _item_name_pattern.search(line):
                store_name = line
                print(f"Detected store name: {store_name}")

        if date is None:
            # Look for date patterns
            date_match = re.search(r"(\d{2}[/\-]\d{2}[/\-]\d{4})", line)
            if date_match:
                date = date_match.group(1)
                print(f"Detected date: {date}")

        if time is None:
            # Look for time patterns
            time_match = re.search(r"(\d{2}:\d{2}(?::\d{2})?)", line)
            if time_match:
                time = time_match.group(1)
                print(f"Detected time: {time}")

        # Skip short lines and other garbage
        if len(line) < 2:
            print(f"Skipping short line: '{line}'")
            i += 1
            continue

        # Skip non-item lines based on keywords
        if any(keyword in line_upper for keyword in ["BILL", "DINEIN", "SDC1", "TABLE", "SERVER", "CASHIER", "CUSTOMER", "PAX"]):
            print(f"Skipping non-item keyword line: '{line}'")
            i += 1
            continue

        # Skip lines that contain only digits and special characters
        if _non_item_line_pattern.match(line):
            print(f"Skipping non-item line: '{line}'")
            i += 1
            continue

        # --- Attempt to detect Tax/Tip/Total amounts ---
        # Check if the current line contains a tax or tip keyword
        is_tax_keyword_line = any(keyword in line_upper for keyword in _tax_keywords)
        is_tip_keyword_line = any(keyword in line_upper for keyword in _tip_keywords)
        is_total_keyword_line = "TOTAL" in line_upper

        if is_tax_keyword_line or is_tip_keyword_line or is_total_keyword_line:
             # Try to find a number on the same line at the end
             amount_match = re.search(r"([\d,]+(?:\.\d+)?)$", line)
             if amount_match:
                 cleaned_amount_str = clean_number_string_basic(amount_match.group(1))
                 # Convert to float using split_logic's cleaner for consistency
                 amount_float = split_logic.clean_and_convert_number(cleaned_amount_str) or 0.0

                 if is_tax_keyword_line:
                     total_tax_amount += amount_float # Add to total tax
                     print(f"Detected tax line: '{line}', amount: {amount_float}. Total tax so far: {total_tax_amount}")
                 elif is_tip_keyword_line:
                     total_tip_amount += amount_float # Add to total tip
                     print(f"Detected tip line: '{line}', amount: {amount_float}. Total tip so far: {total_tip_amount}")
                 # Handle total line if needed for validation, but don't add to tax/tip sums
                 # if is_total_keyword_line:
                 #     detected_total_str = cleaned_amount_str
                 #     print(f"Detected total line: '{line}', amount: {detected_total_str}")

                 i += 1 # Consume this line
                 continue # Move to the next iteration
             # If no number found at the end of the current line, check the next line (for TOTAL split across lines)
             elif is_total_keyword_line and i + 1 < len(lines):
                 next_line = lines[i+1].strip()
                 amount_match_next = _quantity_pattern.match(next_line) # Check if next line is just a number
                 if amount_match_next:
                     # Found TOTAL on line i, amount on line i+1
                     # detected_total_str = clean_number_string_basic(amount_match_next.group(1))
                     # print(f"Detected total split across lines: '{line}' and '{next_line}', amount: {detected_total_str}")
                     i += 2 # Consume both lines
                     continue # Move to the next iteration
             # If keyword found but no amount found on this or next line, fall through

        # Skip other non-item keywords that don't have amounts immediately following/on the same line
        # This check should happen *after* the tax/tip/total check, but before item parsing
        if any(keyword in line_upper for keyword in _non_item_keywords):
             print(f"Skipping non-item keyword line: '{line}'")
             i += 1
             continue

        # --- Attempt to match single-line item patterns ---
        # Pattern 1: Qty Item Price (e.g., 1.0 PORK BELLY SAMBAL MATA 165,000)
        qty_item_price_match = _qty_item_price_pattern.match(line)
        if qty_item_price_match:
            quantity_str = qty_item_price_match.group(1)
            item_name = qty_item_price_match.group(2).strip()
            price_str = qty_item_price_match.group(3)

            cleaned_price_str = clean_number_string_basic(price_str)
            cleaned_quantity_str = clean_number_string_basic(quantity_str)

            items.append({"item": item_name, "qty": cleaned_quantity_str, "price": cleaned_price_str})
            print(f"Matched Qty Item Price pattern: Item='{item_name}', Qty='{cleaned_quantity_str}', Price='{cleaned_price_str}'")
            i += 1 # Consume this line
            continue # Move to the next iteration

        # Pattern 2: Item Qty Price (e.g., Item Name 1.0 120,000) - less common on this receipt but useful
        item_qty_price_match = _item_qty_price_pattern.match(line)
        if item_qty_price_match:
            item_name = item_qty_price_match.group(1).strip()
            quantity_str = item_qty_price_match.group(2)
            price_str = item_qty_price_match.group(3)

            cleaned_price_str = clean_number_string_basic(price_str)
            cleaned_quantity_str = clean_number_string_basic(quantity_str)

            items.append({"item": item_name, "qty": cleaned_quantity_str, "price": cleaned_price_str})
            print(f"Matched Item Qty Price pattern: Item='{item_name}', Qty='{cleaned_quantity_str}', Price='{cleaned_price_str}'")
            i += 1 # Consume this line
            continue # Move to the next iteration


        # --- Attempt to match multi-line item pattern: Item Name -> Price ---
        # Check if current line looks like an item name and next line looks like a price
        if i + 1 < len(lines):
            potential_item_name_line = line
            potential_price_line = lines[i+1].strip()

            # Check if current line contains letters and doesn't look like a number/price/known keyword
            is_potential_item_name = (_item_name_pattern.search(potential_item_name_line) is not None and
                                      _price_pattern.match(potential_item_name_line) is None and
                                      _quantity_pattern.match(potential_item_name_line) is None and
                                      not any(keyword in potential_item_name_line.upper() for keyword in _tax_keywords + _tip_keywords + _non_item_keywords))

            # Modified price check: look for a number on the next line
            price_match = re.search(r"([\d,]+(?:[\.,]\d+)?)$", potential_price_line, re.IGNORECASE)

            if is_potential_item_name and price_match:
                # Found the sequence: Item Name (line i), Price (line i+1)
                item_name = potential_item_name_line.replace("Iove", "love").replace("carame]", "caramel")
                price_str = price_match.group(1)

                # Try to extract quantity from the item name line
                qty_match = re.search(r"^(\d+[,.]?\d*)\s+(.+)", item_name, re.IGNORECASE)
                if qty_match:
                    quantity_str = qty_match.group(1)
                    item_name = qty_match.group(2).strip()
                else:
                    quantity_str = "1"  # Assume quantity 1 if not specified

                cleaned_price_str = clean_number_string_basic(price_str)
                cleaned_quantity_str = clean_number_string_basic(quantity_str)

                items.append({"item": item_name, "qty": cleaned_quantity_str, "price": cleaned_price_str})
                print(f"Matched Item -> Price pattern: Item='{item_name}', Qty='{cleaned_quantity_str}', Price='{cleaned_price_str}'")
                i += 2  # Consume these two lines
                continue  # Move to the next iteration

        # --- If none of the specific patterns matched, move to the next line ---
        print(f"No pattern matched for line {i+1}. Skipping.")
        i += 1

            # Debug output every 10 lines (using i)
            if i > 0 and i % 10 == 0:
                print(f"Processed {i} lines, {len(items)} items found so far")

        print(f"Successfully parsed {len(items)} items from receipt!")
        parse_time = time.time() - start_time
        parse_rate = len(text)/parse_time if parse_time > 0 else 0
        print(f"Receipt parsing completed in {parse_time:.2f} seconds ({parse_rate:.1f} lines/sec)")
        # Convert final sums back to strings for the return dict
        final_tax_str = str(round(total_tax_amount, 2)) # Round to 2 decimal places
        final_tip_str = str(round(total_tip_amount, 2)) # Round to 2 decimal places
        print(f"Found {len(items)} items, total tax: {final_tax_str}, total tip: {final_tip_str}")
        return {"items": items, "total_tax": final_tax_str, "total_tip": final_tip_str}
    except Exception as e:
        print("Error during parsing:", e)
        return {"Error": str(e)}

# Keep example usage section for debugging but commented out
if __name__ == '__main__':
    # Updated sample text to match the structure seen in the image and user's OCR output
    sample_text = """
SPORT STUBE
PONDOk INDAH GOLF GALERY
JL. METRO PONDOk INDAH
JAKARTA
Table 404 Pax
BILL : A178622
Server: edi
Cashier: melia
Customer:
DINEIN
24/05/2025 21:08 SDC1 202505241
===========
1.0 PORK BELLY SAMBAL MATA 165,000
1.0 promo guiness stout 210,000
1.0 pink love sour 140,000
1.0 SCRAMBLED PANCAKE LARG 90,000
1.0 PIZZAS SPORT STUBE 120,000
1.0 ice tea 30,000
1.0 caramel latte 70,000
SUBTTL 825,000
SVC CHG 9% 74,250
PBI 10% 89,925
---------
TOTAL 989,175
"""
    # lines = [entry[1] for entry in ocr_result]
    # print("First 3 OCR lines:", [entry[1] for entry in ocr_result[:3]])
    # parsed_data = parse_receipt_text(sample_text)
    # import json
    # print("\n--- Parsed Data ---")
    # print(json.dumps(parsed_data, indent=2))
