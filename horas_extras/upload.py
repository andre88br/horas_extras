from arruma_arquivos import arruma_frequencia, arruma_confirmacao_solicitacao, arruma_saldo_mes, arruma_banco
from empregados.models import Importacoes
from .dbchanges import salva_confirmacao, salva_frequencia, salva_solicitacao, salva_banco_mes, salva_banco_total


def valida_upload(request):
    try:
        if request.method == "POST":
            planilhas = request.FILES.getlist("upload")
            confirmacao, planilhas_com_erro, sem_setor = arruma_confirmacao_solicitacao(planilhas)
            data = request.POST['data']
            ano, mes = int(str(data).split('-')[0]), int(str(data).split('-')[1])
            tipo = request.POST.get("tipo")
            resposta = "OK"
            return confirmacao, mes, ano, tipo, resposta, planilhas_com_erro, sem_setor
        else:
            dados = None
            mes = None
            ano = None
            tipo = None
            planilhas_com_erro = None
            sem_setor = None
            resposta = "formato_não_suportado"
            return dados, mes, ano, tipo, resposta, planilhas_com_erro, sem_setor
    except IndexError as error:
        print(error)
        dados = None
        mes = None
        ano = None
        tipo = None
        sem_setor = None
        planilhas_com_erro = None
        resposta = "arquivo_vazio"
        return dados, mes, ano, tipo, resposta, planilhas_com_erro, sem_setor


def arruma_dados_do_arquivo(request, dados, mes, ano, tipo):
    if tipo == 'Confirmação':
        busca = Importacoes.objects.filter(mes=mes, ano=ano, tipo='Confirmação').all()
        if busca:
            busca.delete()

        confirmacao_a_mostar = []
        nao_cadastrados = []

        for i, j in dados.iterrows():
            document, nao_cadastrados = salva_confirmacao(j, request.user, mes, ano, nao_cadastrados)
            confirmacao_a_mostar.append(document)
        if len(confirmacao_a_mostar) == 0:
            raise KeyError
        else:
            resposta = "OK"
            return resposta, nao_cadastrados
    if tipo == 'Solicitação':
        busca = Importacoes.objects.filter(mes=mes, ano=ano, tipo='Solicitação').all()
        if busca:
            busca.delete()
        solicitacao_a_mostar = []
        nao_cadastrados = []

        for i, j in dados.iterrows():
            document, nao_cadastrados = salva_solicitacao(j, request.user, mes, ano, nao_cadastrados)
            solicitacao_a_mostar.append(document)

        if len(solicitacao_a_mostar) == 0:
            raise KeyError
        else:
            resposta = "OK"
            return resposta, nao_cadastrados


def processa_horas_extras(request):
    try:
        if request.method == "POST":
            data = request.POST['data']
            ano, mes = int(str(data).split('-')[0]), int(str(data).split('-')[1])
            planilha_frequencia = request.FILES.getlist("frequencia")
            planilha_banco_mes = request.FILES.get("banco_mes")
            planilha_banco_total = request.FILES.get("banco_total")
            try:
                if planilha_frequencia != '':
                    processa_frequencia(request, planilha_frequencia, mes, ano)
            except ValueError:
                pass
            finally:
                try:
                    if planilha_banco_mes is not None:
                        processa_banco_mes(request, planilha_banco_mes, mes, ano)
                except ValueError:
                    pass
                finally:
                    try:
                        if planilha_banco_total is not None:
                            processa_banco_total(request, planilha_banco_total, mes, ano)
                        resposta = "OK"
                        return mes, ano, resposta
                    except ValueError:
                        if not planilha_frequencia and not planilha_banco_mes:
                            resposta = 'sem arquivos'
                            return mes, ano, resposta
                        else:
                            resposta = "OK"
                            return mes, ano, resposta
    except KeyError as error:
        print(error)
        resposta = "arquivo_vazio"
        data = request.POST['data']
        ano, mes = int(str(data).split('-')[0]), int(str(data).split('-')[1])
        return mes, ano, resposta


def processa_frequencia(request, planilha, mes, ano):
    busca = Importacoes.objects.filter(mes=mes, ano=ano, tipo='frequencia').all()
    if busca:
        busca.delete()
    frequencias_a_mostrar = []
    frequencia, data_min, data_max = arruma_frequencia(planilha)
    for i, j in frequencia.iterrows():
        fields = j
        document = salva_frequencia(fields, request.user, mes, ano)
        frequencias_a_mostrar.append(document)
    if len(frequencias_a_mostrar) == 0:
        raise KeyError


def processa_banco_total(request, planilha_banco_total, mes, ano):
    busca = Importacoes.objects.filter(mes=mes, ano=ano, tipo='banco_total').all()
    if busca:
        busca.delete()
    banco_total = arruma_banco(planilha_banco_total)
    banco_total_a_mostrar = []

    for i, j in banco_total.iterrows():
        fields = j
        document = salva_banco_total(fields, request.user, mes, ano)
        banco_total_a_mostrar.append(document)
    if len(banco_total_a_mostrar) == 0:
        raise KeyError


def processa_banco_mes(request, planilha_banco_mes, mes, ano):
    busca = Importacoes.objects.filter(mes=mes, ano=ano, tipo='banco_mes').all()
    if busca:
        busca.delete()
    banco_mes = arruma_saldo_mes(planilha_banco_mes)
    banco_mes_a_mostrar = []

    for i, j in banco_mes.iterrows():
        fields = j
        document = salva_banco_mes(fields, request.user, mes, ano)
        banco_mes_a_mostrar.append(document)

    if len(banco_mes_a_mostrar) == 0:
        raise KeyError
