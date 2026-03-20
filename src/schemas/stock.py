from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from src.domain.stock import UnitType, Category
from src.core.exceptions import MinStockAlertExceedsQuantityError


class StockCreate(BaseModel):
    """
    Pydantic model for stock creation request.
    
    Validates incoming data before creating a stock entity.
    """
    item_name: str = Field(..., min_length=1, max_length=200, description="Name of the item")
    sku: str = Field(..., min_length=1, max_length=100, description="Unique stock keeping unit identifier")
    quantity: float = Field(..., ge=0, description="Current quantity in stock (must be >= 0)")
    unit: str = Field(..., description="Unit of measurement type")
    category: str = Field(..., description="Product category")
    min_stock_alert: Optional[float] = Field(None, ge=0, description="Optional minimum stock threshold for alerts")

    @field_validator('unit')
    @classmethod
    def validate_unit(cls, v):
        if v not in [unit.value for unit in UnitType]:
            raise ValueError(f"Invalid unit: {v}. Allowed: {[unit.value for unit in UnitType]}")
        return v

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        if v not in [cat.value for cat in Category]:
            raise ValueError(f"Invalid category: {v}. Allowed: {[cat.value for cat in Category]}")
        return v

    @field_validator('min_stock_alert')
    @classmethod
    def validate_min_stock_alert(cls, v, info):
        """Validate that min_stock_alert does not exceed quantity."""
        if v is not None and 'quantity' in info.data:
            if v > info.data['quantity']:
                # Use the same message as the centralized exception
                raise MinStockAlertExceedsQuantityError()
        return v

    class Config:
        from_attributes = True
        use_enum_values = True


class StockResponse(BaseModel):
    """
    Pydantic model for stock response.
    
    Returns stock data after creation or retrieval.
    """
    id: int
    item_name: str
    sku: str
    quantity: float
    unit: str
    category: str
    min_stock_alert: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
