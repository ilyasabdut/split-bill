"""Templates router for the Split Bill API.

This module handles split template CRUD operations.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.deps import get_current_user, get_db
from src.db.models import Template, User

logger = logging.getLogger(__name__)

templates_router = APIRouter(prefix="/templates", tags=["templates"])


async def _get_own_template(db: AsyncSession, template_id: int, user: User):
    """404 for missing templates and for other users' templates alike."""
    template = await db.scalar(
        select(Template).where(Template.id == template_id, Template.user_id == user.id)
    )
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with ID {template_id} not found",
        )
    return template


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class TemplateCreate(BaseModel):
    """Request model for creating a template."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    config: dict = Field(..., description="Template configuration (split settings)")


class TemplateUpdate(BaseModel):
    """Request model for updating a template."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Template name"
    )
    config: Optional[dict] = Field(None, description="Template configuration")


class TemplateResponse(BaseModel):
    """Response model for template data."""

    id: int
    name: str
    user_id: int
    config: dict
    created_at: str

    class Config:
        from_attributes = True


# ============================================================================
# ENDPOINTS
# ============================================================================


@templates_router.post(
    "/",
    response_model=TemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_template(
    request: Request,
    template_data: TemplateCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TemplateResponse:
    """Create a new split template.

    Args:
        request: FastAPI request object
        template_data: Template creation data
        db: Database session

    Returns:
        TemplateResponse with created template details

    Raises:
        HTTPException: If user not found (404)
    """
    try:
        logger.info(f"Creating template: {template_data.name}")

        # Create template
        template = Template(
            name=template_data.name,
            user_id=user.id,
            config=template_data.config,
        )
        db.add(template)
        await db.commit()
        await db.refresh(template)

        logger.info(f"Template created with ID: {template.id}")
        return TemplateResponse(
            id=template.id,
            name=template.name,
            user_id=template.user_id,
            config=template.config,
            created_at=template.created_at.isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating template: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@templates_router.get(
    "/{template_id}",
    response_model=TemplateResponse,
    status_code=status.HTTP_200_OK,
)
async def get_template(
    request: Request,
    template_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TemplateResponse:
    """Get a template by ID.

    Args:
        request: FastAPI request object
        template_id: Template ID
        db: Database session

    Returns:
        TemplateResponse with template details

    Raises:
        HTTPException: If template not found (404)
    """
    try:
        logger.info(f"Fetching template: {template_id}")

        template = await _get_own_template(db, template_id, user)

        return TemplateResponse(
            id=template.id,
            name=template.name,
            user_id=template.user_id,
            config=template.config,
            created_at=template.created_at.isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching template: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@templates_router.get(
    "/",
    response_model=List[TemplateResponse],
    status_code=status.HTTP_200_OK,
)
async def list_templates(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> List[TemplateResponse]:
    """List the current user's templates.

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        List of TemplateResponse objects
    """
    try:
        logger.info(f"Listing templates for user {user.id}")

        result = await db.execute(select(Template).where(Template.user_id == user.id))
        templates = result.scalars().all()

        return [
            TemplateResponse(
                id=t.id,
                name=t.name,
                user_id=t.user_id,
                config=t.config,
                created_at=t.created_at.isoformat(),
            )
            for t in templates
        ]

    except Exception as e:
        logger.error(f"Error listing templates: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@templates_router.put(
    "/{template_id}",
    response_model=TemplateResponse,
    status_code=status.HTTP_200_OK,
)
async def update_template(
    request: Request,
    template_id: int,
    template_data: TemplateUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TemplateResponse:
    """Update a template.

    Args:
        request: FastAPI request object
        template_id: Template ID
        template_data: Template update data
        db: Database session

    Returns:
        TemplateResponse with updated template details

    Raises:
        HTTPException: If template not found (404)
    """
    try:
        logger.info(f"Updating template: {template_id}")

        template = await _get_own_template(db, template_id, user)

        if template_data.name is not None:
            template.name = template_data.name
        if template_data.config is not None:
            template.config = template_data.config

        await db.commit()
        await db.refresh(template)

        return TemplateResponse(
            id=template.id,
            name=template.name,
            user_id=template.user_id,
            config=template.config,
            created_at=template.created_at.isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating template: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@templates_router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_template(
    request: Request,
    template_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    """Delete a template.

    Args:
        request: FastAPI request object
        template_id: Template ID
        db: Database session

    Raises:
        HTTPException: If template not found (404)
    """
    try:
        logger.info(f"Deleting template: {template_id}")

        template = await _get_own_template(db, template_id, user)

        await db.delete(template)
        await db.commit()

        logger.info(f"Template deleted: {template_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting template: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
