from sqlalchemy import Column, Integer, Float, String, Date
from .database import Base

class BloodPressure(Base):
    __tablename__ = "blood_pressure"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    systolic = Column(Integer)     # 収縮期（上）
    diastolic = Column(Integer)    # 拡張期（下）
    pulse = Column(Integer, nullable=True)
    note = Column(String, nullable=True)
