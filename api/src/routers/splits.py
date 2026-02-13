"""Split calculation router for the Split Bill API.

This module handles bill split calculation and viewing endpoints.
"""

import hashlib
import json
import logging
import time
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request, status

from .dependencies import get_api_key, rate_limit
from .models.schemas import (
    CalculateSplitRequest,
    CalculateSplitResponse,
    SharedSplitDataResponse,
)

logger = logging.getLogger(__name__)

splits_router = APIRouter(prefix="/splits", tags=["splits"])


def calculate_split(
    item_assignments: List[Dict[str, Any]],
    tax_str: str,
    tip_str: str,
    person_names: List[str],
    split_evenly_flag: bool = False,
    overall_subtotal_for_even_split: float = 0.0,
    total_discount_amount: float = 0.0,
) -> Dict[str, Any]:
    """Calculate bill split among participants.

    This function implements the core bill splitting logic:
    - Even split: Divides subtotal equally among all participants
    - Individual assignment: Distributes items to assigned people

    Args:
        item_assignments: List of item assignments with details
        tax_str: Tax amount as string
        tip_str: Tip amount as string
        person_names: List of participant names
        split_evenly_flag: Whether to split evenly
        overall_subtotal_for_even_split: Subtotal for even split calculation
        total_discount_amount: Total discount amount

    Returns:
        Dict containing split results per person
    """
    try:
        split_results = {
            person: {"subtotal": 0.0, "items": []} for person in person_names
        }

        if split_evenly_flag:
            num_people = len(person_names)
            subtotal_per_person = (
                overall_subtotal_for_even_split / num_people if num_people > 0 else 0.0
            )

            for person in person_names:
                split_results[person]["subtotal"] = subtotal_per_person
                split_results[person]["items"] = []
        else:
            for assignment in item_assignments:
                item_details = assignment.get("item_details", {})
                assigned_to = assignment.get("assigned_to", [])
                item_price = float(item_details.get("price", 0))

                if assigned_to and item_price > 0:
                    per_person_share = item_price / len(assigned_to)
                    for person in assigned_to:
                        if person in split_results:
                            split_results[person]["subtotal"] += per_person_share
                            split_results[person]["items"].append(
                                {
                                    "item": item_details.get("item", ""),
                                    "price": per_person_share,
                                }
                            )

        # Add tax and tip proportionally
        try:
            tax_amount = float(tax_str) if tax_str else 0.0
            tip_amount = float(tip_str) if tip_str else 0.0
        except (ValueError, TypeError):
            tax_amount = 0.0
            tip_amount = 0.0

        total_subtotal = sum(
            person_data["subtotal"] for person_data in split_results.values()
        )
        if total_subtotal > 0:
            for person in person_names:
                person_share = split_results[person]["subtotal"] / total_subtotal
                split_results[person]["tax"] = tax_amount * person_share
                split_results[person]["tip"] = tip_amount * person_share
                split_results[person]["total"] = (
                    split_results[person]["subtotal"]
                    + split_results[person]["tax"]
                    + split_results[person]["tip"]
                )
        else:
            tax_per_person = (
                tax_amount / len(person_names) if len(person_names) > 0 else 0.0
            )
            tip_per_person = (
                tip_amount / len(person_names) if len(person_names) > 0 else 0.0
            )
            for person in person_names:
                split_results[person]["tax"] = tax_per_person
                split_results[person]["tip"] = tip_per_person
                split_results[person]["total"] = (
                    split_results[person]["subtotal"] + tax_per_person + tip_per_person
                )

        return split_results

    except Exception as e:
        logger.error(f"Split calculation error: {e}", exc_info=True)
        return {"Error": f"Calculation failed: {str(e)}"}


