# src/split_logic.py
import re
from typing import List, Dict, Any # Python 3.9+
import json
def clean_number_string(num_str: str) -> str:
    """Clean number string by removing non-numeric characters (except .) and spaces."""
    if not isinstance(num_str, str): return ""
    num_str = num_str.replace(" ", "").replace(",", "")
    return re.sub(r'[^\d.]', '', num_str)

def parse_quantity(num_str: str) -> float | None: # Python 3.10+ type hint
    """Parse quantity string to float, handling common formats including decimals."""
    if not isinstance(num_str, str): return None
    num_str_cleaned = num_str.replace("x", "", 1).replace("X", "", 1).strip().lower() # Replace only first 'x'
    match = re.match(r'^(\d+(?:[.,]\d*)?)$', num_str_cleaned) # Allows 1 or 1.0 or 1,0 or 1.
    if match:
        quantity_str_standardized = match.group(1).replace(',', '.')
        try:
            # Handle cases like "1." -> "1.0"
            if quantity_str_standardized.endswith('.'):
                quantity_str_standardized += '0'
            val = float(quantity_str_standardized)
            return val if val > 0 else None # Quantity should be positive
        except ValueError: return None
    return None

def clean_and_convert_number(num_str: str | int | float, is_quantity: bool = False) -> float | None: # Python 3.10+
    """Clean and convert number string/value to float."""
    if isinstance(num_str, (int, float)): return float(num_str)
    if not isinstance(num_str, str): return None
    num_str_stripped = num_str.strip()
    if not num_str_stripped: return None

    if is_quantity: return parse_quantity(num_str_stripped)
    else: # For prices, tax, tip, discounts
        # Handle potential European decimal format first if a comma is present and only one dot or no dot.
        if ',' in num_str_stripped and num_str_stripped.count('.') <= 1:
            try: # Attempt to interpret comma as decimal if it makes sense
                temp_str = num_str_stripped.replace('.', '').replace(',', '.') # 1.234,56 -> 1234.56
                return float(temp_str)
            except ValueError:
                pass # Fall through to standard cleaning if that fails
        
        # Standard cleaning (removes all commas, keeps one dot)
        cleaned = clean_number_string(num_str_stripped)
        try: return float(cleaned) if cleaned else None
        except ValueError: return None


