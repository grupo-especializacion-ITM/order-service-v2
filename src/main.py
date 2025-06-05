import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from src.infrastructure.config.settings import get_settings
from src.infrastructure.adapters.input.api.order_router import router as order_router
from src.infrastructure.adapters.input.api.error_handler import setup_error_handlers
from src.infrastructure.adapters.output.messaging.kafka_event_publisher import KafkaEventPublisher


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Get application settings
settings = get_settings()

# Kafka event publisher
kafka_publisher = KafkaEventPublisher()

# Define FastAPI lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the application...")
    try:
        await kafka_publisher.start()
        logger.info("Kafka producer started successfully")
    except Exception as e:
        logger.error(f"Failed to start Kafka producer: {str(e)}")

    yield  # Aquí corre la app

    logger.info("Shutting down the application...")
    try:
        await kafka_publisher.stop()
        logger.info("Kafka producer stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping Kafka producer: {str(e)}")

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    root_path="/order"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up error handlers
setup_error_handlers(app)

# Include routers
app.include_router(order_router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)