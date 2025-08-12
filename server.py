from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import create_gas_price, get_last_gas_price, get_last_exchange_value, create_exchange_values, get_last_soybean_cost, create_soybean_cost, get_auth_user
from models import get_db
from datetime import datetime, timezone, timedelta
import jwt
from passlib.context import CryptContext
from decouple import config
import models

SECRET_KEY = config('API_SECRET_KEY', cast=str)
ALGORITHM = config('JWT_ALGORITHM', cast=str)
ACCESS_TOKEN_EXPIRE_MINUTES = config('ACCESS_TOKEN_EXPIRE_MINUTES', cast=int)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_jwt_token(user: models.AuthUser, exp: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    payload = {
        'user_id': user.id,
        'username': user.username,
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
clientes = []
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
    token = token.split()[1]
    decode_token = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)
    exp = decode_token.get('exp', 0)
    now = datetime.now(timezone.utc).timestamp()
    if now > exp:
        raise HTTPException(
            status_code=401,
            detail='Unauthorized'
        )
    return True


class GasPrice(BaseModel):
    id: int | None
    price: int
    date_created: None | datetime = datetime.now()
    active: None | bool = True


class ExchangeValues(BaseModel):
    id: int | None
    buy: int
    sell: int
    date_created: None | datetime = datetime.now()
    active: None | bool = True


class SoybeanCost(BaseModel):
    id: int | None
    cost: int
    ref_month: int
    date_created: None | datetime = datetime.now()
    active: None | bool = True


class AuthUser(BaseModel):
    username: str
    password: str


@app.post("/new-gas-price")
async def new_gas_price(gas_price: GasPrice, db: Session = Depends(get_db), authorized: bool = Depends(verify_token)):
    data = create_gas_price(db, gas_price.price)
    # db.commit()
    print(data)
    value = f'{data.price}'
    notificar_clientes(value=value, message='Combustible')
    return {
        'id': data.id,
        'price': data.price,
        'date': data.date_created,
        'active': data.active
    }

@app.post("/new-exchange-values")
async def new_exchange_values(exchange_value: ExchangeValues, db: Session = Depends(get_db), authorized: bool = Depends(verify_token)):
    data = create_exchange_values(db, exchange_value.buy, exchange_value.sell)
    # db.commit()
    print(data)
    value = f'{data.buy}/{data.sell}'
    notificar_clientes(value=value, message='Cambio')
    return {
        'id': data.id,
        'buy': data.buy,
        'sell': data.sell,
        'date': data.date_created,
        'active': data.active
    }

@app.post("/new-soybean-cost")
async def new_soybean_cost(soybean_cost: SoybeanCost, db: Session = Depends(get_db), authorized: bool = Depends(verify_token)):
    data = create_soybean_cost(db, soybean_cost.cost, soybean_cost.ref_month)
    # db.commit()
    print(data)
    value = f'{data.cost}/{data.ref_month}'
    notificar_clientes(value=value, message='Costo')
    return {
        'id': data.id,
        'cost': data.cost,
        'ref_month': data.ref_month,
        'date': data.date_created,
        'active': data.active
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, authorized: bool = Depends(verify_token)):
    await websocket.accept()
    clientes.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clientes.remove(websocket)

@app.post("/signin/")
async def sign_user_in(user: AuthUser, db:Session = Depends(get_db)):
    user = authenticate_user(db, username=user.username, password=user.password)
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized')
    token = create_jwt_token(user=user)
    return {
        'token': token,
    }

@app.get("/get-exchange-values/")
async def get_exchange_values(db: Session = Depends(get_db), authorized: bool = Depends(verify_token)):
    exchange = get_last_exchange_value(db)
    if not exchange:
        return {
            'error': 'Error retrieving data',
        }
    value = f'{exchange.buy}/{exchange.sell}'
    notificar_clientes(value=value, message='Cambio')
    return {
        'buy': exchange.buy,
        'sell': exchange.sell,
        'date': exchange.date_created.isoformat()
    }

@app.get("/get-gas-price/")
async def get_gas_price(db: Session = Depends(get_db), authorized: bool = Depends(verify_token)):
    gas_price = get_last_gas_price(db)
    if not gas_price:
        return {
            'error': 'Error retrieving data',
        }
    value = f'{gas_price.price}'
    notificar_clientes(value=value, message='Combustible')
    return {
        'price': gas_price.price,
        'date': gas_price.date_created.isoformat(),
    }

@app.get("/get-soybean-cost/")
async def get_soybean_cost(db: Session = Depends(get_db), authorized: bool = Depends(verify_token)):
    soybean_cost = get_last_soybean_cost(db)
    if not soybean_cost:
        return {
            'error': 'Error retrieving data',
        }
    value = f'{soybean_cost.cost}/{soybean_cost.ref_month}'
    notificar_clientes(value=value, message='Costo')
    return {
        'cost': soybean_cost.cost,
        'ref_month': soybean_cost.ref_month,
    }

async def notificar_clientes(value, message: str):
    for cliente in clientes:
        await cliente.send_text(f"{message}: {value}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)
