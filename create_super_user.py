from sqlalchemy import Column, Integer, String, Boolean, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from getpass import getpass
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

engine = create_engine('sqlite:///database.db', echo=True)
Base = declarative_base()


class AuthUser(Base):
    __tablename__ = 'auth_user'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    read_only = Column(Boolean, nullable=False)
    date_created = Column(DateTime, default=datetime.now)
    active = Column(Boolean, default=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_auth_user(session, username: str, password: str, read_only: bool):
    db_auth_user = AuthUser(username=username, password=password, read_only=read_only)
    session.add(db_auth_user)
    session.commit()
    session.refresh(db_auth_user)
    return db_auth_user


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def get_password_hash(password):
    return pwd_context.hash(password)

def create_super_user(username: str, password: str):
    try:
        if username == '' or not username:
            raise Exception('Error: username was not provided')
        if password == '' or not password:
            raise Exception('Error: password was not provided')
        session = get_db()
        password = get_password_hash(password)
        user = create_auth_user(session, username, password, read_only=False)
        return user
    except Exception as e:
        print(f'Error: {e}')
        return False


if __name__ == '__main__':
    username = str(input('Username: '))
    password = getpass()
    print(create_super_user(username=username, password=password))