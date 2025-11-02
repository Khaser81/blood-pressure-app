from datetime import date
from pydantic import BaseModel

class BPBase(BaseModel):
    date: date
    systolic: int
    diastolic: int
    pulse: int | None = None
    note: str | None = None

class BPCreate(BPBase):
    pass

class BP(BPBase):
    id: int
    class Config:
        orm_mode = True
