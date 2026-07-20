import base64

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Tarefa

_NIVEL_PARA_MENSAGEM = {
    Tarefa.Nivel.SUCESSO: messages.success,
    Tarefa.Nivel.ERRO: messages.error,
    Tarefa.Nivel.INFO: messages.info,
}


def acompanhar(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, pk=tarefa_id)
    if tarefa.status in (Tarefa.Status.CONCLUIDO, Tarefa.Status.ERRO):
        return redirect("tarefa_resultado", tarefa_id=tarefa.id)
    return render(request, "tarefas/acompanhar.html", {"tarefa": tarefa})


def status_json(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, pk=tarefa_id)
    return JsonResponse({
        "status": tarefa.status,
        "percentual": tarefa.percentual,
        "mensagem": tarefa.mensagem,
        "pronto": tarefa.status in (Tarefa.Status.CONCLUIDO, Tarefa.Status.ERRO),
    })


def resultado(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, pk=tarefa_id)
    if tarefa.status not in (Tarefa.Status.CONCLUIDO, Tarefa.Status.ERRO):
        return redirect("tarefa_acompanhar", tarefa_id=tarefa.id)

    if tarefa.mensagem:
        enviar_mensagem = _NIVEL_PARA_MENSAGEM.get(tarefa.nivel_mensagem, messages.info)
        enviar_mensagem(request, tarefa.mensagem)

    if tarefa.redirect_url:
        return redirect(tarefa.redirect_url)

    if '_arquivo_base64' in tarefa.contexto_extra:
        conteudo = base64.b64decode(tarefa.contexto_extra['_arquivo_base64'])
        resp = HttpResponse(conteudo,
                            content_type=tarefa.contexto_extra.get('_arquivo_content_type',
                                                                    'application/octet-stream'))
        resp['Content-Disposition'] = f'attachment; filename="{tarefa.contexto_extra.get("_arquivo_nome", "arquivo")}"'
        return resp

    contexto = dict(tarefa.contexto_extra)
    if tarefa.resultado_html:
        contexto["relatorio"] = tarefa.resultado_html
    return render(request, tarefa.template_resultado, contexto)
