"""
Routes pour le webhook WhatsApp/Twilio
"""
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import AuthService, WhatsAppService
from app import crud
from app.models import MessageType, SessionState
from app.schemas import MessageCreate
from loguru import logger

router = APIRouter(prefix="/webhook", tags=["webhook"])
whatsapp_service = WhatsAppService()


@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Webhook pour recevoir les messages WhatsApp de Twilio
    
    Ce endpoint est appelé par Twilio à chaque message reçu
    """
    # Nettoyer le numéro de téléphone
    phone_number = whatsapp_service.format_phone_number(From)
    message_content = Body.strip()
    
    logger.info(f"Message reçu de {phone_number}: {message_content[:50]}...")
    
    # Créer le log d'audit
    crud.create_audit_log(
        db, 
        phone_number, 
        "MESSAGE_RECEIVED",
        f"Message: {message_content[:100]}"
    )
    
    # 1. Vérifier si la personne existe
    exists, person = AuthService(db).check_person_exists(phone_number)
    
    if not exists:
        logger.warning(f"Numéro inconnu: {phone_number}")
        whatsapp_service.send_unknown_number_message(phone_number)
        crud.create_audit_log(
            db,
            phone_number,
            "UNKNOWN_NUMBER",
            "Numéro non enregistré dans la base",
            success=False
        )
        return {"status": "rejected", "reason": "unknown_number"}
    
    # 2. Vérifier si la personne est déjà vérifiée
    auth_service = AuthService(db)
    
    if person.verified:
        # Personne déjà authentifiée - Enregistrer le message comme suivi
        crud.create_message(
            db,
            MessageCreate(
                phone_number=phone_number,
                content=message_content,
                message_type=MessageType.TRACKING,
                twilio_message_sid=MessageSid,
                direction="inbound"
            )
        )
        crud.update_last_activity(db, phone_number)
        
        # Réponse de confirmation
        whatsapp_service.send_message(
            phone_number,
            "Merci pour votre message. Il a bien été enregistré."
        )
        
        logger.info(f"Message de suivi enregistré pour {phone_number}")
        return {"status": "tracked", "verified": True}
    
    # 3. Personne non vérifiée - Lancer ou continuer l'authentification
    session = auth_service.get_or_create_session(phone_number)
    
    if not session:
        # Session rejetée (trop de tentatives)
        whatsapp_service.send_rejection_message(phone_number)
        return {"status": "rejected", "reason": "max_attempts"}
    
    # 4. Traiter l'authentification
    # Si c'est la première interaction pour cette personne (session en PENDING)
    if session.state == SessionState.PENDING:
        next_q_num, next_q_text = auth_service.get_next_question(session)
        whatsapp_service.send_message(phone_number, next_q_text)
        
        # Mettre à jour le statut de la session à AUTHENTICATING
        crud.update_session_state(db, session.id, SessionState.AUTHENTICATING)
        crud.update_current_question(db, session.id, next_q_num)
        
        # Enregistrer le message comme message d'authentification
        crud.create_message(
            db,
            MessageCreate(
                phone_number=phone_number,
                content=message_content,
                message_type=MessageType.AUTH,
                twilio_message_sid=MessageSid,
                direction="inbound"
            )
        )
        
        return {"status": "authenticating", "question": next_q_num}
    
    # 5. Traiter la réponse
    result = auth_service.process_answer(session, message_content)
    
    # Enregistrer le message
    crud.create_message(
        db,
        MessageCreate(
            phone_number=phone_number,
            content=message_content,
            message_type=MessageType.AUTH,
            twilio_message_sid=MessageSid,
            direction="inbound"
        )
    )
    
    # Envoyer la réponse appropriée
    whatsapp_service.send_message(phone_number, result["message"])
    
    logger.info(f"Authentification résultat pour {phone_number}: {result['status']}")
    
    return {
        "status": result["status"],
        "authenticated": result.get("authenticated", False),
        "question_number": result.get("question_number")
    }


@router.get("/health")
async def webhook_health():
    """Endpoint de santé pour vérifier que le webhook est actif"""
    return {"status": "ok", "service": "whatsapp-webhook"}
