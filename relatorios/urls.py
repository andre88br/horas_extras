from django.urls import path
from . import views

urlpatterns = [
    path("", views.relatorios, name="relatorios"),
    path("gera_relatorio", views.gera_relatorio, name="gera_relatorio"),
    path("escolhe_relatorio", views.escolhe_relatorio, name="escolhe_relatorio"),
    path("imprime", views.imprime, name="imprime"),
]
