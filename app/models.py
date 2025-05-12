from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Float, PrimaryKeyConstraint

Base = declarative_base()

class History(Base):
    __tablename__ = 'history'

    Date = Column(DateTime, primary_key=True)
    Currency = Column(String(20), primary_key=True)
    Rate = Column(Float)
    Locals = Column(DateTime)

class Threshold(Base):
    __tablename__ = 'thresholds'

    Currency = Column(String(20), primary_key=True)
    Upper = Column(Float)
    Lower = Column(Float)
