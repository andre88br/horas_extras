from django.db import models

from empregados.models import Empregado, Importacoes


class RelatorioConfirmacao(models.Model):
    objects = models.Manager()
    empregado = models.ForeignKey(
        Empregado, on_delete=models.CASCADE
    )
    importacao = models.ForeignKey(
        Importacoes, on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    salario = models.FloatField()
    insalubridade_periculosidade = models.FloatField()
    saldo_mes = models.CharField(max_length=30)
    saldo_mes_decimal = models.FloatField()
    saldo_banco = models.CharField(max_length=30)
    saldo_banco_decimal = models.FloatField()
    horas_diurnas = models.FloatField()
    valor_diurnas = models.FloatField()
    horas_noturnas = models.FloatField()
    valor_noturnas = models.FloatField()
    horas_trabalhadas = models.FloatField()
    valor_total = models.FloatField()
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
    importado_por = models.CharField(max_length=100)
    importado_por_id = models.IntegerField()
    data_upload = models.DateTimeField()
    setor = models.CharField(max_length=100)

    class Meta:
        ordering = ['nome', 'cargo', 'salario', 'insalubridade_periculosidade', 'saldo_mes',
                    'saldo_mes_decimal', 'saldo_banco', 'saldo_banco_decimal', 'horas_diurnas',
                    'valor_diurnas', 'horas_noturnas', 'valor_noturnas', 'horas_trabalhadas',
                    'valor_total', 'dia1', 'dia2', 'dia3', 'dia4', 'dia5', 'dia6', 'dia7',
                    'dia8', 'dia9', 'dia10', 'dia11', 'dia12', 'dia13', 'dia14', 'dia15',
                    'dia16', 'dia17', 'dia18', 'dia19', 'dia20', 'dia21', 'dia22', 'dia23',
                    'dia24', 'dia25', 'dia26', 'dia27', 'dia28', 'dia29', 'dia30', 'dia31',
                    'importado_por', 'importado_por_id', 'data_upload']


class RelatorioSolicitacao(models.Model):
    objects = models.Manager()
    empregado = models.ForeignKey(
        Empregado, on_delete=models.CASCADE
    )
    importacao = models.ForeignKey(
        Importacoes, on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    salario = models.FloatField()
    insalubridade_periculosidade = models.FloatField()
    saldo_banco = models.CharField(max_length=30)
    saldo_banco_decimal = models.FloatField()
    horas_diurnas = models.FloatField()
    valor_diurnas = models.FloatField()
    horas_noturnas = models.FloatField()
    valor_noturnas = models.FloatField()
    horas_totais = models.FloatField()
    valor_total = models.FloatField()
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
    importado_por = models.CharField(max_length=100)
    importado_por_id = models.IntegerField()
    data_upload = models.DateTimeField()
    setor = models.CharField(max_length=100)

    class Meta:
        ordering = ['nome', 'cargo', 'salario', 'insalubridade_periculosidade', 'saldo_banco',
                    'saldo_banco_decimal', 'horas_diurnas', 'valor_diurnas', 'horas_noturnas',
                    'valor_noturnas', 'horas_totais', 'valor_total', 'dia1', 'dia2', 'dia3',
                    'dia4', 'dia5', 'dia6', 'dia7', 'dia8', 'dia9', 'dia10', 'dia11', 'dia12',
                    'dia13', 'dia14', 'dia15', 'dia16', 'dia17', 'dia18', 'dia19', 'dia20',
                    'dia21', 'dia22', 'dia23', 'dia24', 'dia25', 'dia26', 'dia27', 'dia28',
                    'dia29', 'dia30', 'dia31', 'importado_por', 'importado_por_id',
                    'data_upload']


class RelatorioNegativos(models.Model):
    objects = models.Manager()
    empregado = models.ForeignKey(
        Empregado, on_delete=models.CASCADE
    )
    importacao = models.ForeignKey(
        Importacoes, on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    saldo_mes = models.CharField(max_length=30)
    saldo_mes_decimal = models.FloatField()
    saldo_banco = models.CharField(max_length=30)
    saldo_banco_decimal = models.FloatField()
    importado_por = models.CharField(max_length=100)
    importado_por_id = models.IntegerField()
    data_upload = models.DateTimeField()
    setor = models.CharField(max_length=100)
    tipo = models.CharField(max_length=30)


class RelatorioCodigo90(models.Model):
    objects = models.Manager()
    empregado = models.ForeignKey(
        Empregado, on_delete=models.CASCADE
    )
    importacao = models.ForeignKey(
        Importacoes, on_delete=models.CASCADE
    )
    cod_afastamento = models.IntegerField(default=90)
    inicio = models.CharField(max_length=15)
    fim = models.CharField(max_length=15)
    importado_por = models.CharField(max_length=100)
    importado_por_id = models.IntegerField()
    data_upload = models.DateTimeField()


class RelatorioRejeitarBatidas(models.Model):
    objects = models.Manager()
    empregado = models.ForeignKey(
        Empregado, on_delete=models.CASCADE
    )
    importacao = models.ForeignKey(
        Importacoes, on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=100)
    dia1 = models.CharField(max_length=30, null=True)
    dia2 = models.CharField(max_length=30, null=True)
    dia3 = models.CharField(max_length=30, null=True)
    dia4 = models.CharField(max_length=30, null=True)
    dia5 = models.CharField(max_length=30, null=True)
    dia6 = models.CharField(max_length=30, null=True)
    dia7 = models.CharField(max_length=30, null=True)
    dia8 = models.CharField(max_length=30, null=True)
    dia9 = models.CharField(max_length=30, null=True)
    dia10 = models.CharField(max_length=30, null=True)
    dia11 = models.CharField(max_length=30, null=True)
    dia12 = models.CharField(max_length=30, null=True)
    dia13 = models.CharField(max_length=30, null=True)
    dia14 = models.CharField(max_length=30, null=True)
    dia15 = models.CharField(max_length=30, null=True)
    dia16 = models.CharField(max_length=30, null=True)
    dia17 = models.CharField(max_length=30, null=True)
    dia18 = models.CharField(max_length=30, null=True)
    dia19 = models.CharField(max_length=30, null=True)
    dia20 = models.CharField(max_length=30, null=True)
    dia21 = models.CharField(max_length=30, null=True)
    dia22 = models.CharField(max_length=30, null=True)
    dia23 = models.CharField(max_length=30, null=True)
    dia24 = models.CharField(max_length=30, null=True)
    dia25 = models.CharField(max_length=30, null=True)
    dia26 = models.CharField(max_length=30, null=True)
    dia27 = models.CharField(max_length=30, null=True)
    dia28 = models.CharField(max_length=30, null=True)
    dia29 = models.CharField(max_length=30, null=True)
    dia30 = models.CharField(max_length=30, null=True)
    dia31 = models.CharField(max_length=30, null=True)
    importado_por = models.CharField(max_length=100)
    importado_por_id = models.IntegerField()
    data_upload = models.DateTimeField()
    tipo = models.CharField(max_length=15)
    

class RelatorioPagas(models.Model):
    objects = models.Manager()
    cargo = models.CharField(max_length=100)
    empregado = models.ForeignKey(
        Empregado, on_delete=models.CASCADE
    )
    importacao = models.ForeignKey(
        Importacoes, on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=100)
    qtd = models.IntegerField(default=1)
    hs_diurnas = models.FloatField()
    valor_diurnas = models.FloatField()
    hs_noturnas = models.FloatField()
    valor_noturnas = models.FloatField()
    total = models.FloatField()
    importado_por = models.CharField(max_length=100)
    importado_por_id = models.IntegerField()
    data_upload = models.DateTimeField()
    setor = models.CharField(max_length=100)


class RelatorioEntradaSaida(models.Model):
    objects = models.Manager()
    empregado = models.ForeignKey(
        Empregado, on_delete=models.CASCADE
    )
    importacao = models.ForeignKey(
        Importacoes, on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    data = models.CharField(max_length=15)
    escala = models.CharField(max_length=10)
    entrada = models.TimeField()
    saida = models.TimeField()
    horas_trabalhadas = models.FloatField()
    horas_diurnas = models.FloatField()
    horas_noturnas = models.FloatField()
    importado_por = models.CharField(max_length=100)
    importado_por_id = models.IntegerField()
    data_upload = models.DateTimeField()
    setor = models.CharField(max_length=100)


class RelatorioErros(models.Model):
    objects = models.Manager()
    empregado = models.ForeignKey(
        Empregado, on_delete=models.CASCADE
    )
    importacao = models.ForeignKey(
        Importacoes, on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=100)
    data = models.CharField(max_length=15)
    escala = models.CharField(max_length=10)
    entrada = models.CharField(max_length=15)
    saida = models.CharField(max_length=15)
    horas_trabalhadas = models.FloatField()
    horas_diurnas = models.FloatField()
    horas_noturnas = models.FloatField()
    importado_por = models.CharField(max_length=100)
    importado_por_id = models.IntegerField()
    data_upload = models.DateTimeField()
    tipo = models.CharField(max_length=30)

    class Meta:
        ordering = ['nome', 'data', 'escala', 'entrada', 'saida', 'horas_diurnas',
                    'horas_noturnas', 'horas_trabalhadas', 'importado_por', 'importado_por_id',
                    'data_upload']
