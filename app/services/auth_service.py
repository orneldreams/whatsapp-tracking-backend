"""
Service d'authentification - Logique métier pour l'identification des personnes
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Tuple, Dict
from app import crud
from app.models import SessionState, Person, AuthSession
from app.config import get_settings

settings = get_settings()


class AuthService:
    """Service gérant l'authentification des personnes via WhatsApp"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_person_exists(self, phone_number: str) -> Tuple[bool, Optional[Person]]:
        """
        Vérifie si une personne existe dans la base
        Returns: (exists, person)
        """
        person = crud.get_person_by_phone(self.db, phone_number)
        return (person is not None, person)
    
    def is_person_verified(self, phone_number: str) -> bool:
        """Vérifie si une personne est déjà vérifiée"""
        person = crud.get_person_by_phone(self.db, phone_number)
        return person.verified if person else False
    
    def get_or_create_session(self, phone_number: str) -> Optional[AuthSession]:
        """Récupère ou crée une session d'authentification"""
        # Vérifier s'il existe une session active
        session = crud.get_active_session(self.db, phone_number)
        
        if session:
            # Vérifier le nombre de tentatives
            if session.attempts >= settings.max_auth_attempts:
                crud.update_session_state(self.db, session.id, SessionState.REJECTED)
                crud.create_audit_log(
                    self.db, 
                    phone_number, 
                    "MAX_ATTEMPTS_REACHED",
                    f"Session {session.id} rejetée après {session.attempts} tentatives",
                    success=False
                )
                return None
            return session
        
        # Créer une nouvelle session
        new_session = crud.create_auth_session(self.db, phone_number)
        crud.create_audit_log(
            self.db, 
            phone_number, 
            "AUTH_SESSION_CREATED",
            f"Session {new_session.id} créée"
        )
        return new_session
    
    def get_next_question(self, session: AuthSession) -> Tuple[int, str]:
        """
        Retourne la prochaine question à poser
        Returns: (question_number, question_text)
        """
        next_q = session.current_question + 1
        
        questions = {
            1: "Pour confirmer votre identité, veuillez fournir votre identifiant interne.",
            2: "Quelle est votre localité enregistrée ?",
            3: "Quel est le numéro de votre référent ?"
        }
        
        return (next_q, questions.get(next_q, ""))
    
    def process_answer(self, session: AuthSession, answer: str) -> Dict:
        """
        Traite la réponse d'une question d'authentification
        Returns: dict avec status, message, next_question
        """
        person = crud.get_person_by_phone(self.db, session.phone_number)
        if not person:
            return {
                "status": "error",
                "message": "Personne introuvable",
                "authenticated": False
            }
        
        # Question en attente de réponse (1 à 3)
        current_q = session.current_question if session.current_question > 0 else 1
        
        # Sauvegarder la réponse
        crud.save_session_answer(self.db, session.id, current_q, answer)
        
        # Réactualiser la session depuis la BD (important!)
        session = crud.get_active_session(self.db, session.phone_number)
        
        # Vérifier la réponse
        is_correct = self._verify_answer(person, current_q, answer)
        
        if not is_correct:
            # Incrémenter les tentatives
            crud.update_session_state(
                self.db, 
                session.id, 
                SessionState.AUTHENTICATING,
                increment_attempts=True
            )
            
            # Vérifier si le max de tentatives est atteint
            if session.attempts + 1 >= settings.max_auth_attempts:
                crud.update_session_state(self.db, session.id, SessionState.REJECTED)
                crud.create_audit_log(
                    self.db,
                    session.phone_number,
                    "AUTH_FAILED",
                    "Nombre maximum de tentatives atteint",
                    success=False
                )
                return {
                    "status": "rejected",
                    "message": "Authentification échouée. Nombre maximum de tentatives atteint.",
                    "authenticated": False
                }
            
            return {
                "status": "retry",
                "message": "Réponse incorrecte. Veuillez réessayer.",
                "authenticated": False,
                "attempts_left": settings.max_auth_attempts - (session.attempts + 1),
                "question_number": current_q
            }
        
        # Si on a répondu aux 3 questions correctement
        if current_q >= 3:
            # Vérifier si toutes les réponses sont correctes
            if self._verify_all_answers(person, session):
                # Authentification réussie
                crud.update_session_state(self.db, session.id, SessionState.AUTHENTICATED)
                crud.mark_person_verified(self.db, session.phone_number)
                crud.create_audit_log(
                    self.db,
                    session.phone_number,
                    "AUTH_SUCCESS",
                    "Authentification réussie"
                )
                return {
                    "status": "authenticated",
                    "message": "Authentification réussie ! Vous pouvez maintenant utiliser le service.",
                    "authenticated": True
                }
            else:
                # Au moins une réponse est incorrecte
                crud.update_session_state(
                    self.db, 
                    session.id, 
                    SessionState.REJECTED,
                    increment_attempts=True
                )
                crud.create_audit_log(
                    self.db,
                    session.phone_number,
                    "AUTH_FAILED",
                    "Réponses incorrectes",
                    success=False
                )
                return {
                    "status": "rejected",
                    "message": "Authentification échouée. Les informations fournies sont incorrectes.",
                    "authenticated": False
                }
        
        # Passer à la question suivante uniquement après une réponse correcte
        next_q_num = current_q + 1
        crud.update_current_question(self.db, session.id, next_q_num)

        questions = {
            1: "Pour confirmer votre identité, veuillez fournir votre identifiant interne.",
            2: "Quelle est votre localité enregistrée ?",
            3: "Quel est le numéro de votre référent ?"
        }
        next_q_text = questions.get(next_q_num, "")

        return {
            "status": "next_question",
            "message": next_q_text,
            "authenticated": False,
            "question_number": next_q_num
        }
    
    def _verify_answer(self, person: Person, question_number: int, answer: str) -> bool:
        """Vérifie si une réponse est correcte"""
        answer = answer.strip().lower()
        
        if question_number == 1:
            # Vérifier l'identifiant interne
            return answer == person.identifiant_interne.strip().lower()
        
        elif question_number == 2:
            # Vérifier la localité
            return answer == person.localite.strip().lower()
        
        elif question_number == 3:
            # Vérifier le numéro référent
            return answer == person.numero_referent.strip().lower()
        
        return False
    
    def _verify_all_answers(self, person: Person, session: AuthSession) -> bool:
        """Vérifie que toutes les réponses sont correctes"""
        q1_ok = self._verify_answer(person, 1, session.question_1_answer or "")
        q2_ok = self._verify_answer(person, 2, session.question_2_answer or "")
        q3_ok = self._verify_answer(person, 3, session.question_3_answer or "")
        
        return q1_ok and q2_ok and q3_ok
