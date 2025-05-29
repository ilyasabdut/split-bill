import easyocr
import re
import cv2
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Optional, Union # Keep imports from split_logic summary

# Pre-compile regex patterns outside the function for efficiency
# Price pattern: number (with optional comma/dot) potentially with currency, entire line
_price_pattern = re.compile(r"^\s*[\$\£\€]?\s*([\d,]+(?:\.\d+)?)\s*$", re.IGNORECASE)
# Quantity pattern: number (with optional comma/dot), entire line
_quantity_pattern = re.compile(r"^\s*([\d,.]+)\s*$", re.IGNORECASE)
# Item name pattern: contains at least two letters
_item_name_pattern = re.compile(r"[A-Za-z]{2,}")
# Single line item pattern: Item Name + Quantity + Price anywhere on the line
_single_line_item_pattern = re.compile(r"(.+?)\s+(\d+)\s+([\d,.]+)", re.IGNORECASE)

# Keywords for tax detection
_tax_keywords = ["SVC CHG", "PB1", "PPH", "PPN"]
# Keywords for tip detection (add more as needed)
_tip_keywords = ["TIP", "GRATUITY"]
# Keywords that should NOT be parsed as items
_non_item_keywords = ["SUBTTL", "SVC CHG", "PBI", "PPN", "TOTAL"]

# Helper function to clean number strings (price/quantity/tax/tip)
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

# This function is currently not used in extract_text_from_image with detail=0
# Keeping it in case the OCR strategy changes.
def group_ocr_lines(lines):
    """Group broken lines into logical item blocks"""
    grouped_items = []
    current_item = ""

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
    # Use the reader object passed to the function
    lines = reader.readtext(
        np.array(processed_img),
        detail=0, # Returns list of strings
        paragraph=False,
        batch_size=4  # Smaller batches for progress updates
    )
    print(f"EasyOCR readtext took {time.time() - start_time:.2f} seconds")

    if progress_callback:
        progress_callback(80)

    # Group lines function is not used with detail=0
    # The lines list already contains one string per detected line.

    # Join with newlines for the parser
    return "\n".join(lines)


