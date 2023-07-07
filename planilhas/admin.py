from django.contrib import admin

from planilhas.models import *


class ListandoPlanilhaConfirmacao(admin.ModelAdmin):
    list_display = ("id", "matricula_empregado", "nome_empregado", "setor")
    list_display_links = ("matricula_empregado", "nome_empregado")
    search_fields = ("matricula_empregado", "nome_empregado", "setor")
    list_filter = ("importacao__ano", "importacao__mes", "setor")
    list_per_page = 20

    def nome_empregado(self, obj):
        return obj.empregado.nome

    def matricula_empregado(self, obj):
        return obj.empregado.matricula


class ListandoPlanilhaSolicitacao(admin.ModelAdmin):
    list_display = ("id", "matricula_empregado", "nome_empregado", "setor")
    list_display_links = ("matricula_empregado", "nome_empregado")
    search_fields = ("empregado__matricula", "empregado__nome", "setor")
    list_filter = ("importacao__ano", "importacao__mes", "setor")
    list_per_page = 20

    def nome_empregado(self, obj):
        return obj.empregado.nome

    def matricula_empregado(self, obj):
        return obj.empregado.matricula


admin.site.register(PlanilhaConfirmacao, ListandoPlanilhaConfirmacao)
admin.site.register(PlanilhaSolicitacao, ListandoPlanilhaSolicitacao)
