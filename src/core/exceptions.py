"""
Custom exceptions for the Legno Intaglo Stock API.

This module provides a hierarchy of domain-specific exceptions
to improve error handling and maintain consistency across the application.
"""


class StockError(Exception):
    """Base exception for all stock-related errors."""
    pass


class DuplicateSKUError(StockError):
    """Raised when attempting to create a stock with an existing SKU."""

    def __init__(self, sku: str):
        self.sku = sku
        super().__init__(f"Stock with SKU '{sku}' already exists")


class InvalidSKUError(StockError):
    """Raised when SKU validation fails."""

    def __init__(self):
        super().__init__("SKU cannot be empty")


class InvalidQuantityError(StockError):
    """Raised when quantity validation fails."""

    def __init__(self):
        super().__init__("Quantity cannot be negative")


class InvalidAmountError(StockError):
    """Raised when an amount operation (add/remove) is invalid."""

    def __init__(self, message: str = "Invalid amount"):
        self.message = message
        super().__init__(message)


class InsufficientStockError(StockError):
    """Raised when attempting to remove more stock than available."""

    def __init__(self, current_quantity: float, attempted_removal: float):
        self.current_quantity = current_quantity
        self.attempted_removal = attempted_removal
        message = f"Insufficient stock: {current_quantity} available, {attempted_removal} requested"
        super().__init__(message)


class InvalidMinStockAlertError(StockError):
    """Raised when minimum stock alert validation fails."""

    def __init__(self, message: str = "Minimum stock alert validation failed"):
        self.message = message
        super().__init__(message)


class MinStockAlertExceedsQuantityError(InvalidMinStockAlertError):
    """Raised when minimum stock alert exceeds current quantity."""

    def __init__(self):
        super().__init__("Minimum stock alert cannot exceed current quantity")


class StockNotFoundError(StockError):
    """Raised when a stock entry cannot be found."""

    def __init__(self, stock_id: int = None, sku: str = None):
        self.stock_id = stock_id
        self.sku = sku
        if stock_id:
            super().__init__(f"Stock with ID {stock_id} not found")
        elif sku:
            super().__init__(f"Stock with SKU '{sku}' not found")
        else:
            super().__init__("Stock not found")
