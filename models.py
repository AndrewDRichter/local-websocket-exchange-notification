from uuid import uuid4
from sqlalchemy import Column, Integer, String, Boolean, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


engine = create_engine('sqlite:///database.db', echo=True)
Base = declarative_base()


class AuthUser(Base):
    __tablename__ = 'auth_user'

    id = Column(String, primary_key=True)
    username = Column(String, nullable=False)
    password = Column(String)
    date_created = Column(DateTime, default=datetime.now)
    active = Column(Boolean, default=True)


class GasPrice(Base):
    __tablename__ = 'gas_price'

    id = Column(Integer, primary_key=True)
    price = Column(Integer, nullable=False)
    date_created = Column(DateTime, default=datetime.now)
    # created_by = Column(String, nullable=False)
    active = Column(Boolean, default=True)


class ExchangeValue(Base):
    __tablename__ = 'exchange_value'

    id = Column(Integer, primary_key=True)
    buy = Column(Integer, nullable=False)
    sell = Column(Integer, nullable=False)
    date_created = Column(DateTime, default=datetime.now)
    # created_by = Column(String, nullable=False)
    active = Column(Boolean, default=True)


class SoybeanCost(Base):
    __tablename__ = 'soybean_cost'

    id = Column(Integer, primary_key=True)
    cost = Column(Integer, nullable=False)
    ref_month = Column(Integer, nullable=False)
    date_created = Column(DateTime, default=datetime.now)
    # created_by = Column(String, nullable=False)
    active = Column(Boolean, default=True)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
