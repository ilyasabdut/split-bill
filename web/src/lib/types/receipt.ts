/** Parsed receipt data from OCR */
export interface ReceiptData {
  items: ReceiptItem[];
  subtotal?: number;
  tax?: number;
  tip?: number;
  total?: number;
  merchant_name?: string;
  date?: string;
}

/** Individual receipt item */
export interface ReceiptItem {
  name: string;
  price: number;
  quantity?: number;
}

/** Item assignment for split */
export interface ItemAssignment {
  item_id: string;
  assigned_to: string[];
}
