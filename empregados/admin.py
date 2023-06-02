from django.contrib import admin

from .models import Empregado, CargaHoraria, Importacoes


class ListandoImportacoes(admin.ModelAdmin):
    list_display = ("id", "tipo", "ano", "mes")
    list_display_links = ("id", "tipo")
    search_fields = ("id", "mes", "ano", "tipo")
    list_filter = ("mes", "ano", "tipo")
    list_per_page = 20


class ListandoEmpregado(admin.ModelAdmin):
    list_display = ("id", "matricula", "nome")
    list_display_links = ("matricula", "nome")
    search_fields = ("matricula", "nome")
    list_filter = ("importacao__ano", "importacao__mes")
    list_per_page = 200


class ListandoCargaHoraria(admin.ModelAdmin):
    list_display = ("id", "nome", "carga_horaria")
    list_display_links = ("nome", "carga_horaria")
    search_fields = ("nome", "carga_horaria")
    list_filter = ("carga_horaria", "importacao__ano", "importacao__mes")
    list_per_page = 200


admin.site.register(Importacoes, ListandoImportacoes)
admin.site.register(Empregado, ListandoEmpregado)
admin.site.register(CargaHoraria, ListandoCargaHoraria)
