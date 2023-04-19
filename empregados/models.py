from django.db import models


class Importacoes(models.Model):
    objects = models.Manager()
    data_upload = models.DateTimeField()
    importado_por_id = models.IntegerField()
    importado_por = models.CharField(max_length=100)
    mes = models.IntegerField()
    ano = models.IntegerField()
    tipo = models.CharField(max_length=20)

    class Meta:
        # Define a chave primária composta
        unique_together = ('tipo', 'mes', 'ano')


class Empregado(models.Model):
    objects = models.Manager()
    importacao = models.ForeignKey(
        Importacoes, on_delete=models.CASCADE
    )
    matricula = models.IntegerField()
    nome = models.CharField(max_length=100)
    salario = models.FloatField()
    insalubridade = models.FloatField()
    data_atualizacao = models.DateTimeField()
    mes = models.IntegerField()
    ano = models.IntegerField()

    class Meta:
        # Define a chave primária composta
        unique_together = ('matricula', 'mes', 'ano')


class CargaHoraria(models.Model):
    objects = models.Manager()
    empregado = models.ForeignKey(
        Empregado, on_delete=models.CASCADE)
    importacao = models.ForeignKey(
        Importacoes, on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=100)
    carga_horaria = models.FloatField()
    importado_por = models.CharField(max_length=100)
    importado_por_id = models.IntegerField()

