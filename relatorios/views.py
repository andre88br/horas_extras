import base64
import os

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render

from horas_extras.calcula import calcula_he
from relatorios.processa_relatorios import gera_relatorio_solicitacao, gera_relatorio_erros, \
    gera_relatorio_confirmacao, gera_relatorio_entrada_saida, gera_relatorio_codigo90, \
    gera_relatorio_negativos, gera_relatorio_rejeitar_batidas, gera_relatorio_pagas, gera_relatorio_setores, \
    gera_relatorio_rejeitadas, gera_voltar_negativos, gera_escalas_voltadas
from tarefas.executor import iniciar_tarefa


def _despacha_relatorio(tipo, mes, ano, mes2, ano2, matricula, tipo3, progress_callback):
    if tipo in ('erros2', 'erros'):
        return gera_relatorio_erros(mes, ano, mes2, ano2, tipo3, matricula, progress_callback=progress_callback)
    if tipo == 'confirmacao':
        return gera_relatorio_confirmacao(mes, ano, mes2, ano2, matricula, progress_callback=progress_callback)
    if tipo == 'entrada_saida':
        return gera_relatorio_entrada_saida(mes, ano, mes2, ano2, matricula, progress_callback=progress_callback)
    if tipo == 'cod_90':
        return gera_relatorio_codigo90(mes, ano, mes2, ano2, matricula, progress_callback=progress_callback)
    if tipo == 'negativos':
        return gera_relatorio_negativos(mes, ano, mes2, ano2, tipo3, matricula, progress_callback=progress_callback)
    if tipo == 'rejeitar_batidas':
        return gera_relatorio_rejeitar_batidas(mes, ano, mes2, ano2, matricula, progress_callback=progress_callback)
    if tipo == 'pagas':
        return gera_relatorio_pagas(mes, ano, matricula, mes2, ano2, progress_callback=progress_callback)
    if tipo == 'setores':
        return gera_relatorio_setores(mes, ano, mes2, ano2, progress_callback=progress_callback)
    if tipo == 'rejeitadas':
        return gera_relatorio_rejeitadas(mes, ano, mes2, ano2, matricula, progress_callback=progress_callback)
    if tipo == 'voltar_negativos':
        return gera_voltar_negativos(mes, ano, progress_callback=progress_callback)
    if tipo == 'escalas_voltadas':
        return gera_escalas_voltadas(mes, ano, progress_callback=progress_callback)
    return '', '', ''


def _despacha_relatorio_imprime(tipo2, mes, ano, mes2, ano2, matricula, tipo3, progress_callback):
    if tipo2 == 'solicitacao':
        return gera_relatorio_solicitacao(mes, ano, mes2, ano2, matricula, progress_callback=progress_callback)
    if tipo2 == 'erros2':
        return gera_relatorio_erros(mes, ano, mes2, ano2, 'solicitacao', matricula,
                                    progress_callback=progress_callback)
    if tipo2 == 'confirmacao':
        return gera_relatorio_confirmacao(mes, ano, mes2, ano2, matricula, progress_callback=progress_callback)
    if tipo2 == 'erros':
        return gera_relatorio_erros(mes, ano, mes2, ano2, 'confirmacao', matricula,
                                    progress_callback=progress_callback)
    if tipo2 == 'entrada_saida':
        return gera_relatorio_entrada_saida(mes, ano, mes2, ano2, matricula, progress_callback=progress_callback)
    if tipo2 == 'cod_90':
        return gera_relatorio_codigo90(mes, ano, mes2, ano2, matricula, progress_callback=progress_callback)
    if tipo2 == 'negativos':
        sub_tipo = tipo3 if tipo3 != '' else 'confirmacao'
        return gera_relatorio_negativos(mes, ano, mes2, ano2, sub_tipo, matricula,
                                        progress_callback=progress_callback)
    if tipo2 == 'negativos2':
        return gera_relatorio_negativos(mes, ano, mes2, ano2, 'solicitacao', matricula,
                                        progress_callback=progress_callback)
    if tipo2 == 'rejeitar_batidas':
        return gera_relatorio_rejeitar_batidas(mes, ano, mes2, ano2, matricula, progress_callback=progress_callback)
    if tipo2 == 'rejeitadas':
        return gera_relatorio_rejeitadas(mes, ano, mes2, ano2, matricula, progress_callback=progress_callback)
    if tipo2 == 'pagas':
        return gera_relatorio_pagas(mes, ano, matricula, mes2, ano2, progress_callback=progress_callback)
    if tipo2 == 'setores':
        return gera_relatorio_setores(mes, ano, mes2, ano2, progress_callback=progress_callback)
    if tipo2 == 'voltar_negativos':
        return gera_voltar_negativos(mes, ano, progress_callback=progress_callback)
    if tipo2 == 'escalas_voltadas':
        return gera_escalas_voltadas(mes, ano, progress_callback=progress_callback)
    return '', '', ''


