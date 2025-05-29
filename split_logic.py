# split_logic.py
import re
from typing import Optional, Union

def clean_number_string(num_str: str) -> str:
    """Clean number string by removing non-numeric characters (except .)"""
    num_str = num_str.replace(" ", "")  # Remove spaces first
    num_str = num_str.replace(",", "") # Remove comma
    return re.sub(r'[^\d.]', '', num_str)

def parse_quantity(num_str: str) -> Optional[float]:
    """Parse quantity string to float, handling common formats."""
    num_str = num_str.replace("x", "").strip()  # Remove "x" and spaces
    match = re.match(r'^(\d+)[.,]?\d*$', num_str)  # Match integer or decimal
    return float(match.group(1)) if match else None

def clean_and_convert_number(num_str: Union[str, int, float], is_quantity: bool = False) -> Optional[float]:
    """Clean and convert number string to float, with special handling for quantities.
    
    Args:
        num_str: Input string/number to convert
        is_quantity: Whether to use quantity parsing rules
        
    Returns:
        Converted float or None if invalid
    """
    if not isinstance(num_str, str):
        return float(num_str) if isinstance(num_str, (int, float)) else None
        
    num_str = num_str.strip()
    if not num_str:
        return None

    # Try quantity-specific parsing first
    if is_quantity:
        quantity = parse_quantity(num_str)
        if quantity is not None:
            return quantity

    cleaned = clean_number_string(num_str)
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


from typing import List, Dict, Any, Union

def validate_inputs(person_names: List[str]) -> Dict[str, Any]:
    """Validate people names input"""
    if not person_names:
        return {"Error": "Please enter names for the people splitting the bill."}
    return {"people": person_names}

def initialize_results(person_names: List[str]) -> Dict[str, Dict[str, Any]]:
    """Initialize empty results structure"""
    return {
        name: {"items": [], "subtotal": 0.0, "tax": 0.0, "tip": 0.0, "total": 0.0} 
        for name in person_names
    }

def process_item_assignment(
    assignment: Dict[str, Any], 
    results: Dict[str, Dict[str, Any]], 
    total_bill_subtotal: float
) -> float:
    """Process a single item assignment and update results"""
    item = assignment["item_details"]
    assigned_to = assignment.get("assigned_to", [])
    
    qty = clean_and_convert_number(item.get("qty", "0"), is_quantity=True) or 0.0
    price = clean_and_convert_number(item.get("price", "0.0")) or 0.0
    item_total = qty * price
    
    if price <= 0 or qty <= 0 or not assigned_to:
        return total_bill_subtotal
        
    cost_per_share = item_total / len(assigned_to) if assigned_to else 0
    for person in assigned_to:
        if person in results:
            results[person]["items"].append({
                "item": item.get("item", "Unknown Item"),
                "qty": qty,
                "price": price,
                "share_cost": cost_per_share
            })
            results[person]["subtotal"] += cost_per_share
    
    return total_bill_subtotal + item_total

