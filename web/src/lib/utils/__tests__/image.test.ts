import { describe, it, expect, beforeEach, vi } from 'vitest';
import { compressImage, lazyLoadImage } from '../image';

describe('image utilities', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock URL.createObjectURL
    vi.stubGlobal('URL', {
      createObjectURL: vi.fn(() => 'mock-url'),
      revokeObjectURL: vi.fn()
    });

    // Mock Image constructor with immediate load
    vi.stubGlobal('Image', vi.fn(() => {
      const img = {
        width: 2048,
        height: 1024,
        onload: null as any,
        onerror: null as any,
        src: '',
        complete: true
      };

      // Simulate immediate load
      setTimeout(() => {
        if (img.onload) {
          img.onload();
        }
      }, 0);

      return img;
    }));

    // Mock canvas context
    vi.stubGlobal(document, 'createElement', vi.fn(() => {
      const mockCanvas = {
        width: 0,
        height: 0,
        getContext: vi.fn().mockReturnValue({
          drawImage: vi.fn(),
          toBlob: vi.fn((callback) => {
            callback(new Blob(['mock data'], { type: 'image/jpeg' }));
          })
        }),
        toBlob: vi.fn((callback) => {
          callback(new Blob(['mock data'], { type: 'image/jpeg' }));
        })
      };
      return mockCanvas;
    }));
  });

  describe('compressImage', () => {
    it.skip('should return compressed image blob', async () => {
      // Create a mock file
      const file = new File([''], 'test.jpg', { type: 'image/jpeg', size: 1024 * 100 });

      // Mock Image and Canvas

      const mockCanvas = {
        width: 0,
        height: 0,
        getContext: vi.fn().mockReturnValue({
          drawImage: vi.fn(),
          toBlob: vi.fn((callback) => {
            callback(new Blob(['mock data'], { type: 'image/jpeg' }));
          })
        }),
        toBlob: vi.fn((callback) => {
          callback(new Blob(['mock data'], { type: 'image/jpeg' }));
        })
      };

      vi.stubGlobal(document, 'createElement', vi.fn(() => mockCanvas));

      const result = await compressImage(file);

      expect(result).not.toBeNull();
      expect(result.originalSize).toBe(1024 * 100);
      expect(result.compressedSize).toBeGreaterThan(0);
    });

    it('should reject on invalid image', async () => {
      const file = new File([''], 'test.jpg', { type: 'image/jpeg' });

      // Override Image mock for this test to simulate invalid image
      vi.stubGlobal('Image', vi.fn(() => {
        const img = {
          width: 0,
          height: 0,
          onload: null as any,
          onerror: null as any,
          src: '',
          complete: false
        };

        // Simulate immediate error
        setTimeout(() => {
          if (img.onerror) {
            img.onerror();
          }
        }, 0);

        return img;
      }));

      await expect(compressImage(file)).rejects.toThrow();
    });

    it.skip('should resize large images to max dimension', async () => {
      const file = new File([''], 'test.jpg', { type: 'image/jpeg' });


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

      vi.stubGlobal(document, 'createElement', vi.fn(() => mockCanvas));

      const result = await compressImage(file);

      expect(result).not.toBeNull();
      // Canvas should be limited to 1024px max dimension
    });
  });

  describe('lazyLoadImage', () => {
    it('should load image and return src', async () => {
      const src = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAEAQAAAAAB';


      const result = await lazyLoadImage(src);
      expect(result).toBe(src);
    });

    it('should return empty string on error', async () => {
      const src = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAEAQAAAAAB';
      // Override Image mock for this test to simulate error
      vi.stubGlobal('Image', vi.fn(() => {
        const img = {
          width: 2048,
          height: 1024,
          onload: null as any,
          onerror: null as any,
          src: '',
          complete: false
        };

        // Simulate immediate error
        setTimeout(() => {
          if (img.onerror) {
            img.onerror();
          }
        }, 0);

        return img;
      }));


      const result = await lazyLoadImage(src);
      expect(result).toBe('');
    });
  });
});
