import pandas as pd
from django.core.paginator import Paginator
import json

from empregados.dbchanges import salva_carga_horaria
from empregados.models import Empregado, CargaHoraria
from empregados.upload import importa_empregados

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from empregados.models import Importacoes
from horas_extras.models import BancoMes, BancoTotal, Frequencia, Confirmacao, Solicitacao
from relatorios.models import RelatorioPagas
from usuarios.utils import verifica_vazio


def upload_empregados(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            resposta = importa_empregados(request)

            if resposta == 'Erro':
                messages.error(request, "Arquivo inválido")
                return render(
                    request,
                    "empregados/empregados_upload.html",
                    context={"files": Empregado.objects.order_by("matricula").all()},
                )

            if resposta == "dados_invalidos":
                messages.error(request, "Dados inválidos")
                return render(
                    request,
                    "empregados/empregados_upload.html",
                    context={"files": Empregado.objects.order_by("matricula").all()},
                )
            elif resposta == "arquivo_vazio":
                messages.error(request, "Arquivo não pode ser vazio!")
                return render(
                    request,
                    "empregados/empregados_upload.html",
                    context={"files": Empregado.objects.order_by("matricula").all()},
                )
            else:
                messages.success(request, "Empregados cadastrados com sucesso!")
                return render(
                    request,
                    "empregados/empregados_upload.html",
                    context={"files": Empregado.objects.order_by("matricula").all()},
                )
        else:
            return render(
                request,
                "empregados/empregados_upload.html",
                context={"files": Empregado.objects.order_by("matricula").all()},
            )
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def empregados(request, file_id):
    if request.user.is_authenticated:
        file = get_object_or_404(Importacoes, pk=file_id)
        mes = file.mes
        ano = file.ano
        empregados_a_mostrar = Empregado.objects.filter(mes=mes, ano=ano).all().order_by('nome')
        paginator = Paginator(empregados_a_mostrar, 20)
        page = request.GET.get('page')
        empregados_paginados = paginator.get_page(page)
        try:
            if request.method == 'GET':

                query = request.GET.get('q')
                if query != '':
                    if str(query).isnumeric():
                        empregado = Empregado.objects.filter(matricula=query, mes=mes, ano=ano).order_by("nome")
                        if empregado:
                            return render(
                                request,
                                "empregados/empregados.html",
                                context={"files": empregado, "mes": mes, "ano": ano,
                                         "files2": file_id})
                    else:
                        empregado = Empregado.objects.filter(nome__icontains=query, mes=mes, ano=ano). \
                            order_by("nome")
                        if empregado:
                            return render(
                                request,
                                "empregados/empregados.html",
                                context={"files": empregado, "mes": mes, "ano": ano,
                                         "files2": file_id})
                if query != "":
                    messages.error(request, "Empregado não encontrato!")
        except ValueError:
            return render(
                request,
                "empregados/empregados.html",
                context={"files": empregados_paginados, "mes": mes, "ano": ano,
                         "files2": file_id})
        return render(
            request,
            "empregados/empregados.html",
            context={"files": empregados_paginados, "mes": mes, "ano": ano,
                     "files2": file_id})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def empregado_detalhes(request, file_id):
    if request.user.is_authenticated:
        empregado = get_object_or_404(Empregado, id=file_id)
        return render(
            request,
            "empregados/empregados.html",
            context={"empregado": empregado})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def deleta_empregado(request, file_id):
    files2 = request.POST.get("files2")
    file = Importacoes.objects.filter(id=files2).values()
    file = pd.DataFrame(file)
    empregados_a_mostrar = Empregado.objects.filter(mes=file.mes, ano=file.ano).all().order_by('nome')
    paginator = Paginator(empregados_a_mostrar, 20)
    page = request.GET.get('page')
    empregados_paginados = paginator.get_page(page)
    if request.user.is_authenticated:
        empregado = get_object_or_404(Empregado, pk=file_id)
        pagas = RelatorioPagas.objects.filter(empregado__mes=empregado.mes, empregado__ano=empregado.ano,
                                              empregado_id=file_id)
        mes = empregado.mes
        if empregado.mes < 10:
            mes = f'0{empregado.mes}'
        if pagas:
            messages.error(request, f'Exclusão não permitida. Horas extras do mês'
                                    f' {mes}/{empregado.ano} já foram processadas!')
            return render(request, 'empregados/empregados.html', context={'files': empregados_paginados,
                                                                          'files2': files2})
        else:
            empregado.delete()
            deletar = [CargaHoraria.objects.filter(empregado_id=file_id),
                       BancoMes.objects.filter(empregado_id=file_id),
                       BancoTotal.objects.filter(empregado_id=file_id),
                       Frequencia.objects.filter(empregado_id=file_id),
                       Confirmacao.objects.filter(empregado_id=file_id),
                       Solicitacao.objects.filter(empregado_id=file_id)]
            for i in deletar:
                i.delete()

        messages.success(request, "Empregado deletado com sucesso!")
        return render(request, 'empregados/empregados.html', context={'files': empregados_paginados,
                                                                      'files2': files2})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def editar_empregado(request, file_id):
    if request.user.is_authenticated:
        empregado = get_object_or_404(Empregado, id=file_id)
        contexto = {"empregado": empregado, 'files2': empregado.importacao.id}
        return render(request, "empregados/editar_empregado.html", contexto)
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def salvar_empregado(request, file_id):
    if request.user.is_authenticated:
        files2 = request.POST.get("files2")
        file = get_object_or_404(Importacoes, pk=files2)
        mes = file.mes
        ano = file.ano
        empregados_a_mostrar = Empregado.objects.filter(mes=mes, ano=ano).all().order_by('nome')
        paginator = Paginator(empregados_a_mostrar, 20)
        page = request.GET.get('page')
        empregados_paginados = paginator.get_page(page)
        if request.method == "POST":
            dados = request.POST
            empregado = Empregado.objects.get(id=file_id)
            if empregado.nome == dados["nome"] \
                    and empregado.salario == dados["salario"] \
                    and empregado.insalubridade == dados["insalubridade"]:
                messages.error(request, "Nenhum dado foi alterado!")
                return redirect("empregados")
            if empregado.nome != dados["nome"]:
                if verifica_vazio(dados["nome"]):
                    messages.error(request, "O campo nome não pode ser vazio!")
                    return redirect("editar_empregado", empregado.matricula)
                empregado.nome = dados["nome"]

            empregado.salario = float(str(dados.get("salario")).replace(',', '.'))
            empregado.insalubridade = float(str(dados.get("insalubridade")).replace(',', '.'))

            empregado.save()
            messages.success(request, "Cadastro atualizado com sucesso!")
            return render(
                request,
                "empregados/empregados.html",
                context={"files": empregados_paginados, "mes": mes, "ano": ano,
                         "files2": files2})
        return render(
            request,
            "empregados/empregados.html",
            context={"files": empregados_paginados, "mes": mes, "ano": ano,
                     "files2": files2})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def carga_detalhe(request, file_id):
    if request.user.is_authenticated:
        cargas = get_object_or_404(Importacoes, pk=file_id)
        carga_a_mostrar = CargaHoraria.objects.filter(importacao=cargas, carga_horaria__gt=0).order_by('nome')
        paginator = Paginator(carga_a_mostrar, 20)
        page = request.GET.get('page')
        carga_paginada = paginator.get_page(page)
        try:
            if request.method == 'GET':

                query = request.GET.get('q')
                if query != '':
                    if str(query).isnumeric():
                        empregado = CargaHoraria.objects.filter(empregado__matricula=query, empregado__mes=cargas.mes,
                                                                empregado__ano=cargas.ano,
                                                                carga_horaria__gt=0).order_by("nome")
                        if empregado:
                            return render(
                                request,
                                "empregados/carga_detalhe.html",
                                context={"files": empregado,
                                         "files2": file_id})
                    else:
                        empregado = CargaHoraria.objects.filter(nome__icontains=query, empregado__mes=cargas.mes,
                                                                empregado__ano=cargas.ano,
                                                                carga_horaria__gt=0).order_by("nome")
                        if empregado:
                            return render(
                                request,
                                "empregados/carga_detalhe.html",
                                context={"files": empregado,
                                         "files2": file_id})
                if query != "":
                    messages.error(request, "Empregado não encontrato!")
        except ValueError:
            return render(
                request,
                "empregados/carga_detalhe.html",
                context={"files": carga_paginada,
                         "files2": file_id})
        return render(
            request,
            "empregados/carga_detalhe.html",
            context={"files": carga_paginada,
                     "files2": file_id})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def carga_horaria(request):
    if request.user.is_authenticated:
        mostrar = Importacoes.objects.filter(tipo='carga_horaria').order_by('-ano', "-mes")
        if not mostrar:
            messages.error(request, 'Sem carga horária cadastrada!')
        return render(request, "empregados/carga_horaria.html", context={'files': mostrar})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def salvar_carga(request):
    if request.user.is_authenticated:
        dados = json.loads(request.POST.get('dados'))
        mes = dados['mes']
        ano = dados['ano']
        salva_carga_horaria(dados, mes, ano, request.user)
        cargas_mostrar = CargaHoraria.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                     carga_horaria__gt=0).order_by('-nome')
        paginator = Paginator(cargas_mostrar, 20)
        page = request.GET.get('page')
        carga_paginada = paginator.get_page(page)
        file_id = dados['file_id']
        return render(request, "horas_extras/banco_mes.html",
                      context={"files": carga_paginada, "mes": mes, "ano": ano, "files2": file_id})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def deleta_carga_horaria(request):
    if request.user.is_authenticated:
        dados = json.loads(request.POST.get('dados'))
        file_id = int(dados['file_id'])
        cargas = get_object_or_404(Importacoes, pk=file_id)
        pagas = Importacoes.objects.filter(mes=cargas.empregado.mes, ano=cargas.empregado.ano,
                                           tipo='rel_pagas')
        if pagas:
            messages.error(request, f'Exclusão não permitida. Horas extras do mês '
                                    f'{cargas.empregado.mes}/{cargas.empregado.ano} já foram processadas!')
            return render(request, 'empregados/carga_horaria.html')
        cargas.delete()
        carga_horaria_lista = Importacoes.objects.filter(tipo='carga_horaria').all()
        if len(carga_horaria_lista) == 0 or len(carga_horaria_lista) == 0:
            messages.error(request, "Sem carga horária importada")
        return render(request, "empregados/carga_horaria.html",
                      context={"files": carga_horaria_lista.order_by("-ano", "-mes"),
                               'file_id': 1})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def importacoes_empregados(request):
    if request.user.is_authenticated:
        empregados_lista = Importacoes.objects.filter(tipo='empregados').all()
        if len(empregados_lista) == 0:
            messages.error(request, "Sem empregados cadastrados")
        return render(request, "empregados/importacoes.html",
                      context={"files": empregados_lista.order_by("-ano", "-mes"),
                               'file_id': 1})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def deleta_mes_empregados(request, file_id):
    if request.user.is_authenticated:
        empregados_a_deletar = get_object_or_404(Importacoes, pk=file_id)
        pagas = Importacoes.objects.filter(mes=empregados_a_deletar.mes, ano=empregados_a_deletar.ano,
                                           tipo='rel_pagas')
        if pagas:
            empregados_a_mostar = Importacoes.objects.filter(tipo='empregados').order_by("-ano", "-mes").all()
            if not empregados_a_mostar:
                messages.error(request, "Sem empregados cadastrados!")
            paginator = Paginator(empregados_a_mostar, 5)
            page = request.GET.get('page')
            empregados_paginados = paginator.get_page(page)
            mes = empregados_a_deletar.mes
            if empregados_a_deletar.mes < 10:
                mes = f"0{empregados_a_deletar.mes}"

            messages.error(request, f'Exclusão não permitida. Horas extras de '
                                    f'{mes}/{empregados_a_deletar.ano} já foram processadas!')
            return render(request, "empregados/importacoes.html", context={
                                    'files': empregados_paginados})
        else:
            empregados_a_deletar.delete()
            deletar = Importacoes.objects.filter(mes=empregados_a_deletar.mes,
                                                 ano=empregados_a_deletar.ano)
            deletar.delete()

            mes = empregados_a_deletar.mes
            if empregados_a_deletar.mes < 10:
                mes = f"0{empregados_a_deletar.mes}"
            messages.success(request, f'Empregados de {mes}/{empregados_a_deletar.ano} deletados com sucesso!')
            empregados_a_mostar = Importacoes.objects.filter(tipo='empregados').order_by("-ano", "-mes").all()
            if not empregados_a_mostar:
                messages.error(request, "Sem empregados cadastrados!")

            paginator = Paginator(empregados_a_mostar, 5)
            page = request.GET.get('page')
            empregados_paginados = paginator.get_page(page)
            return render(request, "empregados/importacoes.html", context={
                'files': empregados_paginados})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def confirma_deletar(request):
    file_id = request.POST.get('file_id')
    pagina = request.POST.get('pagina')
    files2 = request.POST.get('files2')
    return render(request, 'empregados/confirma_deletar.html',
                  context={'file_id': file_id, 'pagina': pagina, 'files2': files2})
