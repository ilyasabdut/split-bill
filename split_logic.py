# split_logic.py

def calculate_split(item_assignments, tax_amount, tip_amount, person_names):
    """
    Calculates the bill split based on item assignments, tax, tip, and people.

    Args:
        item_assignments (list): List of dictionaries like
                                 [{"item_details": {"item": "Burger", "qty": 2, "price": 7.99},
                                   "assigned_to": ["Person 1", "Person 2"]}]
        tax_amount (float): Total tax amount.
        tip_amount (float): Total tip amount.
        person_names (list): List of names of people splitting the bill.

    Returns:
        dict: A dictionary representing the split results per person.
              Example:
              {
                "Alice": {"items": [...], "subtotal": 12.49, "tax": 1.24, "tip": 1.00, "total": 14.73},
                ...
              }
              Returns {"Error": "..."} if there's an issue.
    """
    if not person_names:
        return {"Error": "Please enter names for the people splitting the bill."}

    # Initialize results structure for each person
    split_results = {name: {"items": [], "subtotal": 0.0, "tax": 0.0, "tip": 0.0, "total": 0.0} for name in person_names}
    total_bill_subtotal = 0.0 # Sum of costs of all assigned items

    # --- Step 1: Calculate subtotal per person based on assigned items ---
    for assignment in item_assignments:
        item = assignment["item_details"]
        assigned_to = assignment["assigned_to"]

        item_name = item.get("item", "Unknown Item")
        quantity = item.get("qty", 0)
        price = item.get("price", 0.0)

        item_total_cost = quantity * price

        # If no one is assigned, this item's cost is not included in the split calculation
        if not assigned_to:
            print(f"Warning: Item '{item_name}' is not assigned to anyone. Its cost (${item_total_cost:.2f}) will not be included in the split.")
            continue # Skip to the next assignment

        # Calculate the cost share for this item per person assigned
        cost_per_share = item_total_cost / len(assigned_to)

        # Add the cost share to the subtotal of each assigned person
        for person in assigned_to:
            if person in split_results:
                split_results[person]["items"].append({"item": item_name, "qty": quantity, "price": price, "share_cost": round(cost_per_share, 2)})
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
             tax_per_person_even = tax_amount / len(person_names) if person_names else 0
             tip_per_person_even = tip_amount / len(person_names) if person_names else 0
             for person in person_names:
                 split_results[person]["tax"] = round(tax_per_person_even, 2)
                 split_results[person]["tip"] = round(tip_per_person_even, 2)
                 split_results[person]["total"] = round(tax_per_person_even + tip_per_person_even, 2)
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
    for person, data in split_results.items():
        data["subtotal"] = round(data["subtotal"], 2)
        data["tax"] = round(data["tax"], 2)
        data["tip"] = round(data["tip"], 2)
        data["total"] = round(data["total"], 2)
        # Round share_cost within items list
        for item_share in data["items"]:
             item_share["share_cost"] = round(item_share["share_cost"], 2)


    return split_results

# Example usage (for testing the function independently if needed)
if __name__ == '__main__':
    sample_item_assignments = [
        {"item_details": {"item": "Burger", "qty": 2, "price": 7.99}, "assigned_to": ["Alice", "Bob"]}, # Burger cost: 15.98
        {"item_details": {"item": "Coke", "qty": 1, "price": 2.50}, "assigned_to": ["Alice"]}, # Coke cost: 2.50
        {"item_details": {"item": "Fries", "qty": 3, "price": 3.00}, "assigned_to": ["Alice", "Bob", "Charlie"]}, # Fries cost: 9.00
        {"item_details": {"item": "Salad", "qty": 1, "price": 10.00}, "assigned_to": []}, # Unassigned item
    ]
    sample_tax = 5.00
    sample_tip = 3.00
    sample_person_names = ["Alice", "Bob", "Charlie"]

    split = calculate_split(sample_item_assignments, sample_tax, sample_tip, sample_person_names)
    import json
    print(json.dumps(split, indent=2))

    print("\n--- Test Case: No Items Assigned ---")
    sample_item_assignments_empty = [
         {"item_details": {"item": "Burger", "qty": 2, "price": 7.99}, "assigned_to": []},
         {"item_details": {"item": "Coke", "qty": 1, "price": 2.50}, "assigned_to": []},
    ]
    split_empty_items = calculate_split(sample_item_assignments_empty, sample_tax, sample_tip, sample_person_names)
    print(json.dumps(split_empty_items, indent=2))

    print("\n--- Test Case: No Items, Only Tax/Tip ---")
    split_only_tax_tip = calculate_split([], sample_tax, sample_tip, sample_person_names)
    print(json.dumps(split_only_tax_tip, indent=2))

    print("\n--- Test Case: No People ---")
    split_no_people = calculate_split(sample_item_assignments, sample_tax, sample_tip, [])
    print(json.dumps(split_no_people, indent=2))
