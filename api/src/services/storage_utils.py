# src/storage_utils.py
import io
import json  # For JSON operations
import logging
import os
from typing import Any, Dict, Optional  # For type hints

from minio import Minio
from minio.error import S3Error

# Get logger for this module
logger = logging.getLogger(__name__)

# --- Storage Configuration (Garage S3 API compatible) ---
MINIO_ENDPOINT = os.environ.get(
    "MINIO_ENDPOINT", "garage:3900"
)
# Define prefixes (folders) within the bucket
IMAGE_PREFIX = "receipts/"
METADATA_PREFIX = "metadata/"
MINIO_BUCKET_NAME = None
MINIO_USE_SSL = None
MINIO_ACCESS_KEY = None
MINIO_SECRET_KEY = None

storage_client_instance = (
    None  # Garage S3 API compatible client
)


def initialize_minio_globals():
    global MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET_NAME, MINIO_USE_SSL
    MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY")
    MINIO_BUCKET_NAME = os.environ.get("MINIO_BUCKET_NAME", "split-bill")
    MINIO_USE_SSL_STR = os.environ.get("MINIO_USE_SSL", "False").lower()
    MINIO_USE_SSL = MINIO_USE_SSL_STR == "true"


def get_storage_client() -> Optional[Minio]:
    global storage_client_instance
    if storage_client_instance is None:
        initialize_minio_globals()
        if not all(
            [MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET_NAME]
        ):
            logger.critical(
                "Storage environment variables not fully set. Cannot initialize client."
            )
            return None
        try:
            logger.info(
                f"Initializing Garage S3 client for endpoint: {MINIO_ENDPOINT}, SSL: {MINIO_USE_SSL}"
            )
            storage_client_instance = Minio(
                MINIO_ENDPOINT,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                secure=MINIO_USE_SSL,
            )
            found = storage_client_instance.bucket_exists(MINIO_BUCKET_NAME)
            if not found:
                logger.warning(
                    f"Storage bucket '{MINIO_BUCKET_NAME}' does not exist. Attempting to create it."
                )
                try:
                    storage_client_instance.make_bucket(MINIO_BUCKET_NAME)
                    logger.info(f"Bucket '{MINIO_BUCKET_NAME}' created successfully.")
                except S3Error as mb_exc:
                    logger.error(
                        f"Error creating storage bucket '{MINIO_BUCKET_NAME}': {mb_exc}"
                    )
                    storage_client_instance = None  # Cannot proceed without bucket
                    return None
            else:
                logger.info(
                    f"Successfully connected to Garage S3 and bucket '{MINIO_BUCKET_NAME}' found."
                )
        except S3Error as exc:
            logger.error(f"S3Error initializing storage client: {exc}")
            storage_client_instance = None
        except Exception as e:
            logger.error(
                f"A non-S3 error occurred during storage client initialization: {e}"
            )
            storage_client_instance = None
    return storage_client_instance


def upload_to_storage(
    data_bytes: bytes, object_name_with_prefix: str, content_type: str
) -> Optional[str]:
    """Generic upload function to Garage S3 storage."""
    client = get_storage_client()
    if not client:
        return None
    try:
        data_stream = io.BytesIO(data_bytes)
        data_length = len(data_bytes)

        client.put_object(
            MINIO_BUCKET_NAME,
            object_name_with_prefix,
            data_stream,
            length=data_length,
            content_type=content_type,
        )
        logger.info(
            f"Successfully uploaded {object_name_with_prefix} to storage bucket {MINIO_BUCKET_NAME}."
        )
        return object_name_with_prefix
    except S3Error as exc:
        logger.error(f"Error uploading '{object_name_with_prefix}' to storage: {exc}")
        return None
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during storage upload of '{object_name_with_prefix}': {e}"
        )
        return None


def get_from_storage(object_name_with_prefix: str) -> Optional[bytes]:
    """Generic retrieval function from Garage S3 storage, returns bytes."""
    client = get_storage_client()
    if not client:
        return None
    try:
        response = client.get_object(MINIO_BUCKET_NAME, object_name_with_prefix)
        data_bytes = response.read()
        response.close()
        response.release_conn()
        return data_bytes
    except S3Error as exc:
        if exc.code == "NoSuchKey":
            logger.warning(
                f"Object '{object_name_with_prefix}' not found in storage bucket '{MINIO_BUCKET_NAME}'."
            )
        else:
            logger.error(
                f"S3Error getting object '{object_name_with_prefix}' from storage: {exc}"
            )
        return None
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during storage get of '{object_name_with_prefix}': {e}"
        )
        return None


