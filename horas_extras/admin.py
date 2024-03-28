from django.contrib import admin

from .models import Confirmacao, Frequencia, BancoMes, BancoTotal, Solicitacao


class ListandoConfirmacao(admin.ModelAdmin):
    list_display = ("id", "matricula", "nome", "cargo", "setor", "mes", "ano")
    list_display_links = ("id", "matricula", "nome")
    search_fields = ("nome", "cargo", "setor")
    list_filter = ("importacao__ano", "importacao__mes", "cargo", "setor")
    list_per_page = 20

    @staticmethod
    def ano(obj):
        return obj.importacao.ano

    @staticmethod
    def mes(obj):
        return obj.importacao.mes

    @staticmethod
    def matricula(obj):
        return obj.empregado.matricula


class ListandoSolicitacao(admin.ModelAdmin):
    list_display = ("id", "matricula", "nome", "cargo", "setor", "mes", "ano")
    list_display_links = ("id", "matricula", "nome")
    search_fields = ("nome", "cargo", "setor", "matricula")
    list_filter = ("importacao__ano", "importacao__mes", "cargo", "setor")
    list_per_page = 10

    @staticmethod
    def ano(obj):
        return obj.importacao.ano

    @staticmethod
    def mes(obj):
        return obj.importacao.mes

    @staticmethod
    def matricula(obj):
        return obj.empregado.matricula


class ListandoFrequencia(admin.ModelAdmin):
    list_display = ("matricula", "nome", "data")
    list_display_links = ("matricula", "nome", "data")
    search_fields = ("nome", "data")
    list_filter = ("importacao__ano", "importacao__mes", "data")
    list_per_page = 20

    @staticmethod
    def ano(obj):
        return obj.importacao.ano

    @staticmethod
    def mes(obj):
        return obj.importacao.mes

    @staticmethod
    def matricula(obj):
        return obj.empregado.matricula


class ListandoBancoMes(admin.ModelAdmin):
    list_display = ("matricula", "nome", "saldo_decimal_", "mes", "ano")
    list_display_links = ("matricula", "nome", "saldo_decimal_")
    search_fields = ("nome",)
    list_filter = ("importacao__ano", "importacao__mes")
    list_per_page = 20

    @staticmethod
    def saldo_decimal_(obj):
        return round(obj.saldo_decimal, 2)

    @staticmethod
    def ano(obj):
        return obj.importacao.ano


    @staticmethod
    def mes(obj):
        return obj.importacao.mes

    @staticmethod
    def matricula(obj):
        return obj.empregado.matricula


class ListandoBancoTotal(admin.ModelAdmin):
    list_display = ("matricula", "nome", "saldo_decimal_", "mes", "ano")
    list_display_links = ("matricula", "nome", "saldo_decimal_")
    search_fields = ("nome",)
    list_filter = ("importacao__ano", "importacao__mes")
    list_per_page = 20

    @staticmethod
    def saldo_decimal_(obj):
        return round(obj.saldo_decimal, 2)

    @staticmethod
    def ano(obj):
        return obj.importacao.ano

    @staticmethod
    def mes(obj):
        return obj.importacao.mes

    @staticmethod
    def matricula(obj):
        return obj.empregado.matricula


admin.site.register(Confirmacao, ListandoConfirmacao)
admin.site.register(Solicitacao, ListandoSolicitacao)
admin.site.register(Frequencia, ListandoFrequencia)
admin.site.register(BancoMes, ListandoBancoMes)
admin.site.register(BancoTotal, ListandoBancoTotal)
