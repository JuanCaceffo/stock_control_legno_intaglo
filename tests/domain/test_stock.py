"""
Unit tests for the Stock domain object.

This module tests all functionality of the Stock class including:
- Initialization and validation
- Business logic methods (add_stock, remove_stock, etc.)
- Status checking methods
- Serialization (to_dict)
"""

import pytest
from datetime import datetime, timezone
from src.domain.stock import Stock, UnitType, Category
from src.core.exceptions import (
    InvalidSKUError,
    InvalidQuantityError,
    InvalidAmountError,
    InsufficientStockError,
    InvalidMinStockAlertError,
    MinStockAlertExceedsQuantityError
)


class TestStockInitialization:
    """Tests for Stock object initialization and validation."""

    def test_create_valid_stock(self, basic_stock):
        """Test creating a valid Stock object."""
        assert basic_stock.item_name == "Test Wood Panel"
        assert basic_stock.sku == "TEST-001"
        assert basic_stock.quantity == 100.0
        assert basic_stock.unit == UnitType.UNITS
        assert basic_stock.category == Category.RAW_MATERIAL
        assert basic_stock.min_stock_alert == 20.0
        assert basic_stock.created_at is None
        assert basic_stock.updated_at is None

    def test_create_stock_without_min_stock_alert(self, stock_without_alert):
        """Test creating a Stock without min_stock_alert."""
        assert stock_without_alert.min_stock_alert is None

    def test_create_stock_with_timestamps(self, stock_with_timestamps):
        """Test creating a Stock with timestamps."""
        assert stock_with_timestamps.created_at is not None
        assert stock_with_timestamps.updated_at is not None

    def test_empty_sku_raises_error(self):
        """Test that empty SKU raises InvalidSKUError."""
        with pytest.raises(InvalidSKUError):
            Stock(
                item_name="Test Item",
                sku="",
                quantity=100.0,
                unit=UnitType.UNITS,
                category=Category.RAW_MATERIAL
            )

    def test_whitespace_only_sku_raises_error(self):
        """Test that whitespace-only SKU raises InvalidSKUError."""
        with pytest.raises(InvalidSKUError):
            Stock(
                item_name="Test Item",
                sku="   ",
                quantity=100.0,
                unit=UnitType.UNITS,
                category=Category.RAW_MATERIAL
            )

    def test_negative_quantity_raises_error(self):
        """Test that negative quantity raises InvalidQuantityError."""
        with pytest.raises(InvalidQuantityError):
            Stock(
                item_name="Test Item",
                sku="TEST-001",
                quantity=-10.0,
                unit=UnitType.UNITS,
                category=Category.RAW_MATERIAL
            )

    def test_negative_min_stock_alert_raises_error(self):
        """Test that negative min_stock_alert raises InvalidMinStockAlertError."""
        with pytest.raises(InvalidMinStockAlertError):
            Stock(
                item_name="Test Item",
                sku="TEST-001",
                quantity=100.0,
                unit=UnitType.UNITS,
                category=Category.RAW_MATERIAL,
                min_stock_alert=-10.0
            )

    def test_min_stock_alert_exceeds_quantity_raises_error(self):
        """Test that min_stock_alert > quantity raises MinStockAlertExceedsQuantityError."""
        with pytest.raises(MinStockAlertExceedsQuantityError):
            Stock(
                item_name="Test Item",
                sku="TEST-001",
                quantity=50.0,
                unit=UnitType.UNITS,
                category=Category.RAW_MATERIAL,
                min_stock_alert=100.0
            )


