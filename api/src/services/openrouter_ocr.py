"""Receipt OCR helpers backed by OpenRouter chat completions."""

import base64
import io
import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import PIL.Image
import requests
from loguru import logger
from pydantic import BaseModel, Field

OPENROUTER_API_BASE_URL = os.getenv(
    "OPENROUTER_API_BASE_URL", "https://openrouter.ai/api/v1"
)
DEFAULT_OPENROUTER_MODEL = "mistralai/mistral-small-3.2-24b-instruct:free"


class LineItem(BaseModel):
    item_description: str = Field(description="Full description of the item")
    quantity: float = Field(default=1.0, description="Quantity of the item")
    item_total_price: float = Field(description="Total price for the item line")


class Discount(BaseModel):
    description: str = Field(description="Description of the discount")
    amount: float = Field(description="Positive numeric value of the discount")


class TaxDetail(BaseModel):
    tax_label: str = Field(description="Label for the tax or charge")
    tax_amount: float = Field(description="Amount of the tax or charge")


class ReceiptData(BaseModel):
    store_name: Optional[str] = Field(default=None, description="Name of the store")
    transaction_date: Optional[str] = Field(
        default=None, description="Transaction date (YYYY-MM-DD)"
    )
    transaction_time: Optional[str] = Field(
        default=None, description="Transaction time (HH:MM)"
    )
    line_items: List[LineItem] = Field(default_factory=list)
    discounts: List[Discount] = Field(default_factory=list)
    tax_details: List[TaxDetail] = Field(default_factory=list)
    subtotal: Optional[float] = Field(
        default=None, description="Subtotal before taxes/discounts"
    )
    total_amount: Optional[float] = Field(
        default=None, description="The final grand total paid"
    )
    tip_amount: Optional[float] = Field(
        default=None, description="Tip or gratuity amount"
    )


@dataclass
class OpenRouterConfig:
    api_key: str
    model_name: str
    referer: Optional[str]
    title: Optional[str]


def create_flattened_schema() -> Dict[str, Any]:
    """Flattened JSON schema for compatibility with large language models."""
    return {
        "type": "object",
        "properties": {
            "store_name": {
                "type": "string",
                "description": "Name of the store",
                "default": None,
            },
            "transaction_date": {
                "type": "string",
                "description": "Transaction date (YYYY-MM-DD)",
                "default": None,
            },
            "transaction_time": {
                "type": "string",
                "description": "Transaction time (HH:MM)",
                "default": None,
            },
            "line_items": {
                "type": "array",
                "description": "List of items purchased",
                "items": {
                    "type": "object",
                    "properties": {
                        "item_description": {
                            "type": "string",
                            "description": "Full description of the item",
                        },
                        "quantity": {
                            "type": "number",
                            "description": "Quantity of the item",
                            "default": 1.0,
                        },
                        "item_total_price": {
                            "type": "number",
                            "description": "Total price for the item line",
                        },
                    },
                    "required": ["item_description", "item_total_price"],
                },
            },
            "discounts": {
                "type": "array",
                "description": "List of discounts applied",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Description of the discount",
                        },
                        "amount": {
                            "type": "number",
                            "description": "Positive numeric value of the discount",
                        },
                    },
                    "required": ["description", "amount"],
                },
            },
            "tax_details": {
                "type": "array",
                "description": "List of taxes and charges",
                "items": {
                    "type": "object",
                    "properties": {
                        "tax_label": {
                            "type": "string",
                            "description": "Label for the tax or charge",
                        },
                        "tax_amount": {
                            "type": "number",
                            "description": "Amount of the tax or charge",
                        },
                    },
                    "required": ["tax_label", "tax_amount"],
                },
            },
            "subtotal": {
                "type": "number",
                "description": "Subtotal before taxes/discounts",
                "default": None,
            },
            "total_amount": {
                "type": "number",
                "description": "The final grand total paid",
                "default": None,
            },
            "tip_amount": {
                "type": "number",
                "description": "Tip or gratuity amount",
                "default": None,
            },
        },
    }


