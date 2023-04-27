import pandas as pd

from empregados.models import Empregado
from pos_calculo.lancamento import LancarRubricas
from pos_calculo.recalcular import RecalcularBanco
from pos_calculo.rejeitar import Diurno, Noturno, VinteQuatroHoras
from relatorios.models import RelatorioRejeitarBatidas, RelatorioConfirmacao, RelatorioPagas
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


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


def  inicia_driver():
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
    return driver


def clica_frequencia(driver):
    wait = WebDriverWait(driver, 30)
    wait.until(ec.presence_of_element_located((By.LINK_TEXT, 'Registro de Frequência')))
    frequencia = driver.find_element(By.LINK_TEXT, 'Registro de Frequência')
    frequencia.click()

    wait = WebDriverWait(driver, 30)
    wait.until(ec.presence_of_element_located((By.ID, 'frame1')))

    frame1 = driver.find_element(By.ID, 'frame1')
    driver.switch_to.frame(frame1)


def clica_banco(driver):
    wait = WebDriverWait(driver, 30)
    wait.until(ec.presence_of_element_located((By.LINK_TEXT, 'Recalcular BH Homologado')))

    recalcular_banco = driver.find_element(By.LINK_TEXT, 'Recalcular BH Homologado')
    recalcular_banco.click()

    wait = WebDriverWait(driver, 30)
    wait.until(ec.presence_of_element_located((By.ID, 'frame1')))

    frame1 = driver.find_element(By.ID, 'frame1')
    driver.switch_to.frame(frame1)


def clica_folha(driver):
    wait = WebDriverWait(driver, 120)
    wait.until(ec.presence_of_element_located((By.LINK_TEXT, 'Rubrica Individual')))

    rubrica_individual = driver.find_element(By.LINK_TEXT, 'Rubrica Individual')
    rubrica_individual.click()


def login(driver, username, password):
    username_input = driver.find_element(By.ID, 'login')
    username_input.send_keys(username)

    # Find the password input by inspecting on password input
    password_input = driver.find_element(By.ID, 'senha')
    password_input.send_keys(password)

    # Click on submit
    submit_button = driver.find_element(By.CLASS_NAME, 'btn-primary')
    submit_button.click()


def rejeita_todos(mes, ano, driver, c):
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


def rejeita_especifico(mes, ano, driver, c, matricula):
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


def recalcula_todos(mes, ano, processo):
    mes_ano = f'{mes}{ano}'
    observacao = f'Recalculo do banco de horas após processamento de horas extras, processo SEI {processo}'
    confirmacoes = RelatorioConfirmacao.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                       saldo_banco_decimal__gte=0, saldo_mes_decimal__gte=0,
                                                       valor_total__gt=0).values()
    if confirmacoes:
        driver = inicia_driver()
        clica_banco(driver)
        confirmacoes = pd.DataFrame(confirmacoes)
        pega_matricula(confirmacoes, mes, ano)
        confirmacoes['matricula'] = confirmacoes['matricula'].astype(int)
        confirmacoes = confirmacoes['matricula']
        RecalcularBanco(confirmacoes, driver, mes_ano, observacao)
        return 'ok'
    else:
        return 'erro'


def recalcula_especifico(mes, ano, matricula, processo):
    mes_ano = f'{mes}{ano}'
    observacao = f'Recalculo do banco de horas após processamento de horas extras, processo SEI {processo}'
    print(observacao)
    confirmacoes = RelatorioConfirmacao.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                       saldo_banco_decimal__gte=0, saldo_mes_decimal__gte=0,
                                                       empregado__matricula=matricula).values()
    if confirmacoes:
        driver = inicia_driver()
        clica_banco(driver)
        confirmacoes = pd.DataFrame(confirmacoes)
        confirmacoes = pd.DataFrame(confirmacoes)
        pega_matricula(confirmacoes, mes, ano)
        confirmacoes['matricula'] = confirmacoes['matricula'].astype(int)
        confirmacoes = confirmacoes['matricula']
        RecalcularBanco(confirmacoes, driver, mes_ano, observacao)
        return 'ok'
    else:
        return 'erro'


def lanca_todos(mes, ano, mes_folha, ano_folha, processo):
    folha = f'{mes_folha}/{ano_folha}'
    observacao = f'Recalculo do banco de horas após processamento de horas extras, processo SEI {processo}'
    confirmacoes = RelatorioPagas.objects.filter(importacao__mes=mes, importacao__ano=ano).values()
    if confirmacoes:
        driver = inicia_driver()
        login(driver, 'andre.ribeiro.1', 'l6r7w588')
        clica_folha(driver)
        confirmacoes = pd.DataFrame(confirmacoes)
        confirmacoes = pd.DataFrame(confirmacoes)
        pega_matricula(confirmacoes, mes, ano)
        confirmacoes['matricula'] = confirmacoes['matricula'].astype(int)
        confirmacoes['rubrica_diurna'] = ''
        confirmacoes['rubrica_noturna'] = ''
        for i, j in confirmacoes.iterrows():
            confirmacoes.at[i, 'rubrica_diurna'] = 81 if j['valor_diurnas'] > 0 else ''
            confirmacoes.at[i, 'rubrica_noturna'] = 878 if j['valor_noturnas'] > 0 else ''

        confirmacoes = confirmacoes.drop(columns={'id', 'cargo', 'empregado_id', 'importacao_id',
                                                  'data_upload', 'setor', 'qtd', 'valor_diurnas', 'valor_noturnas',
                                                  'total', 'importado_por', 'importado_por_id'})
        print(confirmacoes)

        LancarRubricas(confirmacoes, driver, mes, ano, folha, processo)
        return 'ok'
    else:
        return 'erro'


def lanca_especifico(mes, ano, mes_folha, ano_folha, matricula, processo):
    folha = f'{mes_folha}/{ano_folha}'
    observacao = f'Recalculo do banco de horas após processamento de horas extras, processo SEI {processo}'
    print(observacao)
    confirmacoes = RelatorioPagas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                 empregado__matricula=matricula).values()
    if confirmacoes:
        driver = inicia_driver()
        login(driver, 'andre.ribeiro.1', 'l6r7w588')
        clica_folha(driver)
        confirmacoes = pd.DataFrame(confirmacoes)
        confirmacoes = pd.DataFrame(confirmacoes)
        pega_matricula(confirmacoes, mes, ano)
        confirmacoes['matricula'] = confirmacoes['matricula'].astype(int)
        confirmacoes['rubrica_diurna'] = ''
        confirmacoes['rubrica_noturna'] = ''
        for i, j in confirmacoes.iterrows():
            confirmacoes.at[i, 'rubrica_diurna'] = 81 if j['valor_diurnas'] > 0 else ''
            confirmacoes.at[i, 'rubrica_noturna'] = 878 if j['valor_noturnas'] > 0 else ''

        confirmacoes = confirmacoes.drop(columns={'id', 'cargo', 'empregado_id', 'importacao_id',
                                                  'data_upload', 'setor', 'qtd', 'valor_diurnas', 'valor_noturnas',
                                                  'total', 'importado_por', 'importado_por_id'})
        print(confirmacoes)

        LancarRubricas(confirmacoes, driver, mes, ano, folha, processo)
        return 'ok'
    else:
        return 'erro'
