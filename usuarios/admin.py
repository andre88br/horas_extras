from django.contrib import admin

from .models import AnoSelecionado


class ListandoAno(admin.ModelAdmin):
    list_display = ("id", "ano")
    list_display_links = ("id", "ano")
    search_fields = ("id", "ano")
    list_filter = ("id", "ano")

    
admin.site.register(AnoSelecionado, ListandoAno)