def calculate_split(
    assignments,
    tax_amount_str: str,
    tip_amount_str: str,
    person_names: List[str],
    split_evenly_flag: bool = False,
    overall_subtotal_for_even_split: float = 0.0,
    total_discount_amount: float = 0.0 # Should be a positive value
) -> Dict[str, Any]:
    if not person_names:
        return {"Error": "Please enter at least one person's name."}

    tax_amount = clean_and_convert_number(tax_amount_str) or 0.0
    tip_amount = clean_and_convert_number(tip_amount_str) or 0.0
    
    # Ensure total_discount_amount is positive, as it represents a reduction
    actual_total_discount = abs(clean_and_convert_number(total_discount_amount) or 0.0)


    split_results = {name: {"items": [], "subtotal": 0.0, "tax": 0.0, "tip": 0.0, "total": 0.0} for name in person_names}
    
    # This is the subtotal to be used for tax/tip proportioning.
    # It starts as sum of items (or provided overall subtotal) and then discount is subtracted.
    subtotal_basis_for_tax_tip = 0.0

    if split_evenly_flag:
        print(f"Splitting bill evenly. Initial overall subtotal: {overall_subtotal_for_even_split}, Discount: {actual_total_discount}")
        subtotal_after_discount = overall_subtotal_for_even_split - actual_total_discount
        if subtotal_after_discount < 0: subtotal_after_discount = 0.0
        
        subtotal_basis_for_tax_tip = subtotal_after_discount
        
        cost_per_person_even = subtotal_basis_for_tax_tip / len(person_names) if person_names else 0
        
        for person in person_names:
            split_results[person]["subtotal"] = cost_per_person_even
            split_results[person]["items"].append({
                "item": "Even Share of Bill (after discount)", "qty_share": 1.0,
                "price_per_unit": cost_per_person_even, "share_cost": cost_per_person_even
            })
    else: # Individual item assignment logic
        current_calculated_subtotal_from_items = 0.0
        for assignment in assignments:
            item_details = assignment.item_details
            assigned_to_list = assignment.assigned_to
            item_name = item_details.get("item", "Unknown")
            line_item_quantity = clean_and_convert_number(item_details.get("qty", "1"), is_quantity=True) or 1.0
            line_item_total_price = clean_and_convert_number(item_details.get("price", "0.0")) or 0.0

            if not assigned_to_list: # Unassigned items don't contribute to anyone's subtotal or the bill's subtotal
                print(f"Info: Item '{item_name}' not assigned, cost not included in split.")
                continue

            current_calculated_subtotal_from_items += line_item_total_price
            
            price_per_single_unit = line_item_total_price / line_item_quantity if line_item_quantity > 0 else line_item_total_price
            cost_per_person_for_this_item = line_item_total_price / len(assigned_to_list) if assigned_to_list else 0
            quantity_share_per_person = line_item_quantity / len(assigned_to_list) if assigned_to_list else 0

            for person in assigned_to_list:
                if person in split_results:
                    split_results[person]["items"].append({"item": item_name, "qty_share": quantity_share_per_person, "price_per_unit": price_per_single_unit, "share_cost": cost_per_person_for_this_item})
                    split_results[person]["subtotal"] += cost_per_person_for_this_item
        
        # Apply overall discount proportionally to each person's item-based subtotal
        subtotal_basis_for_tax_tip = current_calculated_subtotal_from_items # Start with sum of assigned items
        if actual_total_discount > 0 and current_calculated_subtotal_from_items > 0:
            print(f"Applying total discount of {actual_total_discount} proportionally to item-based subtotals.")
            for person in person_names:
                person_subtotal_before_discount = split_results[person]["subtotal"]
                # Proportion based on their share of the item costs
                proportion_of_subtotal = person_subtotal_before_discount / current_calculated_subtotal_from_items if current_calculated_subtotal_from_items > 0 else 0
                person_discount_share = actual_total_discount * proportion_of_subtotal
                split_results[person]["subtotal"] -= person_discount_share
                if split_results[person]["subtotal"] < 0: split_results[person]["subtotal"] = 0.0
            subtotal_basis_for_tax_tip -= actual_total_discount # Reduce the basis for tax/tip
            if subtotal_basis_for_tax_tip < 0: subtotal_basis_for_tax_tip = 0.0
        elif actual_total_discount > 0 and current_calculated_subtotal_from_items == 0:
            # This case implies discount exists but no items were assigned a cost.
            # The discount can't be applied to item subtotals. It effectively reduces the amount tax/tip might be based on if they are a % of "something"
            # For now, we assume if no items assigned, discount is just noted but doesn't reduce anyone's share to negative.
            # Tax/tip will be split evenly later.
            print(f"Note: Discount of {actual_total_discount} exists but no item costs to apply it against proportionally.")


    # --- Tax and Tip Distribution (based on subtotal_basis_for_tax_tip) ---
    if subtotal_basis_for_tax_tip == 0:
        if tax_amount > 0 or tip_amount > 0:
            print("Subtotal basis for tax/tip is zero, distributing tax/tip evenly.")
            num_people = len(person_names)
            tax_per_person_even = tax_amount / num_people if num_people > 0 else 0
            tip_per_person_even = tip_amount / num_people if num_people > 0 else 0
            for person in person_names:
                split_results[person]["tax"] = tax_per_person_even
                split_results[person]["tip"] = tip_per_person_even
    else:
        for person_name in person_names:
            person_subtotal_after_discount = split_results[person_name]["subtotal"]
            proportion = person_subtotal_after_discount / subtotal_basis_for_tax_tip if subtotal_basis_for_tax_tip > 0 else 0
            split_results[person_name]["tax"] = tax_amount * proportion
            split_results[person_name]["tip"] = tip_amount * proportion

    # --- Calculate Total per person and Round ---
    for person_name in person_names:
        data = split_results[person_name]
        data["subtotal"] = round(data["subtotal"], 2)
        data["tax"] = round(data["tax"], 2)
        data["tip"] = round(data["tip"], 2)
        data["total"] = round(data["subtotal"] + data["tax"] + data["tip"], 2)
        for item_share in data["items"]:
            item_share["qty_share"] = round(item_share.get("qty_share", 0), 3)
            item_share["price_per_unit"] = round(item_share.get("price_per_unit", 0), 2)
            item_share["share_cost"] = round(item_share.get("share_cost", 0), 2)
            
    return split_results

