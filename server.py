from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


app = FastAPI()
clientes = []
cambio_atual = 0.0
combustivel_atual = 0.0

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clientes.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clientes.remove(websocket)

@app.post("/atualizar-cambio/{valor}")
async def atualizar_cambio(valor: float):
    global cambio_atual
    cambio_atual = valor
    mensagem = "Câmbio"
    await notificar_clientes(valor, mensagem)
    return {"mensagem": f"Câmbio atualizado para {valor}"}

@app.post("/atualizar-combustivel/{valor}")
async def atualizar_combustivel(valor: float):
    global combustivel_atual
    combustivel_atual = valor
    mensagem = "Combustível"
    await notificar_clientes(valor, mensagem)
    return {"mensagem": f"Combustível atualizado para {valor}"}

@app.get("/get-cambio/")
async def get_cambio():
    global cambio_atual
    return {"mensagem": f"Câmbio: {cambio_atual}"}

@app.get("/get-combustivel/")
async def get_combustivel():
    global combustivel_atual
    return {"mensagem": f"Combustível: {combustivel_atual}"}

async def notificar_clientes(valor, mensagem: str):
    for cliente in clientes:
        await cliente.send_text(f"{mensagem}: {valor}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)
