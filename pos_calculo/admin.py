# Register your models here.
from django.contrib import admin

from pos_calculo.models import RelatorioBatidasRejeitadas, RelatorioRubricasLancadas, RelatorioBatidasDesrejeitadas


class ListandoRelatorioBatidasRejeitadas(admin.ModelAdmin):
    list_display = ("id", "nome", "data", "tipo", "data_upload")
    list_display_links = ("nome", "tipo")
    search_fields = ("nome", "data", "tipo")
    list_filter = ("importacao__ano", "importacao__mes", "tipo")
    list_per_page = 30


class ListaRubricasLancadas(admin.ModelAdmin):
    list_display = ("id", "nome")
    list_display_links = ("nome",)
    search_fields = ("nome",)
    list_filter = ("importacao__ano", "importacao__mes")
    list_per_page = 30


class ListandoRelatorioBatidasDesrejeitadas(admin.ModelAdmin):
    list_display = ("id", "nome", "data", "tipo", "data_upload")
    list_display_links = ("nome", "tipo")
    search_fields = ("nome", "data", "tipo")
    list_filter = ("importacao__ano", "importacao__mes", "tipo")
    list_per_page = 30


admin.site.register(RelatorioBatidasRejeitadas, ListandoRelatorioBatidasRejeitadas)
admin.site.register(RelatorioRubricasLancadas, ListaRubricasLancadas)
admin.site.register(RelatorioBatidasDesrejeitadas, ListandoRelatorioBatidasDesrejeitadas)

