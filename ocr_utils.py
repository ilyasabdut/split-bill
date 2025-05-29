import easyocr
import re
import cv2
import numpy as np
from PIL import Image

def preprocess_image(image_bytes):
    """Clean and enhance the image before OCR"""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    thresh = cv2.resize(thresh, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)
    return Image.fromarray(thresh)

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
    
    return grouped_items

def extract_text_from_image(uploaded_file, progress_callback=None):
    """
    Extracts text from an uploaded image file using enhanced OCR pipeline.

    Args:
        uploaded_file: The file uploaded via Streamlit.

    Returns:
        str: The extracted and grouped text
    """
    reader = easyocr.Reader(['en'], gpu=False)
    image_bytes = uploaded_file.getvalue()
    
    # Preprocess image
    processed_img = preprocess_image(image_bytes)
    
    # OCR with optimized settings and progress updates
    if progress_callback:
        progress_callback(10)
    lines = reader.readtext(
        np.array(processed_img), 
        detail=0, 
        paragraph=False,
        batch_size=4  # Smaller batches for progress updates
    )
    if progress_callback:
        progress_callback(80)
    
    # Group lines into logical items
    grouped_lines = group_ocr_lines(lines)
    
    # Join with newlines for the parser
    return "\n".join(grouped_lines)

