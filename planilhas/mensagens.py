from django.contrib import messages

from planilhas.upload import arruma_dados_planilha


def DataLimite(request, tipo, maximo_s, maximo_c, hoje):
    if tipo.capitalize() == 'Confirmação' and hoje > maximo_c:
        messages.error(request, f'A data limite para {tipo} de horas extras foi '
                                f'{maximo_c.strftime("%d/%m/%Y")}.')

        return True

    if tipo.capitalize() == 'Solicitação' and hoje > maximo_s:
        messages.error(request, f'A data limite para {tipo} de horas extras foi '
                                f'{maximo_s.strftime("%d/%m/%Y")}.')

        return True


def ValidaResposta(request, resposta, dados, mes, ano, tipo, planilhas_com_erro, setor):
    if resposta == "formato_não_suportado":
        messages.error(request, "Formato de arquivo não suportado")
    if resposta == "arquivo_vazio":
        messages.error(request, "Arquivo não pode ser vazio!")
    if resposta == 'OK':
        resposta2, nao_cadastrados = arruma_dados_planilha(request, dados, mes, ano, tipo, setor)
        if len(nao_cadastrados) > 0:
            messages.error(request, f"Empregados não cadastrados: {nao_cadastrados}")
        if len(planilhas_com_erro) > 0:
            messages.error(request, f"Planilhas com erro: {planilhas_com_erro}")
        if resposta2 == "dados_inválidos":
            messages.error(request, "Arquivo com dados inválidos!")
        if resposta2 == "arquivo_vazio":
            messages.error(request, "Arquivo não pode ser vazio!")
        if resposta2 == "OK":
            messages.success(request, 'Importação efetuada com sucesso! Clique em '
                                      '"VISUALIZAR PLANILHAS" e selecione o setor para imprimir')
