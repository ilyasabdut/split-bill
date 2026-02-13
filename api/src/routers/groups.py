"""Groups router for the Split Bill API.

This module handles group management CRUD operations.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.deps import get_db
from src.db.models import Group, GroupMember, User

logger = logging.getLogger(__name__)

groups_router = APIRouter(prefix="/groups", tags=["groups"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class GroupCreate(BaseModel):
    """Request model for creating a group."""

    name: str = Field(..., min_length=1, max_length=255, description="Group name")
    owner_id: int = Field(..., description="Owner user ID")


class GroupUpdate(BaseModel):
    """Request model for updating a group."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Group name"
    )


class GroupResponse(BaseModel):
    """Response model for group data."""

    id: int
    name: str
    owner_id: int
    created_at: str
    member_count: int = 0

    class Config:
        from_attributes = True


class GroupMemberAdd(BaseModel):
    """Request model for adding a member to a group."""

    user_id: int = Field(..., description="User ID to add")


class GroupMemberResponse(BaseModel):
    """Response model for group member."""

    user_id: int
    user_name: str
    user_email: Optional[str] = None
    joined_at: str


# ============================================================================
# ENDPOINTS
# ============================================================================


@groups_router.post(
    "/",
    response_model=GroupResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_group(
    request: Request,
    group_data: GroupCreate,
    db: AsyncSession = Depends(get_db),
) -> GroupResponse:
    """Create a new group.

    Args:
        request: FastAPI request object
        group_data: Group creation data
        db: Database session

    Returns:
        GroupResponse with created group details

    Raises:
        HTTPException: If owner not found (404)
    """
    try:
        logger.info(f"Creating group: {group_data.name}")

        # Verify owner exists
        owner_result = await db.execute(
            select(User).where(User.id == group_data.owner_id)
        )
        owner = owner_result.scalar_one_or_none()

        if not owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {group_data.owner_id} not found",
            )

        # Create group
        group = Group(name=group_data.name, owner_id=group_data.owner_id)
        db.add(group)
        await db.commit()
        await db.refresh(group)

        logger.info(f"Group created with ID: {group.id}")
        return GroupResponse(
            id=group.id,
            name=group.name,
            owner_id=group.owner_id,
            created_at=group.created_at.isoformat(),
            member_count=0,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating group: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@groups_router.get(
    "/{group_id}",
    response_model=GroupResponse,
    status_code=status.HTTP_200_OK,
)
async def get_group(
    request: Request,
    group_id: int,
    db: AsyncSession = Depends(get_db),
) -> GroupResponse:
    """Get a group by ID.

    Args:
        request: FastAPI request object
        group_id: Group ID
        db: Database session

    Returns:
        GroupResponse with group details

    Raises:
        HTTPException: If group not found (404)
    """
    try:
        logger.info(f"Fetching group: {group_id}")

        result = await db.execute(select(Group).where(Group.id == group_id))
        group = result.scalar_one_or_none()

        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with ID {group_id} not found",
            )

        # Count members
        member_count_result = await db.execute(
            select(GroupMember).where(GroupMember.group_id == group_id)
        )
        member_count = len(member_count_result.scalars().all())

        return GroupResponse(
            id=group.id,
            name=group.name,
            owner_id=group.owner_id,
            created_at=group.created_at.isoformat(),
            member_count=member_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching group: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@groups_router.get(
    "/",
    response_model=List[GroupResponse],
    status_code=status.HTTP_200_OK,
)
async def list_groups(
    request: Request,
    owner_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
) -> List[GroupResponse]:
    """List all groups, optionally filtered by owner.

    Args:
        request: FastAPI request object
        owner_id: Optional filter for owner ID
        db: Database session

    Returns:
        List of GroupResponse objects
    """
    try:
        logger.info(f"Listing groups (owner_id filter: {owner_id})")

        query = select(Group)
        if owner_id is not None:
            query = query.where(Group.owner_id == owner_id)

        result = await db.execute(query)
        groups = result.scalars().all()

        response = []
        for group in groups:
            # Count members
            member_count_result = await db.execute(
                select(GroupMember).where(GroupMember.group_id == group.id)
            )
            member_count = len(member_count_result.scalars().all())

            response.append(
                GroupResponse(
                    id=group.id,
                    name=group.name,
                    owner_id=group.owner_id,
                    created_at=group.created_at.isoformat(),
                    member_count=member_count,
                )
            )

        return response

    except Exception as e:
        logger.error(f"Error listing groups: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@groups_router.put(
    "/{group_id}",
    response_model=GroupResponse,
    status_code=status.HTTP_200_OK,
)
async def update_group(
    request: Request,
    group_id: int,
    group_data: GroupUpdate,
    db: AsyncSession = Depends(get_db),
) -> GroupResponse:
    """Update a group.

    Args:
        request: FastAPI request object
        group_id: Group ID
        group_data: Group update data
        db: Database session

    Returns:
        GroupResponse with updated group details

    Raises:
        HTTPException: If group not found (404)
    """
    try:
        logger.info(f"Updating group: {group_id}")

        result = await db.execute(select(Group).where(Group.id == group_id))
        group = result.scalar_one_or_none()

        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with ID {group_id} not found",
            )

        if group_data.name is not None:
            group.name = group_data.name

        await db.commit()
        await db.refresh(group)

        # Count members
        member_count_result = await db.execute(
            select(GroupMember).where(GroupMember.group_id == group_id)
        )
        member_count = len(member_count_result.scalars().all())

        return GroupResponse(
            id=group.id,
            name=group.name,
            owner_id=group.owner_id,
            created_at=group.created_at.isoformat(),
            member_count=member_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating group: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@groups_router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_group(
    request: Request,
    group_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a group.

    Args:
        request: FastAPI request object
        group_id: Group ID
        db: Database session

    Raises:
        HTTPException: If group not found (404)
    """
    try:
        logger.info(f"Deleting group: {group_id}")

        result = await db.execute(select(Group).where(Group.id == group_id))
        group = result.scalar_one_or_none()

        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with ID {group_id} not found",
            )

        await db.delete(group)
        await db.commit()

        logger.info(f"Group deleted: {group_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting group: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@groups_router.post(
    "/{group_id}/members",
    response_model=GroupMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_group_member(
    request: Request,
    group_id: int,
    member_data: GroupMemberAdd,
    db: AsyncSession = Depends(get_db),
) -> GroupMemberResponse:
    """Add a member to a group.

    Args:
        request: FastAPI request object
        group_id: Group ID
        member_data: Member addition data
        db: Database session

    Returns:
        GroupMemberResponse with member details

    Raises:
        HTTPException: If group or user not found (404), or already member (400)
    """
    try:
        logger.info(f"Adding member {member_data.user_id} to group {group_id}")

        # Verify group exists
        group_result = await db.execute(select(Group).where(Group.id == group_id))
        group = group_result.scalar_one_or_none()

        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with ID {group_id} not found",
            )

        # Verify user exists
        user_result = await db.execute(
            select(User).where(User.id == member_data.user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {member_data.user_id} not found",
            )

        # Check if already a member
        existing_result = await db.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == member_data.user_id,
            )
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this group",
            )

        # Add member
        member = GroupMember(group_id=group_id, user_id=member_data.user_id)
        db.add(member)
        await db.commit()
        await db.refresh(member)

        return GroupMemberResponse(
            user_id=user.id,
            user_name=user.name,
            user_email=user.email,
            joined_at=member.joined_at.isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding group member: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@groups_router.get(
    "/{group_id}/members",
    response_model=List[GroupMemberResponse],
    status_code=status.HTTP_200_OK,
)
async def list_group_members(
    request: Request,
    group_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[GroupMemberResponse]:
    """List all members of a group.

    Args:
        request: FastAPI request object
        group_id: Group ID
        db: Database session

    Returns:
        List of GroupMemberResponse objects

    Raises:
        HTTPException: If group not found (404)
    """
    try:
        logger.info(f"Listing members for group: {group_id}")

        # Verify group exists
        group_result = await db.execute(select(Group).where(Group.id == group_id))
        group = group_result.scalar_one_or_none()

        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with ID {group_id} not found",
            )

        # Get members
        result = await db.execute(
            select(GroupMember).where(GroupMember.group_id == group_id)
        )
        members = result.scalars().all()

        response = []
        for member in members:
            # Get user details
            user_result = await db.execute(
                select(User).where(User.id == member.user_id)
            )
            user = user_result.scalar_one_or_none()

            if user:
                response.append(
                    GroupMemberResponse(
                        user_id=user.id,
                        user_name=user.name,
                        user_email=user.email,
                        joined_at=member.joined_at.isoformat(),
                    )
                )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing group members: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@groups_router.delete(
    "/{group_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_group_member(
    request: Request,
    group_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove a member from a group.

    Args:
        request: FastAPI request object
        group_id: Group ID
        user_id: User ID to remove
        db: Database session

    Raises:
        HTTPException: If group or membership not found (404)
    """
    try:
        logger.info(f"Removing member {user_id} from group {group_id}")

        # Find membership
        result = await db.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id,
            )
        )
        member = result.scalar_one_or_none()

        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membership not found",
            )

        await db.delete(member)
        await db.commit()

        logger.info("Member removed from group")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing group member: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