def relatorios(request):
    if request.user.is_authenticated:
        return render(request, "relatorios/relatorios.html")
    else:
        return render(request, "usuarios/login.html")


def gera_relatorio(request):
    if request.user.is_authenticated:
        relatorio = ''
        nome = ''
        response1, response2 = '', ''
        tipo = request.POST.get('tipo')
        matricula = request.POST.get('matricula')
        final = request.POST.get('final')
        data_inicial = request.POST['data_inicial']
        data_final = request.POST['data_final']
        ano, mes = str(data_inicial).split('-')
        ano2, mes2 = str(data_final).split('-')
        usuario = request.user
        if tipo == 'solicitadas_mes':
            relatorio = gera_relatorio_solicitacao(mes, ano, mes2, ano2, matricula)

        if tipo == 'pagas_mes':
            relatorio, conclusao, response1, response2 = calcula_he(ano, mes, usuario, final)
            relatorio['saldo_mes_decimal'] = relatorio['saldo_mes_decimal'].map(lambda x: format(x, '.2f'))
            relatorio['saldo_banco_decimal'] = relatorio['saldo_banco_decimal'].map(lambda x: format(x, '.2f'))
            relatorio['horas_trabalhadas'] = relatorio['horas_trabalhadas'].map(lambda x: format(x, '.2f'))
            relatorio['horas_diurnas'] = relatorio['horas_diurnas'].map(lambda x: format(x, '.2f'))
            relatorio['horas_noturnas'] = relatorio['horas_noturnas'].map(lambda x: format(x, '.2f'))

            relatorio = relatorio.head(1000)
            relatorio = relatorio.to_html(index=True)
            nome = f'Horas extras pagas - {mes}/{ano}'
            messages.info(request, conclusao)

        return render(request, "relatorios.html", context={'relatorio': relatorio,
                                                           'nome': nome, 'mes': mes, 'ano': ano,
                                                           'response1': response1, 'response2': response2})
    else:
        return render(request, "usuarios/login.html")


def escolhe_relatorio(request):
    try:
        if request.user.is_authenticated:
            arquivo, response, df = '', '', ''
            tipo = request.POST.get('tipo')
            tipo3 = request.POST.get('tipo3')
            matricula = request.POST.get('matricula')
            data = request.POST.get('data')
            data2 = request.POST.get('data2')
            ano, mes = str(data).split('-')[0], str(data).split('-')[1]
            if data2 != '' and data2 is not None:
                ano2, mes2 = str(data2).split('-')[0], str(data2).split('-')[1]
            else:
                ano2, mes2 = '', ''

            if tipo == 'solicitacao':
                def worker(progress_callback):
                    response, arquivo, df = gera_relatorio_solicitacao(
                        mes, ano, mes2, ano2, matricula, progress_callback=progress_callback)
                    if not response:
                        return {
                            'mensagem': 'Relatório não disponível!', 'nivel': 'error',
                            'contexto_extra': {'mes': mes, 'ano': ano, 'mes2': mes2, 'ano2': ano2,
                                                'matricula': matricula, 'tipo': tipo, 'tipo3': tipo3},
                        }

                    diretorio = os.getcwd()
                    for i in os.listdir(diretorio):
                        if i == arquivo:
                            os.remove(os.path.join(diretorio, arquivo))
                    nome = arquivo.replace('-', '/').replace('.xlsx', '').replace('.txt', '')

                    return {
                        'mensagem': '',
                        'nivel': 'info',
                        'resultado_html': df.to_html(index=False),
                        'contexto_extra': {'nome': nome, 'mes': mes, 'ano': ano, 'mes2': mes2, 'ano2': ano2,
                                            'matricula': matricula, 'tipo': tipo, 'tipo3': tipo3},
                    }

                tarefa = iniciar_tarefa(
                    tipo='relatorios.gera_relatorio_solicitacao', usuario=request.user,
                    template_resultado='relatorios/relatorios.html', func=worker,
                )
                return redirect('tarefa_acompanhar', tarefa_id=tarefa.id)

            def worker(progress_callback):
                response, arquivo, df = _despacha_relatorio(tipo, mes, ano, mes2, ano2, matricula, tipo3,
                                                            progress_callback)
                contexto_base = {'mes': mes, 'ano': ano, 'mes2': mes2, 'ano2': ano2,
                                  'matricula': matricula, 'tipo': tipo, 'tipo3': tipo3}
                if not response:
                    return {'mensagem': 'Relatório não disponível!', 'nivel': 'error',
                            'contexto_extra': contexto_base}

                diretorio = os.getcwd()
                for i in os.listdir(diretorio):
                    if i == arquivo:
                        os.remove(os.path.join(diretorio, arquivo))
                nome = arquivo.replace('-', '/').replace('.xlsx', '').replace('.txt', '')

                return {
                    'mensagem': '', 'nivel': 'info',
                    'resultado_html': df.to_html(index=False),
                    'contexto_extra': {**contexto_base, 'nome': nome},
                }

            tarefa = iniciar_tarefa(
                tipo=f'relatorios.escolhe_relatorio.{tipo}', usuario=request.user,
                template_resultado='relatorios/relatorios.html', func=worker,
            )
            return redirect('tarefa_acompanhar', tarefa_id=tarefa.id)
    except Exception as e:
        messages.error(request, f'Erro {e}')
        return render(request, "relatorios/relatorios.html")
    else:
        return render(request, "usuarios/login.html")


