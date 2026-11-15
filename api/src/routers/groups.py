"""Groups router for the Split Bill API.

This module handles group management CRUD operations.
"""

import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.deps import get_current_user, get_db
from src.db.models import Group, GroupMember, User

logger = logging.getLogger(__name__)

groups_router = APIRouter(prefix="/groups", tags=["groups"])


def _visible_to(user: User):
    """Groups the user owns or is a member of."""
    member_of = select(GroupMember.group_id).where(GroupMember.user_id == user.id)
    return or_(Group.owner_id == user.id, Group.id.in_(member_of))


async def _get_group(db: AsyncSession, group_id: int, user: User, owner_only=False):
    """404 unless visible to the user; 403 if visible but owner_only and not owner."""
    group = await db.scalar(
        select(Group).where(Group.id == group_id, _visible_to(user))
    )
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with ID {group_id} not found",
        )
    if owner_only and group.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the group owner can do this",
        )
    return group


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class GroupCreate(BaseModel):
    """Request model for creating a group."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=255, description="Group name")


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
    """Request model for adding a member to a group.

    People are added by name (and optional email): without accounts there is
    no other user id to point at. Each becomes a User row with no device_id.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)


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
    user: User = Depends(get_current_user),
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

        group = Group(name=group_data.name, owner_id=user.id)
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
    user: User = Depends(get_current_user),
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

        group = await _get_group(db, group_id, user)

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
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> List[GroupResponse]:
    """List the groups the current user owns or belongs to.

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        List of GroupResponse objects
    """
    try:
        logger.info(f"Listing groups for user {user.id}")

        result = await db.execute(select(Group).where(_visible_to(user)))
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
    user: User = Depends(get_current_user),
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

        group = await _get_group(db, group_id, user, owner_only=True)

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
    user: User = Depends(get_current_user),
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

        group = await _get_group(db, group_id, user, owner_only=True)

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
    user: User = Depends(get_current_user),
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
        logger.info(f"Adding member to group {group_id}")

        await _get_group(db, group_id, user, owner_only=True)

        # Same email = same person (email is unique on users); never a device user
        person = None
        if member_data.email:
            person = await db.scalar(
                select(User).where(
                    User.email == member_data.email, User.device_id.is_(None)
                )
            )
        if person is None:
            person = User(
                name=member_data.name,
                email=member_data.email,
                api_key=uuid.uuid4().hex,
            )
            db.add(person)
            await db.flush()

        existing = await db.scalar(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == person.id,
            )
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this group",
            )

        member = GroupMember(group_id=group_id, user_id=person.id)
        db.add(member)
        await db.commit()
        await db.refresh(member)

        return GroupMemberResponse(
            user_id=person.id,
            user_name=person.name,
            user_email=person.email,
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
    user: User = Depends(get_current_user),
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

        await _get_group(db, group_id, user)

        # Get members
        result = await db.execute(
            select(GroupMember).where(GroupMember.group_id == group_id)
        )
        members = result.scalars().all()

        response = []
        for member in members:
            # Get user details
            person = await db.get(User, member.user_id)

            if person:
                response.append(
                    GroupMemberResponse(
                        user_id=person.id,
                        user_name=person.name,
                        user_email=person.email,
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
    user: User = Depends(get_current_user),
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

        await _get_group(db, group_id, user, owner_only=True)

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
