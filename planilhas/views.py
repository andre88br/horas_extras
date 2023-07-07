from datetime import date

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from usuarios.utils import verifica_vazio
from .forms import DivForm, TipoForm, DateForm, SetorForm, SetForm
from .mensagens import DataLimite, ValidaResposta
from .upload import valida_upload_planilha, importa_listaempregados
from .models import *
from .valida_forms import ValidaFormDate, ValidaFormTipo, ValidaFormDivisao, ValidaFormSetor, ValidaFormSetor2


def planilha_upload(request):
    if request.user.is_authenticated:
        formTipo = TipoForm(request.POST or None)
        formDiv = DivForm(request.POST or None)
        formDiv.fields['divisao'].widget.attrs['class'] = 'divisao'
        formSetor = SetForm(request.POST or None)
        # formSetor.fields['setor2'].widget.attrs['class'] = 'adm'
        formSetor.fields['setor'].widget.attrs['class'] = 'ass'
        formDate = DateForm(request.POST)

        if request.method == "POST":
            mes, ano = ValidaFormDate(formDate)
            tipo = ValidaFormTipo(formTipo)
            divisao = ValidaFormDivisao(formDiv)
            setor = ValidaFormSetor(formSetor, divisao)
            print(setor)

            hoje = date.today()
            if mes == 12:
                maximo_c = date(ano, 1, 10)
            else:
                maximo_c = date(ano, mes + 1, 10)

            if mes == 1:
                maximo_s = date(ano, 12, 10)
            else:
                maximo_s = date(ano, mes - 1, 10)

            verifica_prazo = DataLimite(request, tipo, maximo_s, maximo_c, hoje)
            if verifica_prazo:
                return render(request, "planilhas/planilha_upload.html",
                              context={'formDiv': formDiv, 'formSetor': formSetor, 'formTipo': formTipo,
                                       'formDate': formDate})

            empregados = ListaEmpregados.objects.filter(mes=mes, ano=ano)

            if empregados:
                dados, resposta, planilhas_com_erro = valida_upload_planilha(request)
                ValidaResposta(request, resposta, dados, mes, ano, tipo, planilhas_com_erro, setor)
            else:
                if int(mes) < 10:
                    mes = f'0{mes}'
                messages.error(request, f'Nenhum empregado cadastrado para {mes}/{ano}')
                return render(
                    request,
                    "planilhas/planilha_upload.html",
                    context={'formDiv': formDiv, 'formSetor': formSetor,  'formTipo': formTipo,
                             'formDate': formDate})

        return render(request, "planilhas/planilha_upload.html",
                      context={'formDiv': formDiv, 'formSetor': formSetor,  'formTipo': formTipo,
                               'formDate': formDate})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def planilha_confirmacao(request, file_id):
    if request.user.is_authenticated:

        formDiv = DivForm(request.POST or None)
        divisao = ValidaFormDivisao(formDiv)
        formSetor = SetorForm(request.POST or None)
        if formSetor.is_valid():
            setor = ValidaFormSetor2(formSetor)
        else:
            formSetor = SetForm(request.POST or None)
            if formSetor.is_valid():
                setor = ValidaFormSetor(formSetor, divisao)
            else:
                setor = request.POST.get('setor')

        importacao = get_object_or_404(Importacoes, pk=file_id)

        if setor is not None and setor != '':
            confirmacoes_a_mostrar = PlanilhaConfirmacao. \
                objects.filter(importacao=importacao, setor=setor).all().order_by("empregado__nome")
        else:
            confirmacoes_a_mostrar = PlanilhaConfirmacao. \
                objects.filter(importacao=importacao).all().order_by("empregado__nome")

        paginator = Paginator(confirmacoes_a_mostrar, 20)
        page = request.GET.get('page')
        confirmacoes_paginadas = paginator.get_page(page)

        if request.method == 'POST':
            query = request.POST.get('q')
            if query != '' and query is not None:
                try:
                    if str(query[1]).isnumeric():
                        if setor is not None and setor != '':
                            empregado = PlanilhaConfirmacao.objects.filter(empregado__matricula__icontains=str(query).
                                                                           strip(), empregado__mes=importacao.mes,
                                                                           empregado__ano=importacao.ano,
                                                                           setor=setor).order_by("empregado__nome")
                        else:
                            empregado = PlanilhaConfirmacao.objects.filter(empregado__matricula__icontains=str(query).
                                                                           strip(), empregado__mes=importacao.mes,
                                                                           empregado__ano=importacao.ano
                                                                           ).order_by("empregado__nome")

                        if empregado:
                            return render(request,
                                          "planilhas/planilha_confirmacao.html",
                                          context={"files": empregado,
                                                   "files2": file_id, 'objetos': confirmacoes_a_mostrar,
                                                   'setor': setor, 'divisao': divisao})
                    else:
                        if setor is not None and setor != '':
                            empregado = PlanilhaConfirmacao.objects.filter(empregado__nome__icontains=str(query).strip()
                                                                           , empregado__mes=importacao.mes,
                                                                           empregado__ano=importacao.ano,
                                                                           setor=setor).order_by("empregado__nome")
                        else:
                            empregado = PlanilhaConfirmacao.objects.filter(empregado__nome__icontains=str(query).strip()
                                                                           , empregado__mes=importacao.mes,
                                                                           empregado__ano=importacao.ano,
                                                                           ).order_by("empregado__nome")

                        if empregado:
                            return render(request, "planilhas/planilha_confirmacao.html",
                                          context={"files": empregado,
                                                   "files2": file_id, 'objetos': confirmacoes_a_mostrar,
                                                   'setor': setor, 'divisao': divisao})
                except ValueError:
                    return render(request, "planilhas/planilha_confirmacao.html",
                                  context={"files": confirmacoes_paginadas,
                                           "files2": file_id, 'objetos': confirmacoes_a_mostrar,
                                           'setor': setor, 'divisao': divisao})
            if query != "" and query is not None:
                messages.error(request, "Empregado não encontrato!")

        if confirmacoes_a_mostrar:
            return render(request, "planilhas/planilha_confirmacao.html",
                          context={"files": confirmacoes_paginadas,
                                   "files2": file_id, 'objetos': confirmacoes_a_mostrar,
                                   'setor': setor, 'divisao': divisao})
        else:
            messages.error(request, 'Sem planilha importadas para o setor informado!')
            return redirect('planilha_importacoes')
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def planilha_solicitacao(request, file_id):
    if request.user.is_authenticated:

        formDiv = DivForm(request.POST or None)
        divisao = ValidaFormDivisao(formDiv)
        formSetor = SetorForm(request.POST or None)
        if formSetor.is_valid():
            setor = ValidaFormSetor2(formSetor)
        else:
            formSetor = SetForm(request.POST or None)
            if formSetor.is_valid():
                setor = ValidaFormSetor(formSetor, divisao)
            else:
                setor = request.POST.get('setor')

        importacao = get_object_or_404(Importacoes, pk=file_id)

        if setor is not None and setor != '':
            solicitacoes_a_mostrar = PlanilhaSolicitacao. \
                objects.filter(importacao=importacao, setor=setor).all().order_by("empregado__nome")
        else:
            solicitacoes_a_mostrar = PlanilhaSolicitacao. \
                objects.filter(importacao=importacao).all().order_by("empregado__nome")

        paginator = Paginator(solicitacoes_a_mostrar, 20)
        page = request.GET.get('page')
        solicitacoes_paginadas = paginator.get_page(page)

        if request.method == 'POST':
            query = request.POST.get('q')
            if query != '' and query is not None:
                try:
                    if str(query[1]).isnumeric():
                        if setor is not None and setor != '':
                            empregado = PlanilhaSolicitacao.objects.filter(
                                empregado__matricula__icontains=str(query).strip(),
                                empregado__mes=importacao.mes,
                                empregado__ano=importacao.ano,
                                setor=setor).order_by("empregado__nome")
                        else:
                            empregado = PlanilhaSolicitacao.objects.filter(
                                empregado__matricula__icontains=str(query).strip(), empregado__mes=importacao.mes,
                                empregado__ano=importacao.ano).order_by("empregado__nome")

                        if empregado:
                            return render(request,
                                          "planilhas/planilha_solicitacao.html",
                                          context={"files": empregado,
                                                   "files2": file_id, 'objetos': solicitacoes_a_mostrar,
                                                   'setor': setor, 'divisao': divisao})
                    else:
                        if setor is not None and setor != '':
                            empregado = PlanilhaSolicitacao.objects.filter(empregado__nome__icontains=str(query).strip()
                                                                           , empregado__mes=importacao.mes,
                                                                           empregado__ano=importacao.ano,
                                                                           setor=setor).order_by("empregado__nome")
                        else:
                            empregado = PlanilhaSolicitacao.objects.filter(empregado__nome__icontains=str(query).strip()
                                                                           , empregado__mes=importacao.mes,
                                                                           empregado__ano=importacao.ano
                                                                           ).order_by("empregado__nome")
                        if empregado:
                            return render(request, "planilhas/planilha_solicitacao.html",
                                          context={"files": empregado,
                                                   "files2": file_id, 'objetos': solicitacoes_a_mostrar,
                                                   'setor': setor, 'divisao': divisao})
                except ValueError:
                    return render(request, "planilhas/planilha_solicitacao.html",
                                  context={"files": solicitacoes_paginadas,
                                           "files2": file_id, 'objetos': solicitacoes_a_mostrar,
                                           'setor': setor, 'divisao': divisao})
            if query != "" and query is not None:
                messages.error(request, "Empregado não encontrato!")

        if solicitacoes_a_mostrar:
            return render(request, "planilhas/planilha_solicitacao.html",
                          context={"files": solicitacoes_paginadas,
                                   "files2": file_id, 'objetos': solicitacoes_a_mostrar,
                                   'setor': setor, 'divisao': divisao})
        else:
            messages.error(request, 'Sem planilha importadas para o setor informado!')
            return redirect('planilha_importacoes')
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def planilha_importacoes(request):
    if request.user.is_authenticated:
        formSetor = SetorForm(request.POST or None)
        formSetor.fields['setor'].widget.attrs['class'] = 'ass'

        solicitacoes_a_mostar = Importacoes.objects.filter(tipo='PlanilhaSolicitação').order_by("-ano", "mes").all()
        paginator = Paginator(solicitacoes_a_mostar, 2)
        page = request.GET.get('page')
        solicitacoes_paginadas = paginator.get_page(page)

        confirmacoes_a_mostar = Importacoes.objects.filter(tipo='PlanilhaConfirmação').order_by("-ano", "mes").all()
        paginator = Paginator(confirmacoes_a_mostar, 2)
        page = request.GET.get('page')
        confirmacoes_paginadas = paginator.get_page(page)

        return render(request, "planilhas/planilha_importacoes.html", context={
            'files': confirmacoes_paginadas, 'files2': solicitacoes_paginadas, 'formSetor': formSetor})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def relatorios_planilhas(request):
    if request.user.is_authenticated:
        return render(request, "planilhas/relatorios_planilhas.html")
    else:
        return render(request, "usuarios/login.html")


