# WhatsApp Tracking Backend

Système de suivi et d'identification des personnes via WhatsApp.

## Installation

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
.\venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

## Configuration

1. Copier `.env.example` vers `.env`
2. Remplir les variables d'environnement

## Base de données

```bash
# Initialiser Alembic
alembic init alembic

# Créer une migration
alembic revision --autogenerate -m "Initial migration"

# Appliquer les migrations
alembic upgrade head
```

## Import des données

```bash
python scripts/import_excel.py votre_fichier.xlsx
```

## Lancement

```bash
# Développement
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Structure du projet

```
app/
├── main.py              # Point d'entrée FastAPI
├── config.py            # Configuration
├── database.py          # Connexion DB
├── models/              # Modèles SQLAlchemy
├── schemas/             # Schémas Pydantic
├── services/            # Logique métier
├── routes/              # Endpoints API
└── utils/               # Utilitaires
```

## API Documentation

Une fois lancé, accéder à :
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
