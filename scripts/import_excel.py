"""
Script d'import de données depuis Excel
"""
import sys
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from pathlib import Path

# Ajouter le répertoire parent au path pour importer app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import Person
from app.config import get_settings
from loguru import logger

settings = get_settings()


def clean_phone_number(phone: str) -> str:
    """Nettoie et formate un numéro de téléphone"""
    if pd.isna(phone):
        return ""
    
    phone = str(phone).strip()
    # Retirer les espaces, tirets, parenthèses
    phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # S'assurer que le numéro commence par +
    if not phone.startswith("+"):
        # Si c'est un numéro français qui commence par 0, le convertir
        if phone.startswith("0"):
            phone = "+33" + phone[1:]
        else:
            phone = "+" + phone
    
    return phone


def parse_date(date_str) -> datetime:
    """Parse une date depuis Excel"""
    if pd.isna(date_str):
        return None
    
    if isinstance(date_str, datetime):
        return date_str
    
    # Essayer différents formats
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"]
    
    for fmt in formats:
        try:
            return datetime.strptime(str(date_str), fmt)
        except ValueError:
            continue
    
    logger.warning(f"Impossible de parser la date: {date_str}")
    return None


def import_from_excel(file_path: str, db: Session):
    """
    Importe les données depuis un fichier Excel
    
    Le fichier doit contenir les colonnes:
    - phone_number
    - identifiant_interne
    - date_cle
    - localite
    - numero_referent
    - nom (optionnel)
    - prenom (optionnel)
    - email (optionnel)
    """
    logger.info(f"Lecture du fichier: {file_path}")
    
    try:
        # Lire le fichier Excel
        df = pd.read_excel(file_path)
        
        logger.info(f"Fichier chargé: {len(df)} lignes trouvées")
        logger.info(f"Colonnes: {', '.join(df.columns)}")
        
        # Vérifier les colonnes obligatoires
        required_columns = [
            "phone_number", "identifiant_interne", "date_cle", 
            "localite", "numero_referent"
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Colonnes manquantes: {', '.join(missing_columns)}")
            return
        
        # Importer les données
        imported = 0
        errors = 0
        
        for index, row in df.iterrows():
            try:
                # Nettoyer et valider les données
                phone = clean_phone_number(row["phone_number"])
                if not phone:
                    logger.warning(f"Ligne {index + 2}: Numéro de téléphone vide, ignorée")
                    errors += 1
                    continue
                
                date_cle = parse_date(row["date_cle"])
                if not date_cle:
                    logger.warning(f"Ligne {index + 2}: Date invalide, ignorée")
                    errors += 1
                    continue
                
                # Vérifier si la personne existe déjà
                existing = db.query(Person).filter(
                    Person.phone_number == phone
                ).first()
                
                if existing:
                    logger.info(f"Ligne {index + 2}: Numéro {phone} déjà existant, ignoré")
                    continue
                
                # Créer la personne
                person = Person(
                    phone_number=phone,
                    identifiant_interne=str(row["identifiant_interne"]).strip(),
                    date_cle=date_cle,
                    localite=str(row["localite"]).strip(),
                    numero_referent=str(row["numero_referent"]).strip(),
                    nom=str(row.get("nom", "")).strip() if pd.notna(row.get("nom")) else None,
                    prenom=str(row.get("prenom", "")).strip() if pd.notna(row.get("prenom")) else None,
                    email=str(row.get("email", "")).strip() if pd.notna(row.get("email")) else None,
                    verified=False
                )
                
                db.add(person)
                imported += 1
                
                # Commit tous les 100 enregistrements
                if imported % 100 == 0:
                    db.commit()
                    logger.info(f"✅ {imported} personnes importées...")
                
            except Exception as e:
                logger.error(f"Erreur ligne {index + 2}: {e}")
                errors += 1
                continue
        
        # Commit final
        db.commit()
        
        logger.info(f"\n{'='*50}")
        logger.info(f"✅ Import terminé:")
        logger.info(f"   - {imported} personnes importées")
        logger.info(f"   - {errors} erreurs")
        logger.info(f"{'='*50}")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'import: {e}")
        db.rollback()


def main():
    """Point d'entrée du script"""
    if len(sys.argv) < 2:
        logger.error("Usage: python import_excel.py <fichier.xlsx>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not Path(file_path).exists():
        logger.error(f"Fichier introuvable: {file_path}")
        sys.exit(1)
    
    # Créer une session de base de données
    db = SessionLocal()
    
    try:
        import_from_excel(file_path, db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
