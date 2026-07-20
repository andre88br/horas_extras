from django.shortcuts import redirect, render

from pos_calculo.processamento import rejeita_todos, rejeita_especifico, inicia_driver, \
    clica_frequencia, recalcula_todos, recalcula_especifico, lanca_todos, lanca_especifico, voltar_todos, \
    recalcula_negativos, clica_horario_excepcional
from pos_calculo.tirar_escala import tirar_escala
from pos_calculo.voltar_negativos import voltar_escala
from tarefas.executor import iniciar_tarefa

_LOCK_SELENIUM = 'pos_calculo_selenium'


def rejeitar_batidas(request):
    if request.method == "POST":
        data = request.POST.get('data')
        mes = int(str(data).split('-')[1])
        ano = int(str(data).split('-')[0])
        matricula = request.POST.get('matricula')
        usuario = request.user

        def worker(progress_callback):
            progress_callback(10, 'Iniciando navegador...')
            driver = inicia_driver()
            try:
                clica_frequencia(driver)
                progress_callback(30, 'Rejeitando batidas...')
                c = 0
                if matricula == '':
                    rejeita_todos(mes, ano, driver, c, usuario)
                else:
                    rejeita_especifico(mes, ano, driver, c, matricula, usuario)
                return {'mensagem': 'Batidas rejeitadas com sucesso', 'nivel': 'success'}
            finally:
                driver.quit()

        tarefa = iniciar_tarefa(tipo='pos_calculo.rejeitar_batidas', usuario=usuario,
                                template_resultado='pos_calculo/rejeitar_batidas.html', func=worker,
                                lock_key=_LOCK_SELENIUM)
        return redirect('tarefa_acompanhar', tarefa_id=tarefa.id)
    return render(request, "pos_calculo/rejeitar_batidas.html")


def recalcular_banco(request):
    if request.method == "POST":
        data = request.POST.get('data')
        mes = int(str(data).split('-')[1])
        ano = int(str(data).split('-')[0])
        matricula = request.POST.get('matricula')
        processo = request.POST.get('processo')
        usuario = request.user

        def worker(progress_callback):
            progress_callback(10, 'Iniciando navegador...')
            if matricula == '':
                resposta = recalcula_todos(mes, ano, processo, usuario)
            else:
                resposta = recalcula_especifico(mes, ano, matricula, processo, usuario)
            mes_exibido = f'0{mes}' if mes < 10 else mes
            if resposta == 'ok':
                return {'mensagem': 'Bancos calculados com sucesso', 'nivel': 'success'}
            return {'mensagem': f'Matrícula não localizada na confirmação de horas extras do mês de '
                                f'{mes_exibido}/{ano}', 'nivel': 'error'}

        tarefa = iniciar_tarefa(tipo='pos_calculo.recalcular_banco', usuario=usuario,
                                template_resultado='pos_calculo/recalcular_banco.html', func=worker,
                                lock_key=_LOCK_SELENIUM)
        return redirect('tarefa_acompanhar', tarefa_id=tarefa.id)
    return render(request, "pos_calculo/recalcular_banco.html")


def pagamento(request):
    if request.method == "POST":
        data = request.POST.get('data')
        mes = int(str(data).split('-')[1])
        ano = int(str(data).split('-')[0])
        data_folha = request.POST.get('data_folha')
        mes_folha = int(str(data_folha).split('-')[1])
        ano_folha = int(str(data_folha).split('-')[0])
        matricula = request.POST.get('matricula')
        fator = request.POST.get('fator')
        processo = request.POST.get('processo')
        usuario = request.user

        if mes_folha < 10:
            mes_folha = f'0{mes_folha}'

        def worker(progress_callback):
            progress_callback(10, 'Iniciando navegador...')
            if matricula == '':
                resposta = lanca_todos(mes, ano, mes_folha, ano_folha, fator, processo, usuario)
            else:
                resposta = lanca_especifico(mes, ano, mes_folha, ano_folha, matricula, fator, processo, usuario)
            mes_exibido = f'0{mes}' if mes < 10 else mes
            if resposta == 'ok':
                return {'mensagem': 'Rubricas lançadas com sucesso', 'nivel': 'success'}
            return {'mensagem': f'Matrícula não localizada na confirmação de horas extras do mês de '
                                f'{mes_exibido}/{ano}', 'nivel': 'error'}

        tarefa = iniciar_tarefa(tipo='pos_calculo.pagamento', usuario=usuario,
                                template_resultado='pos_calculo/pagamento.html', func=worker,
                                lock_key=_LOCK_SELENIUM)
        return redirect('tarefa_acompanhar', tarefa_id=tarefa.id)
    return render(request, "pos_calculo/pagamento.html")


