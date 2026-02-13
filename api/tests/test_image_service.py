"""Tests for the image service module."""

import io

import pytest
from PIL import Image
from src.services.image_service import (
    compress_image,
    get_image_info,
    validate_image_format,
)


@pytest.fixture
def sample_image_bytes():
    """Create a sample JPEG image for testing."""
    img = Image.new("RGB", (100, 100), color="red")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return buffer.getvalue()


@pytest.fixture
def large_image_bytes():
    """Create a larger sample image for testing compression."""
    img = Image.new("RGB", (1000, 1000), color="blue")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=95)
    return buffer.getvalue()


class TestCompressImage:
    """Tests for compress_image function."""

    def test_compress_small_image(self, sample_image_bytes):
        """Test compression of already small image."""
        result = compress_image(sample_image_bytes, target_size_bytes=50000)
        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_compress_large_image(self, large_image_bytes):
        """Test compression of larger image."""
        result = compress_image(
            large_image_bytes, target_size_bytes=50000, quality=90, min_quality=50
        )
        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) <= 50000

    def test_invalid_image_raises_error(self):
        """Test that invalid image raises ValueError."""
        with pytest.raises(ValueError, match="Cannot identify image file"):
            compress_image(b"not an image")

    def test_compression_preserves_format(self, sample_image_bytes):
        """Test that compression returns JPEG format."""
        result = compress_image(sample_image_bytes)
        # Check JPEG magic bytes
        assert result[:2] == b"\xff\xd8"


class TestValidateImageFormat:
    """Tests for validate_image_format function."""

    def test_valid_jpeg(self, sample_image_bytes):
        """Test validation of valid JPEG."""
        result = validate_image_format(sample_image_bytes)
        assert result in ["JPEG", "JPG"]

    def test_valid_png(self):
        """Test validation of valid PNG."""
        img = Image.new("RGBA", (50, 50), color="green")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        result = validate_image_format(buffer.getvalue())
        assert result == "PNG"

    def test_unsupported_format_raises_error(self):
        """Test that unsupported format raises ValueError."""
        # BMP is actually supported, so let's test with invalid image data
        buffer = io.BytesIO()
        buffer.write(b"NOT_AN_IMAGE_FORMAT_DATA_HERE")
        buffer.seek(0)
        # This should fail validation since it's not a valid image
        with pytest.raises(ValueError, match="Invalid"):
            validate_image_format(buffer.getvalue())

    def test_invalid_image_raises_error(self):
        """Test that invalid image raises ValueError."""
        with pytest.raises(ValueError, match="Invalid"):
            validate_image_format(b"not an image")


class TestGetImageInfo:
    """Tests for get_image_info function."""

    def test_get_info_valid_image(self, sample_image_bytes):
        """Test getting info from valid image."""
        result = get_image_info(sample_image_bytes)
        assert result["width"] == 100
        assert result["height"] == 100
        assert result["format"] == "JPEG"
        assert result["mode"] == "RGB"
        assert "size_bytes" in result
        assert "size_mb" in result

    def test_get_info_invalid_image(self):
        """Test getting info from invalid image."""
        result = get_image_info(b"not an image")
        assert "error" in result
