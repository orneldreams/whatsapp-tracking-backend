"""
Application principale FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.database import init_db
from app.routes import webhook, persons, messages, admin
from app.config import get_settings

settings = get_settings()

# Configuration de Loguru
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.log_level
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    logger.info("🚀 Démarrage de l'application WhatsApp Tracking Backend")
    logger.info(f"Environment: {settings.app_env}")
    
    # Initialiser la base de données
    try:
        init_db()
        logger.info("✅ Base de données initialisée")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation de la base de données: {e}")
    
    yield
    
    logger.info("👋 Arrêt de l'application")


# Création de l'application FastAPI
app = FastAPI(
    title="WhatsApp Tracking Backend",
    description="Système de suivi et d'identification des personnes via WhatsApp",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrement des routes
app.include_router(webhook.router, prefix="/api/v1")
app.include_router(persons.router, prefix="/api/v1")
app.include_router(messages.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Route racine"""
    return {
        "service": "WhatsApp Tracking Backend",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/api/v1/health")
async def health():
    """Endpoint de santé"""
    return {
        "status": "healthy",
        "service": "whatsapp-tracking-backend",
        "environment": settings.app_env
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
