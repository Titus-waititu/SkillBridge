from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.routes import skills, roadmap, jobs
from app.db.database import engine, Base
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting Skill Coach API...")
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    logger.info("👋 Shutting down Skill Coach API...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Career Path Navigator with RAG and Vector Search",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
cors_origins = settings.CORS_ORIGINS.copy()
# Add Vercel domain explicitly if not already present
if "https://skill-bridge-jade.vercel.app" not in cors_origins:
    cors_origins.append("https://skill-bridge-jade.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
)

# Include routers
app.include_router(skills.router, prefix="/api/v1/skills", tags=["Skills"])
app.include_router(roadmap.router, prefix="/api/v1/roadmap", tags=["Roadmap"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Welcome to Skill Coach API",
        "status": "healthy",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "vector_search": "enabled",
    }


@app.get("/debug/cors")
async def debug_cors():
    """Debug endpoint to check CORS configuration"""
    return {
        "cors_origins": settings.CORS_ORIGINS,
        "app_name": settings.APP_NAME,
        "debug": settings.DEBUG
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
