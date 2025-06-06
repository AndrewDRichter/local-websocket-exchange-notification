import subprocess
import psutil
import os
import sys
import time

NOME_CLIENTE = "client.exe"  # Nome do seu cliente compilado
CAMINHO_CLIENTE = os.path.join(os.path.dirname(__file__), NOME_CLIENTE)

def encerrar_clientes():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == NOME_CLIENTE and proc.pid != os.getpid():
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def iniciar_cliente():
    subprocess.Popen(CAMINHO_CLIENTE, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    encerrar_clientes()
    time.sleep(0.5)  # pequeno delay para garantir encerramento
    iniciar_cliente()
    sys.exit()
