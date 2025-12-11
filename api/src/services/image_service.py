"""
Image processing utilities for the application.
"""

import io
import logging
from typing import Optional

from PIL import Image as PILImage
from PIL import UnidentifiedImageError

# Get logger for this module
logger = logging.getLogger(__name__)

# Simple configuration without imports to avoid circular dependencies
MAX_IMAGE_SIZE_BYTES = 2 * 1024 * 1024  # 2MB default


def compress_image(
    image_bytes: bytes,
    target_size_bytes: int = MAX_IMAGE_SIZE_BYTES,
    quality: int = 90,
    min_quality: int = 70,
) -> Optional[bytes]:
    """
    Compress image to meet size requirements.

    Args:
        image_bytes: Raw image bytes
        target_size_bytes: Target size in bytes
        quality: Initial compression quality
        min_quality: Minimum compression quality

    Returns:
        Compressed image bytes or None if compression fails
    """
    try:
        img = PILImage.open(io.BytesIO(image_bytes))
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        compressed_bytes = None
        for q in range(quality, min_quality - 1, -5):
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=q, optimize=True)
            compressed_bytes = buffer.getvalue()

            if len(compressed_bytes) <= target_size_bytes:
                logger.info(
                    f"Image compressed to {len(compressed_bytes) / 1024:.2f} KB with quality {q}"
                )
                return compressed_bytes

        if compressed_bytes and len(compressed_bytes) > target_size_bytes:
            ratio = (target_size_bytes / len(compressed_bytes)) ** 0.5
            new_width = int(img.width * ratio)
            new_height = int(img.height * ratio)

            if new_width > 0 and new_height > 0:
                img_resized = img.resize(
                    (new_width, new_height), PILImage.Resampling.LANCZOS
                )
                buffer = io.BytesIO()
                img_resized.save(
                    buffer, format="JPEG", quality=min_quality, optimize=True
                )
                compressed_bytes = buffer.getvalue()
                logger.info(
                    f"Resized/compressed image size: {len(compressed_bytes) / 1024:.2f} KB"
                )
                return compressed_bytes

        return compressed_bytes

    except UnidentifiedImageError:
        raise ValueError("Cannot identify image file.")
    except Exception as e:
        logger.error(f"Image compression error: {e}")
        raise ValueError(f"Image compression error: {e}")


def validate_image_format(image_bytes: bytes) -> str:
    """
    Validate and detect image format.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Detected image format (JPEG, PNG, etc.)
    """
    try:
        with PILImage.open(io.BytesIO(image_bytes)) as img:
            format_name = img.format.upper() if img.format else "UNKNOWN"

            supported_formats = {"JPEG", "JPG", "PNG", "WEBP", "GIF", "BMP", "TIFF"}

            if format_name not in supported_formats:
                raise ValueError(f"Unsupported image format: {format_name}")

            return format_name
    except Exception as e:
        raise ValueError(f"Invalid image format: {e}")


def get_image_info(image_bytes: bytes) -> dict:
    """
    Get basic information about an image.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Dictionary with image information (width, height, format, size)
    """
    try:
        with PILImage.open(io.BytesIO(image_bytes)) as img:
            return {
                "width": img.width,
                "height": img.height,
                "format": img.format or "UNKNOWN",
                "mode": img.mode,
                "size_bytes": len(image_bytes),
                "size_mb": round(len(image_bytes) / (1024 * 1024), 2),
            }
    except Exception as e:
        logger.error(f"Error getting image info: {e}")
        return {"error": str(e)}