def generate_extraction_prompt(schema_json: str) -> str:
    return (
        "You are an expert receipt processing assistant."
        "\nAnalyze the provided receipt image and return ONLY valid JSON that conforms to the schema below."
        "\nIf a value is missing on the receipt, use null or an empty list as appropriate."
        "\nSchema:\n"
        f"{schema_json}"
    )


def get_openrouter_config() -> OpenRouterConfig:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY environment variable not set. This key is required for OpenRouter requests."
        )
    model_name = os.getenv("OPENROUTER_MODEL_NAME", DEFAULT_OPENROUTER_MODEL)
    referer = os.getenv("OPENROUTER_HTTP_REFERER")
    title = os.getenv("OPENROUTER_X_TITLE")
    return OpenRouterConfig(
        api_key=api_key, model_name=model_name, referer=referer, title=title
    )


def _build_headers(config: OpenRouterConfig) -> Dict[str, str]:
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if config.referer:
        headers["HTTP-Referer"] = config.referer
    if config.title:
        headers["X-Title"] = config.title
    return headers


def _detect_mime_type(image_bytes: bytes) -> str:
    """Detect a reasonable MIME type for the provided image bytes."""
    try:
        with PIL.Image.open(io.BytesIO(image_bytes)) as img:
            img_format = (img.format or "JPEG").upper()
    except Exception as exc:  # noqa: BLE001 - fall back to jpeg if detection fails
        logger.debug(
            f"Could not detect image format for payload: {exc}. Defaulting to JPEG MIME type."
        )
        img_format = "JPEG"

    return {
        "JPEG": "image/jpeg",
        "JPG": "image/jpeg",
        "PNG": "image/png",
        "WEBP": "image/webp",
        "GIF": "image/gif",
        "BMP": "image/bmp",
        "TIFF": "image/tiff",
        "HEIC": "image/heic",
    }.get(img_format, "image/jpeg")


def _encode_image_for_payload(image_bytes: bytes) -> str:
    """Encode image bytes as a data URI for OpenRouter multimodal endpoints."""
    mime_type = _detect_mime_type(image_bytes)
    base64_data = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{base64_data}"


