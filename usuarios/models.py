from django.db import models

# Create your models here.


class AnoSelecionado(models.Model):
    objects = models.Manager()
    ano = models.IntegerField()
