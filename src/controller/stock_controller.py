from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from src.config.database import get_db
from src.services.stock_service import StockService
from src.schemas.stock import StockCreate
from src.core.exceptions import StockError


router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_stock(stock_data: StockCreate, db: Session = Depends(get_db)) -> dict:
    """
    Create a new stock entry.
    
    Receives stock information and creates a new entity in the database.
    
    Args:
        stock_data: Stock creation data (validated by Pydantic)
        db: Database session (injected by FastAPI)
        
    Returns:
        Created stock entity as dictionary
        
    Raises:
        HTTPException: If SKU already exists or validation fails
    """
    try:
        service = StockService(db)
        stock = service.create_stock(stock_data)
        
        # Use domain object's to_dict method
        return stock.to_dict()
    except StockError as e:
        # Handle domain-specific errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
