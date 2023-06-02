from django.contrib import admin

from relatorios.models import RelatorioConfirmacao, RelatorioSolicitacao, RelatorioErros, RelatorioCodigo90, \
    RelatorioEntradaSaida, RelatorioRejeitarBatidas, RelatorioNegativos, RelatorioPagas, VoltarNegativos


class ListandoRelatorioConfirmacao(admin.ModelAdmin):
    list_display = ("id", "nome", "cargo", "setor")
    list_display_links = ("nome", "cargo", "setor")
    search_fields = ("nome", "cargo", "setor")
    list_filter = ("importacao__ano", "importacao__mes", "cargo", "setor")
    list_per_page = 20


class ListandoRelatorioSolicitacao(admin.ModelAdmin):
    list_display = ("id", "nome", "cargo", "setor")
    list_display_links = ("nome", "cargo", "setor")
    search_fields = ("nome", "cargo", "setor")
    list_filter = ("importacao__ano", "importacao__mes", "cargo", "setor")
    list_per_page = 20


class ListandoRelatorioRejeitarBatidas(admin.ModelAdmin):
    list_display = ("id", "nome", "tipo")
    list_display_links = ("nome", "tipo")
    search_fields = ("nome", "tipo")
    list_filter = ("importacao__ano", "importacao__mes", "tipo")
    list_per_page = 30


class ListandoRelatorioErros(admin.ModelAdmin):
    list_display = ("id", "nome", "data", "escala", "tipo")
    list_display_links = ("nome", "data", "escala")
    search_fields = ("nome", "tipo")
    list_filter = ("importacao__ano", "importacao__mes", "tipo")
    list_per_page = 20


class ListandoRelatorioCodigo90(admin.ModelAdmin):
    list_display = ("id", "inicio", "fim")
    list_display_links = ("inicio", "fim")
    search_fields = ("inicio", "fim")
    list_filter = ("importacao__ano", "importacao__mes",)
    list_per_page = 20


class ListandoRelatorioEntradaSaida(admin.ModelAdmin):
    list_display = ("id", "nome", "cargo")
    list_display_links = ("nome", "cargo")
    search_fields = ("nome", "cargo")
    list_filter = ("importacao__ano", "importacao__mes", "cargo")
    list_per_page = 20


class ListandoRelatorioNegativos(admin.ModelAdmin):
    list_display = ("id", "nome", "cargo", "saldo_mes_decimal", "saldo_banco_decimal", "tipo")
    list_display_links = ("nome", "cargo")
    search_fields = ("nome", "cargo", "tipo")
    list_filter = ("importacao__ano", "importacao__mes", "cargo", "tipo")
    list_per_page = 20


class ListandoRelatorioPagas(admin.ModelAdmin):
    list_display = ("id", "nome", "setor")
    list_display_links = ("nome", "setor")
    search_fields = ("nome", "setor")
    list_filter = ("importacao__mes", "importacao__ano", "setor")
    list_per_page = 100


class ListandoVoltarNegativos(admin.ModelAdmin):
    list_display = ("id", "nome",)
    list_display_links = ("nome", )
    search_fields = ("id", "nome", )
    list_filter = ("importacao__mes", "importacao__ano")
    list_per_page = 20


admin.site.register(RelatorioConfirmacao, ListandoRelatorioConfirmacao)
admin.site.register(RelatorioSolicitacao, ListandoRelatorioSolicitacao)
admin.site.register(RelatorioErros, ListandoRelatorioErros)
admin.site.register(RelatorioCodigo90, ListandoRelatorioCodigo90)
admin.site.register(RelatorioEntradaSaida, ListandoRelatorioEntradaSaida)
admin.site.register(RelatorioRejeitarBatidas, ListandoRelatorioRejeitarBatidas)
admin.site.register(RelatorioNegativos, ListandoRelatorioNegativos)
admin.site.register(RelatorioPagas, ListandoRelatorioPagas)
admin.site.register(VoltarNegativos, ListandoVoltarNegativos)

