"""
Routes pour la gestion des personnes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import crud
from app.schemas import PersonResponse, PersonCreate, PersonUpdate

router = APIRouter(prefix="/persons", tags=["persons"])


@router.get("/", response_model=List[PersonResponse])
def get_all_persons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Récupère toutes les personnes"""
    persons = crud.get_all_persons(db, skip=skip, limit=limit)
    return persons


@router.get("/{person_id}", response_model=PersonResponse)
def get_person(person_id: int, db: Session = Depends(get_db)):
    """Récupère une personne par son ID"""
    person = crud.get_person_by_id(db, person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personne non trouvée"
        )
    return person


@router.get("/phone/{phone_number}", response_model=PersonResponse)
def get_person_by_phone(phone_number: str, db: Session = Depends(get_db)):
    """Récupère une personne par son numéro de téléphone"""
    person = crud.get_person_by_phone(db, phone_number)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personne non trouvée"
        )
    return person


@router.post("/", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
def create_person(person: PersonCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle personne"""
    # Vérifier si le numéro existe déjà
    existing = crud.get_person_by_phone(db, person.phone_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce numéro de téléphone existe déjà"
        )
    
    # Vérifier si l'identifiant existe déjà
    existing = crud.get_person_by_identifiant(db, person.identifiant_interne)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet identifiant interne existe déjà"
        )
    
    return crud.create_person(db, person)


@router.put("/{person_id}", response_model=PersonResponse)
def update_person(
    person_id: int,
    person_update: PersonUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour une personne"""
    person = crud.update_person(db, person_id, person_update)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personne non trouvée"
        )
    return person
