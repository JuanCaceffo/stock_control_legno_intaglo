from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


class UnitType(Enum):
    """Static enumeration for unit types."""
    METERS = "m"
    PIECES = "pcs"
    KILOGRAMS = "kg"
    LITERS = "l"
    UNITS = "units"
    BOXES = "boxes"
    PALLETS = "pallets"


class Category(Enum):
    """Static enumeration for product categories."""
    RAW_MATERIAL = "raw_material"
    FINISHED_PRODUCT = "finished_product"
    PACKAGING = "packaging"
    TOOLS = "tools"
    SPARE_PARTS = "spare_parts"
    CONSUMABLES = "consumables"
    ELECTRONICS = "electronics"
    HARDWARE = "hardware"


@dataclass
class Stock:
    """
    Domain object representing inventory stock.
    
    Attributes:
        item_name: Name of the item
        sku: Unique stock keeping unit identifier
        quantity: Current quantity in stock (must be >= 0)
        unit: Unit of measurement type
        category: Product category
        min_stock_alert: Optional minimum stock threshold for alerts
    """
    item_name: str
    sku: str
    quantity: float
    unit: UnitType
    category: Category
    min_stock_alert: Optional[float] = None

    def __post_init__(self):
        """Validate the stock object after initialization."""
        self._validate_sku()
        self._validate_quantity()
        self._validate_min_stock_alert()

    def _validate_sku(self):
        """Ensure SKU is not empty."""
        if not self.sku or not self.sku.strip():
            raise ValueError("SKU cannot be empty")

    def _validate_quantity(self):
        """Ensure quantity is non-negative."""
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative")

    def _validate_min_stock_alert(self):
        """Validate minimum stock alert if provided."""
        if self.min_stock_alert is not None:
            if self.min_stock_alert < 0:
                raise ValueError("Minimum stock alert cannot be negative")
            # Optionally, ensure min_stock_alert is not greater than current quantity
            # This is a business decision - commented out as it may not always apply
            # if self.min_stock_alert > self.quantity:
            #     raise ValueError("Minimum stock alert cannot exceed current quantity")

    def is_low_stock(self) -> bool:
        """
        Check if current stock is below the minimum alert threshold.
        
        Returns:
            True if stock is low, False otherwise or if no alert is set
        """
        if self.min_stock_alert is None:
            return False
        return self.quantity <= self.min_stock_alert

    def add_stock(self, amount: float):
        """
        Add quantity to stock.
        
        Args:
            amount: Amount to add (must be positive)
            
        Raises:
            ValueError: If amount is not positive
        """
        if amount <= 0:
            raise ValueError("Amount to add must be positive")
        self.quantity += amount

    def remove_stock(self, amount: float):
        """
        Remove quantity from stock.
        
        Args:
            amount: Amount to remove (must be positive and <= current quantity)
            
        Raises:
            ValueError: If amount is invalid or would result in negative stock
        """
        if amount <= 0:
            raise ValueError("Amount to remove must be positive")
        if amount > self.quantity:
            raise ValueError("Cannot remove more than current stock quantity")
        self.quantity -= amount

    def set_min_stock_alert(self, threshold: float):
        """
        Set or update the minimum stock alert threshold.
        
        Args:
            threshold: The minimum quantity threshold (must be non-negative)
            
        Raises:
            ValueError: If threshold is negative
        """
        if threshold < 0:
            raise ValueError("Minimum stock alert cannot be negative")
        self.min_stock_alert = threshold

    def get_stock_status(self) -> str:
        """
        Get a human-readable stock status.
        
        Returns:
            Status string: "low", "adequate", or "overstocked"
        """
        if self.min_stock_alert is not None and self.quantity <= self.min_stock_alert:
            return "low"
        # Could add overstock logic if there's a max threshold
        return "adequate"

    def to_dict(self) -> dict:
        """
        Convert stock object to dictionary representation.
        
        Returns:
            Dictionary with stock data
        """
        return {
            "item_name": self.item_name,
            "sku": self.sku,
            "quantity": self.quantity,
            "unit": self.unit.value,
            "category": self.category.value,
            "min_stock_alert": self.min_stock_alert,
            "status": self.get_stock_status()
        }
