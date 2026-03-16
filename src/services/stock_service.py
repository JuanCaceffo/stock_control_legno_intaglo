from datetime import datetime
from sqlmodel import Session, select
from typing import Optional, List
from src.entities.stock import Stock as DBStock
from src.domain.stock import Stock as DomainStock
from src.schemas.stock import StockCreate
from src.core.exceptions import DuplicateSKUError, StockNotFoundError


class StockService:
    """
    Service layer for stock operations.
    
    Handles business logic and database interactions using domain objects.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_stock(self, stock_data: StockCreate) -> DomainStock:
        """
        Create a new stock entry in the database.
        
        Args:
            stock_data: Validated stock creation data
            
        Returns:
            Created domain stock object
            
        Raises:
            ValueError: If SKU already exists or domain validation fails
        """
        # Check if SKU already exists
        existing = self.db.exec(
            select(DBStock).where(DBStock.sku == stock_data.sku)
        ).first()
        
        if existing:
            raise DuplicateSKUError(stock_data.sku)

        # Create domain stock object (validations happen in __post_init__)
        domain_stock = DomainStock(
            item_name=stock_data.item_name,
            sku=stock_data.sku,
            quantity=stock_data.quantity,
            unit=stock_data.unit,
            category=stock_data.category,
            min_stock_alert=stock_data.min_stock_alert
        )

        # Map to database entity
        db_stock = DBStock(
            item_name=domain_stock.item_name,
            sku=domain_stock.sku,
            quantity=domain_stock.quantity,
            unit=domain_stock.unit,
            category=domain_stock.category,
            min_stock_alert=domain_stock.min_stock_alert,
            created_at=datetime.now(datetime.timezone.utc),
            updated_at=datetime.now(datetime.timezone.utc)
        )

        self.db.add(db_stock)
        self.db.commit()
        self.db.refresh(db_stock)
        
        # Update domain object with timestamps from database
        domain_stock.created_at = db_stock.created_at
        domain_stock.updated_at = db_stock.updated_at
        
        return domain_stock

    def get_stock_by_id(self, stock_id: int) -> Optional[DBStock]:
        """
        Retrieve stock by ID.
        
        Args:
            stock_id: Stock entity ID
            
        Returns:
            Database stock entity or None if not found
        """
        return self.db.exec(
            select(DBStock).where(DBStock.id == stock_id)
        ).first()

    def get_stock_by_sku(self, sku: str) -> Optional[DBStock]:
        """
        Retrieve stock by SKU.
        
        Args:
            sku: Stock keeping unit identifier
            
        Returns:
            Database stock entity or None if not found
        """
        return self.db.exec(
            select(DBStock).where(DBStock.sku == sku)
        ).first()

    def get_all_stocks(self) -> List[DBStock]:
        """
        Retrieve all stock entries.
        
        Returns:
            List of all database stock entities
        """
        return self.db.exec(select(DBStock)).all()

    #TODO: tabala aparte para guardar fecha y hora en la cual se modifico la cantidad de stock para determinado SKU (usar un trigger de la db)
    def update_stock_quantity(self, stock_id: int, quantity: float) -> Optional[DBStock]:
        """
        Update stock quantity using domain object validation.
        
        Args:
            stock_id: Stock entity ID
            quantity: New quantity (must be >= 0)
            
        Returns:
            Updated stock entity or None if not found
        """
        db_stock = self.get_stock_by_id(stock_id)
        if not db_stock:
            raise StockNotFoundError(stock_id=stock_id)
        
        # Convert to domain object to use validation
        domain_stock = DomainStock(
            item_name=db_stock.item_name,
            sku=db_stock.sku,
            quantity=quantity,
            unit=db_stock.unit,
            category=db_stock.category,
            min_stock_alert=db_stock.min_stock_alert
        )
        
        # Update database entity
        db_stock.quantity = domain_stock.quantity
        db_stock.updated_at = datetime.now(datetime.timezone.utc)
        
        self.db.add(db_stock)
        self.db.commit()
        self.db.refresh(db_stock)
        
        return db_stock

    def delete_stock(self, stock_id: int) -> bool:
        """
        Delete stock entry.
        
        Args:
            stock_id: Stock entity ID
            
        Returns:
            True if deleted, False if not found
        """
        db_stock = self.get_stock_by_id(stock_id)
        if not db_stock:
            raise StockNotFoundError(stock_id=stock_id)
        
        self.db.delete(db_stock)
        self.db.commit()
        
        return True

    def to_domain(self, db_stock: DBStock) -> DomainStock:
        """
        Convert database entity to domain object.
        
        Args:
            db_stock: Database stock entity
            
        Returns:
            Domain Stock object
        """
        return DomainStock(
            item_name=db_stock.item_name,
            sku=db_stock.sku,
            quantity=db_stock.quantity,
            unit=db_stock.unit,
            category=db_stock.category,
            min_stock_alert=db_stock.min_stock_alert
        )
