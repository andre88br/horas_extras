import pandas as pd
from django.shortcuts import render

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from empregados.models import Empregado
from pos_calculo.processamento import pega_matricula, rejeita_todos, rejeita_especifico, inicia_driver, \
    clica_frequencia, clica_banco, recalcula_todos, recalcula_especifico
from pos_calculo.rejeitar import Diurno, Noturno, VinteQuatroHoras
from relatorios.models import RelatorioRejeitarBatidas


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

        driver = inicia_driver()
        clica_banco(driver)

        c = 0

        if matricula == '':
            recalcula_todos(mes, ano, driver, c)
        else:
            recalcula_especifico(mes, ano, driver, c, matricula)
    return render(request, "pos_calculo/recalcular_banco.html")