def calculate_split(
    item_assignments: List[Dict[str, Any]], 
    tax_amount_str: str, 
    tip_amount_str: str, 
    person_names: List[str]
) -> Dict[str, Any]:
    """Calculate bill split based on item assignments, tax, tip and people.
    
    Args:
        item_assignments: List of item assignments with 'item_details' and 'assigned_to'
        tax_amount_str: Tax amount as string
        tip_amount_str: Tip amount as string 
        person_names: List of names of people splitting
        
    Returns:
        Dictionary with split results per person or error
    """
    if not person_names:
        return {"Error": "Please enter names for the people splitting the bill."}

    # Convert tax and tip strings to floats
    tax_amount = clean_and_convert_number(tax_amount_str) or 0.0
    tip_amount = clean_and_convert_number(tip_amount_str) or 0.0

    # Initialize results structure for each person
    split_results = {name: {"items": [], "subtotal": 0.0, "tax": 0.0, "tip": 0.0, "total": 0.0} for name in person_names}
    total_bill_subtotal = 0.0 # Sum of costs of all assigned items

    # --- Step 1: Calculate subtotal per person based on assigned items ---
    for assignment in item_assignments:
        item = assignment["item_details"]
        assigned_to = assignment["assigned_to"]

        item_name = item.get("item", "Unknown Item")
        quantity_str = item.get("qty", "0") # Expect string
        price_str = item.get("price", "0.0") # Expect string

        # Convert quantity and price strings to numbers using the robust cleaner
        quantity = clean_and_convert_number(quantity_str, is_quantity=True) or 0.0 # Use quantity flag
        price = clean_and_convert_number(price_str, is_quantity=False) or 0.0 # Don't use quantity flag for price

        # Basic validation: price and quantity should be > 0 for calculation
        if price <= 0 or quantity <= 0:
             print(f"Warning: Item '{item_name}' has non-positive price ({price}) or quantity ({quantity}). Skipping calculation for this item.")
             continue # Skip this item if price or quantity is invalid/zero

        item_total_cost = quantity * price

        # If no one is assigned, this item's cost is not included in the split calculation
        if not assigned_to:
            print(f"Warning: Item '{item_name}' is not assigned to anyone. Its cost ({item_total_cost:.2f}) will not be included in the split.")
            continue # Skip to the next assignment

        # Calculate the cost share for this item per person assigned
        # Avoid division by zero if assigned_to is somehow empty despite the check above
        if len(assigned_to) > 0:
             cost_per_share = item_total_cost / len(assigned_to)
        else:
             print(f"Warning: Item '{item_name}' has an empty assigned_to list unexpectedly.")
             continue


        # Add the cost share to the subtotal of each assigned person
        for person in assigned_to:
            if person in split_results:
                # Store original price and quantity (as numbers now) for breakdown display
                split_results[person]["items"].append({"item": item_name, "qty": quantity, "price": price, "share_cost": cost_per_share}) # Don't round yet
                split_results[person]["subtotal"] += cost_per_share
            else:
                # This case should ideally not happen if person_names is correctly generated
                print(f"Warning: Assigned person '{person}' not found in the list of people splitting.")

        # Add the item's total cost to the overall bill subtotal (only if assigned to someone)
        total_bill_subtotal += item_total_cost

    # Handle case where no items were assigned or parsed
    if total_bill_subtotal == 0:
         # If there's tax/tip but no items, distribute tax/tip evenly
         if tax_amount > 0 or tip_amount > 0:
             print("No items assigned, distributing tax/tip evenly.")
             num_people = len(person_names)
             tax_per_person_even = tax_amount / num_people if num_people > 0 else 0
             tip_per_person_even = tip_amount / num_people if num_people > 0 else 0
             for person in person_names:
                 split_results[person]["tax"] = tax_per_person_even
                 split_results[person]["tip"] = tip_per_person_even
                 split_results[person]["total"] = tax_per_person_even + tip_per_person_even
             # Round values before returning
             for person, data in split_results.items():
                 data["tax"] = round(data["tax"], 2)
                 data["tip"] = round(data["tip"], 2)
                 data["total"] = round(data["total"], 2)
             return split_results # Return results with only tax/tip distributed evenly
         else:
             # If no items and no tax/tip, everyone owes 0
             for person in person_names:
                  split_results[person]["total"] = 0.0
             return split_results # Return results with all zeros


    # --- Step 2: Distribute Tax and Tip proportionally ---
    # Tax and tip are distributed based on each person's subtotal relative to the total assigned subtotal
    for person, data in split_results.items():
        person_subtotal = data["subtotal"]
        if total_bill_subtotal > 0: # Avoid division by zero
            proportion = person_subtotal / total_bill_subtotal
            split_results[person]["tax"] = tax_amount * proportion
            split_results[person]["tip"] = tip_amount * proportion
        else:
             # This case should be handled by the total_bill_subtotal == 0 check above,
             # but as a safeguard:
             split_results[person]["tax"] = 0.0
             split_results[person]["tip"] = 0.0


    # --- Step 3: Calculate Total per person ---
    for person, data in split_results.items():
        data["total"] = data["subtotal"] + data["tax"] + data["tip"]

    # --- Step 4: Round all monetary values for display ---
    # Rounding is done at the very end to minimize floating point errors
    for person, data in split_results.items():
        data["subtotal"] = round(data["subtotal"], 2)
        data["tax"] = round(data["tax"], 2)
        data["tip"] = round(data["tip"], 2)
        data["total"] = round(data["total"], 2)
        # Round share_cost within items list
        for item_share in data["items"]:
             # Ensure 'share_cost' key exists before rounding
             if 'share_cost' in item_share:
                 item_share["share_cost"] = round(item_share["share_cost"], 2)
             # Also round original price if needed for display consistency (though main.py formats it)
             if 'price' in item_share:
                  item_share['price'] = round(item_share['price'], 2)


    return split_results

# Example usage (for testing the function independently if needed)
if __name__ == '__main__':
    # Example with strings as returned by ocr_utils
    sample_item_assignments_str = [
        {"item_details": {"item": "Burger", "qty": "2", "price": "7.99"}, "assigned_to": ["Alice", "Bob"]},
        {"item_details": {"item": "Coke", "qty": "1", "price": "2.50"}, "assigned_to": ["Alice"]},
        {"item_details": {"item": "Fries", "qty": "3", "price": "3.00"}, "assigned_to": ["Alice", "Bob", "Charlie"]},
        {"item_details": {"item": "Salad", "qty": "1", "price": "10.00"}, "assigned_to": []},
        {"item_details": {"item": "Item with comma price", "qty": "1", "price": "1,234.56"}, "assigned_to": ["Alice"]},
        {"item_details": {"item": "Item with comma qty", "qty": "1,0", "price": "5.00"}, "assigned_to": ["Bob"]},
        {"item_details": {"item": "Large Item", "qty": "1", "price": "165,000"}, "assigned_to": ["Alice"]}, # Test case for 165,000
        {"item_details": {"item": "Another Item", "qty": "2.0", "price": "50,000"}, "assigned_to": ["Charlie"]}, # Test case for 2.0
    ]
    sample_tax_str = "5.00"
    sample_tip_str = "3.00"
    sample_person_names = ["Alice", "Bob", "Charlie"]

    split = calculate_split(sample_item_assignments_str, sample_tax_str, sample_tip_str, sample_person_names)
    import json
    print(json.dumps(split, indent=2))

    print("\n--- Test Case: No Items Assigned ---")
    sample_item_assignments_empty_str = [
         {"item_details": {"item": "Burger", "qty": "2", "price": "7.99"}, "assigned_to": []},
         {"item_details": {"item": "Coke", "qty": "1", "price": "2.50"}, "assigned_to": []},
    ]
    split_empty_items = calculate_split(sample_item_assignments_empty_str, sample_tax_str, sample_tip_str, sample_person_names)
    print(json.dumps(split_empty_items, indent=2))

    print("\n--- Test Case: No Items, Only Tax/Tip ---")
    split_only_tax_tip = calculate_split([], sample_tax_str, sample_tip_str, sample_person_names)
    print(json.dumps(split_only_tax_tip, indent=2))

    print("\n--- Test Case: No People ---")
    split_no_people = calculate_split(sample_item_assignments_str, sample_tax_str, sample_tip_str, [])
    print(json.dumps(split_no_people, indent=2))
