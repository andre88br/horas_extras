from django.contrib import admin
from .models import Empregado, CargaHoraria, Importacoes


class ListandoImportacoes(admin.ModelAdmin):
    list_display = ("id", "mes", "ano", "data_upload", "tipo")
    list_display_links = ("mes", "ano", "data_upload", "tipo")
    list_filter = ("mes", "ano", "data_upload", "tipo")
    search_fields = ("id", "mes", "ano", "data_upload", "tipo")
    list_per_page = 16


class ListandoEmpregado(admin.ModelAdmin):
    list_display = ("id", "matricula", "nome", "data_atualizacao")
    list_display_links = ("matricula", "nome")
    search_fields = ("id", "matricula", "nome", "data_atualizacao")
    list_filter = ("data_atualizacao", "salario", "insalubridade")
    list_per_page = 700


class ListandoCargaHoraria(admin.ModelAdmin):
    list_display = ("id", "empregado", "nome", "carga_horaria")
    list_display_links = ("empregado", "nome", "carga_horaria")
    search_fields = ("empregado", "nome", "carga_horaria")
    list_filter = ("carga_horaria", )
    list_per_page = 500


admin.site.register(Importacoes, ListandoImportacoes)
admin.site.register(Empregado, ListandoEmpregado)
admin.site.register(CargaHoraria, ListandoCargaHoraria)
