import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import Person, AuthSession, SessionState

PHONE = "+237659119612"
IDENTIFIANT = "REAL_USER_001"
LOCALITE = "Cameroon"
REFERENT = "REF_CM_001"


def main():
    db = SessionLocal()
    try:
        person = db.query(Person).filter(Person.phone_number == PHONE).first()
        if person is None:
            person = Person(
                phone_number=PHONE,
                identifiant_interne=IDENTIFIANT,
                date_cle=datetime(2024, 2, 19),
                localite=LOCALITE,
                numero_referent=REFERENT,
                nom="Real",
                prenom="User",
                email="real.user@example.com",
                verified=False,
            )
            db.add(person)
            db.commit()
            db.refresh(person)
            print(f"CREATED person id={person.id}")
        else:
            person.identifiant_interne = IDENTIFIANT
            person.localite = LOCALITE
            person.numero_referent = REFERENT
            person.verified = False
            db.commit()
            print(f"UPDATED person id={person.id}")

        sessions = db.query(AuthSession).filter(AuthSession.phone_number == PHONE).all()
        for session in sessions:
            if session.state in [SessionState.PENDING, SessionState.AUTHENTICATING]:
                session.state = SessionState.REJECTED
        db.commit()
        print(f"RESET {len(sessions)} sessions")

        print(f"PHONE={PHONE}")
        print(f"Q1={IDENTIFIANT}")
        print(f"Q2={LOCALITE}")
        print(f"Q3={REFERENT}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
