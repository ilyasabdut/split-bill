/** API response wrapper */
export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
}

/** API error structure */
export interface ApiError {
  type: string;
  status_code: number;
  detail: string;
}

/** OCR result, as returned by the API (api/src/services/openrouter_ocr.py ReceiptData) */
export interface OcrReceiptData {
  line_items: { item_description: string; quantity: number; item_total_price: number }[];
  tax_details: { tax_label: string; tax_amount: number }[];
  subtotal?: number | null;
  total_amount?: number | null;
}

/** Receipt upload response */
export interface UploadReceiptResponse {
  parsed_data: OcrReceiptData;
}

/** Split calculation request */
export interface CalculateSplitRequest {
  person_names: string[];
  item_assignments: ItemAssignment[];
  tax_amount_input: number;
  tip_amount_input: number;
  split_evenly: boolean;
  /** Results computed on this device; the share link shows exactly these */
  client_results?: SplitResults;
}

/** Split calculation response */
export interface CalculateSplitResponse {
  split_results: SplitResults;
  split_id: string;
}

/** Shared split data response */
export interface SharedSplitDataResponse {
  split_id: string;
  person_names: string[];
  calculated_split_results: SplitResults;
  /** Epoch seconds */
  creation_timestamp: number;
}

/** Health check response */
export interface HealthResponse {
  status: string;
  version: string;
}

// Import related types
import type { ReceiptData } from './receipt';
import type { ItemAssignment } from './receipt';
import type { SplitResults } from './split';
