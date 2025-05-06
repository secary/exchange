from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Float, PrimaryKeyConstraint

Base = declarative_base()

class Prediction(Base):
    __tablename__ = 'predictions'

    Date = Column(DateTime, primary_key=True)
    Currency = Column(String(20), primary_key=True)
    现汇卖出 = Column(Float)
    Locals = Column(DateTime)
