"""Tests for storage_utils module."""

import json
import os
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock

import pytest
from minio.error import S3Error

from src.services import storage_utils
from src.services.storage_utils import (
    get_storage_client,
    upload_to_storage,
    get_from_storage,
    upload_image_to_storage,
    get_image_from_storage,
    upload_metadata_to_storage,
    get_metadata_from_storage,
    initialize_minio_globals,
    IMAGE_PREFIX,
    METADATA_PREFIX,
)


class TestInitializeMinioGlobals:
    """Tests for initialize_minio_globals function."""

    @patch.dict(os.environ, {
        'MINIO_ACCESS_KEY': 'test-key',
        'MINIO_SECRET_KEY': 'test-secret',
        'MINIO_BUCKET_NAME': 'test-bucket',
        'MINIO_USE_SSL': 'true'
    })
    def test_initializes_with_environment_variables(self):
        """Test that globals are initialized from environment variables."""
        storage_utils.MINIO_ACCESS_KEY = None
        storage_utils.MINIO_SECRET_KEY = None
        storage_utils.MINIO_BUCKET_NAME = None
        storage_utils.MINIO_USE_SSL = None

        initialize_minio_globals()

        assert storage_utils.MINIO_ACCESS_KEY == 'test-key'
        assert storage_utils.MINIO_SECRET_KEY == 'test-secret'
        assert storage_utils.MINIO_BUCKET_NAME == 'test-bucket'
        assert storage_utils.MINIO_USE_SSL is True

    @patch.dict(os.environ, {}, clear=True)
    def test_initializes_with_defaults(self):
        """Test that globals are initialized with defaults when env vars missing."""
        storage_utils.MINIO_ACCESS_KEY = None
        storage_utils.MINIO_SECRET_KEY = None
        storage_utils.MINIO_BUCKET_NAME = None
        storage_utils.MINIO_USE_SSL = None

        initialize_minio_globals()

        assert storage_utils.MINIO_ACCESS_KEY is None
        assert storage_utils.MINIO_SECRET_KEY is None
        assert storage_utils.MINIO_BUCKET_NAME == 'split-bill'
        assert storage_utils.MINIO_USE_SSL is False


class TestGetStorageClient:
    """Tests for get_storage_client function."""

    @patch.dict(os.environ, {
        'MINIO_ENDPOINT': 'localhost:9000',
        'MINIO_ACCESS_KEY': 'test-key',
        'MINIO_SECRET_KEY': 'test-secret',
        'MINIO_BUCKET_NAME': 'test-bucket',
        'MINIO_USE_SSL': 'false'
    })
    @patch('src.services.storage_utils.Minio')
    def test_returns_client_when_bucket_exists(self, mock_minio_class):
        """Test client is returned when bucket exists."""
        storage_utils.storage_client_instance = None
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_minio_class.return_value = mock_client

        client = get_storage_client()

        assert client is not None
        mock_client.bucket_exists.assert_called_once_with('test-bucket')

    @patch.dict(os.environ, {
        'MINIO_ENDPOINT': 'localhost:9000',
        'MINIO_ACCESS_KEY': 'test-key',
        'MINIO_SECRET_KEY': 'test-secret',
        'MINIO_BUCKET_NAME': 'test-bucket',
        'MINIO_USE_SSL': 'false'
    })
    @patch('src.services.storage_utils.Minio')
    def test_creates_bucket_when_not_exists(self, mock_minio_class):
        """Test bucket is created when it doesn't exist."""
        storage_utils.storage_client_instance = None
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = False
        mock_minio_class.return_value = mock_client

        client = get_storage_client()

        assert client is not None
        mock_client.make_bucket.assert_called_once_with('test-bucket')

    @patch.dict(os.environ, {}, clear=True)
    def test_returns_none_when_env_vars_missing(self):
        """Test returns None when environment variables are not set."""
        storage_utils.storage_client_instance = None
        storage_utils.MINIO_ACCESS_KEY = None
        storage_utils.MINIO_SECRET_KEY = None

        client = get_storage_client()

        assert client is None

    @patch.dict(os.environ, {
        'MINIO_ENDPOINT': 'localhost:9000',
        'MINIO_ACCESS_KEY': 'test-key',
        'MINIO_SECRET_KEY': 'test-secret',
        'MINIO_BUCKET_NAME': 'test-bucket',
        'MINIO_USE_SSL': 'false'
    })
    @patch('src.services.storage_utils.Minio')
    def test_returns_none_on_s3_error(self, mock_minio_class):
        """Test returns None when S3Error occurs."""
        storage_utils.storage_client_instance = None
        mock_minio_class.side_effect = S3Error(
            code='ConnectionError',
            message='Connection failed',
            resource='test',
            request_id='123',
            host_id='abc',
            response='error'
        )

        client = get_storage_client()

        assert client is None

    @patch.dict(os.environ, {
        'MINIO_ENDPOINT': 'localhost:9000',
        'MINIO_ACCESS_KEY': 'test-key',
        'MINIO_SECRET_KEY': 'test-secret',
        'MINIO_BUCKET_NAME': 'test-bucket',
        'MINIO_USE_SSL': 'false'
    })
    @patch('src.services.storage_utils.Minio')
    def test_returns_existing_client(self, mock_minio_class):
        """Test returns existing client without re-initializing."""
        existing_client = MagicMock()
        storage_utils.storage_client_instance = existing_client

        client = get_storage_client()

        assert client is existing_client
        mock_minio_class.assert_not_called()


