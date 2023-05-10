from django.contrib import auth
from django.contrib.auth.models import User


def verifica_vazio(campo):
    if not campo.strip():
        return True


def autenticar(request, username, senha):
    if User.objects.filter(username=username).exists():
        nome = (
            User.objects.filter(username=username)
            .values_list("username", flat=True)
            .get()
        )
        user = auth.authenticate(request, username=nome, password=senha)
        if user is not None:
            auth.login(request, user)
            return True
