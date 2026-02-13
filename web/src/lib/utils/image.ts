/** Image optimization utilities */

export interface CompressedImage {
  blob: Blob;
  originalSize: number;
  compressedSize: number;
}

/** Compress image using Canvas */
export async function compressImage(file: File, quality: number = 0.8): Promise<CompressedImage> {
  return new Promise<CompressedImage>((resolve, reject) => {
    const img = new Image();
    const url = URL.createObjectURL(file);

    img.onload = () => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');

      if (!ctx) {
        reject(new Error('Could not get canvas context'));
        return;
      }

      // Calculate new dimensions (max 1024px width)
      let width = img.width;
      let height = img.height;
      const maxDimension = 1024;

      if (width > height && width > maxDimension) {
        height = (height * maxDimension) / width;
        width = maxDimension;
      } else if (height > width && height > maxDimension) {
        width = (width * maxDimension) / height;
        height = maxDimension;
      }

      canvas.width = width;
      canvas.height = height;

      // Compress
      ctx.drawImage(img, 0, 0, width, height);

      canvas.toBlob(
        (blob) => {
          if (!blob) {
            reject(new Error('Compression failed'));
            return;
          }

          const originalSize = file.size;
          const compressedSize = blob.size;

          resolve({
            blob,
            originalSize,
            compressedSize,
          });
        },
        'image/jpeg',
        quality
      );
    };

    img.onerror = () => reject(new Error('Failed to load image'));
    img.src = url;
  });
}

/** Load image lazily */
export function lazyLoadImage(src: string): Promise<string> {
  return new Promise<string>((resolve) => {
    const img = new Image();
    img.onload = () => resolve(src);
    img.onerror = () => resolve(''); // Fallback to empty on error
    img.src = src;
  });
}
