import json

from django.shortcuts import redirect, get_object_or_404

from empregados.models import Importacoes, Empregado
from horas_extras.calcula import calcula_he, calcula_solicitacao, recalcula_solicitacao, recalcula_he
from relatorios.models import RelatorioPagas
from .dbchanges import salva_solicitacao, salva_confirmacao, salva_banco_total, salva_banco_mes
from .models import Confirmacao, Frequencia, Solicitacao, BancoMes, BancoTotal
from django.contrib import messages

from .upload import valida_upload, arruma_dados_do_arquivo, processa_horas_extras
from django.core.paginator import Paginator

from .valida_formata_str import transforma_data_contrario


from django.shortcuts import render


def solicitacao_confirmacao_upload(request):
    if request.user.is_authenticated:
        if request.method == "POST":       
            data = request.POST.get('data')
            mes = int(str(data).split('-')[1])
            ano = int(str(data).split('-')[0])
            empregados = Empregado.objects.filter(mes=mes, ano=ano)
            if empregados:
                dados, mes, ano, tipo, resposta, planilhas_com_erro, sem_setor = valida_upload(request)
                print(sem_setor)
                if resposta == "formato_não_suportado":
                    messages.error(request, "Formato de arquivo não suportado")
                if resposta == "arquivo_vazio":
                    messages.error(request, "Arquivo não pode ser vazio!")
                if resposta == 'OK':
                    resposta2, nao_cadastrados = arruma_dados_do_arquivo(request, dados, mes, ano, tipo)
                    if len(nao_cadastrados) > 0:
                        messages.error(request, f"Empregados não cadastrados: {nao_cadastrados}")
                    if len(planilhas_com_erro) > 0:
                        messages.error(request, f"Planilhas com erro: {planilhas_com_erro}")
                    if len(sem_setor) > 0:
                        messages.error(request, f"Planilhas sem setor informado: {sem_setor}")
                    if resposta2 == "dados_inválidos":
                        messages.error(request, "Arquivo com dados inválidos!")
                    if resposta2 == "arquivo_vazio":
                        messages.error(request, "Arquivo não pode ser vazio!")
                    if resposta2 == "OK":
                        messages.success(request, 'Importação efetuada com sucesso!')
            else:
                if int(mes) < 10:
                    mes = f'0{mes}'
                messages.error(request, f'Nenhum empregado cadastrado para {mes}/{ano}')
                return render(
                    request,
                    "horas_extras/solicitacao_confirmacao_upload.html",
                    context={"files": Importacoes.objects.filter(tipo='Confirmação').order_by("-ano", "-mes").all(),
                             "files2": Importacoes.objects.filter(tipo='Solicitação').order_by("-ano", "-mes").all()},
                )      

        return render(
            request,
            "horas_extras/solicitacao_confirmacao_upload.html",
            context={"files": Importacoes.objects.filter(tipo='Confirmação').order_by("-ano", "-mes").all(),
                     "files2": Importacoes.objects.filter(tipo='Solicitação').order_by("-ano", "-mes").all()},
        )
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def importacoes(request):
    if request.user.is_authenticated:
        importacoes_lista_confirmacao = Importacoes.objects.filter(tipo='Confirmação').values()
        importacoes_lista_solicitacao = Importacoes.objects.filter(tipo='Solicitação').values()
        solicitacoes_a_mostar = Importacoes.objects.filter(tipo='Solicitação').order_by("-ano", "-mes").all()
        paginator = Paginator(solicitacoes_a_mostar, 5)
        page = request.GET.get('page')
        solicitacoes_paginadas = paginator.get_page(page)
    
        confirmacoes_a_mostar = Importacoes.objects.filter(tipo='Confirmação').order_by("-ano", "-mes").all()
        paginator = Paginator(confirmacoes_a_mostar, 5)
        page = request.GET.get('page')
        confirmacoes_paginadas = paginator.get_page(page)
    
        if not importacoes_lista_solicitacao or not importacoes_lista_confirmacao:
            messages.error(request, "Sem planilhas importadas!")
    
        return render(request, "horas_extras/importacoes.html", context={
            'files': confirmacoes_paginadas, 'files2': solicitacoes_paginadas})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def confirmacao(request, file_id):
    if request.user.is_authenticated:
        importacao = get_object_or_404(Importacoes, pk=file_id)
        confirmacoes_a_mostrar = Confirmacao.objects.filter(importacao=importacao).all().order_by("nome")
        contador = 1
        for objeto in confirmacoes_a_mostrar:
            objeto.contador = contador
            contador += 1
        paginator = Paginator(confirmacoes_a_mostrar, 20)
        page = request.GET.get('page')
        confirmacoes_paginadas = paginator.get_page(page)
        if request.method == 'GET':
            query = request.GET.get('q')
            if query != '':
                try:
                    if str(query).isnumeric():
                        empregado = Confirmacao.objects.filter(empregado__matricula__icontains=query,
                                                               empregado__mes=importacao.mes,
                                                               empregado__ano=importacao.ano).order_by("nome")
                        if empregado:
                            return render(request,
                                          "horas_extras/confirmacao.html",
                                          context={"files": empregado,
                                                   "files2": file_id, 'objetos': confirmacoes_a_mostrar})
                    else:
                        empregado = Confirmacao.objects.filter(nome__icontains=query, empregado__mes=importacao.mes,
                                                               empregado__ano=importacao.ano).order_by("nome")
                        if empregado:
                            return render(request, "horas_extras/confirmacao.html",
                                          context={"files": empregado,
                                                   "files2": file_id, 'objetos': confirmacoes_a_mostrar})
                except ValueError:
                    return render(request, "horas_extras/confirmacao.html",
                                  context={"files": confirmacoes_paginadas,
                                           "files2": file_id, 'objetos': confirmacoes_a_mostrar})
            if query != "":
                messages.error(request, "Empregado não encontrato!")
        return render(request, "horas_extras/confirmacao.html",
                      context={"files": confirmacoes_paginadas,
                               "files2": file_id, 'objetos': confirmacoes_a_mostrar})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def solicitacao(request, file_id):
    if request.user.is_authenticated:
        importacao = get_object_or_404(Importacoes, pk=file_id)
        solicitacoes_a_mostrar = Solicitacao.objects.filter(importacao=importacao).all().order_by("nome")
        paginator = Paginator(solicitacoes_a_mostrar, 20)
        page = request.GET.get('page')
        solicitacao_paginada = paginator.get_page(page)
        if request.method == 'GET':
            query = request.GET.get('q')
            if query != '':
                try:
                    if str(query).isnumeric():
                        empregado = Solicitacao.objects.filter(empregado__matricula__icontains=query,
                                                               empregado__mes=importacao.mes,
                                                               empregado__ano=importacao.ano).order_by("nome")
                        if empregado:
                            return render(request,
                                          "horas_extras/solicitacao.html",
                                          context={"files": empregado,
                                                   "files2": file_id})
                    else:
                        empregado = Solicitacao.objects.filter(nome__icontains=query, empregado__mes=importacao.mes,
                                                               empregado__ano=importacao.ano).order_by("nome")
                        if empregado:
                            return render(request, "horas_extras/solicitacao.html",
                                          context={"files": empregado,
                                                   "files2": file_id})
                except ValueError:
                    return render(request, "horas_extras/solicitacao.html",
                                  context={"files": solicitacao_paginada,
                                           "files2": file_id})
            if query != "":
                messages.error(request, "Empregado não encontrado!")
        return render(request, "horas_extras/solicitacao.html",
                      context={"files": solicitacao_paginada,
                               "files2": file_id})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def deleta_mes(request, file_id):
    if request.user.is_authenticated:
        importacao = get_object_or_404(Importacoes, pk=file_id)
        importacao.delete()
        importacoes_lista_confirmacao = Importacoes.objects.filter(tipo='Confirmação').values()
        importacoes_lista_solicitacao = Importacoes.objects.filter(tipo='Solicitação').values()
        if not importacoes_lista_solicitacao or not importacoes_lista_confirmacao:
            messages.error(request, "Sem planilhas importadas")
        return render(request, "horas_extras/importacoes.html", context={
            'files': Importacoes.objects.filter(tipo='Confirmação').order_by("-ano", "-mes").all(),
            'files2': Importacoes.objects.filter(tipo='Solicitação').order_by("-ano", "-mes").all()},
                      )
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def inserir_bases(request):
    if request.user.is_authenticated:
        frequencias = Importacoes.objects.filter(tipo='frequencia').order_by("-ano", "-mes").all()
        banco_mes = Importacoes.objects.filter(tipo='banco_mes').order_by("-ano", "-mes").all()
        banco_total = Importacoes.objects.filter(tipo='banco_total').order_by("-ano", "-mes").all()
        if request.method == "POST":
            if request.user.is_authenticated:
                mes, ano, resposta = processa_horas_extras(request)
    
                if resposta == 'sem arquivos':
                    messages.error(request, "Insira pelo menos um arquivo")
                if resposta == "formato_não_suportado":
                    messages.error(request, "Formato de arquivo não suportado")
                if resposta == "arquivo_vazio":
                    messages.error(request, "Arquivo não pode ser vazio!")
                if resposta == "dados_inválidos":
                    messages.error(request, "Arquivo com dados inválidos!")
                if resposta == "OK":
                    messages.success(request, "Processado com sucesso")
                return render(request, "horas_extras/inserir_bases.html",
                              context={"files": frequencias, "files2": banco_mes, "files3": banco_total},
                              )
            else:
                return redirect("login")
        else:
            return render(request, "horas_extras/inserir_bases.html",
                          context={"files": frequencias, "files2": banco_mes, "files3": banco_total})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def deleta_mes_frequencia(request):
    if request.user.is_authenticated:
        dados = json.loads(request.POST.get('dados'))
        file_id = int(dados['file_id'])
        importacao = get_object_or_404(Importacoes, pk=file_id)
        importacao.delete()
        frequencias_lista = Importacoes.objects.filter(tipo='frequencia').all()
        if not frequencias_lista:
            messages.error(request, 'Sem frequencias importadas!')
        return render(
            request,
            "horas_extras/frequencia.html",
            context={"files": frequencias_lista.order_by("-ano", "-mes")},
        )
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def frequencia(request):
    if request.user.is_authenticated:
        frequencias_lista = Importacoes.objects.filter(tipo='frequencia').all()
        if len(frequencias_lista) == 0:
            messages.error(request, "Sem frequencias importadas")
        return render(request, "horas_extras/frequencia.html",
                      context={"files": frequencias_lista.order_by("-ano", "-mes"),
                               'file_id': 1})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def frequencias(request, file_id):
    if request.user.is_authenticated:
        importacao = get_object_or_404(Importacoes, pk=file_id)
        dias = len(Frequencia.objects.filter(importacao=importacao).distinct('data'))
        frequencias_a_mostrar = Frequencia.objects.filter(importacao=importacao).all().order_by('nome', 'data')
        paginator = Paginator(frequencias_a_mostrar, dias)
        page = request.GET.get('page')
        frequencias_paginadas = paginator.get_page(page)
        try:
            if request.method == 'GET':
                query = request.GET.get('q')
                if query != '':
                    if str(query).isnumeric():
                        empregado = Frequencia.objects.filter(empregado__matricula__icontains=query,
                                                              empregado__mes=importacao.mes,
                                                              empregado__ano=importacao.ano).order_by("nome")
                        if empregado:
                            return render(
                                request,
                                "horas_extras/frequencias.html",
                                context={"files": empregado,
                                         "files2": file_id})
                    else:
                        empregado = Frequencia.objects.filter(nome__icontains=query, empregado__mes=importacao.mes,
                                                              empregado__ano=importacao.ano).order_by("nome")
                        if empregado:
                            return render(
                                request,
                                "horas_extras/frequencias.html",
                                context={"files": empregado,
                                         "files2": file_id})
                if query != "":
                    messages.error(request, "Empregado não encontrato!")
        except ValueError:
            return render(
                request,
                "horas_extras/frequencias.html",
                context={"files": frequencias_paginadas,
                         "files2": file_id})
        return render(
            request,
            "horas_extras/frequencias.html",
            context={"files": frequencias_paginadas,
                     "files2": file_id})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def salvar_alteracao_frequencia(request):
    if request.user.is_authenticated:
        dados = json.loads(request.POST.get('dados'))
        data = dados['data']
        data = transforma_data_contrario(data)
        matricula = dados['matricula']
        frequencia = Frequencia.objects.get(empregado__matricula=matricula, data=data)
        frequencia.batida1 = dados['batida1']
        frequencia.batida2 = dados['batida2']
        frequencia.batida3 = dados['batida3']
        frequencia.batida4 = dados['batida4']
        frequencia.batida4 = dados['batida5']
        frequencia.batida4 = dados['batida6']
        frequencia.escala = dados['escala']
        frequencia.save()
        mes = frequencia.importacao.mes
        ano = frequencia.importacao.ano
        frequencias_a_mostrar = Frequencia.objects.filter(mes=mes, ano=ano).all().order_by('-matricula', '-data')
        dias = len(Frequencia.objects.filter(mes=mes, ano=ano).distinct('data'))
        paginator = Paginator(frequencias_a_mostrar, dias)
        page = request.GET.get('page')
        frequencias_paginadas = paginator.get_page(page)
        file_id = dados['file_id']
        return render(
            request,
            "horas_extras/frequencias.html",
            context={"files": frequencias_paginadas, "mes": mes, "ano": ano,
                     "files2": file_id})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def salvar_alteracao_confirmacao(request):
    if request.user.is_authenticated:
        dados = json.loads(request.POST.get('dados'))
        matricula = dados['matricula']
        mes = dados['mes']
        ano = dados['ano']
        confirmacao = Confirmacao.objects.get(empregado__matricula=matricula, importacao__mes=mes,
                                              importacao__ano=ano)
        fields = {'matricula': matricula, 'nome': confirmacao.nome, 'cargo': confirmacao.cargo,
                  'setor': confirmacao.setor}
        for n in range(1, 32):
            fields.update({n: dados[str(n)]})
        salva_confirmacao(fields, request.user, mes, ano, nao_cadastrados=[])
        confirmacoes_a_mostrar = Confirmacao.objects.filter(mes=mes, ano=ano).all().order_by('nome')
        paginator = Paginator(confirmacoes_a_mostrar, 20)
        page = request.GET.get('page')
        confirmacoes_paginadas = paginator.get_page(page)
        file_id = dados['file_id']
        return render(request, "horas_extras/confirmacao.html",
                      context={"files": confirmacoes_paginadas, "mes": mes, "ano": ano,
                               "files2": file_id})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def salvar_alteracao_solicitacao(request):
    if request.user.is_authenticated:
        dados = json.loads(request.POST.get('dados'))
        matricula = dados['matricula']
        mes = dados['mes']
        ano = dados['ano']
        solicitacao = Solicitacao.objects.get(empregado__matricula=matricula, importacao__mes=mes,
                                              importacao__ano=ano)
        fields = {'matricula': matricula, 'nome': solicitacao.nome, 'cargo': solicitacao.cargo,
                  'setor': solicitacao.setor}
        for n in range(1, 32):
            fields.update({n: dados[str(n)]})
        salva_solicitacao(fields, request.user, mes, ano, nao_cadastrados=[])
        solicitacoes_a_mostrar = Solicitacao.objects.filter(importacao__mes=mes,
                                                            importacao__ano=ano).all().order_by('nome')
        paginator = Paginator(solicitacoes_a_mostrar, 20)
        page = request.GET.get('page')
        solicitacoes_paginadas = paginator.get_page(page)
        file_id = dados['file_id']
        return render(request, "horas_extras/solicitacao.html",
                      context={"files": solicitacoes_paginadas, "mes": mes, "ano": ano,
                               "files2": file_id})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def salvar_alteracao_banco(request):
    if request.user.is_authenticated:
        dados = json.loads(request.POST.get('dados'))
        banco_total = BancoTotal.objects.get(empregado__matricula=dados['matricula'],
                                             importacao__mes=dados['mes'], importacao__ano=dados['ano'])
        saldo_decimal = float(str(dados['saldo_decimal']).replace(',', '.'))

        fields = {'matricula': dados['matricula'], 'nome': banco_total.nome, 'saldo_banco': dados['saldo_banco'],
                  'saldo_decimal': saldo_decimal}
        salva_banco_total(fields, request.user, dados['mes'], dados['ano'])
        bancos_a_mostrar = BancoTotal.objects.filter(importacao__mes=dados['mes'],
                                                     importacao__ano=dados['ano']
                                                     ).all().order_by('-empregado__matricula')
        paginator = Paginator(bancos_a_mostrar, 20)
        page = request.GET.get('page')
        bancos_paginados = paginator.get_page(page)
        file_id = dados['file_id']
        return render(
            request,
            "horas_extras/banco_total.html",
            context={"files": bancos_paginados, "mes": dados['mes'], "ano": dados['ano'],
                     "files2": file_id})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def salvar_alteracao_saldo_mes(request):
    if request.user.is_authenticated:
        dados = json.loads(request.POST.get('dados'))
        banco_mes = BancoMes.objects.get(empregado__matricula=dados['matricula'],
                                         importacao__mes=dados['mes'], importacao__ano=dados['ano'])
        saldo_decimal = float(str(dados['saldo_decimal']).replace(',', '.'))

        fields = {'matricula': dados['matricula'], 'nome': banco_mes.nome, 'saldo': dados['saldo_banco'],
                  'saldo_decimal': saldo_decimal}
        salva_banco_mes(fields, request.user, dados['mes'], dados['ano'])
        bancos_a_mostrar = BancoMes.objects.filter(importacao__mes=dados['mes'],
                                                   importacao__ano=dados['ano']).all().order_by('-empregado__matricula')
        paginator = Paginator(bancos_a_mostrar, 20)
        page = request.GET.get('page')
        bancos_paginados = paginator.get_page(page)
        file_id = dados['file_id']
        return render(
            request,
            "horas_extras/banco_mes.html",
            context={"files": bancos_paginados, "mes": dados['mes'], "ano": dados['ano'],
                     "files2": file_id})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def bancos(request):
    if request.user.is_authenticated:
        banco_total_lista = Importacoes.objects.filter(tipo='banco_total').all()
        banco_mes_lista = Importacoes.objects.filter(tipo='banco_mes').all()
        if len(banco_mes_lista) == 0 or len(banco_total_lista) == 0:
            messages.error(request, "Sem bancos importados")
        return render(request, "horas_extras/banco_de_horas.html",
                      context={"files1": Importacoes.objects.filter(tipo='banco_total').order_by("-ano", "-mes"),
                               "files2": Importacoes.objects.filter(tipo='banco_mes').order_by("-ano", "-mes"),
                               'file_id': 1})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def banco_total(request, file_id):
    if request.user.is_authenticated:
        importacao = get_object_or_404(Importacoes, pk=file_id)
        bancos_total_a_mostrar = BancoTotal.objects.filter(importacao=importacao).all().order_by('nome')
        paginator = Paginator(bancos_total_a_mostrar, 20)
        page = request.GET.get('page')
        bancos_total_paginados = paginator.get_page(page)
        try:
            if request.method == 'GET':

                query = request.GET.get('q')
                if query != '':
                    if str(query).isnumeric():
                        empregado = BancoTotal.objects.filter(empregado__matricula__icontains=query,
                                                              empregado__mes=importacao.mes,
                                                              empregado__ano=importacao.ano).order_by("nome")
                        if empregado:
                            return render(
                                request,
                                "horas_extras/banco_total.html",
                                context={"files": empregado,
                                         "files2": file_id})
                    else:
                        empregado = BancoTotal.objects.filter(nome__icontains=query, empregado__mes=importacao.mes,
                                                              empregado__ano=importacao.ano).order_by("nome")
                        if empregado:
                            return render(
                                request,
                                "horas_extras/banco_total.html",
                                context={"files": empregado,
                                         "files2": file_id})
                if query != "":
                    messages.error(request, "Empregado não encontrato!")
        except ValueError:
            return render(
                request,
                "horas_extras/banco_total.html",
                context={"files": bancos_total_paginados,
                         "files2": file_id})
        return render(
            request,
            "horas_extras/banco_total.html",
            context={"files": bancos_total_paginados,
                     "files2": file_id})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def banco_mes(request, file_id):
    if request.user.is_authenticated:
        importacao = get_object_or_404(Importacoes, pk=file_id)
        bancos_mes_a_mostrar = BancoMes.objects.filter(importacao=importacao).all().order_by('nome')
        paginator = Paginator(bancos_mes_a_mostrar, 20)
        page = request.GET.get('page')
        bancos_mes_paginados = paginator.get_page(page)
        try:
            if request.method == 'GET':
                query = request.GET.get('q')
                if query != '':
                    if str(query).isnumeric():
                        empregado = BancoMes.objects.filter(empregado__matricula__icontains=query,
                                                            empregado__mes=importacao.mes,
                                                            empregado__ano=importacao.ano).order_by("nome")
                        if empregado:
                            return render(
                                request,
                                "horas_extras/banco_mes.html",
                                context={"files": empregado,
                                         "files2": file_id})
                    else:
                        empregado = BancoMes.objects.filter(nome__icontains=query, empregado__mes=importacao.mes,
                                                            empregado__ano=importacao.ano).order_by("nome")
                        if empregado:
                            return render(
                                request,
                                "horas_extras/banco_mes.html",
                                context={"files": empregado,
                                         "files2": file_id})
                if query != "":
                    messages.error(request, "Empregado não encontrato!")
        except ValueError:
            return render(
                request,
                "horas_extras/banco_mes.html",
                context={"files": bancos_mes_paginados,
                         "files2": file_id})
        return render(
            request,
            "horas_extras/banco_mes.html",
            context={"files": bancos_mes_paginados,
                     "files2": file_id})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def deleta_banco_mes(request):
    if request.user.is_authenticated:
        dados = json.loads(request.POST.get('dados'))
        file_id = int(dados['file_id'])
        file = get_object_or_404(Importacoes, pk=file_id)
        mes = file.mes
        ano = file.ano
        BancoMes.objects.filter(mes=mes, ano=ano).delete()
        Importacoes.objects.filter(mes=mes, ano=ano, tipo='banco_mes').delete()
        banco_total_lista = Importacoes.objects.filter(tipo='banco_total').order_by("-ano", "-mes").all()
        banco_mes_lista = Importacoes.objects.filter(tipo='banco_mes').order_by("-ano", "-mes").all()
        if len(banco_mes_lista) == 0 or len(banco_total_lista) == 0:
            messages.error(request, "Sem bancos importados")
        return render(request, "horas_extras/banco_de_horas.html",
                      context={"files1": banco_total_lista,
                               "files2": banco_mes_lista,
                               'file_id': file_id})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def deleta_banco_total_mes(request):
    if request.user.is_authenticated:
        dados = json.loads(request.POST.get('dados'))
        file_id = int(dados['file_id'])
        file = get_object_or_404(Importacoes, pk=file_id)
        mes = file.mes
        ano = file.ano
        BancoTotal.objects.filter(mes=mes, ano=ano).delete()
        Importacoes.objects.filter(mes=mes, ano=ano, tipo='banco_total').delete()
        banco_total_lista = Importacoes.objects.filter(tipo='banco_total').order_by("-ano", "-mes").all()
        banco_mes_lista = Importacoes.objects.filter(tipo='banco_mes').order_by("-ano", "-mes").all()
        if len(banco_mes_lista) == 0 or len(banco_total_lista) == 0:
            messages.error(request, "Sem bancos importados")
        return render(request, "horas_extras/banco_de_horas.html",
                      context={"files1": banco_total_lista,
                               "files2": banco_mes_lista,
                               'file_id': file_id})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def processar(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            data = request.POST.get('data')
            ano, mes = int(str(data).split('-')[0]), int(str(data).split('-')[1])
            tipo = request.POST.get('tipo')
            usuario = request.user
            if 'processar' in request.POST:
                botao = 'processar'
            else:
                botao = 'bases'

            if tipo == 'solicitacao':
                solicitacao = Importacoes.objects.filter(tipo='Solicitação', mes=mes, ano=ano).order_by("-ano",
                                                                                                        "-mes").all()
                if len(solicitacao) == 0:
                    messages.error(request, f'Planilhas de solicitação do mês 0{mes}/{ano} não foram importadas')

                banco_total = Importacoes.objects.filter(tipo='banco_total', mes=mes, ano=ano).order_by("-ano",
                                                                                                        "-mes").all()
                if len(banco_total) == 0:
                    messages.error(request, f'Banco de horas do mês 0{mes}/{ano} não foi importado')

                if botao == 'bases' or len(solicitacao) == 0 or len(banco_total) == 0:
                    return render(request, "horas_extras/processar.html",
                                  context={"files3": banco_total, 'files5': solicitacao, 'mes': mes,
                                           'ano': ano, })
                elif botao == 'processar':
                    nome = f'Solicitação 0{mes}/{ano}.xlsx'
                    relatorio, conclusao = calcula_solicitacao(ano, mes, usuario)
                    relatorio = relatorio.to_html(index=False)
                    messages.info(request, f'Processamento efetuado - {conclusao}')
                    return render(request, "horas_extras/processar.html",
                                  context={'relatorio': relatorio, 'nome': str(nome).split('.')[0], 'mes': mes,
                                           'ano': ano, 'tipo': tipo})

            if tipo == 'confirmacao':
                frequencias = Importacoes.objects.filter(tipo='frequencia', mes=mes, ano=ano
                                                         ).order_by("-ano", "-mes").all()
                if len(frequencias) == 0:
                    messages.error(request, f'Frequência do mês de 0{mes}/{ano} não foi importada')

                banco_mes = Importacoes.objects.filter(tipo='banco_mes', mes=mes, ano=ano
                                                       ).order_by("-ano", "-mes").all()
                if len(banco_mes) == 0:
                    messages.error(request, f'Saldo de horas do mês 0{mes}/{ano} não foi importado')
                banco_total = Importacoes.objects.filter(tipo='banco_total', mes=mes, ano=ano).order_by("-ano",
                                                                                                        "-mes").all()
                if len(banco_total) == 0:
                    messages.error(request, f'Banco de horas do mês 0{mes}/{ano} não foi importado')
                confirmacao = Importacoes.objects.filter(tipo='Confirmação', mes=mes, ano=ano).order_by("-ano",
                                                                                                        "-mes").all()
                if len(confirmacao) == 0:
                    messages.error(request, f'Planilhas de confirmação do mês 0{mes}/{ano} não foram importadas')

                if botao == 'bases' or len(frequencias) == 0 or len(banco_mes) == 0 or len(banco_total) == 0 or len(
                        confirmacao) == 0:
                    return render(request, "horas_extras/processar.html",
                                  context={"files": frequencias, "files2": banco_mes, "files3": banco_total,
                                           'files4': confirmacao, 'files6': frequencia, 'mes': mes,
                                           'ano': ano, })
                elif botao == 'processar':
                    pagas = RelatorioPagas.objects.filter(importacao__mes=mes, importacao__ano=ano)
                    if pagas:
                        if mes < 10:
                            mes = f'0{mes}'
                        messages.info(request, f'Horas extras de {mes}/{ano} já calculadas!')
                        return render(request, "horas_extras/processar.html")
                    final = request.POST.get('processamentoFinal')
                    nome = f'Confirmação 0{mes}/{ano}.xlsx'
                    relatorio, conclusao = calcula_he(ano, mes, usuario, final)
                    relatorio = relatorio.to_html(index=True)
                    messages.info(request, f'Processamento efetuado - {conclusao}')
                    return render(request, "horas_extras/processar.html",
                                  context={'relatorio': relatorio, 'nome': str(nome).split('.')[0], 'mes': mes,
                                           'ano': ano, 'tipo': tipo, 'final': final})
        else:
            return render(request, "horas_extras/processar.html")
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def reprocessar(request):
    if request.user.is_authenticated:
        if 'processar' in request.POST:
            botao = 'processar'
        else:
            botao = 'pesquisar'

        matricula = request.POST.get('matricula')
        tipo = request.POST.get('tipo')
        data = request.POST.get('data')
        usuario = request.user
        if data is not None and tipo == 'confirmacao' and botao == 'pesquisar':
            ano, mes = str(data).split('-')[0], str(data).split('-')[1]

            confirmacao = Confirmacao.objects.filter(empregado__matricula=matricula,
                                                     importacao__mes=mes, importacao__ano=ano).values()

            frequencia = Frequencia.objects.filter(empregado__matricula=matricula,
                                                   importacao__mes=mes, importacao__ano=ano).order_by('data').values()

            banco_mes = BancoMes.objects.filter(empregado__matricula=matricula,
                                                importacao__mes=mes, importacao__ano=ano).values()

            banco_total = BancoTotal.objects.filter(empregado__matricula=matricula,
                                                    importacao__mes=mes, importacao__ano=ano).values()
            return render(request, 'horas_extras/reprocessar.html',
                          context={'matricula': matricula, 'mes': mes, 'ano': ano, 'files': frequencia,
                                   'files2': banco_mes, 'files3': banco_total,
                                   'files4': confirmacao, 'tipo': tipo})
        elif data is not None and tipo == 'confirmacao' and botao == 'processar':
            ano, mes = str(data).split('-')[0], str(data).split('-')[1]
            nome = f'Solicitação {mes}/{ano}.xlsx'
            relatorio, conclusao = recalcula_he(matricula, ano, mes, usuario)
            relatorio = relatorio.to_html(index=False)
            messages.info(request, f'Processamento efetuado - {conclusao}')
            return render(request, "horas_extras/reprocessar.html",
                          context={'relatorio': relatorio, 'nome': str(nome).split('.')[0], 'mes': mes,
                                   'ano': ano, 'tipo': tipo, 'matricula': matricula})
        if data is not None and tipo == 'solicitacao' and botao == 'pesquisar':
            ano, mes = str(data).split('-')[0], str(data).split('-')[1]

            solicitacao = Solicitacao.objects.filter(empregado__matricula=matricula,
                                                     importacao__mes=mes, importacao__ano=ano).values()

            banco_total = BancoTotal.objects.filter(empregado__matricula=matricula,
                                                    importacao__mes=mes, importacao__ano=ano).values()

            return render(request, 'horas_extras/reprocessar.html',
                          context={'matricula': matricula, 'mes': mes, 'ano': ano,
                                   'files3': banco_total, 'files5': solicitacao, 'tipo': tipo})
        elif data is not None and tipo == 'solicitacao' and botao == 'processar':
            ano, mes = str(data).split('-')[0], str(data).split('-')[1]
            nome = f'Solicitação {mes}/{ano}.xlsx'
            relatorio, conclusao = recalcula_solicitacao(matricula, ano, mes, usuario)
            relatorio = relatorio.to_html(index=False)
            messages.info(request, f'Processamento efetuado - {conclusao}')
            return render(request, "horas_extras/reprocessar.html",
                          context={'relatorio': relatorio, 'nome': str(nome).split('.')[0], 'mes': mes,
                                   'ano': ano, 'tipo': tipo, 'matricula': matricula})

        return render(request, 'horas_extras/reprocessar.html')
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def salva_solicitacao_reprocessar(request):
    if request.user.is_authenticated:
        dados = json.loads(request.POST.get('dados'))
        matricula = dados['matricula']
        mes = dados['mes']
        ano = dados['ano']
        tipo = dados['tipo']
        solicitacao = Solicitacao.objects.get(empregado__matricula=matricula, importacao__mes=mes, importacao__ano=ano)
        fields = {'matricula': matricula, 'nome': solicitacao.nome, 'cargo': solicitacao.cargo,
                  'setor': solicitacao.setor}
        for n in range(1, 32):
            fields.update({n: dados[str(n)]})
        salva_solicitacao(fields, request.user, mes, ano, nao_cadastrados=[])
        solicitacao = Solicitacao.objects.filter(empregado__matricula=matricula, importacao__mes=mes,
                                                 importacao__ano=ano).values()
        banco_total = BancoTotal.objects.filter(empregado__matricula=matricula, importacao__mes=mes,
                                                importacao__ano=ano).values()
        context = {'matricula': matricula, 'files3': banco_total, 'files5': solicitacao, 'tipo': tipo}
        return render(request, 'horas_extras/reprocessar.html', context=context)
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def salva_confirmacao_reprocessar(request):
    if request.user.is_authenticated:
        dados = json.loads(request.POST.get('dados'))
        matricula = dados['matricula']
        mes = dados['mes']
        ano = dados['ano']
        tipo = dados['tipo']
        confirmacao = Confirmacao.objects.get(empregado__matricula=matricula, importacao__mes=mes,
                                              importacao__ano=ano)
        fields = {'matricula': matricula, 'nome': confirmacao.nome,
                  'cargo': confirmacao.cargo, 'setor': confirmacao.setor}
        for n in range(1, 32):
            fields.update({n: dados[str(n)]})
        salva_confirmacao(fields, request.user, mes, ano, nao_cadastrados=[])

        confirmacao = Confirmacao.objects.filter(empregado__matricula=matricula,
                                                 importacao__mes=mes, importacao__ano=ano).values()

        banco_mes = BancoMes.objects.filter(empregado__matricula=matricula,
                                            importacao__mes=mes, importacao__ano=ano).values()

        frequencia = Frequencia.objects.filter(empregado__matricula=matricula,
                                               importacao__mes=mes, importacao__ano=ano).order_by('data').values()

        banco_total = BancoTotal.objects.filter(empregado__matricula=matricula,
                                                importacao__mes=mes, importacao__ano=ano).values()
        return render(request, 'horas_extras/reprocessar.html',
                      context={'matricula': matricula, 'mes': mes, 'ano': ano, 'files': frequencia,
                               'files2': banco_mes, 'files3': banco_total,
                               'files4': confirmacao, 'tipo': tipo})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def salvar_banco_total_reprocessar(request):
    if request.user.is_authenticated:
        dados = json.loads(request.POST.get('dados'))
        matricula = dados['matricula']
        mes = dados['mes']
        ano = dados['ano']
        tipo = dados['tipo']
        banco_total = BancoTotal.objects.get(empregado__matricula=matricula,
                                             importacao__mes=mes, importacao__ano=ano)
        saldo_decimal = float(str(dados['saldo_decimal']).replace(',', '.'))

        fields = {'matricula': matricula, 'nome': banco_total.nome, 'saldo_banco': dados['saldo_banco'],
                  'saldo_decimal': saldo_decimal}
        salva_banco_total(fields, request.user, mes, ano)
        banco_total = BancoTotal.objects.filter(empregado__matricula=matricula,
                                                importacao__mes=mes, importacao__ano=ano).values()
        if tipo == 'confirmacao':

            confirmacao = Confirmacao.objects.filter(empregado__matricula=matricula,
                                                     importacao__mes=mes, importacao__ano=ano).values()

            frequencia = Frequencia.objects.filter(empregado__matricula=matricula,
                                                   importacao__mes=mes, importacao__ano=ano).order_by('data').values()

            banco_mes = BancoMes.objects.filter(empregado__matricula=matricula,
                                                importacao__mes=mes, importacao__ano=ano).values()
            return render(request, 'horas_extras/reprocessar.html',
                          context={'matricula': matricula, 'mes': mes, 'ano': ano, 'files': frequencia,
                                   'files2': banco_mes, 'files3': banco_total,
                                   'files4': confirmacao, 'tipo': tipo})

        if tipo == 'solicitacao':
            solicitacao = Solicitacao.objects.filter(empregado__matricula=matricula, importacao__mes=mes,
                                                     importacao__ano=ano).values()
            return render(request, 'horas_extras/reprocessar.html',
                          context={'matricula': matricula, 'files3': banco_total, 'files5': solicitacao, 'tipo': tipo})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def salvar_banco_mes_reprocessar(request):
    if request.user.is_authenticated:
        dados = json.loads(request.POST.get('dados'))
        matricula = dados['matricula']
        mes = dados['mes']
        ano = dados['ano']
        tipo = dados['tipo']
        banco_mes = BancoMes.objects.get(empregado__matricula=matricula,
                                         importacao__mes=mes, importacao__ano=ano)
        saldo_decimal = float(str(dados['saldo_decimal']).replace(',', '.'))

        fields = {'matricula': matricula, 'nome': banco_mes.nome, 'saldo': dados['saldo_banco'],
                  'saldo_decimal': saldo_decimal}
        salva_banco_mes(fields, request.user, mes, ano)
        banco_mes = BancoMes.objects.filter(empregado__matricula=matricula,
                                            importacao__mes=mes, importacao__ano=ano).values()

        confirmacao = Confirmacao.objects.filter(empregado__matricula=matricula,
                                                 importacao__mes=mes, importacao__ano=ano).values()

        frequencia = Frequencia.objects.filter(empregado__matricula=matricula,
                                               importacao__mes=mes, importacao__ano=ano).order_by('data').values()

        banco_total = BancoTotal.objects.filter(empregado__matricula=matricula,
                                                importacao__mes=mes, importacao__ano=ano).values()
        return render(request, 'horas_extras/reprocessar.html',
                      context={'matricula': matricula, 'mes': mes, 'ano': ano, 'files': frequencia,
                               'files2': banco_mes, 'files3': banco_total,
                               'files4': confirmacao, 'tipo': tipo})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")


def salvar_frequencia_reprocessar(request):
    if request.user.is_authenticated:
        dados = json.loads(request.POST.get('dados'))
        data = dados['data']
        data = transforma_data_contrario(data)
        matricula = dados['matricula']
        tipo = dados['tipo']
        frequencia = Frequencia.objects.get(empregado__matricula=matricula, data=data)
        frequencia.batida1 = dados['batida1']
        frequencia.batida2 = dados['batida2']
        frequencia.batida3 = dados['batida3']
        frequencia.batida4 = dados['batida4']
        frequencia.batida4 = dados['batida5']
        frequencia.batida4 = dados['batida6']
        frequencia.escala = dados['escala']
        frequencia.save()
        mes = frequencia.importacao.mes
        ano = frequencia.importacao.ano

        banco_mes = BancoMes.objects.filter(empregado__matricula=matricula,
                                            importacao__mes=mes, importacao__ano=ano).values()

        confirmacao = Confirmacao.objects.filter(empregado__matricula=matricula,
                                                 importacao__mes=mes, importacao__ano=ano).values()

        frequencia = Frequencia.objects.filter(empregado__matricula=matricula,
                                               importacao__mes=mes, importacao__ano=ano).order_by('data').values()

        banco_total = BancoTotal.objects.filter(empregado__matricula=matricula,
                                                importacao__mes=mes, importacao__ano=ano).values()
        return render(request, 'horas_extras/reprocessar.html',
                      context={'matricula': matricula, 'mes': mes, 'ano': ano, 'files': frequencia,
                               'files2': banco_mes, 'files3': banco_total,
                               'files4': confirmacao, 'tipo': tipo})
    else:
        messages.error(request, 'Faça o login para acessar essa página!')
        return render(request, "usuarios/login.html")
