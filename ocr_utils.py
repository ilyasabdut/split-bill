import easyocr
import re
from PIL import Image # PIL is imported but not used in extract_text_from_image, could be removed if not needed elsewhere

def extract_text_from_image(uploaded_file):
    """
    Extracts text from an uploaded image file using EasyOCR.

    Args:
        uploaded_file (streamlit.runtime.uploaded_file_manager.UploadedFile): The file uploaded via Streamlit.

    Returns:
        str: The extracted text.
    """
    # Initialize EasyOCR reader for English.
    # Consider moving this outside the function or using caching (st.cache_resource)
    # if initialization is slow and happens frequently.
    # Note: The main.py file now has a cached reader function, but this function
    # currently initializes its own. For performance, this function should ideally
    # accept the cached reader as an argument.
    reader = easyocr.Reader(['en'])

    # Read the content of the uploaded file as bytes
    image_bytes = uploaded_file.getvalue()

    # Pass the bytes content to EasyOCR's readtext function
    results = reader.readtext(image_bytes)

    text = ""
    # Sort results by vertical position to improve text flow
    # Sort by y-coordinate of the top-left corner of the bounding box
    results.sort(key=lambda r: r[0][0][1])

    for (bbox, text_content, prob) in results:
        text += text_content + "\n"
    return text

def parse_receipt_text(text):
    """
    Parses the raw text extracted from a receipt to find items, quantities, prices,
    and automatically detect tax based on keywords.
    This version attempts to handle price-item-quantity across multiple lines
    based on the provided example text structure, with more flexible number parsing
    and added debugging prints. Returns numbers as cleaned strings (without separators).

    Args:
        text (str): The raw text extracted from the receipt.

    Returns:
        dict: A dictionary containing:
              - 'items' (list): List of dictionaries for each item, with 'qty' and 'price' as strings.
              - 'total_tax' (str): The detected total tax amount as a string.
              - 'total_tip' (str): Placeholder for detected tip amount as a string (not implemented yet).
    """
    print("\n--- Raw Text for Parsing ---")
    print(text)
    print("----------------------------\n")

    lines = text.strip().splitlines()
    items = []
    total_tax_str = "0" # Store as string, default to "0"
    total_tip_str = "0" # Store as string (Placeholder for tip detection), default to "0"

    i = 0

    # Regex for price: digits, commas, dots, potentially at the start/end of the line
    # Allows for optional currency symbols or spaces
    # Captures the number part including commas/dots
    price_pattern = re.compile(r"^\s*[\$\£\€]?\s*([\d,.]+)\s*$", re.IGNORECASE)

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
    # Returns cleaned string, does NOT convert to float here
    def clean_number_string(num_str):
        """Removes spaces, commas, and dots, returns cleaned string."""
        if not isinstance(num_str, str):
            # print(f"Debug: clean_number_string received non-string: {num_str}") # Avoid excessive prints
            return "0" # Return default string for non-strings

        num_str = num_str.strip() # Strip leading/trailing spaces

        # Remove ALL commas and dots
        cleaned_str = num_str.replace(',', '').replace('.', '')

        # Remove any characters that are not digits after removing separators
        cleaned_str = re.sub(r'[^\d]', '', cleaned_str)


        # Ensure it's not an empty string after cleaning
        if not cleaned_str:
             return "0" # Return "0" for empty string

        return cleaned_str

    while i < len(lines):
        line = lines[i].strip()
        # print(f"Debug: Processing line {i+1}: '{line}'") # Too verbose

        # --- Attempt to match the multi-line item pattern 1: Price -> Item Name -> Quantity ---
        # Check if current line is a price, next is item name, line after is quantity
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

                        # Clean price and quantity strings
                        cleaned_price_str = clean_number_string(price_str)
                        cleaned_quantity_str = clean_number_string(quantity_str)

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

                          # Clean price and quantity strings
                          cleaned_price_str = clean_number_string(price_str)
                          cleaned_quantity_str = clean_number_string(quantity_str)

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

            # Clean price and quantity strings
            cleaned_price_str = clean_number_string(price_str)
            cleaned_quantity_str = clean_number_string(quantity_str)

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
                cleaned_amount_str = clean_number_string(next_line)

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


# Example usage (for testing the function independently if needed)
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