def process_item_assignments(assignments):
    """Helper function to process item assignments"""
    assignments_dict = {}
    for assignment in assignments:
        # Access fields using dot notation instead of dictionary access
        item_details = assignment.item_details
        assigned_to = assignment.assigned_to
        item_desc = item_details.get("item", "")
        item_price = clean_and_convert_number(item_details.get("price", 0))
        item_qty = clean_and_convert_number(item_details.get("qty", 1))
        
        if not item_price or not item_qty:
            continue

        for person in assigned_to:
            if person not in assignments_dict:
                assignments_dict[person] = []
            assignments_dict[person].append({
                "item": item_desc,
                "price": item_price,
                "qty": item_qty,
                "share_count": len(assigned_to)
            })
    
    return assignments_dict

if __name__ == '__main__':
    # Test cases for calculate_split
    sample_assignments = [
        {"item_details": {"item": "Burger A", "qty": "1", "price": "10.00"}, "assigned_to": ["Alice"]},
        {"item_details": {"item": "Burger B", "qty": "1", "price": "12.00"}, "assigned_to": ["Bob"]},
        {"item_details": {"item": "Fries", "qty": "1", "price": "5.00"}, "assigned_to": ["Alice", "Bob", "Charlie"]},
    ]
    people = ["Alice", "Bob", "Charlie"]
    tax_str = "2.70" # 10% of (10+12+5) = 2.7
    tip_str = "4.00"
    
    print("--- Test: Individual Items, No Discount ---")
    results_no_disc = calculate_split(sample_assignments, tax_str, tip_str, people)
    print(json.dumps(results_no_disc, indent=2))
    # Expected Alice Subtotal: 10 + 5/3 = 11.67
    # Expected Bob Subtotal:   12 + 5/3 = 13.67
    # Expected Charlie Subtotal: 0 + 5/3 = 1.67
    # Total Item Subtotal = 27.00. Tax/Tip based on this.

    print("\n--- Test: Individual Items, With Overall Discount ---")
    # Discount $7.00. New subtotal basis for tax/tip is 27.00 - 7.00 = 20.00
    # Tax should be 10% of 20.00 = 2.00. (Adjust tax_str for test)
    results_with_disc = calculate_split(sample_assignments, "2.00", tip_str, people, total_discount_amount=7.00)
    print(json.dumps(results_with_disc, indent=2))
    # Alice subtotal before disc share: 11.67. Her share of discount: 7.00 * (11.67/27.00) = 3.02
    # Alice subtotal after disc share: 11.67 - 3.02 = 8.65

    print("\n--- Test: Split Evenly, No Discount ---")
    # Overall subtotal from items = 27.00
    results_even_no_disc = calculate_split([], tax_str, tip_str, people, 
                                           split_evenly_flag=True, 
                                           overall_subtotal_for_even_split=27.00, 
                                           total_discount_amount=0.0)
    print(json.dumps(results_even_no_disc, indent=2))
    # Each person's subtotal: 27.00 / 3 = 9.00. Tax/Tip based on this.

    print("\n--- Test: Split Evenly, With Discount ---")
    # Overall subtotal 27.00, discount 7.00. Subtotal basis for tax/tip = 20.00
    # Tax = 10% of 20 = 2.00
    results_even_with_disc = calculate_split([], "2.00", tip_str, people, 
                                             split_evenly_flag=True, 
                                             overall_subtotal_for_even_split=27.00, 
                                             total_discount_amount=7.00)
    print(json.dumps(results_even_with_disc, indent=2))
    # Each person's subtotal: (27.00 - 7.00) / 3 = 20.00 / 3 = 6.67