def parse_receipt_text(text):
    """
    Parses the raw text extracted from a receipt to find items, quantities, prices,
    and automatically detect tax based on keywords.
    This version attempts to handle price-item-quantity across multiple lines
    based on the provided example text structure, with more flexible number parsing.
    Returns numbers as raw strings (with spaces, commas, dots).

    Args:
        text (str): The raw text extracted from the receipt.

    Returns:
        dict: A dictionary containing:
              - 'items' (list): List of dictionaries for each item, with 'qty' and 'price' as strings.
              - 'total_tax' (str): The detected total tax amount as a string.
              - 'total_tip' (str): Placeholder for detected tip amount as a string (not implemented yet).
    """
    text = text.strip()

    lines = text.strip().splitlines()
    items = []
    total_tax_str = "0.0" # Store as string, default to "0.0"
    total_tip_str = "0.0" # Store as string (Placeholder for tip detection), default to "0.0"

    i = 0

    # Regex patterns for parsing
    price_pattern = re.compile(r"^\s*[\$\£\€]?\s*([\d,.]+)\s*$", re.IGNORECASE)
    quantity_pattern = re.compile(r"^\s*([\d,.]+)\s*$", re.IGNORECASE)
    single_line_pattern = re.compile(r"(.+?)\s+(\d+(?:\.\d+)?)\s+([0-9,.]+)", re.IGNORECASE)

    # Regex for quantity: digits, optional dot/comma and digits, potentially at the start/end of the line
    # Captures the number part including commas/dots
    quantity_pattern = re.compile(r"^\s*([\d,.]+)\s*$", re.IGNORECASE)

    # Regex for item name: looks like text, contains at least two letters, not just numbers or symbols
    item_name_pattern = re.compile(r"[A-Za-z]{2,}")

    # Keywords for tax detection
    tax_keywords = ["SVC CHG", "PB1", "PPH", "PPN"]
    # Keywords for tip detection (add more as needed)
    tip_keywords = ["TIP", "GRATUITY"] # Placeholder keywords

    # Keywords that should NOT be parsed as items
    non_item_keywords = ["SUBTTL", "SVC CHG", "PBI", "PPN", "TOTAL"]


    # Helper function to clean number strings (price/quantity/tax/tip)
    # Returns cleaned string (only spaces removed), does NOT convert to float here
    def clean_number_string_basic(num_str):
        """Removes spaces, keeps commas and dots, returns cleaned string."""
        if not isinstance(num_str, str):
            return "0.0" # Return default string for non-strings
        return num_str.strip()


    while i < len(lines):
        line = lines[i].strip()
        
        # First try single-line pattern matching
        single_match = single_line_pattern.search(line)
        if single_match:
            item_name = single_match.group(1).strip()
            qty = single_match.group(2)
            price = single_match.group(3)
            price = price.replace(",", "").replace(".", "") if "," in price else price
            
            # Convert numeric values and format
            try:
                qty = float(qty)
                price = float(price) / 100  # Handle IDR format
            except ValueError:
                continue
                
            if item_name.upper() not in non_item_keywords:
                items.append({"item": item_name, "qty": qty, "price": price})
                i += 1
                continue
        if i + 2 < len(lines):
            price_match = price_pattern.match(line)
            if price_match:
                potential_item_name_line = lines[i+1].strip()
                potential_quantity_line = lines[i+2].strip()

                # Check if the next line looks like an item name
                if item_name_pattern.search(potential_item_name_line):
                     # Check if the line after that looks like a quantity
                     quantity_match = quantity_pattern.match(potential_quantity_line)

                     if quantity_match:
                        # Found the sequence: Price (line i), Item Name (line i+1), Quantity (line i+2)
                        price_str = price_match.group(1)
                        item_name = potential_item_name_line
                        quantity_str = quantity_match.group(1)

                        # Clean price and quantity strings (basic cleaning)
                        cleaned_price_str = clean_number_string_basic(price_str)
                        cleaned_quantity_str = clean_number_string_basic(quantity_str)

                        # Check if item name is a non-item keyword
                        if item_name.upper() not in non_item_keywords:
                            # Store cleaned strings
                            items.append({"item": item_name, "qty": cleaned_quantity_str, "price": cleaned_price_str})
                            # print(f"Debug: Parsed P->I->Q item: '{item_name}', Qty: '{cleaned_quantity_str}', Price: '{cleaned_price_str}' (from lines {i+1}-{i+3})") # Removed debug print
                            i += 3 # Consume these three lines and move to the next potential item start
                            continue # Successfully parsed a multi-line item, continue loop from new position
                        # else:
                           # print(f"Debug: P->I->Q pattern matched lines {i+1}-{i+3}, but item name '{item_name}' is a non-item keyword. Skipping.") # Removed debug print


        # --- Attempt to match the multi-line item pattern 2: Price -> Quantity -> Item Name ---
        # Check if current line is a price, next is quantity, line after is item name
        if i + 2 < len(lines):
            price_match = price_pattern.match(line)
            if price_match:
                potential_quantity_line = lines[i+1].strip()
                potential_item_name_line = lines[i+2].strip()

                # Check if the next line looks like a quantity
                quantity_match = quantity_pattern.match(potential_quantity_line)
                if quantity_match:
                     # Check if the line after that looks like an item name
                     if item_name_pattern.search(potential_item_name_line):
                          # Found the sequence: Price (line i), Quantity (line i+1), Item Name (line i+2)
                          price_str = price_match.group(1)
                          quantity_str = quantity_match.group(1)
                          item_name = potential_item_name_line

                          # Clean price and quantity strings (basic cleaning)
                          cleaned_price_str = clean_number_string_basic(price_str)
                          cleaned_quantity_str = clean_number_string_basic(quantity_str)

                          # Check if item name is a non-item keyword
                          if item_name.upper() not in non_item_keywords:
                               # Store cleaned strings
                               items.append({"item": item_name, "qty": cleaned_quantity_str, "price": cleaned_price_str})
                               # print(f"Debug: Parsed P->Q->I item: '{item_name}', Qty: '{cleaned_quantity_str}', Price: '{cleaned_price_str}' (from lines {i+1}-{i+3})") # Removed debug print
                               i += 3 # Consume these three lines and move to the next potential item start
                               continue # Successfully parsed, continue loop from new position
                          # else:
                               # print(f"Debug: P->Q->I pattern matched lines {i+1}-{i+3}, but item name '{item_name}' is a non-item keyword. Skipping.") # Removed debug print


        # --- Attempt to match single-line item pattern ---
        # This pattern looks for Item Name, Quantity, and Price all on the same line.
        # Regex: Item Name (greedy) + spaces + Quantity + spaces + Price
        single_line_pattern = re.compile(r"(.+?)\s+(\d+)\s+([\d,.]+)", re.IGNORECASE)
        single_match = single_line_pattern.search(line)
        if single_match:
            item_name = single_match.group(1).strip()
            quantity_str = single_match.group(2)
            price_str = single_match.group(3)

            # Clean price and quantity strings (basic cleaning)
            cleaned_price_str = clean_number_string_basic(price_str)
            cleaned_quantity_str = clean_number_string_basic(quantity_str)

            # Check if item name is a non-item keyword
            if item_name.upper() not in non_item_keywords:
               # Store cleaned strings
               items.append({"item": item_name, "qty": cleaned_quantity_str, "price": cleaned_price_str})
               # print(f"Debug: Parsed single-line item: '{item_name}', Qty: '{cleaned_quantity_str}', Price: '{cleaned_price_str}' (from line {i+1})") # Removed debug print
               i += 1 # Consume this line
               continue # Successfully parsed a single-line item, continue loop from new position
            # else:
               # print(f"Debug: Single-line pattern matched line {i+1}, but item name '{item_name}' is a non-item keyword. Skipping.") # Removed debug print


        # --- Attempt to detect Tax/Tip amounts ---
        # Check if the current line contains a tax or tip keyword
        is_tax_keyword_line = any(keyword in line.upper() for keyword in tax_keywords)
        is_tip_keyword_line = any(keyword in line.upper() for keyword in tip_keywords)

        if (is_tax_keyword_line or is_tip_keyword_line): # Check keyword first
             # print(f"Debug: Found potential tax/tip keyword on line {i+1}: '{line}'") # Removed debug print
             if i + 1 < len(lines):
                next_line = lines[i+1].strip()
                # print(f"Debug: Checking next line {i+2} for amount: '{next_line}'") # Removed debug print
                cleaned_amount_str = clean_number_string_basic(next_line)

                # We don't sum here, just store the last detected amount for now
                # More sophisticated logic might sum multiple tax lines
                if is_tax_keyword_line:
                    total_tax_str = cleaned_amount_str
                    # print(f"Detected Tax: '{total_tax_str}' (from line {i+2})") # Removed debug print
                    i += 2 # Consume keyword line and amount line
                    continue # Continue loop
                elif is_tip_keyword_line:
                    total_tip_str = cleaned_amount_str
                    # print(f"Detected Tip: '{total_tip_str}' (from line {i+2})") # Removed debug print
                    i += 2 # Consume keyword line and amount line
                    continue # Continue loop
                # else:
                     # print(f"Warning: Found tax/tip keyword '{line}' on line {i+1}, but could not parse amount from next line '{next_line}'.") # Removed debug print
                     # Fall through to general increment i += 1
             # else:
                  # print(f"Warning: Found tax/tip keyword '{line}' on line {i+1}, but no next line to check for amount.") # Removed debug print
                  # Fall through to general increment i += 1


        # If none of the patterns matched starting at line i, just move to the next line
        i += 1

    # print(f"Debug: Finished parsing. Total detected tax (string): '{total_tax_str}', Total detected tip (string): '{total_tip_str}'") # Removed debug print
    # print(f"Debug: Parsed items (strings): {items}") # Removed debug print
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
