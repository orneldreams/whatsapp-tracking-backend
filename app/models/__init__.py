"""
Modèles SQLAlchemy pour la base de données
"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base


class SessionState(str, enum.Enum):
    """États possibles d'une session"""
    PENDING = "pending"
    AUTHENTICATING = "authenticating"
    AUTHENTICATED = "authenticated"
    REJECTED = "rejected"


class MessageType(str, enum.Enum):
    """Types de messages"""
    AUTH = "authentication"
    TRACKING = "tracking"
    SYSTEM = "system"


class Person(Base):
    """Table des personnes enregistrées"""
    __tablename__ = "persons"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    identifiant_interne = Column(String(50), unique=True, nullable=False)
    date_cle = Column(DateTime, nullable=False)
    localite = Column(String(100), nullable=False)
    numero_referent = Column(String(50), nullable=False)
    verified = Column(Boolean, default=False, nullable=False)
    
    # Champs additionnels
    nom = Column(String(100))
    prenom = Column(String(100))
    email = Column(String(100))
    
    # Métadonnées
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    last_activity = Column(DateTime)
    
    def __repr__(self):
        return f"<Person {self.identifiant_interne} - {self.phone_number}>"


class AuthSession(Base):
    """Table des sessions d'authentification"""
    __tablename__ = "auth_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), nullable=False, index=True)
    state = Column(SQLEnum(SessionState), default=SessionState.PENDING, nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    
    # Réponses temporaires (stockage JSON-like)
    question_1_answer = Column(String(200))
    question_2_answer = Column(String(200))
    question_3_answer = Column(String(200))
    
    # Compteurs
    current_question = Column(Integer, default=0)
    
    # Métadonnées
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<AuthSession {self.phone_number} - {self.state}>"


class Message(Base):
    """Table des messages WhatsApp"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), nullable=False, index=True)
    content = Column(Text, nullable=False)
    message_type = Column(SQLEnum(MessageType), nullable=False)
    
    # Métadonnées Twilio
    twilio_message_sid = Column(String(100), unique=True)
    direction = Column(String(20))  # inbound / outbound
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    sent_at = Column(DateTime)
    
    def __repr__(self):
        return f"<Message {self.phone_number} - {self.message_type}>"


class AuditLog(Base):
    """Table des logs d'audit pour traçabilité"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), index=True)
    action = Column(String(100), nullable=False)
    details = Column(Text)
    success = Column(Boolean, nullable=False)
    
    # Métadonnées
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<AuditLog {self.action} - {self.phone_number}>"
