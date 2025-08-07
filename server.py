from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import get_gas_prices, create_gas_price, get_last_gas_price, get_last_exchange_value, create_exchange_values, get_last_soybean_cost, create_auth_user, get_auth_user
from models import get_db, get_hashed_password, verify_password
from datetime import datetime

app = FastAPI()
clientes = []
cambio_atual = 0.0
combustivel_atual = 0.0
custo_atual = 0.0
chat_messages = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class GasPrice(BaseModel):
    id: int | None
    price: int
    date_created: None | datetime = datetime.now()
    active: None | bool = True

    # class Config:
    #     json_schema_extra = {'example': {'price': 7100}}

class ExchangeValues(BaseModel):
    id: int | None
    buy: int
    sell: int
    date_created: None | datetime = datetime.now()
    active: None | bool = True


class AuthUser(BaseModel):
    id: int | None
    username: str
    password: str
    date_created: None | datetime = datetime.now()
    active: None | bool = True


@app.post("/new-gas-price")
async def new_gas_price(gas_price: GasPrice, db: Session = Depends(get_db)):
    # if gas_price:
    data = create_gas_price(db, gas_price.price)
    db.commit()
    print(data)
    return {
        'id': data.id,
        'price': data.price,
        'date': data.date_created,
        'active': data.active
    }

@app.post("/new-exchange-values")
async def new_exchange_values(exchange_value: ExchangeValues, db: Session = Depends(get_db)):
    # if gas_price:
    data = create_exchange_values(db, exchange_value.buy, exchange_value.sell)
    db.commit()
    print(data)
    return {
        'id': data.id,
        'buy': data.buy,
        'sell': data.sell,
        'date': data.date_created,
        'active': data.active
    }

@app.post("/new-auth-user")
async def new_auth_user(auth_user: AuthUser, db: Session = Depends(get_db)):
    user = get_auth_user(db, auth_user.username)
    if user:
        return {
            'error': 'User with this username already exists!',
        }
    hashed_password = get_hashed_password(auth_user.password)
    data = create_auth_user(db, auth_user.username, hashed_password)
    db.commit()
    print(data)
    return {
        'id': data.id,
        'username': data.username,
        'date': data.date_created,
        'active': data.active
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clientes.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clientes.remove(websocket)

@app.get("/signin/")
async def sign_user_in(username: str, password: str, db:Session = Depends(get_db)):
    user = get_auth_user(db, username)
    if not user:
        return{
            'error': 'Wrong username',
        }
    correct_pass = verify_password(password, user.password)
    if not correct_pass:
        return{
            'error': 'Wrong password'
        }
    print('User in!')
    return {
        'token': 'sometoken123',
    }

@app.get("/get-cambio/")
async def get_cambio(db: Session = Depends(get_db)):
    exchange = get_last_exchange_value(db)
    if not exchange:
        return {
            'error': 'Error retrieving data',
        }
    value = f'{exchange.buy}/{exchange.sell}'
    notificar_clientes(valor=value, mensagem='Câmbio alterado para')
    return {
        'buy': exchange.buy,
        'sell': exchange.sell,
        'date': exchange.date_created.isoformat()
    }

@app.get("/get-combustivel/")
async def get_combustivel(db: Session = Depends(get_db)):
    combustible = get_last_gas_price(db)
    if not combustible:
        return {
            'error': 'Error retrieving data',
        }
    value = f'{combustible.price}'
    notificar_clientes(valor=value, mensagem='Combustível alterado para')
    return {
        'price': combustible.price,
        'date': combustible.date_created.isoformat()
    }

@app.get("/get-custo/")
async def get_custo(db: Session = Depends(get_db)):
    custo = get_last_soybean_cost(db)
    if not custo:
        return {
            'error': 'Error retrieving data',
        }
    return {"mensagem": f"Custo: {custo_atual}"}

async def notificar_clientes(valor, mensagem: str):
    for cliente in clientes:
        await cliente.send_text(f"{mensagem}: {valor}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)