class TestUploadToStorage:
    """Tests for upload_to_storage function."""

    @patch('src.services.storage_utils.get_storage_client')
    def test_uploads_data_successfully(self, mock_get_client):
        """Test successful data upload."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        result = upload_to_storage(
            b'test data',
            'test-object.txt',
            'text/plain'
        )

        assert result == 'test-object.txt'
        mock_client.put_object.assert_called_once()
        call_args = mock_client.put_object.call_args
        assert call_args[0][0] == storage_utils.MINIO_BUCKET_NAME
        assert call_args[0][1] == 'test-object.txt'

    @patch('src.services.storage_utils.get_storage_client')
    def test_returns_none_when_client_none(self, mock_get_client):
        """Test returns None when client is None."""
        mock_get_client.return_value = None

        result = upload_to_storage(b'data', 'object', 'type')

        assert result is None

    @patch('src.services.storage_utils.get_storage_client')
    def test_returns_none_on_s3_error(self, mock_get_client):
        """Test returns None on S3Error."""
        mock_client = MagicMock()
        mock_client.put_object.side_effect = S3Error(
            code='UploadError',
            message='Upload failed',
            resource='test',
            request_id='123',
            host_id='abc',
            response='error'
        )
        mock_get_client.return_value = mock_client

        result = upload_to_storage(b'data', 'object', 'type')

        assert result is None


class TestGetFromStorage:
    """Tests for get_from_storage function."""

    @patch('src.services.storage_utils.get_storage_client')
    def test_retrieves_data_successfully(self, mock_get_client):
        """Test successful data retrieval."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.read.return_value = b'test data'
        mock_client.get_object.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = get_from_storage('test-object')

        assert result == b'test data'
        mock_response.close.assert_called_once()
        mock_response.release_conn.assert_called_once()

    @patch('src.services.storage_utils.get_storage_client')
    def test_returns_none_when_object_not_found(self, mock_get_client):
        """Test returns None when object not found."""
        mock_client = MagicMock()
        error = S3Error(
            code='NoSuchKey',
            message='Object not found',
            resource='test',
            request_id='123',
            host_id='abc',
            response='error'
        )
        mock_client.get_object.side_effect = error
        mock_get_client.return_value = mock_client

        result = get_from_storage('nonexistent-object')

        assert result is None

    @patch('src.services.storage_utils.get_storage_client')
    def test_returns_none_when_client_none(self, mock_get_client):
        """Test returns None when client is None."""
        mock_get_client.return_value = None

        result = get_from_storage('object')

        assert result is None


