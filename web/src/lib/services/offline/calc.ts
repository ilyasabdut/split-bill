import type { ReceiptItem } from '$lib/types/receipt';
import type { ItemAssignment } from '$lib/types/receipt';

/** Split calculation result */
export interface SplitResult {
  [personName: string]: PersonSplit;
}

/** Individual person's split */
export interface PersonSplit {
  total: number;
  items: AssignedItem[];
  tax_share: number;
  tip_share: number;
}

/** Item assigned to a person */
export interface AssignedItem {
  name: string;
  price: number;
  quantity: number;
}

/** Calculate split on client side */
export function calculateSplit(
  people: string[],
  items: ReceiptItem[],
  itemAssignments: ItemAssignment[],
  tax: number,
  tip: number,
  splitEvenly: boolean
): SplitResult {
  // Initialize result
  const result: SplitResult = {};

  for (const person of people) {
    result[person] = {
      total: 0,
      items: [],
      tax_share: 0,
      tip_share: 0,
    };
  }

  // Calculate totals per item
  const itemTotals: Record<string, number> = {};
  for (const item of items) {
    const total = item.price * (item.quantity || 1);
    itemTotals[item.name] = total;
  }

  // Assign items to people
  for (const assignment of itemAssignments) {
    const item = items.find(i => i.name === assignment.item_id);
    if (!item) continue;

    const total = itemTotals[item.name] || 0;
    const assignedPeople = assignment.assigned_to || [];
    const sharePerPerson = total / assignedPeople.length;

    for (const person of assignedPeople) {
      result[person].items.push({
        name: item.name,
        price: item.price,
        quantity: item.quantity || 1,
      });
      result[person].total += sharePerPerson;
    }
  }

  // Add tax and tip
  const totalBeforeTaxTip = people.reduce((sum, person) => sum + result[person].total, 0);
  const totalTaxTip = tax + tip;

  if (splitEvenly) {
    const taxTipPerPerson = totalTaxTip / people.length;
    for (const person of people) {
      result[person].tax_share = taxTipPerPerson / 2;
      result[person].tip_share = taxTipPerPerson / 2;
      result[person].total += taxTipPerPerson;
    }
  } else {
    // Proportional based on their share
    for (const person of people) {
      const personRatio = result[person].total / totalBeforeTaxTip;
      result[person].tax_share = personRatio * tax;
      result[person].tip_share = personRatio * tip;
      result[person].total += personRatio * totalTaxTip;
    }
  }

  return result;
}
