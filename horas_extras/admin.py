from django.contrib import admin

from .models import Confirmacao, Frequencia, BancoMes, BancoTotal, Solicitacao


class ListandoConfirmacao(admin.ModelAdmin):
    list_display = ("id", "nome", "cargo", "setor")
    list_display_links = ("nome", "cargo", "setor")
    search_fields = ("nome", "cargo", "setor")
    list_filter = ("importacao__ano", "importacao__mes", "cargo", "setor")
    list_per_page = 20


class ListandoSolicitacao(admin.ModelAdmin):
    list_display = ("id", "nome", "cargo", "setor")
    list_display_links = ("nome", "cargo", "setor")
    search_fields = ("nome", "cargo", "setor")
    list_filter = ("importacao__ano", "importacao__mes", "cargo", "setor")
    list_per_page = 10


class ListandoFrequencia(admin.ModelAdmin):
    list_display = ("id", "nome", "data")
    list_display_links = ("nome",)
    search_fields = ("nome", "data")
    list_filter = ("importacao__ano", "importacao__mes", "data")
    list_per_page = 20


class ListandoBancoMes(admin.ModelAdmin):
    list_display = ("id", "nome", "saldo_decimal")
    list_display_links = ("nome", "saldo_decimal")
    search_fields = ("nome",)
    list_filter = ("importacao__ano", "importacao__mes")
    list_per_page = 20


class ListandoBancoTotal(admin.ModelAdmin):
    list_display = ("id", "nome", "saldo_decimal")
    list_display_links = ("nome", "saldo_decimal")
    search_fields = ("nome",)
    list_filter = ("importacao__ano", "importacao__mes")
    list_per_page = 20


admin.site.register(Confirmacao, ListandoConfirmacao)
admin.site.register(Solicitacao, ListandoSolicitacao)
admin.site.register(Frequencia, ListandoFrequencia)
admin.site.register(BancoMes, ListandoBancoMes)
admin.site.register(BancoTotal, ListandoBancoMes)
