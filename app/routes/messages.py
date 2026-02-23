"""
Routes pour les messages
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import crud
from app.schemas import MessageResponse

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/{phone_number}", response_model=List[MessageResponse])
def get_messages_by_phone(
    phone_number: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Récupère les messages d'une personne"""
    # Vérifier que la personne existe
    person = crud.get_person_by_phone(db, phone_number)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personne non trouvée"
        )
    
    messages = crud.get_messages_by_phone(db, phone_number, skip=skip, limit=limit)
    return messages


@router.get("/sid/{message_sid}", response_model=MessageResponse)
def get_message_by_sid(message_sid: str, db: Session = Depends(get_db)):
    """Récupère un message par son SID Twilio"""
    message = crud.get_message_by_sid(db, message_sid)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message non trouvé"
        )
    return message
