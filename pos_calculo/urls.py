from django.urls import path

from . import views

urlpatterns = [
    path("rejeitar_batidas", views.rejeitar_batidas, name="rejeitar_batidas"),
    path("recalcular_banco", views.recalcular_banco, name="recalcular_banco"),
    path("recalcular_negativos", views.recalcular_negativos, name="recalcular_negativos"),
    path("pagamento", views.pagamento, name="pagamento"),
    path("voltar_batidas", views.voltar_batidas, name="voltar_batidas"),
]