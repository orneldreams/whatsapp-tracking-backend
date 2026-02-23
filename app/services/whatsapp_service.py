"""
Service WhatsApp - Gestion de l'envoi et réception de messages via Twilio
"""
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from app.config import get_settings
from loguru import logger

settings = get_settings()


class WhatsAppService:
    """Service de gestion des messages WhatsApp via Twilio"""
    
    def __init__(self):
        """Initialise le client Twilio"""
        self.client = Client(
            settings.twilio_account_sid, 
            settings.twilio_auth_token
        )
        self.from_number = settings.twilio_whatsapp_number
    
    def send_message(self, to_number: str, message: str) -> dict:
        """
        Envoie un message WhatsApp
        
        Args:
            to_number: Numéro de destination (format: +33612345678)
            message: Contenu du message
            
        Returns:
            dict avec success, message_sid, error
        """
        try:
            # S'assurer que le numéro est au bon format
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"
            
            # Envoyer le message
            message_obj = self.client.messages.create(
                from_=self.from_number,
                to=to_number,
                body=message
            )
            
            logger.info(f"Message envoyé à {to_number} - SID: {message_obj.sid}")
            
            return {
                "success": True,
                "message_sid": message_obj.sid,
                "status": message_obj.status,
                "error": None
            }
            
        except TwilioRestException as e:
            logger.error(f"Erreur Twilio lors de l'envoi à {to_number}: {e}")
            return {
                "success": False,
                "message_sid": None,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du message à {to_number}: {e}")
            return {
                "success": False,
                "message_sid": None,
                "error": str(e)
            }
    
    def send_welcome_message(self, to_number: str) -> dict:
        """Envoie un message de bienvenue"""
        message = (
            "Bienvenue ! Pour commencer, nous devons vérifier votre identité.\n\n"
            "Veuillez répondre aux questions suivantes."
        )
        return self.send_message(to_number, message)
    
    def send_rejection_message(self, to_number: str) -> dict:
        """Envoie un message de rejet"""
        message = (
            "Désolé, nous n'avons pas pu vérifier votre identité. "
            "Veuillez contacter votre responsable pour plus d'informations."
        )
        return self.send_message(to_number, message)
    
    def send_unknown_number_message(self, to_number: str) -> dict:
        """Envoie un message pour numéro inconnu"""
        message = (
            "Ce numéro n'est pas enregistré dans notre système. "
            "Veuillez contacter votre responsable."
        )
        return self.send_message(to_number, message)
    
    def format_phone_number(self, phone_number: str) -> str:
        """
        Formate un numéro de téléphone en retirant le préfixe whatsapp:
        
        Args:
            phone_number: Numéro brut (peut avoir whatsapp: ou non)
            
        Returns:
            Numéro formaté sans préfixe
        """
        return phone_number.replace("whatsapp:", "").strip()
    
    def validate_webhook_signature(self, signature: str, url: str, params: dict) -> bool:
        """
        Valide que le webhook vient bien de Twilio
        
        Args:
            signature: Signature X-Twilio-Signature du header
            url: URL complète du webhook
            params: Paramètres POST du webhook
            
        Returns:
            True si la signature est valide
        """
        from twilio.request_validator import RequestValidator
        
        validator = RequestValidator(settings.twilio_auth_token)
        return validator.validate(url, params, signature)
