"""
Routes d'administration et santé de l'application
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Vérifie la santé de l'application et de la base de données"""
    try:
        # Test de la connexion DB
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "service": "whatsapp-tracking-backend"
    }


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Récupère des statistiques sur l'utilisation"""
    from app.models import Person, Message, AuthSession
    
    total_persons = db.query(Person).count()
    verified_persons = db.query(Person).filter(Person.verified == True).count()
    total_messages = db.query(Message).count()
    active_sessions = db.query(AuthSession).filter(
        AuthSession.state.in_(["pending", "authenticating"])
    ).count()
    
    return {
        "total_persons": total_persons,
        "verified_persons": verified_persons,
        "unverified_persons": total_persons - verified_persons,
        "total_messages": total_messages,
        "active_auth_sessions": active_sessions
    }
