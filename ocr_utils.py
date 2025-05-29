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

    Args:
        text (str): The raw text extracted from the receipt.

    Returns:
        dict: A dictionary containing:
              - 'items' (list): List of dictionaries for each item.
              - 'total_tax' (float): The sum of detected tax amounts.
              - 'total_tip' (float): Placeholder for detected tip amount (not implemented yet).
    """
    print("\n--- Raw Text for Parsing ---")
    print(text)
    print("----------------------------\n")

    lines = text.strip().splitlines()
    items = []
    total_tax = 0.0
    total_tip = 0.0 # Placeholder for tip detection

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

    # Helper function to clean and convert number strings (price/quantity/tax/tip)
    def clean_and_convert_number(num_str):
        """Removes commas and converts string to float."""
        if not isinstance(num_str, str):
            return None # Ensure input is a string

        # Remove thousands separators (commas)
        cleaned_str = num_str.replace(',', '')
        # Handle potential decimal comma if no dot is present (simple heuristic)
        # For now, assuming comma is always thousands separator based on example
        # If decimal comma is possible, more complex logic is needed.
        try:
            return float(cleaned_str)
        except ValueError:
            return None # Return None if conversion fails

    while i < len(lines):
        line = lines[i].strip()

        # --- Attempt to match the multi-line item pattern: Price -> Item Name -> Quantity ---
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

                        # Clean and convert price
                        price = clean_and_convert_number(price_str)
                        if price is None:
                            print(f"Warning: Could not convert price '{price_str}' to number. Skipping sequence starting at line {i+1}.")
                            i += 1 # Move to the next line
                            continue # Continue loop

                        # Clean and convert quantity
                        quantity = clean_and_convert_number(quantity_str)
                        if quantity is None:
                             print(f"Warning: Could not convert quantity '{quantity_str}' to number. Skipping sequence starting at line {i+1}.")
                             i += 1 # Move to the next line
                             continue # Continue loop

                        # Convert quantity to int if it's a whole number like 1.0 -> 1
                        if quantity.is_integer():
                            quantity = int(quantity)


                        # Basic validation: price and quantity should be > 0
                        if price > 0 and quantity > 0:
                             items.append({"item": item_name, "qty": quantity, "price": price})
                             i += 3 # Consume these three lines and move to the next potential item start
                             continue # Successfully parsed a multi-line item, continue loop from new position

        # --- Attempt to match single-line item pattern ---
        # This pattern looks for Item Name, Quantity, and Price all on the same line.
        # Regex: Item Name (greedy) + spaces + Quantity + spaces + Price
        single_line_pattern = re.compile(r"(.+?)\s+(\d+)\s+([\d,.]+)", re.IGNORECASE)
        single_match = single_line_pattern.search(line)
        if single_match:
            item_name = single_match.group(1).strip()
            quantity_str = single_match.group(2)
            price_str = single_match.group(3)

            # Clean and convert price
            price = clean_and_convert_number(price_str)
            if price is None:
                print(f"Warning: Could not convert price '{price_str}' to number. Skipping single-line match on line {i+1}.")
                i += 1 # Move to the next line
                continue # Continue loop

            # Convert quantity (assuming integer for single line)
            try:
                quantity = int(quantity_str)
            except ValueError:
                 print(f"Warning: Could not convert quantity '{quantity_str}' to integer. Skipping single-line match on line {i+1}.")
                 i += 1 # Move to the next line
                 continue # Continue loop

            if price > 0 and quantity > 0:
                 items.append({"item": item_name, "qty": quantity, "price": price})
                 i += 1 # Consume this line
                 continue # Successfully parsed a single-line item, continue loop from new position

        # --- Attempt to detect Tax/Tip amounts ---
        # Check if the current line contains a tax or tip keyword
        is_tax_keyword_line = any(keyword in line.upper() for keyword in tax_keywords)
        is_tip_keyword_line = any(keyword in line.upper() for keyword in tip_keywords)

        if (is_tax_keyword_line or is_tip_keyword_line) and i + 1 < len(lines):
            # If a keyword is found, check the next line for a number (the amount)
            next_line = lines[i+1].strip()
            amount = clean_and_convert_number(next_line)

            if amount is not None:
                if is_tax_keyword_line:
                    total_tax += amount
                    print(f"Detected Tax: {amount} (from line {i+2})") # Print line number of the amount
                    i += 2 # Consume keyword line and amount line
                    continue # Continue loop
                elif is_tip_keyword_line:
                    total_tip += amount
                    print(f"Detected Tip: {amount} (from line {i+2})") # Print line number of the amount
                    i += 2 # Consume keyword line and amount line
                    continue # Continue loop
            else:
                 print(f"Warning: Found tax/tip keyword '{line}' on line {i+1}, but could not parse amount from next line '{next_line}'.")


        # If none of the patterns matched starting at line i, just move to the next line
        i += 1

    # Optional: Add logic here to try and identify SUBTOTAL, TOTAL lines
    # based on keywords and price patterns.

    return {"items": items, "total_tax": total_tax, "total_tip": total_tip}


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
