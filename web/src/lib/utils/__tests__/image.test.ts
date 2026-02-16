import { describe, it, expect, beforeEach, vi } from 'vitest';
import { compressImage, lazyLoadImage } from '../image';

describe('image utilities', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('compressImage', () => {
    it('should return compressed image blob', async () => {
      // Create a mock file
      const file = new File([''], 'test.jpg', { type: 'image/jpeg' });
      file.size = 1024 * 100; // 100KB

      // Mock Image and Canvas
      const mockImage = {
        width: 2048,
        height: 1024,
        onload: null as any,
        onerror: null() as any,
        src: ''
      };

      const mockCanvas = {
        width: 0,
        height: 0,
        getContext: vi.fn().mockReturnValue({
          drawImage: vi.fn(),
          toBlob: vi.fn((callback) => {
            callback(new Blob(['mock data'], { type: 'image/jpeg' }));
          })
        }),
        toBlob: vi.fn()
      };

      vi.stubGlobal(Image, () => mockImage);
      vi.stubGlobal(document, 'createElement', vi.fn(() => mockCanvas));

      const result = await compressImage(file);

      expect(result).not.toBeNull();
      expect(result.originalSize).toBe(1024 * 100);
      expect(result.compressedSize).toBeGreaterThan(0);
    });

    it('should reject on invalid image', async () => {
      const file = new File([''], 'test.jpg', { type: 'image/jpeg' });

      const mockImage = {
        width: 0,
        height: 0,
        onload: null as any,
        onerror: vi.fn(),
        src: ''
      };

      vi.stubGlobal(Image, () => mockImage);

      await expect(compressImage(file)).rejects.toThrow();
    });

    it('should resize large images to max dimension', async () => {
      const file = new File([''], 'test.jpg', { type: 'image/jpeg' });

      const mockImage = {
        width: 2048,
        height: 2048,
        onload: null as any,
        onerror: null() as any,
        src: ''
      };

      const mockCanvas = {
        width: 0,
        height: 0,
        getContext: vi.fn().mockReturnValue({
          drawImage: vi.fn(),
          toBlob: vi.fn((callback) => {
            callback(new Blob(['mock data'], { type: 'image/jpeg' }));
          })
        })
      };

      vi.stubGlobal(Image, () => mockImage);
      vi.stubGlobal(document, 'createElement', vi.fn(() => mockCanvas));

      const result = await compressImage(file);

      expect(result).not.toBeNull();
      // Canvas should be limited to 1024px max dimension
    });
  });

  describe('lazyLoadImage', () => {
    it('should load image and return src', async () => {
      const src = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAEAQAAAAAB';
      const mockImage = {
        onload: null as any,
        onerror: null() as any,
        src: ''
      };

      vi.stubGlobal(Image, () => mockImage);

      const result = await lazyLoadImage(src);
      expect(result).toBe(src);
    });

    it('should return empty string on error', async () => {
      const src = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAEAQAAAAAB';
      const mockImage = {
        onload: null as any,
        onerror: vi.fn(),
        src: ''
      };

      vi.stubGlobal(Image, () => mockImage);

      const result = await lazyLoadImage(src);
      expect(result).toBe('');
    });
  });
});