@splits_router.post(
    "/calculate",
    response_model=CalculateSplitResponse,
    status_code=status.HTTP_200_OK,
)
@rate_limit(30)
async def calculate_split_endpoint(
    request: Request,
    split_request: CalculateSplitRequest,
    api_key: str = Depends(get_api_key),
) -> CalculateSplitResponse:
    """Calculate bill split with caching and security.

    This endpoint:
    1. Validates the split request
    2. Generates a deterministic split ID (idempotency key)
    3. Checks cache for existing result
    4. Calculates split if not cached
    5. Caches and returns the result

    Args:
        request: FastAPI request object
        split_request: Split calculation request data
        api_key: Authenticated API key

    Returns:
        CalculateSplitResponse with results and share link

    Raises:
        HTTPException: If calculation fails (400, 500)
    """
    from .core.cache import cache_service

    try:
        logger.info(
            f"Processing split calculation for {len(split_request.person_names)} people"
        )

        # Validate input
        if not split_request.person_names:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one person is required",
            )

        # Generate idempotency key for cache
        idempotency_key_material = {
            "people": sorted(split_request.person_names),
            "assignments": sorted(
                [
                    {
                        "item": a.get("item_details", {}).get("item", ""),
                        "price": a.get("item_details", {}).get("price", ""),
                        "assigned_to": sorted(a.get("assigned_to", [])),
                    }
                    for a in split_request.item_assignments
                ],
                key=lambda x: x["item"],
            ),
            "tax": split_request.tax_amount_input,
            "tip": split_request.tip_amount_input,
            "split_evenly": split_request.split_evenly,
        }

        id_hasher = hashlib.sha256()
        id_hasher.update(
            json.dumps(idempotency_key_material, sort_keys=True).encode("utf-8")
        )
        split_id = id_hasher.hexdigest()[:12]

        logger.info(f"Generated split ID: {split_id}")

        # Check cache first
        cached_result = await cache_service.get_split_result(split_id)
        if cached_result:
            logger.info(f"Using cached result for split ID: {split_id}")
            share_link = f"{request.base_url}splits/view/{split_id}"
            return CalculateSplitResponse(
                split_results=cached_result,
                share_link=share_link,
                split_id=split_id,
            )

        # Calculate split
        logger.info("Calculating split...")
        subtotal_for_even = split_request.extracted_subtotal_from_gemini or 0.0

        calculated_split = calculate_split(
            split_request.item_assignments,
            str(split_request.tax_amount_input),
            str(split_request.tip_amount_input),
            split_request.person_names,
            split_evenly_flag=split_request.split_evenly,
            overall_subtotal_for_even_split=subtotal_for_even,
            total_discount_amount=split_request.extracted_total_discount,
        )

        if "Error" in calculated_split:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Calculation error: {calculated_split['Error']}",
            )

        # Cache the result
        await cache_service.set_split_result(split_id, calculated_split)
        logger.info(f"Cached result for split ID: {split_id}")

        share_link = f"{request.base_url}splits/view/{split_id}"

        return CalculateSplitResponse(
            split_results=calculated_split,
            share_link=share_link,
            split_id=split_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Split calculation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@splits_router.get(
    "/view/{split_id}",
    response_model=SharedSplitDataResponse,
    status_code=status.HTTP_200_OK,
)
@rate_limit(100)
async def view_split(
    request: Request,
    split_id: str,
    api_key: str = Depends(get_api_key),
) -> SharedSplitDataResponse:
    """View shared split data.

    This endpoint retrieves previously calculated split data
    for sharing and viewing.

    Args:
        request: FastAPI request object
        split_id: Unique split identifier
        api_key: Authenticated API key

    Returns:
        SharedSplitDataResponse with split details

    Raises:
        HTTPException: If split not found (404)
    """
    from .core.cache import cache_service

    try:
        logger.info(f"Retrieving split data for ID: {split_id}")

        # Try to get from cache first
        cached_data = await cache_service.get_share_data(split_id)
        if cached_data:
            return SharedSplitDataResponse(**cached_data)

        # Return mock data for demonstration (in production, fetch from MinIO)
        mock_data = {
            "split_id": split_id,
            "original_parsed_data": {"mock": "data"},
            "person_names": ["Alice", "Bob"],
            "item_assignments": [],
            "split_evenly_choice": False,
            "total_discount_applied": 0.0,
            "user_adjusted_tax": 2.50,
            "user_adjusted_tip": 5.00,
            "calculated_split_results": {
                "Alice": {"total": 15.0, "subtotal": 10.0, "tax": 2.0, "tip": 3.0},
                "Bob": {"total": 15.0, "subtotal": 10.0, "tax": 2.0, "tip": 3.0},
            },
            "creation_timestamp": time.time(),
        }

        return SharedSplitDataResponse(**mock_data)

    except Exception as e:
        logger.error(f"Error retrieving split: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
