from django.contrib import messages
from django.shortcuts import render

from pos_calculo.processamento import rejeita_todos, rejeita_especifico, inicia_driver, \
    clica_frequencia, recalcula_todos, recalcula_especifico, lanca_todos, lanca_especifico, voltar_todos, \
    recalcula_negativos, clica_horario_excepcional
from pos_calculo.tirar_escala import tirar_escala
from pos_calculo.voltar_negativos import voltar_escala


def rejeitar_batidas(request):
    try:
        if request.method == "POST":
            data = request.POST.get('data')
            mes = int(str(data).split('-')[1])
            ano = int(str(data).split('-')[0])
            matricula = request.POST.get('matricula')

            driver = inicia_driver()
            clica_frequencia(driver)
            c = 0
            if matricula == '':
                rejeita_todos(mes, ano, driver, c, request.user)
            else:
                rejeita_especifico(mes, ano, driver, c, matricula, request.user)
            messages.success(request, 'Batidas rejeitadas com sucesso')
    except Exception as error:
        messages.error(request, f'Erro: {error}')
    return render(request, "pos_calculo/rejeitar_batidas.html")


def recalcular_banco(request):
    try:
        if request.method == "POST":
            data = request.POST.get('data')
            mes = int(str(data).split('-')[1])
            ano = int(str(data).split('-')[0])
            matricula = request.POST.get('matricula')
            processo = request.POST.get('processo')

            if matricula == '':
                resposta = recalcula_todos(mes, ano, processo, request.user)
            else:
                resposta = recalcula_especifico(mes, ano, matricula, processo, request.user)

            if int(mes) < 10:
                mes = f'0{mes}'

            if resposta == 'ok':
                messages.success(request, 'Bancos calculados com sucesso')
            else:
                messages.error(request, f'Matrícula não localizada na confirmação de horas extras do mês de {mes}/{ano}')
    except Exception as error:
        messages.error(request, f'Erro: {error}')
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

        if matricula == '':
            resposta = lanca_todos(mes, ano, mes_folha, ano_folha, fator, processo, request.user)
        else:
            resposta = lanca_especifico(mes, ano, mes_folha, ano_folha, matricula, fator, processo, request.user)

        if int(mes) < 10:
            mes = f'0{mes}'

        if resposta == 'ok':
            messages.success(request, 'Rubricas lançadas com sucesso')
        else:
            messages.error(request, f'Matrícula não localizada na confirmação de horas extras do mês de {mes}/{ano}')

    return render(request, "pos_calculo/pagamento.html")


def voltar_batidas(request):
    try:
        if request.method == "POST":
            data = request.POST.get('data')
            mes = int(str(data).split('-')[1])
            ano = int(str(data).split('-')[0])

            driver = inicia_driver()
            clica_frequencia(driver)
            c = 0
            voltar_todos(mes, ano, driver, c, request.user)
            messages.success(request, 'Batidas desrejeitadas com sucesso')
    except Exception as error:
        messages.error(request, f'Erro: {error}')
    return render(request, "pos_calculo/voltar_batidas.html")


def voltar_escalas(request):
    if request.method == "POST":
        data = request.POST.get('data')
        mes = int(str(data).split('-')[1])
        ano = int(str(data).split('-')[0])
        try:
            driver = inicia_driver()
            clica_horario_excepcional(driver)
            c = 0
            voltar_escala(mes, ano, driver, c, request.user)
            messages.success(request, 'Escalas incluídas com sucesso')
        except Exception as error:
            if str(error) == "'matricula'":
                messages.error(request, f'Sem escalas para voltar do mês de {mes}/{ano}')
            else:
                messages.error(request, f'Erro: {error}')
    return render(request, "pos_calculo/voltar_escalas.html")


def recalcular_negativos(request):
    try:
        if request.method == "POST":
            data = request.POST.get('data')
            mes = int(str(data).split('-')[1])
            ano = int(str(data).split('-')[0])
            processo = request.POST.get('processo')

            resposta = recalcula_negativos(mes, ano, processo, request.user)

            if int(mes) < 10:
                mes = f'0{mes}'

            if resposta == 'ok':
                messages.success(request, 'Bancos calculados com sucesso')
            else:
                messages.error(request, f'Matrícula não localizada na confirmação de horas extras do mês de {mes}/{ano}')
    except Exception as error:
        messages.error(request, f'Erro: {error}')
    return render(request, "pos_calculo/recalcular_negativos.html")


def excluir_escalas(request):
    if request.method == "POST":
        data = request.POST.get('data')
        mes = int(str(data).split('-')[1])
        ano = int(str(data).split('-')[0])
        try:
            driver = inicia_driver()
            clica_horario_excepcional(driver)
            print("horario_excepcional")
            c = 0
            tirar_escala(mes, ano, driver, c, request.user)
            messages.success(request, 'Escalas excluídas com sucesso')
        except Exception as error:
            if str(error) == "'matricula'":
                messages.error(request, f'Sem escalas para excluir do mês de {mes}/{ano}')
            else:
                messages.error(request, f'Erro: {error}')
    return render(request, "pos_calculo/excluir_escalas.html")