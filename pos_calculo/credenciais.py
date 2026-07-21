"""Contexto do SIGP por thread de worker: credenciais + callback de progresso.

O login do SIGP é informado uma vez pela pessoa (guardado na sessão do
navegador, no servidor) e precisa chegar até `inicia_driver()`, que roda numa
thread separada da requisição. Da mesma forma, `inicia_driver()` precisa
reportar progresso ("Login efetuado com sucesso") sem receber o callback como
parâmetro em toda a cadeia de chamadas.

Usamos um thread-local: cada worker chama `preparar_selenium(...)` no início da
sua própria thread; `inicia_driver()`/`login()` leem dali.
"""
import threading

_local = threading.local()


def preparar_selenium(usuario, senha, progress_callback=None):
    _local.usuario = usuario
    _local.senha = senha
    _local.progress = progress_callback


def get_credenciais():
    return getattr(_local, 'usuario', None), getattr(_local, 'senha', None)


def reportar_progresso(percentual, mensagem):
    cb = getattr(_local, 'progress', None)
    if cb:
        cb(percentual, mensagem)
