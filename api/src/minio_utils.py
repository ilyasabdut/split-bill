# src/minio_utils.py
import os
from minio import Minio
from minio.error import S3Error
import io
import json # For JSON operations
from typing import Union, Dict, Any, Optional # For type hints

# --- MinIO Configuration ---
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "158.179.26.94:9000") # Ensure API PORT
# Define prefixes (folders) within the bucket
IMAGE_PREFIX = "receipts/"
METADATA_PREFIX = "metadata/"
MINIO_BUCKET_NAME = None
MINIO_USE_SSL = None
MINIO_ACCESS_KEY = None
MINIO_SECRET_KEY = None

minio_client_instance = None # Renamed to avoid conflict if minio_client is used elsewhere

def initialize_minio_globals():
    global MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET_NAME, MINIO_USE_SSL
    MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY")
    MINIO_BUCKET_NAME = os.environ.get("MINIO_BUCKET_NAME", "split-bill")
    MINIO_USE_SSL_STR = os.environ.get("MINIO_USE_SSL", "False").lower()
    MINIO_USE_SSL = MINIO_USE_SSL_STR == 'true'

def get_minio_client() -> Optional[Minio]:
    global minio_client_instance
    if minio_client_instance is None:
        initialize_minio_globals()
        if not all([MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET_NAME]):
            print("CRITICAL: MinIO environment variables not fully set. Cannot initialize client.")
            return None
        try:
            print(f"Initializing MinIO client for endpoint: {MINIO_ENDPOINT}, SSL: {MINIO_USE_SSL}")
            minio_client_instance = Minio(
                MINIO_ENDPOINT,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                secure=MINIO_USE_SSL
            )
            found = minio_client_instance.bucket_exists(MINIO_BUCKET_NAME)
            if not found:
                print(f"Warning: MinIO bucket '{MINIO_BUCKET_NAME}' does not exist. Attempting to create it.")
                try:
                    minio_client_instance.make_bucket(MINIO_BUCKET_NAME)
                    print(f"Bucket '{MINIO_BUCKET_NAME}' created successfully.")
                except S3Error as mb_exc:
                    print(f"Error creating MinIO bucket '{MINIO_BUCKET_NAME}': {mb_exc}")
                    minio_client_instance = None # Cannot proceed without bucket
                    return None
            else:
                print(f"Successfully connected to MinIO and bucket '{MINIO_BUCKET_NAME}' found.")
        except S3Error as exc:
            print(f"S3Error initializing MinIO client: {exc}")
            minio_client_instance = None
        except Exception as e:
            print(f"A non-S3 error occurred during MinIO client initialization: {e}")
            minio_client_instance = None
    return minio_client_instance

def upload_to_minio(data_bytes: bytes, object_name_with_prefix: str, content_type: str) -> Optional[str]:
    """Generic upload function to MinIO."""
    client = get_minio_client()
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
            content_type=content_type
        )
        print(f"Successfully uploaded {object_name_with_prefix} to MinIO bucket {MINIO_BUCKET_NAME}.")
        # It's generally better to return the object_name and construct URLs in the app
        # or use presigned URLs, rather than assuming public accessibility here.
        return object_name_with_prefix # Indicate success by returning the object name
    except S3Error as exc:
        print(f"Error uploading '{object_name_with_prefix}' to MinIO: {exc}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during MinIO upload of '{object_name_with_prefix}': {e}")
        return None

def get_from_minio(object_name_with_prefix: str) -> Optional[bytes]:
    """Generic retrieval function from MinIO, returns bytes."""
    client = get_minio_client()
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
            print(f"Object '{object_name_with_prefix}' not found in MinIO bucket '{MINIO_BUCKET_NAME}'.")
        else:
            print(f"S3Error getting object '{object_name_with_prefix}' from MinIO: {exc}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during MinIO get of '{object_name_with_prefix}': {e}")
        return None

# --- Image Specific Wrappers ---
def upload_image_to_minio(image_bytes: bytes, base_object_name: str, content_type: str = 'image/jpeg') -> Optional[str]:
    """Uploads image bytes to MinIO under the IMAGE_PREFIX."""
    object_name_with_prefix = IMAGE_PREFIX + base_object_name
    return upload_to_minio(image_bytes, object_name_with_prefix, content_type)

def get_image_from_minio(base_object_name: str) -> Optional[bytes]:
    """Retrieves an image from MinIO from the IMAGE_PREFIX."""
    object_name_with_prefix = IMAGE_PREFIX + base_object_name
    return get_from_minio(object_name_with_prefix)

# --- JSON Metadata Specific Wrappers ---
def upload_metadata_to_minio(metadata_dict: Dict[str, Any], base_object_name: str) -> Optional[str]:
    """Uploads metadata dictionary as JSON to MinIO under METADATA_PREFIX."""
    try:
        json_bytes = json.dumps(metadata_dict, indent=2).encode('utf-8')
        object_name_with_prefix = METADATA_PREFIX + base_object_name + ".json" # Add .json extension
        return upload_to_minio(json_bytes, object_name_with_prefix, 'application/json')
    except TypeError as e:
        print(f"Error serializing metadata to JSON: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error preparing metadata for upload: {e}")
        return None

def get_metadata_from_minio(base_object_name: str) -> Optional[Dict[str, Any]]:
    """Retrieves and parses JSON metadata from MinIO from METADATA_PREFIX."""
    object_name_with_prefix = METADATA_PREFIX + base_object_name + ".json"
    json_bytes = get_from_minio(object_name_with_prefix)
    if json_bytes:
        try:
            metadata_dict = json.loads(json_bytes.decode('utf-8'))
            return metadata_dict
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from MinIO object '{object_name_with_prefix}': {e}")
            return None
        except Exception as e:
            print(f"Unexpected error processing metadata from MinIO '{object_name_with_prefix}': {e}")
            return None
    return None


# Example Test
if __name__ == "__main__":
    client = get_minio_client()
    if client:
        print("MinIO client initialized. You can add test logic here.")
        
        # Test metadata upload and retrieval
        test_metadata_id = "test_split_123"
        sample_metadata = {"user": "tester", "items": ["apple", "banana"], "total": 15.50}
        
        print(f"\nAttempting to upload metadata for {test_metadata_id}...")
        meta_obj_name = upload_metadata_to_minio(sample_metadata, test_metadata_id)
        if meta_obj_name:
            print(f"Metadata uploaded, object name should be: {METADATA_PREFIX}{test_metadata_id}.json (Actual MinIO name: {meta_obj_name})")
            
            print(f"\nAttempting to retrieve metadata for {test_metadata_id}...")
            retrieved_meta = get_metadata_from_minio(test_metadata_id)
            if retrieved_meta:
                print("Retrieved metadata:")
                print(json.dumps(retrieved_meta, indent=2))
                if retrieved_meta == sample_metadata:
                    print("Metadata matches: SUCCESS!")
                else:
                    print("Metadata MISMATCH: FAILED!")
            else:
                print(f"Failed to retrieve metadata for {test_metadata_id}.")
        else:
            print(f"Failed to upload metadata for {test_metadata_id}.")

    else:
        print("MinIO client not configured. Set environment variables.")
