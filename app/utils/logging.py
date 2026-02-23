"""
Utilitaires pour le logging structuré
"""
from loguru import logger
from functools import wraps
from time import time


def log_execution_time(func):
    """Décorateur pour logger le temps d'exécution d'une fonction"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        end = time()
        logger.debug(f"{func.__name__} executed in {end - start:.4f}s")
        return result
    return wrapper


def log_api_call(endpoint: str, phone_number: str = None, extra: dict = None):
    """
    Log un appel API
    
    Args:
        endpoint: Nom de l'endpoint appelé
        phone_number: Numéro de téléphone concerné
        extra: Données supplémentaires
    """
    log_data = {
        "endpoint": endpoint,
        "phone_number": phone_number,
    }
    
    if extra:
        log_data.update(extra)
    
    logger.info(f"API Call: {endpoint}", **log_data)
