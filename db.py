from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import models

def get_last_gas_price(db: Session):
    return (db.query(models.GasPrice).order_by(models.GasPrice.date_created.desc()).first())

def get_last_exchange_value(db: Session):
    return (db.query(models.ExchangeValue).order_by(models.ExchangeValue.date_created.desc()).first())

def get_last_soybean_cost(db: Session):
    return (db.query(models.SoybeanCost).order_by(models.SoybeanCost.date_created.desc()).first())

def get_gas_prices(db: Session):
    return db.query(models.GasPrice).filter(models.GasPrice.active == True).all()

def get_exchange_values(db: Session):
    return db.query(models.ExchangeValue).filter(models.ExchangeValue.active == True).order_by(models.ExchangeValue.date_created).all()

def get_auth_user(db: Session, username: str):
    return db.query(models.AuthUser).filter(models.AuthUser.username==username).first()

def create_gas_price(db:Session, price: int):
    db_gas_price = models.GasPrice(price=price)
    db.add(db_gas_price)
    db.commit()
    db.refresh(db_gas_price)
    return db_gas_price

def create_exchange_values(db: Session, buy: int, sell: int):
    db_exchange_values = models.ExchangeValue(buy=buy, sell=sell)
    db.add(db_exchange_values)
    db.commit()
    db.refresh(db_exchange_values)
    return db_exchange_values

def create_auth_user(db: Session, username: str, password: str):
    db_auth_user = models.AuthUser(username=username, password=password)
    db.add(db_auth_user)
    db.commit()
    db.refresh(db_auth_user)
    return db_auth_user
