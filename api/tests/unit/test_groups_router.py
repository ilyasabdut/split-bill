"""Unit tests for groups router."""

import uuid

from fastapi import status
from sqlalchemy import select
from src.db.models import Group, GroupMember, User


class TestGroupsRouter:
    """Test cases for groups router endpoints."""

    async def test_create_group_success(self, async_client, auth_headers, test_user):
        """Test creating a group successfully."""
        group_data = {
            "name": "Weekend Trip",
        }

        response = await async_client.post(
            "/groups/", json=group_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Weekend Trip"
        assert data["owner_id"] == test_user.id
        assert "id" in data
        assert "created_at" in data

    async def test_create_group_unauthorized(self, async_client):
        """Test creating group without authentication."""
        group_data = {
            "name": "Weekend Trip",
        }

        response = await async_client.post("/groups/", json=group_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_group_invalid_api_key(self, async_client):
        """Test creating group with invalid API key."""
        group_data = {
            "name": "Weekend Trip",
        }
        headers = {"X-API-Key": "invalid-key"}

        response = await async_client.post("/groups/", json=group_data, headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_group_missing_name(self, async_client, auth_headers):
        """Test creating group without name."""
        group_data = {}

        response = await async_client.post(
            "/groups/", json=group_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_group_empty_name(self, async_client, auth_headers):
        """Test creating group with empty name."""
        group_data = {
            "name": "",
        }

        response = await async_client.post(
            "/groups/", json=group_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_group_success(
        self, async_client, auth_headers, test_group, test_user
    ):
        """Test getting a group successfully."""
        response = await async_client.get(
            f"/groups/{test_group.id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_group.id
        assert data["name"] == test_group.name
        assert data["owner_id"] == test_user.id
        assert "created_at" in data

    async def test_get_group_not_found(self, async_client, auth_headers):
        """Test getting non-existent group."""
        non_existent_id = 99999

        response = await async_client.get(
            f"/groups/{non_existent_id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_group_unauthorized(self, async_client, test_group):
        """Test getting group without authentication."""
        response = await async_client.get(f"/groups/{test_group.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_list_groups_empty(self, async_client, auth_headers):
        """Test listing groups when user has none."""
        response = await async_client.get("/groups/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["groups"] == []
        assert data["total"] == 0

    async def test_list_groups_with_data(
        self, async_client, auth_headers, db_session, test_user
    ):
        """Test listing groups with existing groups."""
        # Create multiple groups
        groups = []
        for i in range(3):
            group = Group(name=f"Group {i+1}", owner_id=test_user.id)
            db_session.add(group)
            groups.append(group)
        await db_session.commit()

        response = await async_client.get("/groups/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["groups"]) == 4  # Including test_group from fixture
        assert data["total"] == 4
        assert all("id" in g and "name" in g for g in data["groups"])

    async def test_list_groups_pagination(
        self, async_client, auth_headers, db_session, test_user
    ):
        """Test group listing with pagination."""
        # Create multiple groups
        for i in range(5):
            group = Group(name=f"Group {i+1}", owner_id=test_user.id)
            db_session.add(group)
        await db_session.commit()

        # Get first page
        response = await async_client.get(
            "/groups/?skip=0&limit=2", headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["groups"]) == 2

        # Get second page
        response = await async_client.get(
            "/groups/?skip=2&limit=2", headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["groups"]) == 2

    async def test_update_group_success(self, async_client, auth_headers, test_group):
        """Test updating a group successfully."""
        update_data = {
            "name": "Updated Group Name",
        }

        response = await async_client.put(
            f"/groups/{test_group.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_group.id
        assert data["name"] == "Updated Group Name"

    async def test_update_group_not_owner(self, async_client, auth_headers, db_session):
        """Test updating a group when not the owner."""
        # Create another user and group
        other_user = User(
            api_key=str(uuid.uuid4()),
            name="Other User",
            email="other@example.com",
        )
        db_session.add(other_user)
        await db_session.commit()

        other_group = Group(name="Other Group", owner_id=other_user.id)
        db_session.add(other_group)
        await db_session.commit()

        update_data = {
            "name": "Should Not Update",
        }

        response = await async_client.put(
            f"/groups/{other_group.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_update_group_not_found(self, async_client, auth_headers):
        """Test updating non-existent group."""
        non_existent_id = 99999
        update_data = {
            "name": "Updated Name",
        }

        response = await async_client.put(
            f"/groups/{non_existent_id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_group_success(
        self, async_client, auth_headers, test_group, db_session
    ):
        """Test deleting a group successfully."""
        response = await async_client.delete(
            f"/groups/{test_group.id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify group was deleted
        result = await db_session.execute(
            select(Group).where(Group.id == test_group.id)
        )
        deleted_group = result.scalar_one_or_none()
        assert deleted_group is None

    async def test_delete_group_not_owner(self, async_client, auth_headers, db_session):
        """Test deleting a group when not the owner."""
        # Create another user and group
        other_user = User(
            api_key=str(uuid.uuid4()),
            name="Other User",
            email="other@example.com",
        )
        db_session.add(other_user)
        await db_session.commit()

        other_group = Group(name="Other Group", owner_id=other_user.id)
        db_session.add(other_group)
        await db_session.commit()

        response = await async_client.delete(
            f"/groups/{other_group.id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_delete_group_not_found(self, async_client, auth_headers):
        """Test deleting non-existent group."""
        non_existent_id = 99999

        response = await async_client.delete(
            f"/groups/{non_existent_id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_add_group_member_success(
        self, async_client, auth_headers, test_group, db_session
    ):
        """Test adding a member to a group."""
        # Create another user
        new_user = User(
            api_key=str(uuid.uuid4()),
            name="New Member",
            email="new@example.com",
        )
        db_session.add(new_user)
        await db_session.commit()

        response = await async_client.post(
            f"/groups/{test_group.id}/members",
            json={"user_id": new_user.id},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["group_id"] == test_group.id
        assert data["user_id"] == new_user.id
        assert "joined_at" in data

    async def test_add_group_member_not_owner(
        self, async_client, auth_headers, db_session, test_user
    ):
        """Test adding member when not group owner."""
        # Create another user and group
        other_user = User(
            api_key=str(uuid.uuid4()),
            name="Other User",
            email="other@example.com",
        )
        db_session.add(other_user)
        await db_session.commit()

        other_group = Group(name="Other Group", owner_id=other_user.id)
        db_session.add(other_group)
        await db_session.commit()

        response = await async_client.post(
            f"/groups/{other_group.id}/members",
            json={"user_id": test_user.id},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_add_duplicate_member(
        self, async_client, auth_headers, test_group, test_user
    ):
        """Test adding same member twice."""
        response = await async_client.post(
            f"/groups/{test_group.id}/members",
            json={"user_id": test_user.id},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_add_member_invalid_user(
        self, async_client, auth_headers, test_group
    ):
        """Test adding non-existent user."""
        non_existent_id = 99999

        response = await async_client.post(
            f"/groups/{test_group.id}/members",
            json={"user_id": non_existent_id},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_list_group_members(
        self, async_client, auth_headers, test_group, test_group_member
    ):
        """Test listing group members."""
        response = await async_client.get(
            f"/groups/{test_group.id}/members", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["members"]) == 1
        assert data["total"] == 1
        assert data["members"][0]["user_id"] == test_group_member.user_id
        assert "user" in data["members"][0]

    async def test_list_group_members_empty(
        self, async_client, auth_headers, db_session, test_user
    ):
        """Test listing members of empty group."""
        # Create a group without members (owner not automatically added as member)
        empty_group = Group(name="Empty Group", owner_id=test_user.id)
        db_session.add(empty_group)
        await db_session.commit()

        response = await async_client.get(
            f"/groups/{empty_group.id}/members", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["members"] == []
        assert data["total"] == 0

    async def test_remove_group_member_success(
        self, async_client, auth_headers, test_group, db_session
    ):
        """Test removing a member from a group."""
        # Create and add a member
        new_user = User(
            api_key=str(uuid.uuid4()),
            name="To Be Removed",
            email="remove@example.com",
        )
        db_session.add(new_user)
        await db_session.commit()

        member = GroupMember(group_id=test_group.id, user_id=new_user.id)
        db_session.add(member)
        await db_session.commit()

        response = await async_client.delete(
            f"/groups/{test_group.id}/members/{new_user.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify member was removed
        from sqlalchemy import select

        result = await db_session.execute(
            select(GroupMember).where(
                GroupMember.group_id == test_group.id,
                GroupMember.user_id == new_user.id,
            )
        )
        removed_member = result.scalar_one_or_none()
        assert removed_member is None

    async def test_remove_group_member_not_owner(
        self, async_client, auth_headers, db_session
    ):
        """Test removing member when not group owner."""
        # Create another user and group
        other_user = User(
            api_key=str(uuid.uuid4()),
            name="Other User",
            email="other@example.com",
        )
        db_session.add(other_user)
        await db_session.commit()

        other_group = Group(name="Other Group", owner_id=other_user.id)
        db_session.add(other_group)
        await db_session.commit()

        response = await async_client.delete(
            f"/groups/{other_group.id}/members/{other_user.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_remove_non_member(self, async_client, auth_headers, test_group):
        """Test removing user who is not a member."""
        non_member_id = 99999

        response = await async_client.delete(
            f"/groups/{test_group.id}/members/{non_member_id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_remove_member_not_found_group(self, async_client, auth_headers):
        """Test removing member from non-existent group."""
        non_existent_id = 99999

        response = await async_client.delete(
            f"/groups/{non_existent_id}/members/{non_existent_id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
