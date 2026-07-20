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


def processa_horas_extras(usuario, mes, ano, planilha_frequencia, planilha_banco_mes, planilha_banco_total,
                          progress_callback=None):
    try:
        try:
            if planilha_frequencia != '' and planilha_frequencia is not None:
                processa_frequencia(usuario, planilha_frequencia, mes, ano, progress_callback=progress_callback)
        except ValueError:
            pass
        finally:
            try:
                if planilha_banco_mes is not None:
                    processa_banco_mes(usuario, planilha_banco_mes, mes, ano, progress_callback=progress_callback)
            except ValueError:
                pass
            finally:
                try:
                    if planilha_banco_total is not None:
                        processa_banco_total(usuario, planilha_banco_total, mes, ano,
                                             progress_callback=progress_callback)
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
        return mes, ano, resposta


def processa_frequencia(usuario, planilha, mes, ano, progress_callback=None):
    frequencias_a_mostrar = []
    frequencia, data_min, data_max = arruma_frequencia(planilha)
    total = len(frequencia) or 1
    for indice, (i, j) in enumerate(frequencia.iterrows()):
        fields = j
        document = salva_frequencia(fields, usuario, mes, ano)
        frequencias_a_mostrar.append(document)
        if progress_callback:
            progress_callback(int((indice + 1) / total * 100), 'Importando frequência...')
    if len(frequencias_a_mostrar) == 0:
        raise KeyError


def processa_banco_total(usuario, planilha_banco_total, mes, ano, progress_callback=None):
    banco_total = arruma_banco(planilha_banco_total)
    banco_total_a_mostrar = []
    total = len(banco_total) or 1

    for indice, (i, j) in enumerate(banco_total.iterrows()):
        fields = j
        document = salva_banco_total(fields, usuario, mes, ano)
        banco_total_a_mostrar.append(document)
        if progress_callback:
            progress_callback(int((indice + 1) / total * 100), 'Importando banco de horas...')
    if len(banco_total_a_mostrar) == 0:
        raise KeyError


def processa_banco_mes(usuario, planilha_banco_mes, mes, ano, progress_callback=None):
    banco_mes = arruma_saldo_mes(planilha_banco_mes)
    banco_mes_a_mostrar = []
    total = len(banco_mes) or 1

    for indice, (i, j) in enumerate(banco_mes.iterrows()):
        fields = j
        document = salva_banco_mes(fields, usuario, mes, ano)
        banco_mes_a_mostrar.append(document)
        if progress_callback:
            progress_callback(int((indice + 1) / total * 100), 'Importando saldo de horas do mês...')

    if len(banco_mes_a_mostrar) == 0:
        raise KeyError


def arruma_dados_do_arquivo(request, dados, mes, ano, tipo, progress_callback=None):
    total = len(dados) or 1
    if tipo == 'Confirmação':
        busca = Importacoes.objects.filter(mes=mes, ano=ano, tipo='confirmação').all()
        if busca:
            busca.delete()

        confirmacao_a_mostar = []
        nao_cadastrados = []

        for indice, (i, j) in enumerate(dados.iterrows()):
            document, nao_cadastrados = salva_confirmacao(j, request.user, mes, ano, nao_cadastrados)
            confirmacao_a_mostar.append(document)
            if progress_callback:
                progress_callback(int((indice + 1) / total * 100), 'Importando confirmação...')
        if len(confirmacao_a_mostar) == 0:
            raise KeyError
        else:
            resposta = "OK"
            return resposta, nao_cadastrados
    if tipo == 'Solicitação':
        busca = Importacoes.objects.filter(mes=mes, ano=ano, tipo='solicitação').all()
        if busca:
            busca.delete()
        solicitacao_a_mostar = []
        nao_cadastrados = []

        for indice, (i, j) in enumerate(dados.iterrows()):
            document, nao_cadastrados = salva_solicitacao(j, request.user, mes, ano, nao_cadastrados)
            solicitacao_a_mostar.append(document)
            if progress_callback:
                progress_callback(int((indice + 1) / total * 100), 'Importando solicitação...')

        if len(solicitacao_a_mostar) == 0:
            raise KeyError
        else:
            resposta = "OK"
            return resposta, nao_cadastrados
