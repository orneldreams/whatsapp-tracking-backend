"""
Schémas Pydantic pour la validation des données
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from enum import Enum


class SessionStateEnum(str, Enum):
    """États de session"""
    PENDING = "pending"
    AUTHENTICATING = "authenticating"
    AUTHENTICATED = "authenticated"
    REJECTED = "rejected"


class MessageTypeEnum(str, Enum):
    """Types de messages"""
    AUTH = "authentication"
    TRACKING = "tracking"
    SYSTEM = "system"


# Schémas Person
class PersonBase(BaseModel):
    """Schéma de base pour Person"""
    phone_number: str = Field(..., min_length=10, max_length=20)
    identifiant_interne: str = Field(..., min_length=1, max_length=50)
    date_cle: datetime
    localite: str = Field(..., min_length=1, max_length=100)
    numero_referent: str = Field(..., min_length=1, max_length=50)
    nom: Optional[str] = Field(None, max_length=100)
    prenom: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=100)


class PersonCreate(PersonBase):
    """Schéma pour créer une personne"""
    pass


class PersonUpdate(BaseModel):
    """Schéma pour mettre à jour une personne"""
    phone_number: Optional[str] = None
    localite: Optional[str] = None
    numero_referent: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[str] = None
    verified: Optional[bool] = None


class PersonResponse(PersonBase):
    """Schéma de réponse pour Person"""
    id: int
    verified: bool
    created_at: datetime
    updated_at: datetime
    last_activity: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Schémas AuthSession
class AuthSessionBase(BaseModel):
    """Schéma de base pour AuthSession"""
    phone_number: str


class AuthSessionCreate(AuthSessionBase):
    """Schéma pour créer une session"""
    pass


class AuthSessionResponse(AuthSessionBase):
    """Schéma de réponse pour AuthSession"""
    id: int
    state: SessionStateEnum
    attempts: int
    current_question: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Schémas Message
class MessageBase(BaseModel):
    """Schéma de base pour Message"""
    phone_number: str
    content: str
    message_type: MessageTypeEnum


class MessageCreate(MessageBase):
    """Schéma pour créer un message"""
    twilio_message_sid: Optional[str] = None
    direction: Optional[str] = None


class MessageResponse(MessageBase):
    """Schéma de réponse pour Message"""
    id: int
    twilio_message_sid: Optional[str] = None
    direction: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Schémas pour les webhooks Twilio
class TwilioWebhookRequest(BaseModel):
    """Schéma pour les webhooks Twilio entrants"""
    From: str = Field(..., alias="From")
    To: str = Field(..., alias="To")
    Body: str = Field(..., alias="Body")
    MessageSid: str = Field(..., alias="MessageSid")
    
    class Config:
        populate_by_name = True
    
    @validator('From')
    def clean_phone_number(cls, v):
        """Nettoie le numéro de téléphone (enlève whatsapp:)"""
        return v.replace("whatsapp:", "")


# Schémas pour les réponses API
class APIResponse(BaseModel):
    """Schéma de réponse API générique"""
    success: bool
    message: str
    data: Optional[dict] = None


class AuthenticationStatus(BaseModel):
    """Statut d'authentification"""
    is_authenticated: bool
    is_verified: bool
    session_state: Optional[SessionStateEnum] = None
    message: str


# Schémas pour l'import Excel
class PersonImport(BaseModel):
    """Schéma pour l'import de personnes depuis Excel"""
    phone_number: str
    identifiant_interne: str
    date_cle: str  # Sera converti en datetime
    localite: str
    numero_referent: str
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[str] = None
