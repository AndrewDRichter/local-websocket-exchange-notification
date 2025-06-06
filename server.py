from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


app = FastAPI()
clientes = []
cambio_atual = 0.0

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
    await notificar_clientes(valor)
    return {"mensagem": f"Câmbio atualizado para {valor}"}

async def notificar_clientes(valor):
    for cliente in clientes:
        await cliente.send_text(f"{valor}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)
