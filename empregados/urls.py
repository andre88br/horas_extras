from django.urls import path
from . import views


urlpatterns = [
    path("empregados/<int:file_id>", views.empregados, name="empregados"),
    path("importacoes_empregados", views.importacoes_empregados, name="importacoes_empregados"),
    path("deleta_mes_empregados/<int:file_id>", views.deleta_mes_empregados, name="deleta_mes_empregados"),
    path("empregado_detalhes/<int:file_id>", views.empregado_detalhes, name="empregado_detalhes"),
    path("empregados_upload", views.upload_empregados, name="empregados_upload"),
    path("deleta_empregado/<int:file_id>", views.deleta_empregado, name="deleta_empregado"),
    path("editar_empregado/<int:file_id>", views.editar_empregado, name="editar_empregado"),
    path("salvar_empregado<int:file_id>", views.salvar_empregado, name="salvar_empregado"),
    path("carga_horaria", views.carga_horaria, name="carga_horaria"),
    path("carga_detalhe/<int:file_id>", views.carga_detalhe, name="carga_detalhe"),
    path("salvar_carga", views.salvar_carga, name="salvar_carga"),
    path("deleta_carga_horaria", views.deleta_carga_horaria, name="deleta_carga_horaria"),
    path("confirma_deletar", views.confirma_deletar, name="confirma_deletar"),


]