def voltar_batidas(request):
    if request.method == "POST":
        data = request.POST.get('data')
        mes = int(str(data).split('-')[1])
        ano = int(str(data).split('-')[0])
        usuario = request.user

        def worker(progress_callback):
            progress_callback(10, 'Iniciando navegador...')
            driver = inicia_driver()
            try:
                clica_frequencia(driver)
                progress_callback(30, 'Desrejeitando batidas...')
                c = 0
                voltar_todos(mes, ano, driver, c, usuario)
                return {'mensagem': 'Batidas desrejeitadas com sucesso', 'nivel': 'success'}
            finally:
                driver.quit()

        tarefa = iniciar_tarefa(tipo='pos_calculo.voltar_batidas', usuario=usuario,
                                template_resultado='pos_calculo/voltar_batidas.html', func=worker,
                                lock_key=_LOCK_SELENIUM)
        return redirect('tarefa_acompanhar', tarefa_id=tarefa.id)
    return render(request, "pos_calculo/voltar_batidas.html")


def voltar_escalas(request):
    if request.method == "POST":
        data = request.POST.get('data')
        mes = int(str(data).split('-')[1])
        ano = int(str(data).split('-')[0])
        usuario = request.user

        def worker(progress_callback):
            progress_callback(10, 'Iniciando navegador...')
            driver = inicia_driver()
            try:
                clica_horario_excepcional(driver)
                progress_callback(30, 'Incluindo escalas...')
                c = 0
                try:
                    voltar_escala(mes, ano, driver, c, usuario)
                except Exception as error:
                    if str(error) == "'matricula'":
                        return {'mensagem': f'Sem escalas para voltar do mês de {mes}/{ano}', 'nivel': 'error'}
                    raise
                return {'mensagem': 'Escalas incluídas com sucesso', 'nivel': 'success'}
            finally:
                driver.quit()

        tarefa = iniciar_tarefa(tipo='pos_calculo.voltar_escalas', usuario=usuario,
                                template_resultado='pos_calculo/voltar_escalas.html', func=worker,
                                lock_key=_LOCK_SELENIUM)
        return redirect('tarefa_acompanhar', tarefa_id=tarefa.id)
    return render(request, "pos_calculo/voltar_escalas.html")


def recalcular_negativos(request):
    if request.method == "POST":
        data = request.POST.get('data')
        mes = int(str(data).split('-')[1])
        ano = int(str(data).split('-')[0])
        processo = request.POST.get('processo')
        usuario = request.user

        def worker(progress_callback):
            progress_callback(10, 'Iniciando navegador...')
            resposta = recalcula_negativos(mes, ano, processo, usuario)
            mes_exibido = f'0{mes}' if mes < 10 else mes
            if resposta == 'ok':
                return {'mensagem': 'Bancos calculados com sucesso', 'nivel': 'success'}
            return {'mensagem': f'Matrícula não localizada na confirmação de horas extras do mês de '
                                f'{mes_exibido}/{ano}', 'nivel': 'error'}

        tarefa = iniciar_tarefa(tipo='pos_calculo.recalcular_negativos', usuario=usuario,
                                template_resultado='pos_calculo/recalcular_negativos.html', func=worker,
                                lock_key=_LOCK_SELENIUM)
        return redirect('tarefa_acompanhar', tarefa_id=tarefa.id)
    return render(request, "pos_calculo/recalcular_negativos.html")


def excluir_escalas(request):
    if request.method == "POST":
        data = request.POST.get('data')
        mes = int(str(data).split('-')[1])
        ano = int(str(data).split('-')[0])
        usuario = request.user

        def worker(progress_callback):
            progress_callback(10, 'Iniciando navegador...')
            driver = inicia_driver()
            try:
                clica_horario_excepcional(driver)
                progress_callback(30, 'Excluindo escalas...')
                c = 0
                try:
                    tirar_escala(mes, ano, driver, c, usuario)
                except Exception as error:
                    if str(error) == "'matricula'":
                        return {'mensagem': f'Sem escalas para excluir do mês de {mes}/{ano}', 'nivel': 'error'}
                    raise
                return {'mensagem': 'Escalas excluídas com sucesso', 'nivel': 'success'}
            finally:
                driver.quit()

        tarefa = iniciar_tarefa(tipo='pos_calculo.excluir_escalas', usuario=usuario,
                                template_resultado='pos_calculo/excluir_escalas.html', func=worker,
                                lock_key=_LOCK_SELENIUM)
        return redirect('tarefa_acompanhar', tarefa_id=tarefa.id)
    return render(request, "pos_calculo/excluir_escalas.html")
