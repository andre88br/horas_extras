from django.urls import path
from . import views


urlpatterns = [
    path("rejeitar_batidas", views.rejeitar_batidas, name="rejeitar_batidas"),
]