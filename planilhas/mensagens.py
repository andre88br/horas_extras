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


def ValidaResposta(usuario, resposta, dados, mes, ano, tipo, planilhas_com_erro, setor, progress_callback=None):
    if resposta == "formato_não_suportado":
        return "Formato de arquivo não suportado", 'error'
    if resposta == "arquivo_vazio":
        return "Arquivo não pode ser vazio!", 'error'
    if resposta == 'OK':
        resposta2, nao_cadastrados = arruma_dados_planilha(usuario, dados, mes, ano, tipo, setor,
                                                            progress_callback=progress_callback)
        mensagens = []
        nivel = 'success'
        if len(nao_cadastrados) > 0:
            mensagens.append(f"Empregados não cadastrados: {nao_cadastrados}")
            nivel = 'error'
        if len(planilhas_com_erro) > 0:
            mensagens.append(f"Planilhas com erro: {planilhas_com_erro}")
            nivel = 'error'
        if resposta2 == "dados_inválidos":
            mensagens.append("Arquivo com dados inválidos!")
            nivel = 'error'
        if resposta2 == "arquivo_vazio":
            mensagens.append("Arquivo não pode ser vazio!")
            nivel = 'error'
        if resposta2 == "OK":
            mensagens.append('Importação efetuada com sucesso! Clique em '
                             '"VISUALIZAR PLANILHAS" e selecione o setor para imprimir')
        return ' | '.join(mensagens), nivel
    return '', 'info'
