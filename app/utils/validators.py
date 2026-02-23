"""
Utilitaires pour la validation et le formatage des données
"""
import re
import phonenumbers
from typing import Optional


def validate_phone_number(phone: str) -> bool:
    """
    Valide un numéro de téléphone
    
    Args:
        phone: Numéro à valider
        
    Returns:
        True si le numéro est valide
    """
    try:
        parsed = phonenumbers.parse(phone, None)
        return phonenumbers.is_valid_number(parsed)
    except Exception:
        return False


def format_phone_number(phone: str, country_code: str = "FR") -> Optional[str]:
    """
    Formate un numéro de téléphone au format international
    
    Args:
        phone: Numéro à formater
        country_code: Code pays par défaut
        
    Returns:
        Numéro formaté ou None si invalide
    """
    try:
        parsed = phonenumbers.parse(phone, country_code)
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        return None


def clean_whatsapp_number(phone: str) -> str:
    """
    Nettoie un numéro WhatsApp (retire le préfixe whatsapp:)
    
    Args:
        phone: Numéro brut
        
    Returns:
        Numéro nettoyé
    """
    return phone.replace("whatsapp:", "").strip()


def validate_email(email: str) -> bool:
    """
    Valide une adresse email
    
    Args:
        email: Email à valider
        
    Returns:
        True si l'email est valide
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_string(text: str, max_length: int = None) -> str:
    """
    Nettoie une chaîne de caractères
    
    Args:
        text: Texte à nettoyer
        max_length: Longueur maximale
        
    Returns:
        Texte nettoyé
    """
    if not text:
        return ""
    
    # Retirer les espaces en début/fin
    text = text.strip()
    
    # Retirer les caractères de contrôle
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Limiter la longueur si nécessaire
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text