def _call_openrouter(
    messages: List[Dict[str, Any]],
    *,
    temperature: float = 0.0,
    max_tokens: int = 1024,
) -> Dict[str, Any]:
    config = get_openrouter_config()
    payload: Dict[str, Any] = {
        "model": config.model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    url = f"{OPENROUTER_API_BASE_URL.rstrip('/')}/chat/completions"

    try:
        response = requests.post(
            url,
            headers=_build_headers(config),
            json=payload,
            timeout=60,
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to reach OpenRouter API: {exc}") from exc

    if response.status_code >= 400:
        logger.error(
            f"OpenRouter API returned an error {response.status_code}: {response.text}"
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:  # noqa: B904 - we want to preserve context
            raise RuntimeError(
                f"OpenRouter API error {response.status_code}: {response.text}"
            ) from exc

    try:
        return response.json()
    except ValueError as exc:  # JSON decoding error
        raise RuntimeError(
            f"Failed to decode OpenRouter response as JSON: {exc}"
        ) from exc


def _extract_message_text(response_payload: Dict[str, Any]) -> str:
    choices = response_payload.get("choices") or []
    if not choices:
        raise ValueError("OpenRouter response contained no choices.")

    message = choices[0].get("message", {})
    content = message.get("content", "")
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                text_parts.append(str(part["text"]))
            elif isinstance(part, str):
                text_parts.append(part)
        if text_parts:
            return "\n".join(text_parts).strip()

    raise ValueError("Unable to extract text content from OpenRouter response.")


def _parse_json_response(raw_text: str) -> Dict[str, Any]:
    cleaned_text = raw_text.strip()

    if cleaned_text.startswith("```"):
        lines = [
            line
            for line in cleaned_text.splitlines()
            if not line.strip().startswith("```")
        ]
        cleaned_text = "\n".join(lines).strip()

    # Attempt direct JSON parse first
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        pass

    # Fallback: extract substring that looks like JSON
    start = cleaned_text.find("{")
    end = cleaned_text.rfind("}")
    if start != -1 and end != -1 and start < end:
        candidate = cleaned_text[start : end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Model response was not valid JSON: {exc}\nResponse text: {cleaned_text}"
            ) from exc

    raise ValueError(
        f"Model response was not valid JSON. Response text: {cleaned_text}"
    )


def classify_image_as_receipt(image_bytes: bytes) -> bool:
    try:
        start_time = time.time()
        encoded_image = _encode_image_for_payload(image_bytes)
        messages: List[Dict[str, Any]] = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are an assistant that determines whether an image is a retail receipt or bill. Respond with YES or NO only.",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Is this image a retail receipt or bill? Respond with YES or NO.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": encoded_image,
                        },
                    },
                ],
            },
        ]

        logger.info("Sending classification request to OpenRouter API...")
        response_payload = _call_openrouter(messages, temperature=0.0, max_tokens=16)
        classification_result = _extract_message_text(response_payload).upper()
        elapsed = time.time() - start_time
        logger.info(
            f"OpenRouter classification result: {classification_result} (took {elapsed:.2f} seconds)"
        )
        return classification_result.startswith("YES")
    except Exception as exc:  # noqa: BLE001 - surface upstream
        logger.error(f"An error occurred during OpenRouter image classification: {exc}")
        raise RuntimeError(f"OpenRouter classification failed: {exc}") from exc


def extract_receipt_data(image_bytes: bytes) -> Dict[str, Any]:
    start_time = time.time()
    logger.info(
        f"Starting receipt data extraction via OpenRouter at {time.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    try:
        is_receipt = classify_image_as_receipt(image_bytes)
    except RuntimeError as exc:
        return {"Error": "CLASSIFICATION_FAILED", "message": str(exc)}

    if not is_receipt:
        return {
            "Error": "NOT_A_RECEIPT",
            "message": "The uploaded image does not appear to be a receipt.",
        }

    try:
        schema = create_flattened_schema()
        schema_json = json.dumps(schema, indent=2)
        encoded_image = _encode_image_for_payload(image_bytes)

        prompt_text = generate_extraction_prompt(schema_json)
        messages: List[Dict[str, Any]] = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You extract structured data from receipt images. Respond ONLY with valid JSON that matches the provided schema.",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": encoded_image,
                        },
                    },
                ],
            },
        ]

        logger.info("Sending OCR request to OpenRouter API...")
        response_payload = _call_openrouter(messages, temperature=0.1, max_tokens=2048)
        model_text = _extract_message_text(response_payload)
        parsed_json = _parse_json_response(model_text)

        logger.info("\n--- Successfully Parsed Data from OpenRouter ---")
        logger.info(json.dumps(parsed_json, indent=2))

        try:
            validated_data = ReceiptData(**parsed_json)
            logger.info("Data validation successful!")
            elapsed_time = time.time() - start_time
            logger.info(
                f"Receipt data extraction completed in {elapsed_time:.2f} seconds"
            )
            return validated_data.model_dump()
        except (
            Exception
        ) as validation_error:  # noqa: BLE001 - log validation issues and return raw data
            logger.warning(f"Pydantic validation warning: {validation_error}")
            logger.info("Returning raw extracted data...")
            return parsed_json

    except Exception as exc:  # noqa: BLE001 - provide helpful error context to caller
        logger.error(f"An error occurred calling OpenRouter API: {exc}")
        return {"Error": f"OpenRouter API call failed: {exc}"}


# Backwards compatibility export for callers expecting the old name
extract_receipt_data_with_openrouter = extract_receipt_data
