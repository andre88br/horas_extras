from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from numpy import nan
import locale
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User

from relatorios.models import RelatorioPagas, RelatorioSolicitacao
from .forms import YearForm
from .models import AnoSelecionado
from .utils import verifica_vazio, autenticar
from django.contrib import auth, messages

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


def cadastro(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            nome = request.POST["nome"]
            nome_completo = str(nome).split(' ')
            sobrenome = ''
            for i in nome_completo[1:]:
                sobrenome += i + ' '

            username = request.POST["user"]
            senha = request.POST["senha"]
            email = request.POST["email"]
            administrador = request.POST.get('adm')

            if verifica_vazio(nome) or verifica_vazio(username) or verifica_vazio(senha) or verifica_vazio(email):
                messages.error(request, "Todos os campos devem ser preenchidos!")
                return redirect("cadastro")
            if (User.objects.filter(username=username).exists()
                    or (User.objects.filter(first_name=nome_completo[0]).exists()
                        and User.objects.filter(last_name=sobrenome).exists())
                    or User.objects.filter(email=email).exists()):
                messages.error(request, "Usuário já cadastrado!")
                return redirect("cadastro")

            if administrador == 'on':
                user = User.objects.create_user(username=username, first_name=nome_completo[0], last_name=sobrenome,
                                                email=email, password=senha, is_superuser=True)
            else:
                user = User.objects.create_user(username=username, first_name=nome_completo[0], last_name=sobrenome,
                                                email=email, password=senha, is_superuser=False)
            user.save()
            messages.success(request, "Cadastro criado com sucesso!")

            users = User.objects.order_by("id").values()
            return render(request, "usuarios/usuarios.html", context={"usuarios": users})
        else:
            return render(request, "usuarios/cadastro.html")
    else:
        return render(request, "usuarios/login.html")


def login(request):
    if request.method == "POST":
        user = request.POST["user"]
        senha = request.POST["senha"]

        if verifica_vazio(user) or verifica_vazio(senha):
            messages.error(request, "Nome e/ou senha não pode ser vazio")
            return redirect("login")
        if autenticar(request, user, senha):
            return redirect("dashboard")
        else:
            messages.error(request, "Usuário e/ou senha inválidos!")
    return render(request, "usuarios/login.html")


def dashboard(request):
    if request.user.is_authenticated:
        current_year = datetime.now().year
        if request.user.is_authenticated:
            form = YearForm(request.POST or None)
            if form.is_valid():
                selected_year = form.cleaned_data['year']
                form.initial['year'] = selected_year
            else:
                selected_year = current_year

            try:
                ano = AnoSelecionado.objects.update_or_create(id=1, defaults={'ano': selected_year})
            except ObjectDoesNotExist:
                ano = current_year

            return render(request, "dashboard.html",
                          context={'form': form, 'selected_year': selected_year,
                                   'current_year': current_year})
        else:
            return render(request, "usuarios/login.html")
    else:
        return render(request, "usuarios/login.html")


def logout(request):
    auth.logout(request)
    messages.success(request, "Logout efetuado com sucesso!")
    return render(request, "usuarios/login.html")


def usuarios(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            users = User.objects.exclude(id=request.user.id).order_by("id").values()
            return render(request, "usuarios/usuarios.html", context={"usuarios": users})
        else:
            users = ''
            return render(request, "usuarios/usuarios.html", context={"usuarios": users})
    else:
        return render(request, "usuarios/login.html")


def desativa_usuario(request, usuario):
    if request.user.is_authenticated:
        user = get_object_or_404(User, pk=usuario)
        if request.user.username != user.username:
            user.is_active = False
            user.save()
            return redirect("usuarios")
        else:
            messages.error(request, "Você não pode desativar seu próprio usuário!")
            return redirect("usuarios")
    else:
        return render(request, "usuarios/login.html")


def deleta_usuario(request, usuario):
    if request.user.is_authenticated:
        user = get_object_or_404(User, pk=usuario)
        if request.user.username != user.username:
            user.delete()
            return redirect("usuarios")
        else:
            messages.error(request, "Você não pode remover seu próprio usuário!")
            return redirect("usuarios")
    else:
        return render(request, "usuarios/login.html")


def ativa_usuario(request, usuario):
    if request.user.is_authenticated:
        user = get_object_or_404(User, pk=usuario)
        user.is_active = True
        user.save()
        return redirect("usuarios")
    else:
        return render(request, "usuarios/login.html")


def editar_usuario(request, usuario):
    if request.user.is_authenticated:
        user = get_object_or_404(User, pk=usuario)
        contexto = {"usuario": user}
        return render(request, "usuarios/editar_usuario.html", contexto)
    else:
        return render(request, "usuarios/login.html")


def salvar_usuario(request, usuario_id):
    if request.user.is_authenticated:
        if request.method == "POST":
            dados = request.POST
            administrador = request.POST.get('adm')
            user = User.objects.get(pk=usuario_id)
            print(user)
            if (f"{user.first_name} {user.last_name}" == dados["nome"] and
                    user.username == dados["usuario"] and
                    user.email == dados["email"] and
                    ((user.is_superuser is True and administrador == 'on')
                     or (user.is_superuser is False and administrador is None)) and
                    dados["senha"] == ''):
                messages.error(request, "Nenhum dado foi alterado!")
                return redirect("usuarios")

            if f"{user.first_name} {user.last_name}" != dados["nome"]:
                if verifica_vazio(dados["nome"]):
                    messages.error(request, "O campo nome não pode ser vazio!")
                    return redirect("editar_usuario", user.id)
                user.first_name = str(dados["nome"]).split(" ")[0]
                sobrenome = ""
                for i in str(dados["nome"]).split(" ")[1:]:
                    sobrenome += i + " "
                user.last_name = sobrenome
            if user.username != dados["usuario"]:
                if verifica_vazio(dados["usuario"]):
                    messages.error(request, "O campo Usuário não pode ser vazio!")
                    return redirect("editar_usuario", user.id)
                if User.objects.filter(username=dados["usuario"]).exclude(id=user.id).exists():
                    messages.error(request, "Usuário já cadastrado!")
                    return redirect("editar_usuario", user.id)
                user.username = dados["usuario"]
            if user.username != dados["email"]:
                if verifica_vazio(dados["email"]):
                    messages.error(request, "O campo E-mail não pode ser vazio!")
                    return redirect("editar_usuario", user.id)
                if User.objects.filter(username=dados["email"]).exclude(id=user.id).exists():
                    messages.error(request, "E-mail já cadastrado!")
                    return redirect("editar_usuario", user.id)
                user.email = dados["email"]
            if dados["senha"] != '':
                user.set_password(dados["senha"])
            if administrador == 'on':
                user.is_superuser = True
            else:
                user.is_superuser = False
            user.save()

            messages.success(request, "Cadastro atualizado com sucesso!")
            return redirect("usuarios")
        return render(request, "usuarios/usuarios.html")
    else:
        return render(request, "usuarios/login.html")


def retorna_total_pago(request):
    if request.user.is_authenticated:
        try:
            ano = AnoSelecionado.objects.filter(id=1).all()
            ano = ano[0].ano
        except ObjectDoesNotExist:
            ano = datetime.now().year

        if ano == '' or ano is None:
            ano = datetime.now().year

        if ano == 2022:
            total = 905755.76 + 740606.89 + 543553.11 + 603047.47 + 446365.14 + 320282.66 + \
                    343118.75 + 307727.57 + 478808.77 + 570533.39 + 592951.77 + 381670.39

            total = locale.currency(total, symbol=False, grouping=True)
            if request.method == "GET":
                return JsonResponse({'total': total})
        if ano == 2023:
            total = RelatorioPagas.objects.filter(importacao__ano=ano, importacao__mes__gt=1
                                                  ).all().aggregate(Sum('total'))['total__sum']
            total_janeiro = 509532.76
            if total is not None:
                total = locale.currency((total + total_janeiro), symbol=False, grouping=True)
            else:
                total = locale.currency(total_janeiro, symbol=False, grouping=True)
            if request.method == "GET":
                return JsonResponse({'total': total})
        else:
            total = RelatorioPagas.objects.filter(importacao__ano=ano
                                                  ).all().aggregate(Sum('total'))['total__sum']
            total = locale.currency(total, symbol=False, grouping=True)
            if request.method == "GET":
                return JsonResponse({'total': total})
    else:
        return render(request, "usuarios/login.html")


def retorna_total_solicitado(request):
    if request.user.is_authenticated:
        try:
            ano = AnoSelecionado.objects.filter(id=1).all()
            ano = ano[0].ano
        except ObjectDoesNotExist:
            ano = datetime.now().year

        if ano == '' or ano is None:
            ano = datetime.now().year

        total2 = 0

        if ano == 2022:
            ano2022 = [940373.36, 700367.41, 920646.37, 868864.26, 832045.15, 819976.40,
                       644252.04, 684999.78, 724084.88, 759081.57, 633637.60, 600704.14]
            total = locale.currency(sum(ano2022), symbol=False, grouping=True)
        elif ano == 2023:
            total2 = 563062.37 + 477583.13 + 453645.18 + 502795.78
            total3 = RelatorioSolicitacao.objects.filter(~Q(valor_total=nan), importacao__ano=datetime.now().year,
                                                         saldo_banco_decimal__gte=0, importacao__mes__gt=4
                                                         ).all().aggregate(Sum('valor_total'))['valor_total__sum']
            if total3 is None:
                total3 = 0
            total = locale.currency(total2 + total3, symbol=False, grouping=True)
        else:
            total3 = RelatorioSolicitacao.objects.filter(~Q(valor_total=nan), importacao__ano=datetime.now().year,
                                                         saldo_banco_decimal__gte=0
                                                         ).all().aggregate(Sum('valor_total'))['valor_total__sum']
            if total3 is None:
                total3 = 0
            total = locale.currency(total2 + total3, symbol=False, grouping=True)

        if request.method == "GET":
            return JsonResponse({'total': total})
    else:
        return render(request, "usuarios/login.html")


def retorna_diferenca(request):
    if request.user.is_authenticated:
        try:
            ano = AnoSelecionado.objects.filter(id=1).all()
            ano = ano[0].ano
        except ObjectDoesNotExist:
            ano = datetime.now().year

        if ano == '' or ano is None:
            ano = datetime.now().year

        if ano == 2022:
            pago = 6234421.67
            solicitado = 9129032.96
            total = locale.currency(solicitado - pago, symbol=False, grouping=True)
        elif ano == 2023:
            pago_janeiro = 509532.76
            pago1 = RelatorioPagas.objects.filter(importacao__ano=ano, importacao__mes__gt=1
                                                  ).all().aggregate(Sum('total'))['total__sum']
            pago = pago1 + pago_janeiro if pago1 is not None else pago_janeiro

            solicitado1 = 563062.37 + 477583.13 + 453645.18 + 502795.78
            solicitado2 = RelatorioSolicitacao.objects.filter(~Q(valor_total=nan), importacao__ano=ano,
                                                              saldo_banco_decimal__gte=0, importacao__mes__gt=4
                                                              ).all().aggregate(Sum('valor_total'))['valor_total__sum']
            solicitado = solicitado1 + solicitado2 if solicitado2 is not None else solicitado1
            total = locale.currency(solicitado - pago, symbol=False, grouping=True)

        else:
            pago = RelatorioPagas.objects.filter(importacao__ano=ano
                                                 ).all().aggregate(Sum('total'))['total__sum']
            solicitado = RelatorioSolicitacao.objects.filter(~Q(valor_total=nan), importacao__ano=ano,
                                                             saldo_banco_decimal__gte=0,
                                                             ).all().aggregate(Sum('valor_total'))['valor_total__sum']
            total = locale.currency(solicitado - pago, symbol=False, grouping=True)

        if request.method == "GET":
            return JsonResponse({'total': total})
    else:
        return render(request, "usuarios/login.html")


def relatorio_pagas(request):
    if request.user.is_authenticated:
        ano2022 = [905755.76, 740606.89, 543553.11, 603047.47, 446365.14, 320282.66,
                   343118.75, 307727.57, 478808.77, 570533.39, 592951.77, 381670.39]

        x = RelatorioPagas.objects.all()
        meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
        data = []
        labels = []
        mes = 1
        try:
            ano = AnoSelecionado.objects.filter(id=1).all()
            ano = ano[0].ano
        except ObjectDoesNotExist:
            ano = datetime.now().year

        if ano == '' or ano is None:
            ano = datetime.now().year

        if ano == 2022:
            for i in range(12):
                y = ano2022[mes - 1]
                labels.append(meses[mes - 1])
                data.append(round(y, ndigits=2))
                mes += 1
        elif ano == 2023:
            for i in range(12):
                if mes == 1:
                    valor = 509532.76
                    labels.append(meses[mes - 1])
                    data.append(round(valor, ndigits=2))
                else:
                    y = sum([i.total for i in x if i.importacao.mes == mes and i.importacao.ano == ano])
                    labels.append(meses[mes - 1])
                    data.append(round(y, ndigits=2))
                mes += 1
        else:
            for i in range(12):
                y = sum([i.total for i in x if i.importacao.mes == mes and i.importacao.ano == ano])
                labels.append(meses[mes - 1])
                data.append(round(y, ndigits=2))
            mes += 1

        data_json = {'data': data[::1], 'labels': labels[::1]}

        return JsonResponse(data_json)
    else:
        return render(request, "usuarios/login.html")


def grafico_solicitadas(request):
    if request.user.is_authenticated:
        ano2022 = [940373.36, 700367.41, 920646.37, 868864.26, 832045.15, 819976.40,
                   644252.04, 684999.78, 724084.88, 759081.57, 633637.60, 600704.14]
        x = RelatorioSolicitacao.objects.filter(~Q(valor_total=nan), saldo_banco_decimal__gte=0).all()
        meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
        data = []
        labels = []
        mes = 1
        try:
            ano = AnoSelecionado.objects.filter(id=1).all()
            ano = ano[0].ano
        except ObjectDoesNotExist:
            ano = datetime.now().year

        if ano == '' or ano is None:
            ano = datetime.now().year

        if ano == 2022:
            for i in range(12):
                y = ano2022[mes - 1]
                labels.append(meses[mes - 1])
                data.append(round(y, ndigits=2))
                mes += 1
        elif ano == 2023:
            for i in range(12):
                if mes <= 4:
                    ate_abril = [563062.37, 477583.13, 453645.18, 502795.78]
                    y2 = ate_abril[mes - 1]
                    labels.append(meses[mes - 1])
                    data.append(round(y2, ndigits=2))
                else:
                    y = sum([i.valor_total for i in x if i.importacao.mes == mes and i.importacao.ano == ano])
                    labels.append(meses[mes - 1])
                    data.append(round(y, ndigits=2))
                mes += 1
        else:
            for i in range(12):
                y = sum([i.valor_total for i in x if i.importacao.mes == mes and i.importacao.ano == ano])
                labels.append(meses[mes - 1])
                data.append(round(y, ndigits=2))
                mes += 1

        data_json = {'data': data[::1], 'labels': labels[::1]}

        return JsonResponse(data_json)
    else:
        return render(request, "usuarios/login.html")
