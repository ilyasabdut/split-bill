import { getApiClient } from './client';
import { compressImage } from '$lib/utils/image';
import type { UploadReceiptResponse } from '$lib/types/api';

export interface UploadReceiptOptions {
  file: File;
  onProgress?: (progress: number) => void;
}

/** Receipt upload and OCR service */
export class ReceiptsService {
  /** Upload receipt for OCR processing */
  async upload(options: UploadReceiptOptions): Promise<UploadReceiptResponse> {
    const apiClient = getApiClient();

    // Compress image before upload
    const compressed = await compressImage(options.file, 0.8);

    // Create FormData
    const formData = new FormData();
    const fileBlob = compressed.blob;

    // Create new File with compressed blob
    const compressedFile = new File([fileBlob], options.file.name, {
      type: 'image/jpeg',
      lastModified: options.file.lastModified,
    });

    formData.append('file', compressedFile);

    // For large files, use XMLHttpRequest for progress tracking
    if (options.onProgress && options.file.size > 1024 * 1024) {
      return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const progress = Math.round((event.loaded / event.total) * 100);
            options.onProgress!(progress);
          }
        });

        xhr.addEventListener('load', () => {
          if (xhr.status === 200) {
            resolve(JSON.parse(xhr.responseText));
          } else {
            reject(new Error(xhr.responseText));
          }
        });

        xhr.addEventListener('error', () => {
          reject(new Error('Upload failed'));
        });

        xhr.open('POST', `${apiClient['config'].baseURL}/receipts/upload`);
        xhr.setRequestHeader('Authorization', `Bearer ${apiClient['config'].apiKey}`);
        xhr.send(formData);
      });
    }

    return apiClient.postForm<UploadReceiptResponse>('/receipts/upload', formData);
  }

  /** Validate image before upload */
  validateImage(file: File): { valid: boolean; error?: string } {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    const maxSize = 2 * 1024 * 1024; // 2MB

    if (!validTypes.includes(file.type)) {
      return { valid: false, error: 'Invalid file type. Please upload JPEG, PNG, or WebP.' };
    }

    if (file.size > maxSize) {
      return { valid: false, error: `File too large. Maximum size is 2MB.` };
    }

    return { valid: true };
  }
}

export const receiptsService = new ReceiptsService();
