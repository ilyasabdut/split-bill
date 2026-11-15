"""Split math and the calculate -> view share-link round trip."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from src.db.deps import get_db
from src.main import API_KEY, app, calculate_split


class FakeSession:
    """Stands in for AsyncSession: keeps added Split rows in a list."""

    def __init__(self):
        self.rows = []

    def add(self, row):
        row.created_at = row.created_at or datetime(2026, 1, 1)
        self.rows.append(row)

    async def commit(self):
        pass

    async def scalar(self, stmt):
        share_id = stmt.compile().params["share_id_1"]
        return next((r for r in self.rows if r.share_id == share_id), None)


@pytest.fixture
def client():
    session = FakeSession()

    async def _get_db():
        yield session

    app.dependency_overrides[get_db] = _get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_calculate_split_itemized_with_tax_and_tip():
    result = calculate_split(
        [
            {"item_details": {"item": "Pizza", "price": 30}, "assigned_to": ["A", "B"]},
            {"item_details": {"item": "Beer", "price": 10}, "assigned_to": ["A"]},
        ],
        "4",
        "8",
        ["A", "B"],
    )
    assert result["A"]["subtotal"] == 25
    assert result["B"]["subtotal"] == 15
    assert result["A"]["total"] == pytest.approx(25 + 2.5 + 5)
    assert result["B"]["total"] == pytest.approx(15 + 1.5 + 3)


def test_calculate_split_evenly():
    result = calculate_split(
        [],
        "0",
        "0",
        ["A", "B", "C"],
        split_evenly_flag=True,
        overall_subtotal_for_even_split=30,
    )
    assert [result[p]["total"] for p in "ABC"] == [10, 10, 10]


def test_calculate_then_view_round_trip(client):
    body = {
        "person_names": ["Alice", "Bob"],
        "item_assignments": [
            {
                "item_details": {"item": "Ramen", "price": 20},
                "assigned_to": ["Alice", "Bob"],
            }
        ],
        "tax_amount_input": 2,
        "tip_amount_input": 0,
    }
    calc = client.post(
        "/splits/calculate", json=body, headers={"Authorization": f"Bearer {API_KEY}"}
    )
    assert calc.status_code == 200
    data = calc.json()
    assert len(data["split_id"]) == 32
    assert data["share_link"].endswith(f"/splits/view/{data['split_id']}")

    view = client.get(f"/splits/view/{data['split_id']}")  # no API key: public link
    assert view.status_code == 200
    shared = view.json()
    assert shared["split_id"] == data["split_id"]
    assert shared["person_names"] == ["Alice", "Bob"]
    assert shared["user_adjusted_tax"] == 2
    assert shared["calculated_split_results"] == data["split_results"]
    assert shared["calculated_split_results"]["Alice"]["total"] == 11


def test_client_results_are_what_the_share_link_shows(client):
    auth = {"Authorization": f"Bearer {API_KEY}"}
    results = {"Alice": {"total": 12.5, "tax_share": 1}, "Bob": {"total": 7.5}}
    body = {"person_names": ["Alice", "Bob"], "client_results": results}
    split_id = client.post("/splits/calculate", json=body, headers=auth).json()[
        "split_id"
    ]
    assert (
        client.get(f"/splits/view/{split_id}").json()["calculated_split_results"]
        == results
    )

    body["client_results"] = {"Mallory": {"total": 1}}
    assert client.post("/splits/calculate", json=body, headers=auth).status_code == 422
    body["client_results"] = {"Alice": {"total": -1}, "Bob": {"total": 1}}
    assert client.post("/splits/calculate", json=body, headers=auth).status_code == 422


def test_view_missing_split_returns_404(client):
    assert client.get("/splits/view/doesnotexist").status_code == 404


def test_calculate_requires_api_key(client):
    assert client.post(
        "/splits/calculate", json={"person_names": ["A"]}
    ).status_code in (401, 403)
