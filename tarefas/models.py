import uuid

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models


class Tarefa(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        EXECUTANDO = "executando", "Executando"
        CONCLUIDO = "concluido", "Concluído"
        ERRO = "erro", "Erro"

    class Nivel(models.TextChoices):
        SUCESSO = "success", "Sucesso"
        INFO = "info", "Info"
        ERRO = "error", "Erro"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=100)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDENTE)
    percentual = models.PositiveSmallIntegerField(default=0)
    mensagem = models.CharField(max_length=500, blank=True, default="")
    nivel_mensagem = models.CharField(max_length=10, choices=Nivel.choices, default=Nivel.INFO)
    template_resultado = models.CharField(max_length=200, blank=True, default="")
    contexto_extra = models.JSONField(default=dict, blank=True, encoder=DjangoJSONEncoder)
    resultado_html = models.TextField(blank=True, default="")
    redirect_url = models.CharField(max_length=300, blank=True, default="")
    erro_detalhe = models.TextField(blank=True, default="")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    concluido_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.tipo} ({self.status})"
