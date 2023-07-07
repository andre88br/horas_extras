from django.urls import path

from . import views

urlpatterns = [
    path("planilha_upload", views.planilha_upload, name="planilha_upload"),
    path("planilha_confirmacao/<int:file_id>", views.planilha_confirmacao, name="planilha_confirmacao"),
    path("planilha_solicitacao/<int:file_id>", views.planilha_solicitacao, name="planilha_solicitacao"),
    path("planilha_importacoes/<int:file_id>", views.planilha_importacoes, name="planilha_importacoes"),
    path("relatorios_planilhas", views.relatorios_planilhas, name="relatorios_planilhas"),
    path("usuarios_planilhas", views.usuarios_planilhas, name="usuarios_planilhas"),
    path("editar_usuario_planilha/<int:usuario>", views.editar_usuario_planilha, name="editar_usuario_planilha"),
    path("salvar_usuario_planilha/<int:usuario_id>", views.salvar_usuario_planilha, name="salvar_usuario_planilha"),
    path("importacoes_listaempregados", views.importacoes_listaempregados, name="importacoes_listaempregados"),
    path("listaempregados/<int:file_id>", views.listaempregados, name="listaempregados"),
    path("listaempregados_upload", views.listaempregados_upload, name="listaempregados_upload"),
    path("planilha_importacoes", views.planilha_importacoes, name="planilha_importacoes"),

]
