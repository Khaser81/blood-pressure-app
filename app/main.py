from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models, schemas, crud, database

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI(title="Blood Pressure Tracker")

# DBセッション依存
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/bp", response_model=list[schemas.BP])
def read_bps(db: Session = Depends(get_db)):
    return crud.get_all(db)

@app.post("/bp", response_model=schemas.BP)
def create_bp(bp: schemas.BPCreate, db: Session = Depends(get_db)):
    return crud.create(db, bp)
