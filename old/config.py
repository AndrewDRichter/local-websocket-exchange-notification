import os
import sys
from decouple import Config, RepositoryEnv, UndefinedValueError

def carregar_config():
    # Detecta se o app está rodando como .exe (empacotado pelo PyInstaller)
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)  # caminho real do .exe
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))

    # Caminho para o .env
    env_path = os.path.join(exe_dir, ".env")

    if os.path.exists(env_path):
        return Config(RepositoryEnv(env_path))
    else:
        print("⚠️ Arquivo .env não encontrado. Usando valores padrão.")
        return None

config = carregar_config()

def get_config_value(key, default=None):
    try:
        if config:
            return config(key)
    except UndefinedValueError:
        pass
    return default
