from django.urls import path

from . import views

urlpatterns = [
    path("<uuid:tarefa_id>/", views.acompanhar, name="tarefa_acompanhar"),
    path("<uuid:tarefa_id>/status/", views.status_json, name="tarefa_status"),
    path("<uuid:tarefa_id>/resultado/", views.resultado, name="tarefa_resultado"),
]
