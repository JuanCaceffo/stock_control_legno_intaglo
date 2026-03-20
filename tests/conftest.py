"""
Pytest configuration and fixtures for the Legno Intaglo Stock API tests.
"""

import pytest
from datetime import datetime, timezone
from src.domain.stock import Stock, UnitType, Category

@pytest.fixture
def sample_stock_data():
    """Fixture providing sample stock data for tests."""
    return {
        "item_name": "Test Wood Panel",
        "sku": "TEST-001",
        "quantity": 100.0,
        "unit": UnitType.UNITS.value,
        "category": Category.RAW_MATERIAL.value,
        "min_stock_alert": 20.0
    }


@pytest.fixture
def basic_stock(sample_stock_data):
    """Fixture creating a basic valid Stock object."""
    return Stock(**sample_stock_data)


@pytest.fixture
def stock_with_timestamps(sample_stock_data):
    """Fixture creating a Stock object with timestamps."""
    now = datetime.now(timezone.utc)
    stock = Stock(**sample_stock_data)
    stock.created_at = now
    stock.updated_at = now
    return stock


@pytest.fixture
def low_stock(sample_stock_data):
    """Fixture creating a Stock object with low stock (below min_stock_alert)."""
    data = sample_stock_data.copy()
    data["quantity"] = 20.0
    data["min_stock_alert"] = 20.0
    stock = Stock(**data)
    stock.remove_stock(1.0)  # Reduce quantity to 19.0, below min_stock_alert
    return stock


@pytest.fixture
def stock_without_alert(sample_stock_data):
    """Fixture creating a Stock object without min_stock_alert."""
    data = sample_stock_data.copy()
    data["min_stock_alert"] = None
    return Stock(**data)
