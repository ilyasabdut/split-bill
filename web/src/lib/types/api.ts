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

/** Receipt upload response */
export interface UploadReceiptResponse {
  parsed_data: ReceiptData;
  receipt_id: string;
}

/** Split calculation request */
export interface CalculateSplitRequest {
  person_names: string[];
  item_assignments: ItemAssignment[];
  tax_amount_input: number;
  tip_amount_input: number;
  split_evenly: boolean;
}

/** Split calculation response */
export interface CalculateSplitResponse {
  split_results: SplitResults;
  split_id: string;
}

/** Shared split data response */
export interface SharedSplitDataResponse {
  split_results: SplitResults;
  receipt_data: ReceiptData;
  created_at: string;
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
