from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.config.database import init_db
from src.controller.stock_controller import router as stock_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events for FastAPI application.
    
    Initializes database on startup.
    """
    # Startup
    init_db()
    yield
    # Shutdown (if needed)


app = FastAPI(
    title="Legno Intaglo Stock API",
    description="API for managing inventory stock",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(stock_router)


@app.get("/")
def read_root():
    """
    Root endpoint.
    
    Returns:
        Welcome message
    """
    return {"message": "Welcome to Legno Intaglo Stock API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {"status": "healthy"}
