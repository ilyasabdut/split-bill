"""
Unit tests for routers.receipts module.
Tests receipt upload and OCR processing endpoints.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.routers.receipts import receipts_router
from src.models.schemas import ReceiptUploadResponse


class TestReceiptsRouter:
    """Test receipts router."""

    def test_receipts_router_exists(self):
        """Test that receipts router exists."""
        assert receipts_router is not None
        assert receipts_router.prefix == "/receipts"

    def test_receipts_router_tags(self):
        """Test receipts router tags."""
        assert receipts_router.tags == ["receipts"]


class TestUploadReceiptEndpoint:
    """Test upload_receipt endpoint."""

    def test_upload_receipt_exists(self):
        """Test that upload endpoint exists."""
        routes = [route.path for route in receipts_router.routes]
        assert "/upload" in routes

    @pytest.mark.asyncio
    async def test_upload_receipt_no_file(self):
        """Test upload without file raises error."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(receipts_router)
        client = TestClient(app)

        response = client.post("/receipts/upload")
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_upload_receipt_invalid_file_type(self):
        """Test upload with invalid file type raises error."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(receipts_router)

        # Mock the dependencies to bypass auth
        with patch("src.routers.receipts.get_api_key", return_value="test-key"):
            client = TestClient(app)

            # Create a text file (not an image)
            files = {"file": ("test.txt", b"not an image", "text/plain")}
            response = client.post("/receipts/upload", files=files)
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_receipt_file_too_large(self):
        """Test upload with file too large raises error."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(receipts_router)

        with patch("src.routers.receipts.get_api_key", return_value="test-key"):
            client = TestClient(app)

            # Create a large file (over 10MB)
            large_file = b"x" * (11 * 1024 * 1024)
            files = {"file": ("large.jpg", large_file, "image/jpeg")}
            response = client.post("/receipts/upload", files=files)
            assert response.status_code == 413  # Request Entity Too Large

    @pytest.mark.asyncio
    async def test_upload_receipt_compression_failure(self):
        """Test upload with compression failure raises error."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(receipts_router)

        with patch("src.r.routers.receipts.get_api_key", return_value="test-key"):
            with patch("src.routers.receipts.compress_image", return_value=None):
                client = TestClient(app)

                files = {"file": ("test.jpg", b"fake image", "image/jpeg")}
                response = client.post("/receipts/upload", files=files)
                assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_receipt_ocr_error(self):
        """Test upload with OCR error raises error."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(receipts_router)

        with patch("src.routers.receipts.get_api_key", return_value="test-key"):
            with patch("src.routers.receipts.compress_image", return_value=b"compressed"):
                with patch("src.routers.receipts.extract_receipt_data", return_value={"Error": "OCR failed"}):
                    client = TestClient(app)

                    files = {"file": ("test.jpg", b"fake image", "image/jpeg")}
                    response = client.post("/receipts/upload", files=files)
                    assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_receipt_internal_error(self):
        """Test upload with internal error raises 500."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(receipts_router)

        with patch("src.routers.receipts.get_api_key", return_value="test-key"):
            with patch("src.routers.receipts.compress_image", side_effect=Exception("Internal error")):
                client = TestClient(app)

                files = {"file": ("test.jpg", b"fake image", "image/jpeg")}
                response = client.post("/receipts/upload", files=files)
                assert response.status_code == 500


class TestReceiptUploadResponse:
    """Test ReceiptUploadResponse model."""

    def test_receipt_upload_response_creation(self):
        """Test ReceiptUploadResponse creation."""
        parsed_data = {"items": [{"name": "Item 1", "price": 10.0}]}
        processed_image = "base64encodedimage"

        response = ReceiptUploadResponse(
            parsed_data=parsed_data,
            processed_image_bytes_base64=processed_image,
            extracted_subtotal_from_gemini=10.0,
            extracted_total_discount=0.0,
        )

        assert response.parsed_data == parsed_data
        assert response.processed_image_bytes_base64 == processed_image
        assert response.extracted_subtotal_from_gemini == 10.0
        assert response.extracted_total_discount == 0.0

    def test_receipt_upload_response_defaults(self):
        """Test ReceiptUploadResponse with default values."""
        response = ReceiptUploadResponse(
            parsed_data={},
            processed_image_bytes_base64="",
        )

        assert response.extracted_subtotal_from_gemini is None
        assert response.extracted_total_discount == 0.0


class TestReceiptUploadResponseSerialization:
    """Test ReceiptUploadResponse serialization."""

    def test_receipt_upload_response_to_dict(self):
        """Test ReceiptUploadResponse to_dict conversion."""
        response = ReceiptUploadResponse(
            parsed_data={"items": []},
            processed_image_bytes_base64="base64image",
            extracted_subtotal_from_gemini=10.0,
            extracted_total_discount=2.0,
        )

        data = response.model_dump()
        assert "parsed_data" in data
        assert "processed_image_bytes_base64" in data
        assert "extracted_subtotal_from_gemini" in data
        assert "extracted_total_discount" in data

    def test_receipt_upload_response_to_json(self):
        """Test ReceiptUploadResponse to JSON conversion."""
        response = ReceiptUploadResponse(
            parsed_data={"items": []},
            processed="base64image",
        )

        json_str = response.model_dump_json()
        assert isinstance(json_str, str)
        assert len(json_str) > 0
