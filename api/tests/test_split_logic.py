"""Tests for split calculation logic."""

from src.models.schemas import ItemAssignment
from src.services.split_logic import calculate_split


def create_assignment(
    item: str, price: float, assigned_to: list[str]
) -> ItemAssignment:
    """Helper to create ItemAssignment."""
    return ItemAssignment(
        item_details={"item": item, "price": price}, assigned_to=assigned_to
    )


class TestCalculateSplit:
    """Tests for calculate_split function."""

    def test_simple_split_two_people(self):
        """Test simple split between two people."""
        assignments = [create_assignment("Burger", 10.00, ["Alice", "Bob"])]
        result = calculate_split(
            assignments=assignments,
            tax_amount_str="1.00",
            tip_amount_str="2.00",
            person_names=["Alice", "Bob"],
        )

        assert "Alice" in result
        assert "Bob" in result
        assert result["Alice"]["subtotal"] == 5.00
        assert result["Bob"]["subtotal"] == 5.00
        # Tax and tip should be proportional
        assert result["Alice"]["tax"] > 0
        assert result["Alice"]["tip"] > 0

    def test_even_split(self):
        """Test even split flag."""
        result = calculate_split(
            assignments=[],
            tax_amount_str="3.00",
            tip_amount_str="5.00",
            person_names=["Alice", "Bob", "Charlie"],
            split_evenly_flag=True,
            overall_subtotal_for_even_split=30.00,
        )

        assert "Alice" in result
        assert "Bob" in result
        assert "Charlie" in result
        # Each should have equal subtotal
        assert result["Alice"]["subtotal"] == 10.00
        assert result["Bob"]["subtotal"] == 10.00
        assert result["Charlie"]["subtotal"] == 10.00

    def test_item_assigned_to_one_person(self):
        """Test item assigned to single person."""
        assignments = [create_assignment("Steak", 25.00, ["Alice"])]
        result = calculate_split(
            assignments=assignments,
            tax_amount_str="2.00",
            tip_amount_str="4.00",
            person_names=["Alice", "Bob"],
        )

        assert result["Alice"]["subtotal"] == 25.00
        assert result["Bob"]["subtotal"] == 0.00

    def test_shared_item(self):
        """Test item shared by multiple people."""
        assignments = [create_assignment("Pizza", 20.00, ["Alice", "Bob"])]
        result = calculate_split(
            assignments=assignments,
            tax_amount_str="2.00",
            tip_amount_str="3.00",
            person_names=["Alice", "Bob"],
        )

        # Each should pay half
        assert result["Alice"]["subtotal"] == 10.00
        assert result["Bob"]["subtotal"] == 10.00

    def test_empty_assignments(self):
        """Test with no item assignments."""
        result = calculate_split(
            assignments=[],
            tax_amount_str="0",
            tip_amount_str="0",
            person_names=["Alice"],
        )

        assert result["Alice"]["subtotal"] == 0.00
        assert result["Alice"]["tax"] == 0.00
        assert result["Alice"]["tip"] == 0.00

    def test_tax_and_tip_proportional(self):
        """Test that tax and tip are distributed proportionally."""
        assignments = [
            create_assignment("Expensive Item", 80.00, ["Alice"]),
            create_assignment("Cheap Item", 20.00, ["Bob"]),
        ]
        result = calculate_split(
            assignments=assignments,
            tax_amount_str="10.00",
            tip_amount_str="10.00",
            person_names=["Alice", "Bob"],
        )

        # Alice should pay 80% of tax and tip (80/100)
        # Bob should pay 20% of tax and tip (20/100)
        alice_total_tax_tip = result["Alice"]["tax"] + result["Alice"]["tip"]
        bob_total_tax_tip = result["Bob"]["tax"] + result["Bob"]["tip"]

        assert abs(alice_total_tax_tip - 16.00) < 0.01  # 80% of 20
        assert abs(bob_total_tax_tip - 4.00) < 0.01  # 20% of 20

    def test_single_person(self):
        """Test split with single person."""
        assignments = [create_assignment("Solo Item", 50.00, ["Alice"])]
        result = calculate_split(
            assignments=assignments,
            tax_amount_str="5.00",
            tip_amount_str="5.00",
            person_names=["Alice"],
        )

        assert result["Alice"]["subtotal"] == 50.00
        assert result["Alice"]["total"] == 60.00

    def test_multiple_shared_items(self):
        """Test multiple items with different assignments."""
        assignments = [
            create_assignment("Appetizer", 15.00, ["Alice", "Bob"]),
            create_assignment("Main1", 30.00, ["Alice"]),
            create_assignment("Main2", 30.00, ["Bob"]),
            create_assignment("Dessert", 10.00, ["Alice", "Bob"]),
        ]
        result = calculate_split(
            assignments=assignments,
            tax_amount_str="8.50",
            tip_amount_str="8.50",
            person_names=["Alice", "Bob"],
        )

        # Alice: 7.5 + 30 + 5 = 42.5 subtotal
        # Bob: 7.5 + 30 + 5 = 42.5 subtotal
        assert result["Alice"]["subtotal"] == 42.50
        assert result["Bob"]["subtotal"] == 42.50

    def test_error_handling(self):
        """Test error handling for invalid input."""
        # This should not raise, but return error in result
        result = calculate_split(
            assignments=[],
            tax_amount_str="invalid",
            tip_amount_str="invalid",
            person_names=[],
        )

        # Should handle gracefully
        assert isinstance(result, dict)
