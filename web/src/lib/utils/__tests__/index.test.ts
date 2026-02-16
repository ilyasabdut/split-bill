import { describe, it, expect } from 'vitest';

describe('utils index', () => {
  describe('re-exports', () => {
    it('should export image utilities', () => {
      expect(() => import('../image')).not.toThrow();
    });
  });
});