def usuarios_planilhas(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            users = User.objects.exclude(id=request.user.id).order_by("id").values()
            return render(request, "planilhas/usuarios_planilhas.html", context={"usuarios": users})
        else:
            users = ''
            return render(request, "planilhas/usuarios_planilhas.html", context={"usuarios": users})
    else:
        return render(request, "usuarios/login.html")


def editar_usuario_planilha(request, usuario):
    if request.user.is_authenticated:
        user = get_object_or_404(User, pk=usuario)
        contexto = {"usuario": user}
        return render(request, "planilhas/editar_usuario_planilha.html", contexto)
    else:
        return render(request, "usuarios/login.html")


def salvar_usuario_planilha(request, usuario_id):
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
                return redirect("usuarios_planilha")

            if f"{user.first_name} {user.last_name}" != dados["nome"]:
                if verifica_vazio(dados["nome"]):
                    messages.error(request, "O campo nome não pode ser vazio!")
                    return redirect("editar_usuario_planilha", user.id)
                user.first_name = str(dados["nome"]).split(" ")[0]
                sobrenome = ""
                for i in str(dados["nome"]).split(" ")[1:]:
                    sobrenome += i + " "
                user.last_name = sobrenome
            if user.username != dados["usuario"]:
                if verifica_vazio(dados["usuario"]):
                    messages.error(request, "O campo Usuário não pode ser vazio!")
                    return redirect("editar_usuario_planilha", user.id)
                if User.objects.filter(username=dados["usuario"]).exclude(id=user.id).exists():
                    messages.error(request, "Usuário já cadastrado!")
                    return redirect("editar_usuario_planilha", user.id)
                user.username = dados["usuario"]
            if user.username != dados["email"]:
                if verifica_vazio(dados["email"]):
                    messages.error(request, "O campo E-mail não pode ser vazio!")
                    return redirect("editar_usuario", user.id)
                if User.objects.filter(username=dados["email"]).exclude(id=user.id).exists():
                    messages.error(request, "E-mail já cadastrado!")
                    return redirect("editar_usuario_planilha", user.id)
                user.email = dados["email"]
            if dados["senha"] != '':
                user.set_password(dados["senha"])
            if administrador == 'on':
                user.is_superuser = True
            else:
                user.is_superuser = False
            user.save()

            messages.success(request, "Cadastro atualizado com sucesso!")
            return redirect("usuarios_planilha")
        return render(request, "planilhas/usuarios_planilha.html")
    else:
        return render(request, "usuarios/login.html")


def listaempregados_upload(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            resposta = importa_listaempregados(request)

            if resposta == 'Erro':
                messages.error(request, "Arquivo inválido")
                return render(
                    request,
                    "planilhas/listaempregados_upload.html",
                    context={"files": ListaEmpregados.objects.order_by("matricula").all()},
                )

            if resposta == "dados_invalidos":
                messages.error(request, "Dados inválidos")
                return render(
                    request,
                    "planilhas/listaempregados_upload.html",
                    context={"files": ListaEmpregados.objects.order_by("matricula").all()},
                )
            elif resposta == "arquivo_vazio":
                messages.error(request, "Arquivo não pode ser vazio!")
                return render(
                    request,
                    "planilhas/listaempregados_upload.html",
                    context={"files": ListaEmpregados.objects.order_by("matricula").all()},
                )
            else:
                messages.success(request, "Empregados cadastrados com sucesso!")
                return render(
                    request,
                    "planilhas/listaempregados_upload.html",
                    context={"files": ListaEmpregados.objects.order_by("matricula").all()},
                )
        else:
            return render(
                request,
                "planilhas/listaempregados_upload.html",
                context={"files": ListaEmpregados.objects.order_by("matricula").all()},
            )
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def listaempregados(request, file_id):
    if request.user.is_authenticated:
        file = get_object_or_404(Importacoes, pk=file_id)
        mes = file.mes
        ano = file.ano
        empregados_a_mostrar = ListaEmpregados.objects.filter(mes=mes, ano=ano).all().order_by('nome')
        paginator = Paginator(empregados_a_mostrar, 20)
        page = request.GET.get('page')
        empregados_paginados = paginator.get_page(page)
        try:
            if request.method == 'GET':

                query = request.GET.get('q')
                if query != '':
                    if str(query).isnumeric():
                        empregado = ListaEmpregados.objects.filter(matricula=query, mes=mes, ano=ano).order_by("nome")
                        if empregado:
                            return render(
                                request,
                                "planillhas/listaempregados.html",
                                context={"files": empregado, "mes": mes, "ano": ano,
                                         "files2": file_id})
                    else:
                        empregado = ListaEmpregados.objects.filter(nome__icontains=query, mes=mes, ano=ano). \
                            order_by("nome")
                        if empregado:
                            return render(
                                request,
                                "planilhas/listaempregados.html",
                                context={"files": empregado, "mes": mes, "ano": ano,
                                         "files2": file_id})
                if query != "":
                    messages.error(request, "Empregado não encontrato!")
        except ValueError:
            return render(
                request,
                "planilhas/listaempregados.html",
                context={"files": empregados_paginados, "mes": mes, "ano": ano,
                         "files2": file_id})
        return render(
            request,
            "planilhas/listaempregados.html",
            context={"files": empregados_paginados, "mes": mes, "ano": ano,
                     "files2": file_id})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def importacoes_listaempregados(request):
    if request.user.is_authenticated:
        empregados_lista = Importacoes.objects.filter(tipo='listaempregados').all().order_by("-ano", "mes")
        if len(empregados_lista) == 0:
            messages.error(request, "Sem empregados cadastrados")
        return render(request, "planilhas/importacoes_listaempregados.html",
                      context={"files": empregados_lista.order_by("-ano", "mes"),
                               'file_id': 1})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")
