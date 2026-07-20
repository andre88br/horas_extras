class RastreadorProgresso:
    """Distribui 0-100% entre fases nomeadas, com peso relativo por fase.

    Usado quando uma função tem vários loops sequenciais (ex: calcula_he
    percorre confirmações, depois frequências, depois bancos) para que o
    percentual final seja monotônico em vez de resetar a cada loop.
    """

    def __init__(self, progress_callback, pesos):
        self._callback = progress_callback or (lambda percentual, mensagem=None: None)
        total_peso = sum(pesos.values()) or 1
        self._faixas = {}
        acumulado = 0
        for nome, peso in pesos.items():
            self._faixas[nome] = (acumulado / total_peso * 100, peso / total_peso * 100)
            acumulado += peso

    def fase(self, nome, indice, total, mensagem=None):
        base, span = self._faixas.get(nome, (0, 100))
        total = total or 1
        percentual = base + (indice + 1) / total * span
        self._callback(int(percentual), mensagem)
