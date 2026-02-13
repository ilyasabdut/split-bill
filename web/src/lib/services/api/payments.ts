import { getApiClient } from './client';

export interface Payment {
  id: number;
  split_id: string;
  from_user_id: number;
  to_user_id: number;
  amount: number;
  currency: string;
  status: 'pending' | 'paid' | 'failed';
  method: 'cash' | 'transfer' | 'app';
  reference?: string;
  paid_at?: string;
  created_at: string;
}

export interface CreatePaymentRequest {
  split_id: string;
  from_user_id: number;
  to_user_id: number;
  amount: number;
  currency: string;
  method: 'cash' | 'transfer' | 'app';
}

export interface UpdatePaymentRequest {
  status?: 'pending' | 'paid' | 'failed';
  reference?: string;
  paid_at?: string;
}

export interface PaymentStats {
  total_payments: number;
  total_amount: number;
  pending_payments: number;
  completed_payments: number;
  average_payment_amount: number;
}

/** Payment tracking service */
export class PaymentsService {
  /** Get all payments for a split */
  async getSplitPayments(splitId: string): Promise<Payment[]> {
    const apiClient = getApiClient();
    return apiClient.get<Payment[]>(`/payments?split_id=${splitId}`);
  }

  /** Get single payment by ID */
  async getPayment(id: number): Promise<Payment> {
    const apiClient = getApiClient();
    return apiClient.get<Payment>(`/payments/${id}`);
  }

  /** Create new payment */
  async createPayment(request: CreatePaymentRequest): Promise<Payment> {
    const apiClient = getApiClient();
    return apiClient.post<Payment>('/payments', request);
  }

  /** Update payment */
  async updatePayment(id: number, request: UpdatePaymentRequest): Promise<Payment> {
    const apiClient = getApiClient();
    return apiClient.post<Payment>(`/payments/${id}`, request);
  }

  /** Mark payment as paid */
  async markAsPaid(id: number, reference?: string): Promise<Payment> {
    const apiClient = getApiClient();
    return apiClient.post<Payment>(`/payments/${id}/paid`, { reference });
  }

  /** Delete payment */
  async deletePayment(id: number): Promise<void> {
    const apiClient = getApiClient();
    return apiClient.get(`/payments/${id}/delete`);
  }

  /** Get payment statistics */
  async getPaymentStats(userId?: number): Promise<PaymentStats> {
    const apiClient = getApiClient();
    const query = userId ? `?user_id=${userId}` : '';
    return apiClient.get(`/payments/stats${query}`);
  }

  /** Get pending payments for user */
  async getPendingPayments(userId: number): Promise<{
    owed_to_others: Payment[];
    owed_by_others: Payment[];
  }> {
    const apiClient = getApiClient();
    return apiClient.get(`/payments/pending/${userId}`);
  }

  /** Generate payment QR code */
  async generatePaymentQR(paymentId: number): Promise<{
    qr_code: string;
    deep_link: string;
  }> {
    const apiClient = getApiClient();
    return apiClient.get(`/payments/${paymentId}/qr`);
  }
}

export const paymentsService = new PaymentsService();