class TestImageStorageFunctions:
    """Tests for image storage functions."""

    @patch('src.services.storage_utils.upload_to_storage')
    def test_upload_image_to_storage(self, mock_upload):
        """Test image upload with prefix."""
        mock_upload.return_value = 'receipts/test-image.jpg'

        result = upload_image_to_storage(b'image-data', 'test-image.jpg', 'image/jpeg')

        assert result == 'receipts/test-image.jpg'
        mock_upload.assert_called_once_with(
            b'image-data',
            IMAGE_PREFIX + 'test-image.jpg',
            'image/jpeg'
        )

    @patch('src.services.storage_utils.get_from_storage')
    def test_get_image_from_storage(self, mock_get):
        """Test image retrieval with prefix."""
        mock_get.return_value = b'image-data'

        result = get_image_from_storage('test-image.jpg')

        assert result == b'image-data'
        mock_get.assert_called_once_with(IMAGE_PREFIX + 'test-image.jpg')


class TestMetadataStorageFunctions:
    """Tests for metadata storage functions."""

    @patch('src.services.storage_utils.upload_to_storage')
    def test_upload_metadata_to_storage(self, mock_upload):
        """Test metadata upload as JSON."""
        mock_upload.return_value = 'metadata/test-meta.json'
        metadata = {"key": "value", "number": 123}

        result = upload_metadata_to_storage(metadata, 'test-meta')

        assert result == 'metadata/test-meta.json'
        call_args = mock_upload.call_args
        assert call_args[0][1] == METADATA_PREFIX + 'test-meta.json'
        assert call_args[0][2] == 'application/json'
        # Verify JSON was encoded
        uploaded_data = call_args[0][0]
        assert json.loads(uploaded_data) == metadata

    @patch('src.services.storage_utils.get_from_storage')
    def test_get_metadata_from_storage(self, mock_get):
        """Test metadata retrieval and parsing."""
        metadata = {"key": "value", "number": 123}
        mock_get.return_value = json.dumps(metadata).encode('utf-8')

        result = get_metadata_from_storage('test-meta')

        assert result == metadata
        mock_get.assert_called_once_with(METADATA_PREFIX + 'test-meta.json')

    @patch('src.services.storage_utils.get_from_storage')
    def test_get_metadata_returns_none_on_json_error(self, mock_get):
        """Test returns None when JSON is invalid."""
        mock_get.return_value = b'invalid json{'

        result = get_metadata_from_storage('test-meta')

        assert result is None

    @patch('src.services.storage_utils.get_from_storage')
    def test_get_metadata_returns_none_when_not_found(self, mock_get):
        """Test returns None when object not found."""
        mock_get.return_value = None

        result = get_metadata_from_storage('test-meta')

        assert result is None


class TestBackwardCompatibility:
    """Tests for backward compatibility aliases."""

    @patch('src.services.storage_utils.upload_image_to_storage')
    def test_upload_image_to_minio_alias(self, mock_upload):
        """Test upload_image_to_minio is an alias."""
        from src.services.storage_utils import upload_image_to_minio
        mock_upload.return_value = 'test'

        result = upload_image_to_minio(b'data', 'name', 'type')

        assert result == 'test'

    @patch('src.services.storage_utils.get_image_from_storage')
    def test_get_image_from_minio_alias(self, mock_get):
        """Test get_image_from_minio is an alias."""
        from src.services.storage_utils import get_image_from_minio
        mock_get.return_value = b'data'

        result = get_image_from_minio('name')

        assert result == b'data'

    @patch('src.services.storage_utils.upload_metadata_to_storage')
    def test_upload_metadata_to_minio_alias(self, mock_upload):
        """Test upload_metadata_to_minio is an alias."""
        from src.services.storage_utils import upload_metadata_to_minio
        mock_upload.return_value = 'test'

        result = upload_metadata_to_minio({}, 'name')

        assert result == 'test'

    @patch('src.services.storage_utils.get_metadata_from_storage')
    def test_get_metadata_from_minio_alias(self, mock_get):
        """Test get_metadata_from_minio is an alias."""
        from src.services.storage_utils import get_metadata_from_minio
        mock_get.return_value = {}

        result = get_metadata_from_minio('name')

        assert result == {}
