import locale

from django.contrib import admin

from relatorios.models import *


class ListandoRelatorioConfirmacao(admin.ModelAdmin):
    list_display = ("id", "nome", "cargo", "setor")
    list_display_links = ("nome", "cargo", "setor")
    search_fields = ("empregado__matricula", "nome", "cargo", "setor")
    list_filter = ("importacao__ano", "importacao__mes", "cargo", "setor")
    list_per_page = 20


class ListandoRelatorioSolicitacao(admin.ModelAdmin):
    list_display = ("id", "nome", "cargo", "setor")
    list_display_links = ("nome", "cargo", "setor")
    search_fields = ("empregado__matricula", "nome", "cargo", "setor")
    list_filter = ("importacao__ano", "importacao__mes", "cargo", "setor")
    list_per_page = 20


class ListandoRelatorioRejeitarBatidas(admin.ModelAdmin):
    list_display = ("matricula", "nome", "tipo")
    list_display_links = ("matricula", "nome", "tipo")
    search_fields = ("empregado__matricula", "nome", "tipo")
    list_filter = ("importacao__ano", "importacao__mes", "tipo")
    list_per_page = 30

    @staticmethod
    def matricula(obj):
        return obj.empregado.matricula


class ListandoRelatorioErros(admin.ModelAdmin):
    list_display = ("matricula", "nome", "data", "escala", "tipo")
    list_display_links = ("matricula", "nome")
    search_fields = ("empregado__matricula", "nome", "tipo")
    list_filter = ("importacao__ano", "importacao__mes", "tipo")
    list_per_page = 20

    @staticmethod
    def matricula(obj):
        return obj.empregado.matricula


class ListandoRelatorioCodigo90(admin.ModelAdmin):
    list_display = ("matricula", "nome", "inicio", "fim")
    list_display_links = ("matricula", "nome")
    search_fields = ("empregado__matricula", "nome", "inicio", "fim")
    list_filter = ("importacao__ano", "importacao__mes",)
    list_per_page = 20

    @staticmethod
    def matricula(obj):
        return obj.empregado.matricula

    @staticmethod
    def nome(obj):
        return obj.empregado.nome


class ListandoRelatorioEntradaSaida(admin.ModelAdmin):
    list_display = ("id", "nome", "cargo")
    list_display_links = ("nome", "cargo")
    search_fields = ("empregado__matricula", "nome", "cargo")
    list_filter = ("importacao__ano", "importacao__mes", "cargo")
    list_per_page = 20


class ListandoRelatorioNegativos(admin.ModelAdmin):
    list_display = ("matricula", "nome", "cargo", "saldo_mes_", "saldo_banco_", "tipo", "mes", "ano")
    list_display_links = ("matricula", "nome", "cargo")
    search_fields = ("empregado__matricula", "nome", "cargo", "tipo")
    list_filter = ("importacao__ano", "importacao__mes", "cargo", "tipo")
    list_per_page = 20

    @staticmethod
    def mes(obj):
        return obj.importacao.mes

    @staticmethod
    def ano(obj):
        return obj.importacao.ano

    @staticmethod
    def matricula(obj):
        return obj.empregado.matricula

    @staticmethod
    def saldo_mes_(obj):
        saldo_mes = float(str(obj.saldo_mes_decimal).replace(',', '.'))
        return round(saldo_mes, 2)

    @staticmethod
    def saldo_banco_(obj):
        saldo_banco = float(str(obj.saldo_banco_decimal).replace(',', '.'))
        return round(saldo_banco, 2)


class ListandoRelatorioPagas(admin.ModelAdmin):
    list_display = ("matricula", "nome", "hs_diurnas_", "valor_diurnas_",
                    "hs_noturnas_", "valor_noturnas_", "total_", "mes", "ano")
    list_display_links = ("matricula", "nome")
    search_fields = ("empregado__matricula", "nome", "setor")
    list_filter = ("importacao__mes", "importacao__ano", "setor")
    list_per_page = 100

    @staticmethod
    def hs_diurnas_(obj):
        horas = float(str(obj.hs_diurnas).replace(',', '.'))
        return round(horas)

    @staticmethod
    def hs_noturnas_(obj):
        horas = float(str(obj.hs_noturnas).replace(',', '.'))
        return round(horas)

    @staticmethod
    def valor_diurnas_(obj):
        valor = float(str(obj.valor_diurnas).replace(',', '.'))
        return locale.currency(valor, grouping=True, symbol="R$")

    @staticmethod
    def valor_noturnas_(obj):
        valor = float(str(obj.valor_noturnas).replace(',', '.'))
        return locale.currency(valor, grouping=True, symbol="R$")

    @staticmethod
    def total_(obj):
        valor = float(str(obj.total).replace(',', '.'))
        return locale.currency(valor, grouping=True, symbol="R$")

    @staticmethod
    def mes(obj):
        return obj.importacao.mes

    @staticmethod
    def ano(obj):
        return obj.importacao.ano

    @staticmethod
    def matricula(obj):
        return obj.empregado.matricula


class ListandoVoltarNegativos(admin.ModelAdmin):
    list_display = ("id", "matricula", "nome", "mes", "ano")
    list_display_links = ("matricula", "nome")
    search_fields = ("empregado__matricula", "nome")
    list_filter = ("importacao__mes", "importacao__ano")
    list_per_page = 20

    @staticmethod
    def mes(obj):
        return obj.importacao.mes

    @staticmethod
    def ano(obj):
        return obj.importacao.ano

    @staticmethod
    def matricula(obj):
        return obj.empregado.matricula


# class ListandoFaltaRejeitar(admin.ModelAdmin):
#     list_display = ("id", "nome",)
#     list_display_links = ("nome", )
#     search_fields = ("id", "nome", )
#     list_filter = ("importacao__mes", "importacao__ano")
#     list_per_page = 20


admin.site.register(RelatorioConfirmacao, ListandoRelatorioConfirmacao)
admin.site.register(RelatorioSolicitacao, ListandoRelatorioSolicitacao)
admin.site.register(RelatorioErros, ListandoRelatorioErros)
admin.site.register(RelatorioCodigo90, ListandoRelatorioCodigo90)
admin.site.register(RelatorioEntradaSaida, ListandoRelatorioEntradaSaida)
admin.site.register(RelatorioRejeitarBatidas, ListandoRelatorioRejeitarBatidas)
admin.site.register(RelatorioNegativos, ListandoRelatorioNegativos)
admin.site.register(RelatorioPagas, ListandoRelatorioPagas)
admin.site.register(VoltarNegativos, ListandoVoltarNegativos)
# admin.site.register(FaltaRejeitar, ListandoVoltarNegativos)

