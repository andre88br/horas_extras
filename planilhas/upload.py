from django.core.exceptions import ObjectDoesNotExist

from arruma_arquivos import arruma_confirmacao_solicitacao, arruma_empregados, arruma_confirmacao_solicitacao_planilha
from empregados.models import Importacoes
from .dbchanges import salva_confirmacao_planilha, salva_solicitacao_planilha, salva_listaempregados


def valida_upload_planilha(request):
    try:
        if request.method == "POST":
            planilhas = request.FILES.getlist("upload")
            confirmacao, planilhas_com_erro = arruma_confirmacao_solicitacao_planilha(planilhas)
            resposta = "OK"
            return confirmacao, resposta, planilhas_com_erro
        else:
            dados = None
            mes = None
            ano = None
            tipo = None
            planilhas_com_erro = None
            resposta = "formato_não_suportado"
            return dados, mes, ano, tipo, resposta, planilhas_com_erro
    except IndexError as error:
        print(error)
        dados = None
        mes = None
        ano = None
        tipo = None
        planilhas_com_erro = None
        resposta = "arquivo_vazio"
        return dados, mes, ano, tipo, resposta, planilhas_com_erro


def arruma_dados_planilha(request, dados, mes, ano, tipo, setor):
    if tipo == 'PlanilhaConfirmação':
        confirmacao_a_mostar = []
        nao_cadastrados = []

        for i, j in dados.iterrows():
            document, nao_cadastrados = salva_confirmacao_planilha(j, request.user, mes, ano, nao_cadastrados, setor)
            confirmacao_a_mostar.append(document)
        if len(confirmacao_a_mostar) == 0:
            raise KeyError
        else:
            resposta = "OK"
            return resposta, nao_cadastrados
    if tipo == 'PlanilhaSolicitação':
        solicitacao_a_mostar = []
        nao_cadastrados = []

        for i, j in dados.iterrows():
            document, nao_cadastrados = salva_solicitacao_planilha(j, request.user, mes, ano, nao_cadastrados, setor)
            solicitacao_a_mostar.append(document)

        if len(solicitacao_a_mostar) == 0:
            raise KeyError
        else:
            resposta = "OK"
            return resposta, nao_cadastrados


def arruma_dados_do_arquivo(request, dados, mes, ano, tipo, setor):
    if tipo == 'PlanilhaConfirmação':
        confirmacao_a_mostar = []
        nao_cadastrados = []

        for i, j in dados.iterrows():
            document, nao_cadastrados = salva_confirmacao_planilha(j, request.user, mes, ano, nao_cadastrados, setor)
            confirmacao_a_mostar.append(document)
        if len(confirmacao_a_mostar) == 0:
            raise KeyError
        else:
            resposta = "OK"
            return resposta, nao_cadastrados
    if tipo == 'PlanilhaSolicitação':
        solicitacao_a_mostar = []
        nao_cadastrados = []

        for i, j in dados.iterrows():
            document, nao_cadastrados = salva_solicitacao_planilha(j, request.user, mes, ano, nao_cadastrados, setor)
            solicitacao_a_mostar.append(document)

        if len(solicitacao_a_mostar) == 0:
            raise KeyError
        else:
            resposta = "OK"
            return resposta, nao_cadastrados


def importa_listaempregados(request):
    empregados_a_mostrar = []
    salarios, insalubridades = '', ''
    try:
        if request.method == "POST":
            planilha_empregados = request.FILES.get("empregados")
            data = request.POST.get('data')
            ano, mes = str(data).split('-')

            empregados = arruma_empregados(planilha_empregados)

            usuario = request.user

            for i, j in empregados.iterrows():
                empregado = j
                document = salva_listaempregados(empregado, mes, ano, usuario)
                empregados_a_mostrar.append(document)

            if len(empregados_a_mostrar) == 0:
                return "arquivo_vazio"
            else:
                resposta = "OK"
                return resposta
    except IndexError:
        resposta = "dados_inválidos"
        return resposta
    except ObjectDoesNotExist:
        resposta = "arquivo_vazio"
        return resposta
