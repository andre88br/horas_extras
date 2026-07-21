import threading
import traceback

from django.utils import timezone

from tarefas.models import Tarefa

_locks = {}
_locks_guard = threading.Lock()


def _get_lock(lock_key):
    with _locks_guard:
        return _locks.setdefault(lock_key, threading.Lock())


def iniciar_tarefa(*, tipo, usuario, template_resultado, func, args=(), kwargs=None,
                    contexto_base=None, lock_key=None):
    """Cria uma Tarefa e executa `func` numa thread separada.

    `func(*args, progress_callback=fn, **kwargs)` deve retornar um dict:
        {'mensagem': str, 'nivel': 'success'|'info'|'error',
         'resultado_html': str (opcional), 'contexto_extra': dict (opcional),
         'redirect_url': str (opcional)}

    Se `lock_key` for informado, apenas uma tarefa com essa chave roda por vez.
    O lock é adquirido de forma síncrona, na thread da requisição, para que uma
    segunda submissão concorrente já volte com status=ERRO sem nunca iniciar
    o trabalho (usado pelas views do pos_calculo, que compartilham o login do SIGP).
    """
    kwargs = dict(kwargs or {})
    tarefa = Tarefa.objects.create(
        tipo=tipo, usuario=usuario, template_resultado=template_resultado,
        contexto_extra=contexto_base or {},
    )

    lock = _get_lock(lock_key) if lock_key else None
    if lock is not None and not lock.acquire(blocking=False):
        tarefa.status = Tarefa.Status.ERRO
        tarefa.nivel_mensagem = Tarefa.Nivel.ERRO
        tarefa.mensagem = ("Já existe um processamento em andamento utilizando o "
                            "navegador do SIGP. Aguarde a conclusão e tente novamente.")
        tarefa.concluido_em = timezone.now()
        tarefa.save(update_fields=["status", "nivel_mensagem", "mensagem", "concluido_em"])
        return tarefa

    def _run():
        ultimo_percentual = {"valor": -1}
        try:
            Tarefa.objects.filter(pk=tarefa.pk).update(status=Tarefa.Status.EXECUTANDO)

            def progress_callback(percentual, mensagem=None):
                percentual = max(0, min(100, int(percentual)))
                if percentual == ultimo_percentual["valor"] and not mensagem:
                    return
                ultimo_percentual["valor"] = percentual
                campos = {"percentual": percentual}
                if mensagem:
                    campos["mensagem"] = mensagem
                Tarefa.objects.filter(pk=tarefa.pk).update(**campos)

            resultado = func(*args, progress_callback=progress_callback, **kwargs)
            contexto = dict(tarefa.contexto_extra)
            contexto.update(resultado.get("contexto_extra", {}))
            Tarefa.objects.filter(pk=tarefa.pk).update(
                status=Tarefa.Status.CONCLUIDO,
                percentual=100,
                mensagem=resultado.get("mensagem", ""),
                nivel_mensagem=resultado.get("nivel", Tarefa.Nivel.INFO),
                resultado_html=resultado.get("resultado_html", ""),
                redirect_url=resultado.get("redirect_url", ""),
                contexto_extra=contexto,
                concluido_em=timezone.now(),
            )
        except Exception as exc:
            # A mensagem vai para um campo varchar(500); exceções do Selenium/DB
            # podem ser muito maiores e estourariam a coluna (o que impediria a
            # tarefa de ser marcada como ERRO e deixaria a barra travada). Trunca
            # aqui — o traceback completo fica em erro_detalhe (TextField).
            mensagem_erro = str(exc) or "Erro inesperado durante o processamento"
            if len(mensagem_erro) > 500:
                mensagem_erro = mensagem_erro[:497] + "..."
            Tarefa.objects.filter(pk=tarefa.pk).update(
                status=Tarefa.Status.ERRO,
                nivel_mensagem=Tarefa.Nivel.ERRO,
                mensagem=mensagem_erro,
                erro_detalhe=traceback.format_exc(),
                concluido_em=timezone.now(),
            )
        finally:
            if lock is not None:
                lock.release()

    threading.Thread(target=_run, daemon=True).start()
    return tarefa
