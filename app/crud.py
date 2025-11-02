from sqlalchemy.orm import Session
from . import models, schemas

def get_all(db: Session):
    return db.query(models.BloodPressure).order_by(models.BloodPressure.date.desc()).all()

def create(db: Session, bp: schemas.BPCreate):
    db_bp = models.BloodPressure(**bp.dict())
    db.add(db_bp)
    db.commit()
    db.refresh(db_bp)
    return db_bp