def parse_receipt_text(text):
    import time
    start_time = time.time()
    print("\nStarting receipt text parsing...")

    if not text:
        print("Empty text received")
        return {"items": [], "total_tax": "0.0", "total_tip": "0.0"}

    lines = text.strip().splitlines()
    items = []
    total_tax_str = "0.0"
    total_tip_str = "0.0"

    # Regex patterns are pre-compiled globally

    i = 0
    print(f"Starting to parse {len(lines)} lines of text...")
    while i < len(lines):
        line = lines[i].strip()
        # Avoid printing potentially very long lines
        print(f"Processing line {i+1}/{len(lines)}: {line[:100]}{'...' if len(line) > 100 else ''}")

        # --- Attempt to match single-line item pattern ---
        # Looks for Item Name, Quantity, and Price all on the same line.
        single_match = _single_line_item_pattern.search(line) # Use pre-compiled pattern and search()
        if single_match:
            item_name = single_match.group(1).strip()
            quantity_str = single_match.group(2)
            price_str = single_match.group(3)

            # Clean price and quantity strings (basic cleaning)
            cleaned_price_str = clean_number_string_basic(price_str)
            cleaned_quantity_str = clean_number_string_basic(quantity_str)

            # Check if item name is a non-item keyword
            if item_name.upper() not in _non_item_keywords:
               items.append({"item": item_name, "qty": cleaned_quantity_str, "price": cleaned_price_str})
               i += 1 # Consume this line
               continue # Move to the next iteration

        # --- Attempt to match multi-line item pattern 1: Price -> Item Name -> Quantity ---
        # Check if current line is a price, next is item name, line after is quantity
        if i + 2 < len(lines):
            price_match = _price_pattern.match(line) # Use pre-compiled pattern
            if price_match:
                potential_item_name_line = lines[i+1].strip()
                potential_quantity_line = lines[i+2].strip()

                # Check if the next line looks like an item name
                if _item_name_pattern.search(potential_item_name_line): # Use pre-compiled pattern
                     # Check if the line after that looks like a quantity
                     quantity_match = _quantity_pattern.match(potential_quantity_line) # Use pre-compiled pattern

                     if quantity_match:
                        # Found the sequence: Price (line i), Item Name (line i+1), Quantity (line i+2)
                        price_str = price_match.group(1)
                        item_name = potential_item_name_line
                        quantity_str = quantity_match.group(1)

                        # Clean price and quantity strings (basic cleaning)
                        cleaned_price_str = clean_number_string_basic(price_str)
                        cleaned_quantity_str = clean_number_string_basic(quantity_str)

                        # Check if item name is a non-item keyword
                        if item_name.upper() not in _non_item_keywords:
                            items.append({"item": item_name, "qty": cleaned_quantity_str, "price": cleaned_price_str})
                            i += 3 # Consume these three lines
                            continue # Move to the next iteration

        # --- Attempt to match multi-line item pattern 2: Price -> Quantity -> Item Name ---
        # Check if current line is a price, next is quantity, line after is item name
        if i + 2 < len(lines):
            price_match = _price_pattern.match(line) # Use pre-compiled pattern
            if price_match:
                potential_quantity_line = lines[i+1].strip()
                potential_item_name_line = lines[i+2].strip()

                # Check if the next line looks like a quantity
                quantity_match = _quantity_pattern.match(potential_quantity_line) # Use pre-compiled pattern
                if quantity_match:
                     # Check if the line after that looks like an item name
                     if _item_name_pattern.search(potential_item_name_line): # Use pre-compiled pattern
                          # Found the sequence: Price (line i), Quantity (line i+1), Item Name (line i+2)
                          price_str = price_match.group(1)
                          quantity_str = quantity_match.group(1)
                          item_name = potential_item_name_line

                          # Clean price and quantity strings (basic cleaning)
                          cleaned_price_str = clean_number_string_basic(price_str)
                          cleaned_quantity_str = clean_number_string_basic(quantity_str)

                          # Check if item name is a non-item keyword
                          if item_name.upper() not in _non_item_keywords:
                               items.append({"item": item_name, "qty": cleaned_quantity_str, "price": cleaned_price_str})
                               i += 3 # Consume these three lines
                               continue # Move to the next iteration

        # --- Attempt to detect Tax/Tip amounts ---
        # Check if the current line contains a tax or tip keyword
        is_tax_keyword_line = any(keyword in line.upper() for keyword in _tax_keywords) # Use pre-compiled keywords
        is_tip_keyword_line = any(keyword in line.upper() for keyword in _tip_keywords) # Use pre-compiled keywords

        if (is_tax_keyword_line or is_tip_keyword_line):
             if i + 1 < len(lines):
                next_line = lines[i+1].strip()
                cleaned_amount_str = clean_number_string_basic(next_line)

                # Check if the next line actually contains a number using the quantity pattern
                amount_match = _quantity_pattern.match(next_line) # Use pre-compiled quantity pattern
                if amount_match:
                    if is_tax_keyword_line:
                        total_tax_str = cleaned_amount_str
                        i += 2 # Consume keyword line and amount line
                        continue # Move to the next iteration
                    elif is_tip_keyword_line:
                        total_tip_str = cleaned_amount_str
                        i += 2 # Consume keyword line and amount line
                        continue # Move to the next iteration
                # If keyword found but next line doesn't look like an amount, fall through

        # --- If none of the specific patterns matched, move to the next line ---
        # This ensures the loop always progresses if no pattern consumes multiple lines
        i += 1

        # Debug output every 10 lines (using i)
        if i > 0 and i % 10 == 0:
            print(f"Processed {i} lines, {len(items)} items found so far")


    parse_time = time.time() - start_time
    parse_rate = len(lines)/parse_time if parse_time > 0 else 0
    print(f"Receipt parsing completed in {parse_time:.2f} seconds ({parse_rate:.1f} lines/sec)")
    print(f"Found {len(items)} items, tax: {total_tax_str}, tip: {total_tip_str}")
    return {"items": items, "total_tax": total_tax_str, "total_tip": total_tip_str}

# Keep example usage section for debugging but commented out
if __name__ == '__main__':
    sample_text = """
STUBE
SpUKT
poncuk   INAH GOLEGALERY
MEtRO PONDOk  INDAH
JL
JAKARTA
Pax
Table 404
A178622
BILL
edi
Server
Cashier: melia
Customer
DINEIN
202505241
SDC |
24/05/2025 21;08
165,000
PORK  BELLY SAMBAL MATA
1.0
210,000
promo guiness stout
1.0
140,000
pink Iove sour
1,0
90 ,000
SCRAMBLED PANCAKE LARG
1.0
120,000
PIZZAS SPORT  STUBE
1.0
30 ,000
1.0
ice tea
70,000
caramel
latte
1,0
SUBTTL
825 , Q0Q
SVC CHG 97
74,250
PBI107
89,925
989
TOTAL
175
"""
    parsed_data = parse_receipt_text(sample_text)
    import json
    print("\n--- Parsed Data ---")
    print(json.dumps(parsed_data, indent=2))