def imprime(request):
    if request.user.is_authenticated:
        mes = request.POST.get('mes')
        ano = request.POST.get('ano')
        mes2 = request.POST.get('mes2')
        ano2 = request.POST.get('ano2')
        tipo2 = request.POST.get('tipo2')
        matricula = request.POST.get('matricula')
        tipo3 = request.POST.get('tipo3')
        pagina = request.POST.get('pagina')
        relatorio_anterior = request.POST.get('relatorio')
        nome_anterior = request.POST.get('nome')
        tipo_anterior = request.POST.get('tipo')

        def worker(progress_callback):
            response, arquivo, df = _despacha_relatorio_imprime(tipo2, mes, ano, mes2, ano2, matricula, tipo3,
                                                                 progress_callback)

            diretorio = os.getcwd()
            for i in os.listdir(diretorio):
                if i == arquivo:
                    os.remove(os.path.join(diretorio, arquivo))

            if response == '':
                if pagina == 'processar':
                    return {'mensagem': 'Relatório não disponível!', 'nivel': 'error',
                            'contexto_extra': {'relatorio': relatorio_anterior, 'nome': nome_anterior, 'mes': mes,
                                                'ano': ano, 'tipo': tipo_anterior, 'matricula': matricula}}
                if pagina == 'reprocessar':
                    return {'mensagem': 'Relatório não disponível!', 'nivel': 'error',
                            'contexto_extra': {'relatorio': relatorio_anterior, 'nome': nome_anterior, 'mes': mes,
                                                'ano': ano, 'tipo': tipo_anterior, 'matricula': matricula}}
                return {'mensagem': 'Relatório não disponível!', 'nivel': 'error'}

            return {
                'mensagem': '', 'nivel': 'info',
                'contexto_extra': {
                    '_arquivo_base64': base64.b64encode(response.content).decode('ascii'),
                    '_arquivo_content_type': response.get('Content-Type', 'application/octet-stream'),
                    '_arquivo_nome': response.get('Content-Disposition', '').split('filename=')[-1].strip('"'),
                },
            }

        if pagina == 'processar':
            template_resultado = 'horas_extras/processar.html'
        elif pagina == 'reprocessar':
            template_resultado = 'horas_extras/reprocessar.html'
        else:
            template_resultado = 'relatorios/relatorios.html'
        tarefa = iniciar_tarefa(
            tipo=f'relatorios.imprime.{tipo2}', usuario=request.user,
            template_resultado=template_resultado, func=worker,
        )
        return redirect('tarefa_acompanhar', tarefa_id=tarefa.id)
    else:
        return render(request, "usuarios/login.html")
