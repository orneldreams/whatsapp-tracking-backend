"""
CRUD (Create, Read, Update, Delete) pour les opérations de base de données
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import Optional, List
from app.models import Person, AuthSession, Message, AuditLog, SessionState, MessageType
from app.schemas import PersonCreate, PersonUpdate, MessageCreate


# ==================== PERSON ====================

def get_person_by_phone(db: Session, phone_number: str) -> Optional[Person]:
    """Récupère une personne par son numéro de téléphone"""
    return db.query(Person).filter(Person.phone_number == phone_number).first()


def get_person_by_id(db: Session, person_id: int) -> Optional[Person]:
    """Récupère une personne par son ID"""
    return db.query(Person).filter(Person.id == person_id).first()


def get_person_by_identifiant(db: Session, identifiant: str) -> Optional[Person]:
    """Récupère une personne par son identifiant interne"""
    return db.query(Person).filter(Person.identifiant_interne == identifiant).first()


def create_person(db: Session, person: PersonCreate) -> Person:
    """Crée une nouvelle personne"""
    db_person = Person(**person.model_dump())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person


def update_person(db: Session, person_id: int, person_update: PersonUpdate) -> Optional[Person]:
    """Met à jour une personne"""
    db_person = get_person_by_id(db, person_id)
    if not db_person:
        return None
    
    update_data = person_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_person, key, value)
    
    db_person.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_person)
    return db_person


def mark_person_verified(db: Session, phone_number: str) -> Optional[Person]:
    """Marque une personne comme vérifiée"""
    db_person = get_person_by_phone(db, phone_number)
    if not db_person:
        return None
    
    db_person.verified = True
    db_person.last_activity = datetime.utcnow()
    db.commit()
    db.refresh(db_person)
    return db_person


def update_last_activity(db: Session, phone_number: str) -> None:
    """Met à jour la dernière activité d'une personne"""
    db_person = get_person_by_phone(db, phone_number)
    if db_person:
        db_person.last_activity = datetime.utcnow()
        db.commit()


def get_all_persons(db: Session, skip: int = 0, limit: int = 100) -> List[Person]:
    """Récupère toutes les personnes"""
    return db.query(Person).offset(skip).limit(limit).all()


# ==================== AUTH SESSION ====================

def get_active_session(db: Session, phone_number: str) -> Optional[AuthSession]:
    """Récupère la session active pour un numéro"""
    return db.query(AuthSession).filter(
        and_(
            AuthSession.phone_number == phone_number,
            AuthSession.state.in_([SessionState.PENDING, SessionState.AUTHENTICATING])
        )
    ).order_by(AuthSession.created_at.desc()).first()


def create_auth_session(db: Session, phone_number: str) -> AuthSession:
    """Crée une nouvelle session d'authentification"""
    db_session = AuthSession(
        phone_number=phone_number,
        state=SessionState.PENDING,
        attempts=0,
        current_question=0
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def update_session_state(
    db: Session, 
    session_id: int, 
    state: SessionState, 
    increment_attempts: bool = False
) -> Optional[AuthSession]:
    """Met à jour l'état d'une session"""
    db_session = db.query(AuthSession).filter(AuthSession.id == session_id).first()
    if not db_session:
        return None
    
    db_session.state = state
    if increment_attempts:
        db_session.attempts += 1
    
    if state in [SessionState.AUTHENTICATED, SessionState.REJECTED]:
        db_session.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_session)
    return db_session


def save_session_answer(
    db: Session, 
    session_id: int, 
    question_number: int, 
    answer: str
) -> Optional[AuthSession]:
    """Sauvegarde la réponse à une question"""
    db_session = db.query(AuthSession).filter(AuthSession.id == session_id).first()
    if not db_session:
        return None
    
    if question_number == 1:
        db_session.question_1_answer = answer
    elif question_number == 2:
        db_session.question_2_answer = answer
    elif question_number == 3:
        db_session.question_3_answer = answer
    
    db_session.current_question = question_number
    db.commit()
    db.refresh(db_session)
    return db_session


def update_current_question(
    db: Session, 
    session_id: int, 
    question_number: int
) -> Optional[AuthSession]:
    """Met à jour le numéro de question actuelle"""
    db_session = db.query(AuthSession).filter(AuthSession.id == session_id).first()
    if not db_session:
        return None
    
    db_session.current_question = question_number
    db.commit()
    db.refresh(db_session)
    return db_session


# ==================== MESSAGE ====================

def create_message(db: Session, message: MessageCreate) -> Message:
    """Crée un nouveau message"""
    db_message = Message(**message.model_dump())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_messages_by_phone(
    db: Session, 
    phone_number: str, 
    skip: int = 0, 
    limit: int = 50
) -> List[Message]:
    """Récupère les messages d'une personne"""
    return db.query(Message).filter(
        Message.phone_number == phone_number
    ).order_by(Message.created_at.desc()).offset(skip).limit(limit).all()


def get_message_by_sid(db: Session, message_sid: str) -> Optional[Message]:
    """Récupère un message par son SID Twilio"""
    return db.query(Message).filter(Message.twilio_message_sid == message_sid).first()


# ==================== AUDIT LOG ====================

def create_audit_log(
    db: Session, 
    phone_number: str, 
    action: str, 
    details: str = None, 
    success: bool = True
) -> AuditLog:
    """Crée un log d'audit"""
    db_log = AuditLog(
        phone_number=phone_number,
        action=action,
        details=details,
        success=success
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_audit_logs_by_phone(
    db: Session, 
    phone_number: str, 
    skip: int = 0, 
    limit: int = 50
) -> List[AuditLog]:
    """Récupère les logs d'audit d'une personne"""
    return db.query(AuditLog).filter(
        AuditLog.phone_number == phone_number
    ).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
