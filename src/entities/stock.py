from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone
from src.domain.stock import UnitType, Category


class Stock(SQLModel, table=True):
    """
    Database entity for inventory stock.
    
    Maps to the 'stocks' table in PostgreSQL.
    """
    __tablename__ = "stocks"

    id: Optional[int] = Field(default=None, primary_key=True)
    item_name: str = Field(index=True)
    sku: str = Field(unique=True, index=True)
    quantity: float = Field(default=0.0)
    unit: UnitType = Field(default=UnitType.UNITS)
    category: Category = Field(default=Category.CONSUMABLES)
    min_stock_alert: Optional[float] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
