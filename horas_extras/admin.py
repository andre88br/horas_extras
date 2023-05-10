from django.contrib import admin

from .models import Confirmacao, Frequencia, BancoMes, BancoTotal, Solicitacao


class ListandoConfirmacao(admin.ModelAdmin):
    list_display = ("id", "nome", "data_upload", "setor")
    list_display_links = ("nome", "data_upload", "setor")
    search_fields = ("data_upload", "setor")
    list_filter = ("data_upload", "setor")
    list_per_page = 10


class ListandoSolicitacao(admin.ModelAdmin):
    list_display = ("id", "nome", "data_upload", "setor")
    list_display_links = ("nome", "data_upload", "setor")
    search_fields = ("data_upload", "setor")
    list_filter = ("data_upload", "setor")
    list_per_page = 10


class ListandoFrequencia(admin.ModelAdmin):
    list_display = ("id", "nome", "data")
    list_display_links = ("nome",)
    search_fields = ("nome", "data")
    list_filter = ("data",)
    list_per_page = 500


class ListandoBancoMes(admin.ModelAdmin):
    list_display = ("id", "nome",)
    list_display_links = ("nome",)
    search_fields = ("nome",)
    # list_filter = ( )
    list_per_page = 100


class ListandoBancoTotal(admin.ModelAdmin):
    list_display = ("id", "nome",)
    list_display_links = ("nome",)
    search_fields = ("nome",)
    # list_filter = ( )
    list_per_page = 100


admin.site.register(Confirmacao, ListandoConfirmacao)
admin.site.register(Solicitacao, ListandoSolicitacao)
admin.site.register(Frequencia, ListandoFrequencia)
admin.site.register(BancoMes, ListandoBancoMes)
admin.site.register(BancoTotal, ListandoBancoMes)
