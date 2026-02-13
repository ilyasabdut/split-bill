"""Unit tests for templates router."""

import uuid

from fastapi import status
from sqlalchemy import select
from src.db.models import Template, User


class TestTemplatesRouter:
    """Test cases for templates router endpoints."""

    async def test_create_template_success(self, async_client, auth_headers, test_user):
        """Test creating a template successfully."""
        template_data = {
            "name": "Even Split Template",
            "config": {
                "type": "even",
                "settings": {
                    "include_tax": True,
                    "include_tip": True,
                },
            },
        }

        response = await async_client.post(
            "/templates/", json=template_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Even Split Template"
        assert data["user_id"] == test_user.id
        assert data["config"]["type"] == "even"
        assert data["config"]["settings"]["include_tax"] is True
        assert "id" in data
        assert "created_at" in data

    async def test_create_template_unauthorized(self, async_client):
        """Test creating template without authentication."""
        template_data = {
            "name": "Even Split Template",
            "config": {"type": "even"},
        }

        response = await async_client.post("/templates/", json=template_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_template_invalid_api_key(self, async_client):
        """Test creating template with invalid API key."""
        template_data = {
            "name": "Even Split Template",
            "config": {"type": "even"},
        }
        headers = {"X-API-Key": "invalid-key"}

        response = await async_client.post(
            "/templates/", json=template_data, headers=headers
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_template_missing_name(self, async_client, auth_headers):
        """Test creating template without name."""
        template_data = {
            "config": {"type": "even"},
        }

        response = await async_client.post(
            "/templates/", json=template_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_template_empty_name(self, async_client, auth_headers):
        """Test creating template with empty name."""
        template_data = {
            "name": "",
            "config": {"type": "even"},
        }

        response = await async_client.post(
            "/templates/", json=template_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_template_missing_config(self, async_client, auth_headers):
        """Test creating template without config."""
        template_data = {
            "name": "Even Split Template",
        }

        response = await async_client.post(
            "/templates/", json=template_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_template_invalid_config(self, async_client, auth_headers):
        """Test creating template with invalid config."""
        template_data = {
            "name": "Even Split Template",
            "config": "invalid",  # Should be object
        }

        response = await async_client.post(
            "/templates/", json=template_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_template_complex_config(
        self, async_client, auth_headers, test_user
    ):
        """Test creating template with complex config."""
        template_data = {
            "name": "Itemized Split Template",
            "config": {
                "type": "itemized",
                "settings": {
                    "tax_calculation": "proportional",
                    "tip_calculation": "percentage",
                    "default_tax_rate": 0.08,
                    "default_tip_rate": 0.18,
                    "round_to": 0.01,
                },
                "rules": {
                    "min_item_price": 0.01,
                    "max_item_price": 10000.0,
                    "require_item_name": True,
                },
            },
        }

        response = await async_client.post(
            "/templates/", json=template_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["config"]["type"] == "itemized"
        assert data["config"]["settings"]["tax_calculation"] == "proportional"
        assert data["config"]["rules"]["require_item_name"] is True

    async def test_get_template_success(
        self, async_client, auth_headers, test_template, test_user
    ):
        """Test getting a template successfully."""
        response = await async_client.get(
            f"/templates/{test_template.id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_template.id
        assert data["name"] == test_template.name
        assert data["user_id"] == test_user.id
        assert data["config"] == test_template.config
        assert "created_at" in data

    async def test_get_template_not_found(self, async_client, auth_headers):
        """Test getting non-existent template."""
        non_existent_id = 99999

        response = await async_client.get(
            f"/templates/{non_existent_id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_template_unauthorized(self, async_client, test_template):
        """Test getting template without authentication."""
        response = await async_client.get(f"/templates/{test_template.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_template_not_owner(self, async_client, auth_headers, db_session):
        """Test getting template owned by another user."""
        # Create another user and template
        other_user = User(
            api_key=str(uuid.uuid4()),
            name="Other User",
            email="other@example.com",
        )
        db_session.add(other_user)
        await db_session.commit()

        other_template = Template(
            user_id=other_user.id,
            name="Other Template",
            config={"type": "even"},
        )
        db_session.add(other_template)
        await db_session.commit()

        response = await async_client.get(
            f"/templates/{other_template.id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_list_templates_empty(self, async_client, auth_headers):
        """Test listing templates when user has none."""
        response = await async_client.get("/templates/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["templates"] == []
        assert data["total"] == 0

    async def test_list_templates_with_data(
        self, async_client, auth_headers, db_session, test_user
    ):
        """Test listing templates with existing templates."""
        # Create multiple templates
        templates = []
        for i in range(3):
            template = Template(
                user_id=test_user.id,
                name=f"Template {i+1}",
                config={"type": "even" if i % 2 == 0 else "itemized"},
            )
            db_session.add(template)
            templates.append(template)
        await db_session.commit()

        response = await async_client.get("/templates/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["templates"]) == 4  # Including test_template from fixture
        assert data["total"] == 4
        assert all("id" in t and "name" in t for t in data["templates"])

    async def test_list_templates_pagination(
        self, async_client, auth_headers, db_session, test_user
    ):
        """Test template listing with pagination."""
        # Create multiple templates
        for i in range(5):
            template = Template(
                user_id=test_user.id,
                name=f"Template {i+1}",
                config={"type": "even"},
            )
            db_session.add(template)
        await db_session.commit()

        # Get first page
        response = await async_client.get(
            "/templates/?skip=0&limit=2", headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["templates"]) == 2

        # Get second page
        response = await async_client.get(
            "/templates/?skip=2&limit=2", headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["templates"]) == 2

    async def test_update_template_success(
        self, async_client, auth_headers, test_template
    ):
        """Test updating a template successfully."""
        update_data = {
            "name": "Updated Template Name",
            "config": {
                "type": "itemized",
                "settings": {
                    "tax_calculation": "equal",
                },
            },
        }

        response = await async_client.put(
            f"/templates/{test_template.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_template.id
        assert data["name"] == "Updated Template Name"
        assert data["config"]["type"] == "itemized"
        assert data["config"]["settings"]["tax_calculation"] == "equal"

    async def test_update_template_partial(
        self, async_client, auth_headers, test_template
    ):
        """Test partial update of a template."""
        update_data = {
            "name": "Only Name Updated",
        }

        response = await async_client.put(
            f"/templates/{test_template.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_template.id
        assert data["name"] == "Only Name Updated"
        # Config should remain unchanged
        assert data["config"] == test_template.config

    async def test_update_template_not_owner(
        self, async_client, auth_headers, db_session
    ):
        """Test updating template owned by another user."""
        # Create another user and template
        other_user = User(
            api_key=str(uuid.uuid4()),
            name="Other User",
            email="other@example.com",
        )
        db_session.add(other_user)
        await db_session.commit()

        other_template = Template(
            user_id=other_user.id,
            name="Other Template",
            config={"type": "even"},
        )
        db_session.add(other_template)
        await db_session.commit()

        update_data = {
            "name": "Should Not Update",
        }

        response = await async_client.put(
            f"/templates/{other_template.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_update_template_not_found(self, async_client, auth_headers):
        """Test updating non-existent template."""
        non_existent_id = 99999
        update_data = {
            "name": "Updated Name",
        }

        response = await async_client.put(
            f"/templates/{non_existent_id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_template_invalid_config(
        self, async_client, auth_headers, test_template
    ):
        """Test updating template with invalid config."""
        update_data = {
            "config": "invalid",  # Should be object
        }

        response = await async_client.put(
            f"/templates/{test_template.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_delete_template_success(
        self, async_client, auth_headers, test_template, db_session
    ):
        """Test deleting a template successfully."""
        response = await async_client.delete(
            f"/templates/{test_template.id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify template was deleted
        result = await db_session.execute(
            select(Template).where(Template.id == test_template.id)
        )
        deleted_template = result.scalar_one_or_none()
        assert deleted_template is None

    async def test_delete_template_not_owner(
        self, async_client, auth_headers, db_session
    ):
        """Test deleting template owned by another user."""
        # Create another user and template
        other_user = User(
            api_key=str(uuid.uuid4()),
            name="Other User",
            email="other@example.com",
        )
        db_session.add(other_user)
        await db_session.commit()

        other_template = Template(
            user_id=other_user.id,
            name="Other Template",
            config={"type": "even"},
        )
        db_session.add(other_template)
        await db_session.commit()

        response = await async_client.delete(
            f"/templates/{other_template.id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_delete_template_not_found(self, async_client, auth_headers):
        """Test deleting non-existent template."""
        non_existent_id = 99999

        response = await async_client.delete(
            f"/templates/{non_existent_id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_template_user_cascade_delete(
        self, async_client, auth_headers, db_session, test_user
    ):
        """Test that templates are deleted when user is deleted."""
        # Create multiple templates
        for i in range(3):
            template = Template(
                user_id=test_user.id,
                name=f"Template {i+1}",
                config={"type": "even"},
            )
            db_session.add(template)
        await db_session.commit()

        # Delete user
        await db_session.delete(test_user)
        await db_session.commit()

        # Verify all templates were deleted
        result = await db_session.execute(select(Template))
        templates = result.scalars().all()
        assert len(templates) == 0
