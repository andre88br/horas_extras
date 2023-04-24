from django.urls import path
from . import views


urlpatterns = [
    path("rejeitar_batidas", views.rejeitar_batidas, name="rejeitar_batidas"),
    path("recalcular_banco", views.recalcular_banco, name="recalcular_banco"),
]