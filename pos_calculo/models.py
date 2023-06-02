from django.db import models
# Create your models here.
from django.utils import timezone

from empregados.models import Empregado, Importacoes


class RelatorioBatidasRejeitadas(models.Model):
    objects = models.Manager
    empregado = models.ForeignKey(
        Empregado, on_delete=models.CASCADE
    )
    importacao = models.ForeignKey(
        Importacoes, on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=200)
    data = models.CharField(max_length=30)
    batida = models.IntegerField()
    tipo = models.CharField(max_length=30)
    data_upload = models.DateTimeField(default=timezone.now)
    importado_por = models.CharField(max_length=100)
    importado_por_id = models.IntegerField()


class RelatorioBancosRecalculados(models.Model):
    objects = models.Manager
    empregado = models.ForeignKey(
        Empregado, on_delete=models.CASCADE
    )
    importacao = models.ForeignKey(
        Importacoes, on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=200)
    data_upload = models.DateTimeField(default=timezone.now)
    importado_por = models.CharField(max_length=100)
    importado_por_id = models.IntegerField()


class RelatorioRubricasLancadas(models.Model):
    objects = models.Manager
    empregado = models.ForeignKey(
        Empregado, on_delete=models.CASCADE
    )
    importacao = models.ForeignKey(
        Importacoes, on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=200)
    rubrica = models.CharField(max_length=10)
    valor = models.CharField(max_length=50)
    data_upload = models.DateTimeField(default=timezone.now)
    importado_por = models.CharField(max_length=100)
    importado_por_id = models.IntegerField()


class RelatorioBatidasDesrejeitadas(models.Model):
    objects = models.Manager
    empregado = models.ForeignKey(
        Empregado, on_delete=models.CASCADE
    )
    importacao = models.ForeignKey(
        Importacoes, on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=200)
    data = models.CharField(max_length=30)
    batida = models.IntegerField()
    tipo = models.CharField(max_length=30)
    data_upload = models.DateTimeField(default=timezone.now)
    importado_por = models.CharField(max_length=100)
    importado_por_id = models.IntegerField()