class TestStockOperations:
    """Tests for Stock business logic operations."""

    def test_add_stock(self, basic_stock):
        """Test adding stock increases quantity."""
        initial_quantity = basic_stock.quantity
        basic_stock.add_stock(50.0)
        assert basic_stock.quantity == initial_quantity + 50.0

    def test_add_zero_stock_raises_error(self, basic_stock):
        """Test that adding zero raises InvalidAmountError."""
        with pytest.raises(InvalidAmountError):
            basic_stock.add_stock(0)

    def test_add_negative_stock_raises_error(self, basic_stock):
        """Test that adding negative amount raises InvalidAmountError."""
        with pytest.raises(InvalidAmountError):
            basic_stock.add_stock(-10.0)

    def test_remove_stock(self, basic_stock):
        """Test removing stock decreases quantity."""
        initial_quantity = basic_stock.quantity
        basic_stock.remove_stock(30.0)
        assert basic_stock.quantity == initial_quantity - 30.0

    def test_remove_zero_stock_raises_error(self, basic_stock):
        """Test that removing zero raises InvalidAmountError."""
        with pytest.raises(InvalidAmountError):
            basic_stock.remove_stock(0)

    def test_remove_negative_stock_raises_error(self, basic_stock):
        """Test that removing negative amount raises InvalidAmountError."""
        with pytest.raises(InvalidAmountError):
            basic_stock.remove_stock(-10.0)

    def test_remove_more_than_available_raises_error(self, basic_stock):
        """Test that removing more than available raises InsufficientStockError."""
        with pytest.raises(InsufficientStockError) as exc_info:
            basic_stock.remove_stock(200.0)
        assert exc_info.value.current_quantity == basic_stock.quantity
        assert exc_info.value.attempted_removal == 200.0

    def test_remove_exact_quantity(self, basic_stock):
        """Test removing exact available quantity sets quantity to zero."""
        basic_stock.remove_stock(basic_stock.quantity)
        assert basic_stock.quantity == 0

    def test_set_min_stock_alert(self, stock_without_alert):
        """Test setting min_stock_alert."""
        stock_without_alert.set_min_stock_alert(30.0)
        assert stock_without_alert.min_stock_alert == 30.0

    def test_set_negative_min_stock_alert_raises_error(self, basic_stock):
        """Test that setting negative min_stock_alert raises InvalidMinStockAlertError."""
        with pytest.raises(InvalidMinStockAlertError):
            basic_stock.set_min_stock_alert(-10.0)

    def test_update_min_stock_alert(self, basic_stock):
        """Test updating existing min_stock_alert."""
        basic_stock.set_min_stock_alert(50.0)
        assert basic_stock.min_stock_alert == 50.0


class TestStockStatus:
    """Tests for stock status checking methods."""

    def test_is_low_stock_when_below_threshold(self, basic_stock):
        """Test is_low_stock returns True when quantity <= min_stock_alert."""
        assert basic_stock.is_low_stock() is True

    def test_is_low_stock_when_above_threshold(self, basic_stock):
        """Test is_low_stock returns False when quantity > min_stock_alert."""
        basic_stock.add_stock(100.0)
        assert basic_stock.is_low_stock() is False

    def test_is_low_stock_when_equal_to_threshold(self, basic_stock):
        """Test is_low_stock returns True when quantity == min_stock_alert."""
        basic_stock.quantity = 20.0
        assert basic_stock.is_low_stock() is True

    def test_is_low_stock_without_alert(self, stock_without_alert):
        """Test is_low_stock returns False when no min_stock_alert is set."""
        assert stock_without_alert.is_low_stock() is False

    def test_get_stock_status_low(self, basic_stock):
        """Test get_stock_status returns 'low' when below threshold."""
        assert basic_stock.get_stock_status() == "low"

    def test_get_stock_status_adequate(self, basic_stock):
        """Test get_stock_status returns 'adequate' when above threshold."""
        basic_stock.add_stock(100.0)
        assert basic_stock.get_stock_status() == "adequate"

    def test_get_stock_status_adequate_without_alert(self, stock_without_alert):
        """Test get_stock_status returns 'adequate' when no alert is set."""
        assert stock_without_alert.get_stock_status() == "adequate"


class TestStockSerialization:
    """Tests for Stock serialization methods."""

    def test_to_dict_basic(self, basic_stock):
        """Test to_dict returns correct dictionary representation."""
        result = basic_stock.to_dict()
        
        assert result["item_name"] == basic_stock.item_name
        assert result["sku"] == basic_stock.sku
        assert result["quantity"] == basic_stock.quantity
        assert result["unit"] == basic_stock.unit.value
        assert result["category"] == basic_stock.category.value
        assert result["min_stock_alert"] == basic_stock.min_stock_alert
        assert result["status"] == "low"

    def test_to_dict_with_timestamps(self, stock_with_timestamps):
        """Test to_dict includes timestamps when available."""
        result = stock_with_timestamps.to_dict()
        
        assert "created_at" in result
        assert "updated_at" in result
        assert isinstance(result["created_at"], str)
        assert isinstance(result["updated_at"], str)

    def test_to_dict_without_timestamps(self, basic_stock):
        """Test to_dict excludes timestamps when not set."""
        result = basic_stock.to_dict()
        
        assert "created_at" not in result
        assert "updated_at" not in result

    def test_to_dict_without_min_stock_alert(self, stock_without_alert):
        """Test to_dict handles None min_stock_alert correctly."""
        result = stock_without_alert.to_dict()
        
        assert result["min_stock_alert"] is None
        assert result["status"] == "adequate"


