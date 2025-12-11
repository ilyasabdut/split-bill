"""
Cache integration utilities for API endpoints.
Demonstrates how to integrate caching into the Split Bill API.
"""

import hashlib
import json
import logging
from typing import Any, Dict, Optional

# Import cache service
try:
    from core.cache import cache_service
except ImportError:
    cache_service = None

logger = logging.getLogger(__name__)


def generate_image_hash(image_bytes: bytes) -> str:
    """Generate a hash for image caching."""
    return hashlib.sha256(image_bytes).hexdigest()


def generate_split_cache_key(split_data: Dict[str, Any]) -> str:
    """Generate cache key for split calculation based on request data."""
    # Create a deterministic key based on the split data
    key_material = {
        "people": sorted(split_data.get("person_names", [])),
        "assignments": sorted(
            [
                {
                    "item": a.get("item_details", {}).get("item", ""),
                    "qty": a.get("item_details", {}).get("qty", ""),
                    "price": a.get("item_details", {}).get("price", ""),
                    "assigned_to": sorted(a.get("assigned_to", [])),
                }
                for a in split_data.get("item_assignments", [])
            ],
            key=lambda x: x["item"],
        ),
        "tax": split_data.get("tax_amount_input", 0),
        "tip": split_data.get("tip_amount_input", 0),
        "split_evenly": split_data.get("split_evenly", False),
        "subtotal": split_data.get("extracted_subtotal_from_gemini", 0),
        "discount": split_data.get("extracted_total_discount", 0),
    }

    key_string = json.dumps(key_material, sort_keys=True)
    return hashlib.sha256(key_string.encode()).hexdigest()[:12]


class CacheIntegration:
    """Cache integration helper for API endpoints."""

    def __init__(self):
        self.cache_enabled = cache_service is not None
        if not self.cache_enabled:
            logger.warning("Cache service not available - caching disabled")

    async def get_cached_ocr_result(self, image_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached OCR result for an image."""
        if not self.cache_enabled:
            return None

        try:
            return await cache_service.get_ocr_result(image_hash)
        except Exception as e:
            logger.error(f"Error getting cached OCR result: {e}")
            return None

    async def cache_ocr_result(self, image_hash: str, ocr_data: Dict[str, Any]) -> bool:
        """Cache OCR result for an image."""
        if not self.cache_enabled:
            return False

        try:
            return await cache_service.set_ocr_result(image_hash, ocr_data)
        except Exception as e:
            logger.error(f"Error caching OCR result: {e}")
            return False

    async def get_cached_split_result(self, split_key: str) -> Optional[Dict[str, Any]]:
        """Get cached split calculation result."""
        if not self.cache_enabled:
            return None

        try:
            return await cache_service.get_split_result(split_key)
        except Exception as e:
            logger.error(f"Error getting cached split result: {e}")
            return None

    async def cache_split_result(
        self, split_key: str, split_data: Dict[str, Any]
    ) -> bool:
        """Cache split calculation result."""
        if not self.cache_enabled:
            return False

        try:
            return await cache_service.set_split_result(split_key, split_data)
        except Exception as e:
            logger.error(f"Error caching split result: {e}")
            return False

    async def get_cached_share_data(self, split_id: str) -> Optional[Dict[str, Any]]:
        """Get cached shared split data."""
        if not self.cache_enabled:
            return None

        try:
            return await cache_service.get_share_data(split_id)
        except Exception as e:
            logger.error(f"Error getting cached share data: {e}")
            return None

    async def cache_share_data(self, split_id: str, share_data: Dict[str, Any]) -> bool:
        """Cache shared split data."""
        if not self.cache_enabled:
            return False

        try:
            return await cache_service.set_share_data(split_id, share_data)
        except Exception as e:
            logger.error(f"Error caching share data: {e}")
            return False


# Global cache integration instance
cache_integration = CacheIntegration()


async def cached_ocr_processing(image_bytes: bytes, ocr_processing_func):
    """
    Wrapper for OCR processing with caching.

    Args:
        image_bytes: Raw image bytes
        ocr_processing_func: Function to process OCR if not cached

    Returns:
        OCR processing result (cached or fresh)
    """
    if not cache_integration.cache_enabled:
        # No caching - process directly
        return await ocr_processing_func(image_bytes)

    # Generate cache key
    image_hash = generate_image_hash(image_bytes)

    # Try to get from cache
    cached_result = await cache_integration.get_cached_ocr_result(image_hash)
    if cached_result:
        logger.info(f"Using cached OCR result for image hash: {image_hash[:8]}...")
        return cached_result

    # Process OCR and cache result
    logger.info(f"Processing new OCR for image hash: {image_hash[:8]}...")
    result = await ocr_processing_func(image_bytes)

    if result:
        await cache_integration.cache_ocr_result(image_hash, result)
        logger.info(f"Cached OCR result for image hash: {image_hash[:8]}...")

    return result


async def cached_split_calculation(split_data: Dict[str, Any], split_calculation_func):
    """
    Wrapper for split calculation with caching.

    Args:
        split_data: Split calculation request data
        split_calculation_func: Function to calculate split if not cached

    Returns:
        Split calculation result (cached or fresh)
    """
    if not cache_integration.cache_enabled:
        # No caching - calculate directly
        return await split_calculation_func(split_data)

    # Generate cache key
    split_key = generate_split_cache_key(split_data)

    # Try to get from cache
    cached_result = await cache_integration.get_cached_split_result(split_key)
    if cached_result:
        logger.info(f"Using cached split result for key: {split_key}")
        return cached_result

    # Calculate split and cache result
    logger.info(f"Calculating new split for key: {split_key}")
    result = await split_calculation_func(split_data)

    if result:
        await cache_integration.cache_split_result(split_key, result)
        logger.info(f"Cached split result for key: {split_key}")

    return result


async def cached_share_data_retrieval(split_id: str, data_retrieval_func):
    """
    Wrapper for share data retrieval with caching.

    Args:
        split_id: Split ID
        data_retrieval_func: Function to retrieve data if not cached

    Returns:
        Share data (cached or fresh)
    """
    if not cache_integration.cache_enabled:
        # No caching - retrieve directly
        return await data_retrieval_func(split_id)

    # Try to get from cache
    cached_data = await cache_integration.get_cached_share_data(split_id)
    if cached_data:
        logger.info(f"Using cached share data for split ID: {split_id}")
        return cached_data

    # Retrieve data and cache result
    logger.info(f"Retrieving fresh share data for split ID: {split_id}")
    data = await data_retrieval_func(split_id)

    if data:
        await cache_integration.cache_share_data(split_id, data)
        logger.info(f"Cached share data for split ID: {split_id}")

    return data


# Example usage in API endpoints:
"""
# In receipt upload endpoint:
async def upload_receipt(file: UploadFile, ...):
    # ... image processing ...

    # Use cached OCR processing
    ocr_result = await cached_ocr_processing(
        processed_image_bytes,
        lambda img: extract_receipt_data(img)
    )

    return ReceiptUploadResponse(...)

# In split calculation endpoint:
async def calculate_split(request: CalculateSplitRequest, ...):
    # Use cached split calculation
    split_result = await cached_split_calculation(
        request.dict(),
        lambda data: calculate_split_from_data(data)
    )

    return CalculateSplitResponse(...)

# In view split endpoint:
async def view_split(split_id: str, ...):
    # Use cached share data retrieval
    share_data = await cached_share_data_retrieval(
        split_id,
        lambda sid: load_split_data_from_minio(sid)
    )

    return SharedSplitDataResponse(...)
"""
