# -*- coding: utf-8 -*-
"""Servidor de produção (Windows) via waitress.

Roda o app WSGI do Django com DEBUG=False. É o processo mantido no ar pelo
serviço do Windows (NSSM): fica sempre ativo e reinicia sozinho se cair.

Uso manual (para testar):
    python servidor.py
"""
import os
import sys

# Garante que a raiz do projeto está no sys.path, independente do diretório
# de onde o serviço for iniciado.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Força modo produção ANTES de qualquer import do Django. O load_dotenv() em
# settings.py não sobrescreve variáveis já definidas no ambiente, então isto
# vence o DEBUG=True do arquivo .env (que continua servindo ao runserver de dev).
os.environ["DEBUG"] = "False"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")

from waitress import serve
from setup.wsgi import application

HOST = os.getenv("HOST", "0.0.0.0")          # 0.0.0.0 = acessível pela rede local
PORT = int(os.getenv("PORT_WSGI", "8000"))
THREADS = int(os.getenv("WAITRESS_THREADS", "8"))

if __name__ == "__main__":
    print(f"Servidor de produção em http://{HOST}:{PORT} (threads={THREADS}) - DEBUG=False")
    serve(application, host=HOST, port=PORT, threads=THREADS)