class TestUnitTypeEnum:
    """Tests for UnitType enum."""

    def test_unit_type_values(self):
        """Test that UnitType enum has expected values."""
        assert UnitType.METERS.value == "m"
        assert UnitType.PIECES.value == "pcs"
        assert UnitType.KILOGRAMS.value == "kg"
        assert UnitType.LITERS.value == "l"
        assert UnitType.UNITS.value == "units"
        assert UnitType.BOXES.value == "boxes"
        assert UnitType.PALLETS.value == "pallets"

    def test_unit_type_members(self):
        """Test that UnitType has all expected members."""
        expected_members = {
            "METERS", "PIECES", "KILOGRAMS", "LITERS",
            "UNITS", "BOXES", "PALLETS"
        }
        actual_members = {member.name for member in UnitType}
        assert actual_members == expected_members


class TestCategoryEnum:
    """Tests for Category enum."""

    def test_category_values(self):
        """Test that Category enum has expected values."""
        assert Category.RAW_MATERIAL.value == "raw_material"
        assert Category.FINISHED_PRODUCT.value == "finished_product"
        assert Category.PACKAGING.value == "packaging"
        assert Category.TOOLS.value == "tools"
        assert Category.SPARE_PARTS.value == "spare_parts"
        assert Category.CONSUMABLES.value == "consumables"
        assert Category.ELECTRONICS.value == "electronics"
        assert Category.HARDWARE.value == "hardware"

    def test_category_members(self):
        """Test that Category has all expected members."""
        expected_members = {
            "RAW_MATERIAL", "FINISHED_PRODUCT", "PACKAGING", "TOOLS",
            "SPARE_PARTS", "CONSUMABLES", "ELECTRONICS", "HARDWARE"
        }
        actual_members = {member.name for member in Category}
        assert actual_members == expected_members


class TestStockEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_zero_quantity_stock(self):
        """Test creating stock with zero quantity is valid."""
        stock = Stock(
            item_name="Test Item",
            sku="TEST-001",
            quantity=0.0,
            unit=UnitType.UNITS,
            category=Category.RAW_MATERIAL
        )
        assert stock.quantity == 0.0

    def test_very_large_quantity(self):
        """Test creating stock with very large quantity."""
        large_quantity = 1e10
        stock = Stock(
            item_name="Test Item",
            sku="TEST-001",
            quantity=large_quantity,
            unit=UnitType.UNITS,
            category=Category.RAW_MATERIAL
        )
        assert stock.quantity == large_quantity

    def test_fractional_quantity(self):
        """Test creating stock with fractional quantity."""
        stock = Stock(
            item_name="Test Item",
            sku="TEST-001",
            quantity=12.75,
            unit=UnitType.KILOGRAMS,
            category=Category.RAW_MATERIAL
        )
        assert stock.quantity == 12.75

    def test_add_fractional_amount(self, basic_stock):
        """Test adding fractional amount to stock."""
        basic_stock.add_stock(25.5)
        assert basic_stock.quantity == 125.5

    def test_remove_fractional_amount(self, basic_stock):
        """Test removing fractional amount from stock."""
        basic_stock.remove_stock(33.25)
        assert basic_stock.quantity == 66.75

    def test_min_stock_alert_zero(self, stock_without_alert):
        """Test setting min_stock_alert to zero is valid."""
        stock_without_alert.set_min_stock_alert(0.0)
        assert stock_without_alert.min_stock_alert == 0.0
        assert stock_without_alert.is_low_stock() is True

    def test_sku_with_special_characters(self):
        """Test that SKU with special characters is valid."""
        stock = Stock(
            item_name="Test Item",
            sku="TEST-001-ABC/123",
            quantity=100.0,
            unit=UnitType.UNITS,
            category=Category.RAW_MATERIAL
        )
        assert stock.sku == "TEST-001-ABC/123"

    def test_sku_with_spaces_is_valid(self):
        """Test that SKU with leading/trailing spaces is valid (strip happens in validation)."""
        stock = Stock(
            item_name="Test Item",
            sku="  TEST-001  ",
            quantity=100.0,
            unit=UnitType.UNITS,
            category=Category.RAW_MATERIAL
        )
        assert stock.sku == "  TEST-001  "  # SKU is stored as-is, validation only checks it's not empty after strip

    def test_operations_preserve_other_attributes(self, basic_stock):
        """Test that stock operations don't affect other attributes."""
        original_name = basic_stock.item_name
        original_sku = basic_stock.sku
        original_unit = basic_stock.unit
        original_category = basic_stock.category

        basic_stock.add_stock(50.0)
        basic_stock.set_min_stock_alert(25.0)

        assert basic_stock.item_name == original_name
        assert basic_stock.sku == original_sku
        assert basic_stock.unit == original_unit
        assert basic_stock.category == original_category
