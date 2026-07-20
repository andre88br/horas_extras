# Register your models here.
from django.contrib import admin

from pos_calculo.models import RelatorioBatidasRejeitadas, RelatorioRubricasLancadas, RelatorioBatidasDesrejeitadas, \
    RelatorioBancosRecalculados, RelatorioEscalaVoltada, RelatorioEscalaTirada

import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


class ListandoRelatorioBatidasRejeitadas(admin.ModelAdmin):
    list_display = ("matricula", "nome", "data", "tipo", "data_upload")
    list_display_links = ("matricula", "nome", "tipo")
    search_fields = ("empregado__matricula", "nome", "data", "tipo")
    list_filter = ("importacao__ano", "importacao__mes", "tipo")
    list_per_page = 30

    @staticmethod
    def matricula(obj):
        return obj.empregado.matricula


class ListaRubricasLancadas(admin.ModelAdmin):
    list_display = ("matricula","nome", "rubrica", "horas_lancadas", "mes", "ano")
    list_display_links = ("matricula", "nome",)
    search_fields = ("empregado__matricula", "nome",)
    list_filter = ("importacao__ano", "importacao__mes")
    list_per_page = 30

    @staticmethod
    def ano(obj):
        return obj.importacao.ano

    @staticmethod
    def mes(obj):
        return obj.importacao.mes

    @staticmethod
    def matricula(obj):
        return obj.empregado.matricula

    @staticmethod
    def horas_lancadas(obj):
        valor = float(str(obj.valor).replace(',', '.'))

        return valor


class ListandoRelatorioBatidasDesrejeitadas(admin.ModelAdmin):
    list_display = ("id", "nome", "data", "tipo", "data_upload")
    list_display_links = ("nome", "tipo")
    search_fields = ("empregado__matricula", "nome", "data", "tipo")
    list_filter = ("importacao__ano", "importacao__mes", "tipo")
    list_per_page = 30


class ListandoRelatorioBancosRecalculados(admin.ModelAdmin):
    list_display = ("id", "nome", "empregado")
    list_display_links = ("nome", )
    search_fields = ("empregado__matricula", "nome", )
    list_filter = ("importacao__ano", "importacao__mes", )
    list_per_page = 30


class ListandoEscalaVoltada(admin.ModelAdmin):
    list_display = ("id", "nome", "empregado")
    list_display_links = ("nome", )
    search_fields = ("empregado__matricula", "nome", )
    list_filter = ("importacao__ano", "importacao__mes", )
    list_per_page = 30


class ListandoEscalaTirada(admin.ModelAdmin):
    list_display = ("id", "nome", "empregado")
    list_display_links = ("nome", )
    search_fields = ("empregado__matricula", "nome", )
    list_filter = ("importacao__ano", "importacao__mes", )
    list_per_page = 30


admin.site.register(RelatorioBatidasRejeitadas, ListandoRelatorioBatidasRejeitadas)
admin.site.register(RelatorioRubricasLancadas, ListaRubricasLancadas)
admin.site.register(RelatorioBatidasDesrejeitadas, ListandoRelatorioBatidasDesrejeitadas)
admin.site.register(RelatorioBancosRecalculados, ListandoRelatorioBancosRecalculados)
admin.site.register(RelatorioEscalaVoltada, ListandoEscalaVoltada)
admin.site.register(RelatorioEscalaTirada, ListandoEscalaTirada)