def upload_image_to_storage(
    image_bytes: bytes, base_object_name: str, content_type: str = "image/jpeg"
) -> Optional[str]:
    """Uploads image bytes to Garage S3 storage under the IMAGE_PREFIX."""
    object_name_with_prefix = IMAGE_PREFIX + base_object_name
    return upload_to_storage(image_bytes, object_name_with_prefix, content_type)


def get_image_from_storage(base_object_name: str) -> Optional[bytes]:
    """Retrieves an image from Garage S3 storage from the IMAGE_PREFIX."""
    object_name_with_prefix = IMAGE_PREFIX + base_object_name
    return get_from_storage(object_name_with_prefix)


def upload_metadata_to_storage(
    metadata_dict: Dict[str, Any], base_object_name: str
) -> Optional[str]:
    """Uploads metadata dictionary as JSON to Garage S3 storage under METADATA_PREFIX."""
    try:
        json_bytes = json.dumps(metadata_dict, indent=2).encode("utf-8")
        object_name_with_prefix = (
            METADATA_PREFIX + base_object_name + ".json"
        )
        return upload_to_storage(json_bytes, object_name_with_prefix, "application/json")
    except TypeError as e:
        logger.error(f"Error serializing metadata to JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error preparing metadata for upload: {e}")
        return None


def get_metadata_from_storage(base_object_name: str) -> Optional[Dict[str, Any]]:
    """Retrieves and parses JSON metadata from Garage S3 storage from METADATA_PREFIX."""
    object_name_with_prefix = METADATA_PREFIX + base_object_name + ".json"
    json_bytes = get_from_storage(object_name_with_prefix)
    if json_bytes:
        try:
            metadata_dict = json.loads(json_bytes.decode("utf-8"))
            return metadata_dict
        except json.JSONDecodeError as e:
            logger.error(
                f"Error decoding JSON from storage object '{object_name_with_prefix}': {e}"
            )
            return None
        except Exception as e:
            print(
                f"Unexpected error processing metadata from storage '{object_name_with_prefix}': {e}"
            )
            return None
    return None


def upload_image_to_minio(
    image_bytes: bytes, base_object_name: str, content_type: str = "image/jpeg"
) -> Optional[str]:
    """Alias for upload_image_to_storage for backward compatibility."""
    return upload_image_to_storage(image_bytes, base_object_name, content_type)


def get_image_from_minio(base_object_name: str) -> Optional[bytes]:
    """Alias for get_image_from_storage for backward compatibility."""
    return get_image_from_storage(base_object_name)


def upload_metadata_to_minio(
    metadata_dict: Dict[str, Any], base_object_name: str
) -> Optional[str]:
    """Alias for upload_metadata_to_storage for backward compatibility."""
    return upload_metadata_to_storage(metadata_dict, base_object_name)


def get_metadata_from_minio(base_object_name: str) -> Optional[Dict[str, Any]]:
    """Alias for get_metadata_from_storage for backward compatibility."""
    return get_metadata_from_storage(base_object_name)


if __name__ == "__main__":
    client = get_storage_client()
    if client:
        print("Garage S3 client initialized. You can add test logic here.")

        test_metadata_id = "test_split_123"
        sample_metadata = {
            "user": "tester",
            "items": ["apple", "banana"],
            "total": 15.50,
        }

        logger.info(f"Attempting to upload metadata for {test_metadata_id}...")
        meta_obj_name = upload_metadata_to_storage(sample_metadata, test_metadata_id)
        if meta_obj_name:
            logger.info(
                f"Metadata uploaded, object name should be: {METADATA_PREFIX}{test_metadata_id}.json (Actual name: {meta_obj_name})"
            )

            logger.info(f"Attempting to retrieve metadata for {test_metadata_id}...")
            retrieved_meta = get_metadata_from_storage(test_metadata_id)
            if retrieved_meta:
                logger.info("Retrieved metadata:")
                logger.info(json.dumps(retrieved_meta, indent=2))
                if retrieved_meta == sample_metadata:
                    logger.info("Metadata matches: SUCCESS!")
                else:
                    logger.error("Metadata MISMATCH: FAILED!")
            else:
                logger.error(f"Failed to retrieve metadata for {test_metadata_id}.")
        else:
            logger.error(f"Failed to upload metadata for {test_metadata_id}.")

    else:
        logger.warning("Storage client not configured. Set environment variables.")
