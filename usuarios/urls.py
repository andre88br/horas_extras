from django.urls import path

from . import views

urlpatterns = [
    path("cadastro", views.cadastro, name="cadastro"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("", views.usuarios, name="usuarios"),
    path("deleta_usuario/<int:usuario>", views.deleta_usuario, name="deleta_usuario"),
    path("desativa_usuario/<int:usuario>", views.desativa_usuario, name="desativa_usuario"),
    path("ativa_usuario/<int:usuario>", views.ativa_usuario, name="ativa_usuario"),
    path("editar_usuario/<int:usuario>", views.editar_usuario, name="editar_usuario"),
    path("salvar_usuario/<int:usuario_id>", views.salvar_usuario, name="salvar_usuario"),
    path("retorna_total_pago", views.retorna_total_pago, name="retorna_total_pago"),
    path("relatorio_pagas", views.relatorio_pagas, name="relatorio_pagas"),
    path("grafico_solicitadas", views.grafico_solicitadas, name="grafico_solicitadas"),
    path("retorna_total_solicitado", views.retorna_total_solicitado, name="retorna_total_solicitado"),
    path("retorna_diferenca", views.retorna_diferenca, name="retorna_diferenca"),

]
