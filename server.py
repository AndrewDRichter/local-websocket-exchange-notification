from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Request, Header, WebSocketException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import create_gas_price, get_last_gas_price, get_last_exchange_value, create_exchange_values, get_last_soybean_cost, create_soybean_cost, get_auth_user, create_auth_user
from models import get_db
from datetime import datetime, timezone, timedelta
import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError
from passlib.context import CryptContext
from decouple import config
import models
from typing import List

SECRET_KEY = config('API_SECRET_KEY', cast=str)
ALGORITHM = config('JWT_ALGORITHM', cast=str)
ACCESS_TOKEN_EXPIRE_MINUTES = config('ACCESS_TOKEN_EXPIRE_MINUTES', cast=int)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_jwt_token(user: models.AuthUser, exp: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    payload = {
        'user_id': user.id,
        'username': user.username,
        'read_only': user.read_only,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=exp)
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    user = get_auth_user(db=db, username=username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


app = FastAPI()
clientes: List[WebSocket] = []
# cambio_atual = 0.0
# combustivel_atual = 0.0
# custo_atual = 0.0
# chat_messages = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_token(req: Request):
    token = req.headers.get('Authorization', None)
    if token is None:
        raise HTTPException(
            status_code=401,
            detail='Unauthorized'
        )
    try:
        token = token.split()[1]
        decode_token = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)
        return decode_token
    except HTTPException:
        print(f'Error: {HTTPException}')
        return False
    except ExpiredSignatureError as e:
        raise HTTPException(
                status_code=401,
                detail='Unauthorized'
            )


class CreateGasPrice(BaseModel):
    price: int


class GasPrice(BaseModel):
    id: int | None
    price: int
    date_created: None | datetime = datetime.now()
    active: None | bool = True


class CreateExchangeValues(BaseModel):
    buy: int
    sell: int


class ExchangeValues(BaseModel):
    id: int | None
    buy: int
    sell: int
    date_created: None | datetime = datetime.now()
    active: None | bool = True


class CreateSoybeanCost(BaseModel):
    cost: int
    ref_month: int


class SoybeanCost(BaseModel):
    id: int | None
    cost: int
    ref_month: int
    date_created: None | datetime = datetime.now()
    active: None | bool = True


class CreateAuthUser(BaseModel):
    username: str
    password: str
    readonly: bool = True


class AuthUser(BaseModel):
    username: str
    password: str


# GAS PRICE CRUD
@app.post("/gas-price")
async def new_gas_price(gas_price: CreateGasPrice, db: Session = Depends(get_db), authorized: object = Depends(verify_token)):
    if authorized['read_only']:
        raise HTTPException(
            status_code=401,
            detail='Unauthorized'
        )
    data: GasPrice = create_gas_price(db, gas_price.price)
    value = f'{data.price}'
    await notificar_clientes(value=value, message='Combustible')
    return {
        'id': data.id,
        'price': data.price,
        'date': data.date_created.isoformat(),
        'active': data.active
    }

@app.get("/gas-price/")
async def get_gas_price(db: Session = Depends(get_db), authorized: object = Depends(verify_token)):
    gas_price: GasPrice = get_last_gas_price(db)
    if not gas_price:
        return {
            'error': 'Error retrieving data',
        }
    value = f'{gas_price.price}'
    return {
        'price': gas_price.price,
        'date': gas_price.date_created.isoformat(),
    }


# EXCHANGE VALUES CRUD
@app.post("/exchange-values")
async def new_exchange_values(exchange_value: CreateExchangeValues, db: Session = Depends(get_db), authorized: object = Depends(verify_token)):
    if authorized['read_only']:
        raise HTTPException(
            status_code=401,
            detail='Unauthorized'
        )
    data: ExchangeValues = create_exchange_values(db, exchange_value.buy, exchange_value.sell)
    value = f'{data.buy}/{data.sell}'
    await notificar_clientes(value=value, message='Cambio')
    return {
        'id': data.id,
        'buy': data.buy,
        'sell': data.sell,
        'date': data.date_created.isoformat(),
        'active': data.active
    }

@app.get("/exchange-values/")
async def get_exchange_values(db: Session = Depends(get_db), authorized: object = Depends(verify_token)):
    exchange: ExchangeValues = get_last_exchange_value(db)
    if not exchange:
        return {
            'error': 'Error retrieving data',
        }
    value = f'{exchange.buy}/{exchange.sell}'
    return {
        'buy': exchange.buy,
        'sell': exchange.sell,
        'date': exchange.date_created.isoformat()
    }


# SOYBEAN COST CRUD
@app.post("/soybean-cost")
async def new_soybean_cost(soybean_cost: CreateSoybeanCost, db: Session = Depends(get_db), authorized: object = Depends(verify_token)):
    if authorized['read_only']:
        raise HTTPException(
            status_code=401,
            detail='Unauthorized'
        )
    data: SoybeanCost = create_soybean_cost(db, soybean_cost.cost, soybean_cost.ref_month)
    value = f'{data.cost}/{data.ref_month}'
    await notificar_clientes(value=value, message='Costo')
    return {
        'id': data.id,
        'cost': data.cost,
        'ref_month': data.ref_month,
        'date': data.date_created.isoformat(),
        'active': data.active
    }

@app.get("/soybean-cost/")
async def get_soybean_cost(db: Session = Depends(get_db), authorized: object = Depends(verify_token)):
    soybean_cost: SoybeanCost = get_last_soybean_cost(db)
    if not soybean_cost:
        return {
            'error': 'Error retrieving data',
        }
    value = f'{soybean_cost.cost}/{soybean_cost.ref_month}'
    return {
        'cost': soybean_cost.cost,
        'ref_month': soybean_cost.ref_month,
        'date':  soybean_cost.date_created.isoformat()
    }


# USER ROUTES
@app.post("/signin")
async def sign_user_in(user: AuthUser, db:Session = Depends(get_db)):
    user = authenticate_user(db, username=user.username, password=user.password)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid login')
    token = create_jwt_token(user=user)
    return {
        'token': token,
    }

@app.post("/create-auth-user")
async def new_auth_user(user: CreateAuthUser, db: Session = Depends(get_db), authorized: object = Depends(verify_token)):
    if authorized['read_only']:
        raise HTTPException(
            status_code=401,
            detail='Unauthorized'
        )
    hashed_password = get_password_hash(user.password)
    user = create_auth_user(db, user.username, hashed_password, True)
    return {
        "user": user
    }


def is_authorized_ws(bearer: str):
    token = bearer.split()[1]
    if not token:
        return False
    decode_token = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)
    print(decode_token)


# WEBSOCKET CONFIG
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    bearer = websocket.headers.get('authorization', None)
    if not bearer:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    user_data = is_authorized_ws(bearer)
    await websocket.accept()
    clientes.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clientes.remove(websocket)


async def notificar_clientes(value, message: str):
    for cliente in clientes:
        await cliente.send_text(f"{message}: {value}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)
