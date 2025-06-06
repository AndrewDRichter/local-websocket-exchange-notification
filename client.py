import asyncio
import threading
import websockets
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
import sys

cambio_atual = "Aguardando..."  # Valor inicial do câmbio
icone_global = None  # Referência ao ícone da bandeja

def criar_icone():
    imagem = Image.new('RGB', (64, 64), color='green')
    draw = ImageDraw.Draw(imagem)
    draw.rectangle((16, 16, 48, 48), fill='white')
    return imagem

async def receber_cambio():
    global cambio_atual
    uri = "ws://192.168.1.140:8000/ws"  # Troque pelo IP real
    async with websockets.connect(uri) as websocket:
        while True:
            mensagem = await websocket.recv()
            cambio_atual = mensagem
            atualizar_menu()

def iniciar_websocket():
    asyncio.run(receber_cambio())

def atualizar_menu():
    if icone_global:
        icone_global.menu = Menu(
            MenuItem(f"💱 Câmbio atual: {cambio_atual}", None, enabled=False),
            MenuItem("Sair", lambda icon, item: sair(icon))
        )
        icone_global.update_menu()

def iniciar_bandeja():
    global icone_global
    icone = Icon("Cambio Monitor")
    icone.icon = criar_icone()
    icone.title = "Monitor de Câmbio"

    icone.menu = Menu(
        MenuItem(f"💱 Câmbio atual: {cambio_atual}", None, enabled=False),
        MenuItem("Sair", lambda icon, item: sair(icon))
    )

    icone_global = icone

    threading.Thread(target=iniciar_websocket, daemon=True).start()
    icone.run()

def sair(icon):
    icon.stop()
    sys.exit()

if __name__ == "__main__":
    iniciar_bandeja()
