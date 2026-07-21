from django.urls import path

from . import views

urlpatterns = [
    path("login_sigp", views.login_sigp, name="login_sigp"),
    path("logout_sigp", views.logout_sigp, name="logout_sigp"),
    path("rejeitar_batidas", views.rejeitar_batidas, name="rejeitar_batidas"),
    path("recalcular_banco", views.recalcular_banco, name="recalcular_banco"),
    path("recalcular_negativos", views.recalcular_negativos, name="recalcular_negativos"),
    path("pagamento", views.pagamento, name="pagamento"),
    path("voltar_batidas", views.voltar_batidas, name="voltar_batidas"),
    path("voltar_escalas", views.voltar_escalas, name="voltar_escalas"),
    path("excluir_escalas", views.excluir_escalas, name="excluir_escalas"),

]