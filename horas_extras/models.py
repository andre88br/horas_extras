from datetime import datetime

from django.db import models
from django.utils import timezone

from empregados.models import Empregado, Importacoes


class Confirmacao(models.Model):
    objects = models.Manager()
    empregado = models.ForeignKey(
        Empregado, on_delete=models.CASCADE
    )
    importacao = models.ForeignKey(
        Importacoes, on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    dia1 = models.CharField(max_length=10)
    dia2 = models.CharField(max_length=10)
    dia3 = models.CharField(max_length=10)
    dia4 = models.CharField(max_length=10)
    dia5 = models.CharField(max_length=10)
    dia6 = models.CharField(max_length=10)
    dia7 = models.CharField(max_length=10)
    dia8 = models.CharField(max_length=10)
    dia9 = models.CharField(max_length=10)
    dia10 = models.CharField(max_length=10)
    dia11 = models.CharField(max_length=10)
    dia12 = models.CharField(max_length=10)
    dia13 = models.CharField(max_length=10)
    dia14 = models.CharField(max_length=10)
    dia15 = models.CharField(max_length=10)
    dia16 = models.CharField(max_length=10)
    dia17 = models.CharField(max_length=10)
    dia18 = models.CharField(max_length=10)
    dia19 = models.CharField(max_length=10)
    dia20 = models.CharField(max_length=10)
    dia21 = models.CharField(max_length=10)
    dia22 = models.CharField(max_length=10)
    dia23 = models.CharField(max_length=10)
    dia24 = models.CharField(max_length=10)
    dia25 = models.CharField(max_length=10)
    dia26 = models.CharField(max_length=10)
    dia27 = models.CharField(max_length=10)
    dia28 = models.CharField(max_length=10)
    dia29 = models.CharField(max_length=10)
    dia30 = models.CharField(max_length=10)
    dia31 = models.CharField(max_length=10)
    data_upload = models.DateTimeField()
    setor = models.CharField(max_length=100)


class Solicitacao(models.Model):
    objects = models.Manager()
    empregado = models.ForeignKey(
        Empregado, on_delete=models.CASCADE
    )
    importacao = models.ForeignKey(
        Importacoes, on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    dia1 = models.CharField(max_length=10)
    dia2 = models.CharField(max_length=10)
    dia3 = models.CharField(max_length=10)
    dia4 = models.CharField(max_length=10)
    dia5 = models.CharField(max_length=10)
    dia6 = models.CharField(max_length=10)
    dia7 = models.CharField(max_length=10)
    dia8 = models.CharField(max_length=10)
    dia9 = models.CharField(max_length=10)
    dia10 = models.CharField(max_length=10)
    dia11 = models.CharField(max_length=10)
    dia12 = models.CharField(max_length=10)
    dia13 = models.CharField(max_length=10)
    dia14 = models.CharField(max_length=10)
    dia15 = models.CharField(max_length=10)
    dia16 = models.CharField(max_length=10)
    dia17 = models.CharField(max_length=10)
    dia18 = models.CharField(max_length=10)
    dia19 = models.CharField(max_length=10)
    dia20 = models.CharField(max_length=10)
    dia21 = models.CharField(max_length=10)
    dia22 = models.CharField(max_length=10)
    dia23 = models.CharField(max_length=10)
    dia24 = models.CharField(max_length=10)
    dia25 = models.CharField(max_length=10)
    dia26 = models.CharField(max_length=10)
    dia27 = models.CharField(max_length=10)
    dia28 = models.CharField(max_length=10)
    dia29 = models.CharField(max_length=10)
    dia30 = models.CharField(max_length=10)
    dia31 = models.CharField(max_length=10)
    data_upload = models.DateTimeField()
    setor = models.CharField(max_length=100)


class Frequencia(models.Model):
    objects = models.Manager()
    empregado = models.ForeignKey(
        Empregado, on_delete=models.CASCADE
    )
    importacao = models.ForeignKey(
        Importacoes, on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=100)
    data = models.DateField()
    batida1 = models.TimeField()
    batida2 = models.TimeField()
    batida3 = models.TimeField()
    batida4 = models.TimeField()
    batida5 = models.TimeField()
    batida6 = models.TimeField()
    escala = models.CharField(max_length=100)
    data_upload = models.DateTimeField(default=timezone.now)
    importado_por = models.CharField(max_length=100)
    importado_por_id = models.IntegerField()


class BancoMes(models.Model):
    objects = models.Manager()
    empregado = models.ForeignKey(
        Empregado, on_delete=models.CASCADE
    )
    importacao = models.ForeignKey(
        Importacoes, on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=100)
    saldo = models.CharField(max_length=20)
    saldo_decimal = models.FloatField()
    data_upload = models.DateTimeField()
    importado_por = models.CharField(max_length=100)
    importado_por_id = models.IntegerField()


class BancoTotal(models.Model):
    objects = models.Manager()
    empregado = models.ForeignKey(
        Empregado, on_delete=models.CASCADE
    )
    importacao = models.ForeignKey(
        Importacoes, on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=100)
    saldo = models.CharField(max_length=20)
    saldo_decimal = models.FloatField()
    data_upload = models.DateTimeField()
    importado_por = models.CharField(max_length=100)
    importado_por_id = models.IntegerField()
