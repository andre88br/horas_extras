from django.contrib import admin

# Register your models here.
from relatorios.models import RelatorioConfirmacao, RelatorioSolicitacao, RelatorioErros, RelatorioCodigo90, \
    RelatorioEntradaSaida, RelatorioRejeitarBatidas, RelatorioNegativos, RelatorioPagas


class ListandoRelatorioConfirmacao(admin.ModelAdmin):
    list_display = ("id", "nome", "empregado", "data_upload", "setor")
    list_display_links = ("nome", "empregado", "data_upload", "setor")
    search_fields = ("empregado", "data_upload", "setor")
    list_filter = ("empregado", "data_upload", "setor")
    list_per_page = 100


class ListandoRelatorioSolicitacao(admin.ModelAdmin):
    list_display = ("id", "nome", "data_upload", "setor")
    list_display_links = ("nome", "data_upload", "setor")
    search_fields = ("empregado", "data_upload", "setor")
    list_filter = ("data_upload", "setor", "valor_total")
    list_per_page = 100


class ListandoRelatorioRejeitarBatidas(admin.ModelAdmin):
    list_display = ("id", "nome","empregado", "data_upload")
    list_display_links = ("nome", "empregado", "data_upload")
    search_fields = ("empregado", "data_upload")
    list_filter = ("empregado", "data_upload")
    list_per_page = 100


class ListandoRelatorioErros(admin.ModelAdmin):
    list_display = ("id", "nome", "empregado", "data_upload")
    list_display_links = ("nome", "empregado", "data_upload")
    search_fields = ("empregado", "data_upload")
    list_filter = ("empregado", "data_upload")
    list_per_page = 100


class ListandoRelatorioCodigo90(admin.ModelAdmin):
    list_display = ("id", "empregado", "data_upload")
    list_display_links = ("empregado", "data_upload")
    search_fields = ("empregado","data_upload")
    list_filter = ("empregado", "data_upload")
    list_per_page = 100


class ListandoRelatorioEntradaSaida(admin.ModelAdmin):
    list_display = ("id", "nome", "empregado", "data_upload")
    list_display_links = ("empregado", "data_upload")
    search_fields = ("empregado", "data_upload")
    list_filter = ("empregado", "data_upload")
    list_per_page = 100


class ListandoRelatorioNegativos(admin.ModelAdmin):
    list_display = ("id", "nome", "empregado", "data_upload")
    list_display_links = ("nome", "empregado", "data_upload")
    search_fields = ("empregado", "data_upload")
    list_filter = ("empregado", "data_upload")
    list_per_page = 100


class ListandoRelatorioPagas(admin.ModelAdmin):
    list_display = ("id", "nome", "empregado", "data_upload")
    list_display_links = ("nome", "empregado", "data_upload")
    search_fields = ("empregado", "data_upload")
    list_filter = ("empregado", "data_upload")
    list_per_page = 100


admin.site.register(RelatorioConfirmacao, ListandoRelatorioConfirmacao)
admin.site.register(RelatorioSolicitacao, ListandoRelatorioSolicitacao)
admin.site.register(RelatorioErros, ListandoRelatorioErros)
admin.site.register(RelatorioCodigo90, ListandoRelatorioCodigo90)
admin.site.register(RelatorioEntradaSaida, ListandoRelatorioEntradaSaida)
admin.site.register(RelatorioRejeitarBatidas, ListandoRelatorioRejeitarBatidas)
admin.site.register(RelatorioNegativos, ListandoRelatorioNegativos)
admin.site.register(RelatorioPagas, ListandoRelatorioPagas)
