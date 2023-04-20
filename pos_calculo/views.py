import pandas as pd
from django.shortcuts import render

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from empregados.models import Empregado
from pos_calculo.rejeitar import Diurno, Noturno, VinteQuatroHoras
from relatorios.models import RelatorioRejeitarBatidas


def rejeitar_batidas(request):
    rejeitadas = []
    if request.method == "POST":
        data = request.POST.get('data')
        mes = int(str(data).split('-')[1])
        ano = int(str(data).split('-')[0])
        matricula = request.POST.get('matricula')

        service = Service("chromedriver.exe")
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # options.add_argument("--headless")
        # Giving the path of chromedriver to selenium webdriver
        driver = webdriver.Chrome(service=service, options=options)

        # URL of the login page of site
        # which you want to automate login.
        url = "https://sigp.ebserh.gov.br/csp/ebserh/index.csp"

        driver.get(url)
        driver.stop_client()
        driver.get(url)

        wait = WebDriverWait(driver, 30)
        wait.until(ec.presence_of_element_located((By.LINK_TEXT, 'Registro de Frequência')))
        frequencia = driver.find_element(By.LINK_TEXT, 'Registro de Frequência')
        frequencia.click()

        wait = WebDriverWait(driver, 10)
        wait.until(ec.presence_of_element_located((By.ID, 'frame1')))

        frame1 = driver.find_element(By.ID, 'frame1')
        driver.switch_to.frame(frame1)

        c = 0

        if matricula == '':
            diurnos = RelatorioRejeitarBatidas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                              tipo='D').values()
            diurnos = pd.DataFrame(diurnos)
            diurnos.columns = diurnos.columns.str.replace('dia', '')
            diurnos = pega_matricula(diurnos, mes, ano)
            diurnos = diurnos.drop(columns={'id', 'empregado_id', 'importacao_id', 'importacao_id',
                                            'importado_por', 'importado_por_id', 'data_upload'})
            print(diurnos)
            c = Diurno(diurnos, driver, c)

            noturnos = RelatorioRejeitarBatidas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                               tipo='N').values()
            noturnos = pd.DataFrame(noturnos)
            noturnos.columns = noturnos.columns.str.replace('dia', '')
            noturnos = pega_matricula(noturnos, mes, ano)
            noturnos = noturnos.drop(columns={'id', 'empregado_id', 'importacao_id', 'importacao_id',
                                              'importado_por', 'importado_por_id', 'data_upload'})
            print(noturnos)
            c = Noturno(noturnos, driver, c)

            diurno_noturno = RelatorioRejeitarBatidas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                                     tipo='DN').values()
            diurno_noturno = pd.DataFrame(diurno_noturno)
            diurno_noturno = diurno_noturno.drop(columns={'id', 'empregado_id', 'importacao_id', 'importacao_id',
                                                          'importado_por', 'importado_por_id', 'data_upload'})
            diurno_noturno.columns = diurno_noturno.columns.str.replace('dia', '')
            diurno_noturno = pega_matricula(diurno_noturno, mes, ano)
            print(diurno_noturno)
            c = VinteQuatroHoras(diurno_noturno, driver, c)

        else:
            diurnos = RelatorioRejeitarBatidas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                              tipo='D', empregado__matricula=matricula).values()
            diurnos = pd.DataFrame(diurnos)
            diurnos.columns = diurnos.columns.str.replace('dia', '')
            diurnos = pega_matricula(diurnos, mes, ano)
            diurnos = diurnos.drop(columns={'id', 'empregado_id', 'importacao_id', 'importacao_id',
                                            'importado_por', 'importado_por_id', 'data_upload'})
            print(diurnos)
            c = Diurno(diurnos, driver, c)

            noturnos = RelatorioRejeitarBatidas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                               tipo='N', empregado__matricula=matricula).values()
            noturnos = pd.DataFrame(noturnos)
            noturnos.columns = noturnos.columns.str.replace('dia', '')
            noturnos = pega_matricula(noturnos, mes, ano)
            noturnos = noturnos.drop(columns={'id', 'empregado_id', 'importacao_id', 'importacao_id',
                                              'importado_por', 'importado_por_id', 'data_upload'})
            print(noturnos)
            c = Noturno(noturnos, driver, c)

            diurno_noturno = RelatorioRejeitarBatidas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                                     tipo='DN', empregado__matricula=matricula).values()
            diurno_noturno = pd.DataFrame(diurno_noturno)
            diurno_noturno.columns = diurno_noturno.columns.str.replace('dia', '')
            diurno_noturno = pega_matricula(diurno_noturno, mes, ano)
            diurno_noturno = diurno_noturno.drop(columns={'id', 'empregado_id', 'importacao_id', 'importacao_id',
                                                          'importado_por', 'importado_por_id', 'data_upload'})
            print(diurno_noturno)
            c = VinteQuatroHoras(diurno_noturno, driver, c)

    return render(request, "pos_calculo/rejeitar_batidas.html")


def pega_matricula(df, mes, ano):
    empregados = Empregado.objects.filter(mes=mes, ano=ano).values()
    empregados = pd.DataFrame(empregados)
    for i, j in df.iterrows():
        matricula = int(empregados[empregados['id'] == j['empregado_id']]['matricula'].values)
        df.at[i, 'matricula'] = matricula
    coluna_matricula = df['matricula']
    df = df.drop(columns={'matricula'})
    df.insert(0, 'matricula', coluna_matricula)
    df['matricula'] = df['matricula'].astype(int)
    return df


def login(driver, username, password):
    username_input = driver.find_element(By.ID, 'login')
    username_input.send_keys(username)

    # Find the password input by inspecting on password input
    password_input = driver.find_element(By.ID, 'senha')
    password_input.send_keys(password)

    # Click on submit
    submit_button = driver.find_element(By.CLASS_NAME, 'btn-primary')
    submit_button.click()
