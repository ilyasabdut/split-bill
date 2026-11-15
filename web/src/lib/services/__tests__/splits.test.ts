import { describe, it, expect, vi } from 'vitest';
import { splitsService } from '../api/splits';

const put = vi.fn(async () => ({}));
vi.mock('../api/client', () => ({ getApiClient: () => ({ put }) }));

describe('SplitsService.setPaid', () => {
  it('PUTs the paid flag to the person on the split', async () => {
    await splitsService.setPaid('abc', 'Mary Jane', true);
    expect(put).toHaveBeenCalledWith('/splits/abc/payments/Mary%20Jane', { paid: true });
  });
});
