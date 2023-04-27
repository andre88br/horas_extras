from django.contrib import messages
from django.shortcuts import render

from pos_calculo.processamento import rejeita_todos, rejeita_especifico, inicia_driver, \
    clica_frequencia, clica_banco, recalcula_todos, recalcula_especifico, lanca_todos, lanca_especifico


def rejeitar_batidas(request):
    rejeitadas = []
    if request.method == "POST":
        data = request.POST.get('data')
        mes = int(str(data).split('-')[1])
        ano = int(str(data).split('-')[0])
        matricula = request.POST.get('matricula')

        driver = inicia_driver()
        clica_frequencia(driver)
        c = 0
        if matricula == '':
            rejeita_todos(mes, ano, driver, c)
        else:
            rejeita_especifico(mes, ano, driver, c, matricula)
    return render(request, "pos_calculo/rejeitar_batidas.html")


def recalcular_banco(request):
    if request.method == "POST":
        data = request.POST.get('data')
        mes = int(str(data).split('-')[1])
        ano = int(str(data).split('-')[0])
        matricula = request.POST.get('matricula')
        processo = request.POST.get('processo')

        if matricula == '':
            resposta = recalcula_todos(mes, ano, processo)
        else:
            resposta = recalcula_especifico(mes, ano, matricula, processo)

        if int(mes) < 10:
            mes = f'0{mes}'

        if resposta == 'ok':
            messages.success(request, 'Bancos calculados com sucesso')
        else:
            messages.error(request, f'Matrícula não localizada na confirmação de horas extras do mês de {mes}/{ano}')
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
        processo = request.POST.get('processo')

        if matricula == '':
            resposta = lanca_todos(mes, ano, mes_folha, ano_folha,  processo)
        else:
            resposta = lanca_especifico(mes, ano, mes_folha, ano_folha, matricula, processo)

        if int(mes) < 10:
            mes = f'0{mes}'

        if resposta == 'ok':
            messages.success(request, 'Rubricas lançadas com sucesso')
        else:
            messages.error(request, f'Matrícula não localizada na confirmação de horas extras do mês de {mes}/{ano}')

    return render(request, "pos_calculo/pagamento.html")


