from django.contrib import admin
from django.urls import path, include

from usuarios.views import dashboard

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("horas_extras/", include("horas_extras.urls")),
    path("usuarios/", include("usuarios.urls")),
    path("empregados/", include("empregados.urls")),
    path("relatorios/", include("relatorios.urls")),
    path("pos_calculo/", include("pos_calculo.urls")),
    path("planilhas/", include("planilhas.urls")),
    path("admin/", admin.site.urls),
]

