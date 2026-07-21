import os

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        TimeoutException, WebDriverException)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from empregados.models import Empregado
from pos_calculo.credenciais import get_credenciais, reportar_progresso
from pos_calculo.lancamento import LancarRubricas
from pos_calculo.models import RelatorioBatidasRejeitadas, RelatorioBancosRecalculados, RelatorioRubricasLancadas, \
    RelatorioBatidasDesrejeitadas
from pos_calculo.recalcular_negativos import RecalcularNegativos
from pos_calculo.recalcular import RecalcularBanco
from pos_calculo.rejeitar import Diurno, Noturno, VinteQuatroHoras
from pos_calculo.voltar_negativos import VoltarVinteQuatroHoras, VoltarNoturno, VoltarDiurno
from relatorios.models import RelatorioRejeitarBatidas, RelatorioConfirmacao, RelatorioPagas, VoltarNegativos, \
    RelatorioNegativos


def pega_matricula(df, mes, ano):
    if df.empty:
        return df
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


def inicia_driver():
    # webdriver_manager detecta a versão do Chrome instalado e baixa/gerencia
    # o chromedriver compatível automaticamente (dispensa manter chromedriver.exe
    # na mão e evita erro de versão incompatível). O download é cacheado em ~/.wdm.
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # Modo headless: o Chrome roda sem janela visível. Necessário porque o
    # servidor roda como serviço do Windows (Sessão 0, sem área de trabalho).
    # "--headless=new" mantém o comportamento do Chrome normal (inclui downloads).
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")            # exigido ao rodar como serviço/SYSTEM
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")  # viewport virtual p/ elementos renderizarem
    # Giving the path of chromedriver to selenium webdriver
    driver = webdriver.Chrome(service=service, options=options)

    # URL of the login page of site
    # which you want to automate login.
    url = "https://sigp.ebserh.gov.br/csp/ebserh/index.csp"

    driver.get(url)
    driver.stop_client()
    driver.get(url)
    # except SessionNotCreatedException:
    #     try:
    #         service = Service("chromedriver1.exe")
    #         options = webdriver.ChromeOptions()
    #         options.add_experimental_option('excludeSwitches', ['enable-logging'])
    #         # options.add_argument("--headless")
    #         # Giving the path of chromedriver to selenium webdriver
    #         driver = webdriver.Chrome(service=service, options=options)
    #
    #         # URL of the login page of site
    #         # which you want to automate login.
    #         url = "https://sigp.ebserh.gov.br/csp/ebserh/index.csp"
    #
    #         driver.get(url)
    #         driver.stop_client()
    #         driver.get(url)
    #     except SessionNotCreatedException:
    #         try:
    #             service = Service("chromedriver2.exe")
    #             options = webdriver.ChromeOptions()
    #             options.add_experimental_option('excludeSwitches', ['enable-logging'])
    #             # options.add_argument("--headless")
    #             # Giving the path of chromedriver to selenium webdriver
    #             driver = webdriver.Chrome(service=service, options=options)
    #
    #             # URL of the login page of site
    #             # which you want to automate login.
    #             url = "https://sigp.ebserh.gov.br/csp/ebserh/index.csp"
    #
    #             driver.get(url)
    #             driver.stop_client()
    #             driver.get(url)
    #         except SessionNotCreatedException:
    #             service = Service("chromedriver3.exe")
    #             options = webdriver.ChromeOptions()
    #             options.add_experimental_option('excludeSwitches', ['enable-logging'])
    #             # options.add_argument("--headless")
    #             # Giving the path of chromedriver to selenium webdriver
    #             driver = webdriver.Chrome(service=service, options=options)
    #
    #             # URL of the login page of site
    #             # which you want to automate login.
    #             url = "https://sigp.ebserh.gov.br/csp/ebserh/index.csp"
    #
    #             driver.get(url)
    #             driver.stop_client()
    #             driver.get(url)

    wait = WebDriverWait(driver, 10)
    wait.until(ec.presence_of_element_located((By.ID, 'login')))
    # Credenciais do SIGP informadas pela pessoa nesta sessão (thread-local).
    # Se não houver (ex.: execução por linha de comando), cai no login fixo do .env.
    usuario, senha = get_credenciais()
    if not usuario:
        usuario, senha = os.getenv("EBSERH_USERNAME"), os.getenv("EBSERH_PASSWORD")
    login(driver, usuario, senha)
    reportar_progresso(20, 'Login efetuado com sucesso')
    return driver


def _clica_link(driver, texto, timeout=30):
    """Clica num link de menu de forma robusta para headless.

    Espera o link existir, rola até ele e tenta o clique normal. Se o clique
    for interceptado por uma sobreposição (comum em headless), refaz via
    JavaScript, que ignora a interceptação.
    """
    wait = WebDriverWait(driver, timeout)
    elemento = wait.until(ec.presence_of_element_located((By.LINK_TEXT, texto)))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
    try:
        elemento.click()
    except (ElementClickInterceptedException, WebDriverException):
        driver.execute_script("arguments[0].click();", elemento)


def clica_frequencia(driver):
    _clica_link(driver, 'Registro de Frequência')

    wait = WebDriverWait(driver, 30)
    wait.until(ec.presence_of_element_located((By.ID, 'frame1')))

    frame1 = driver.find_element(By.ID, 'frame1')
    driver.switch_to.frame(frame1)

def clica_horario_excepcional(driver):
    _clica_link(driver, 'Cadastro Horário Excepcional')

    wait = WebDriverWait(driver, 30)
    wait.until(ec.presence_of_element_located((By.ID, 'frame1')))

    frame1 = driver.find_element(By.ID, 'frame1')
    driver.switch_to.frame(frame1)


def clica_banco(driver):
    _clica_link(driver, 'Recalcular BH Homologado')

    wait = WebDriverWait(driver, 30)
    wait.until(ec.presence_of_element_located((By.ID, 'frame1')))

    frame1 = driver.find_element(By.ID, 'frame1')
    driver.switch_to.frame(frame1)


def clica_folha(driver):
    _clica_link(driver, 'Rubrica Individual', timeout=120)


def login(driver, username, password):
    username_input = driver.find_element(By.ID, 'login')
    username_input.send_keys(username)

    # Find the password input by inspecting on password input
    password_input = driver.find_element(By.ID, 'senha')
    password_input.send_keys(password)

    # Click on submit
    submit_button = driver.find_element(By.CLASS_NAME, 'btn-primary')
    submit_button.click()

    # Valida o login. Primeiro espera a página reagir (o botão de login antigo
    # sai do DOM). Em seguida verifica o campo de SENHA: ele só existe na tela
    # de login, então se continuar presente é porque as credenciais foram
    # recusadas e a página de login recarregou. (Não dá pra usar o id 'login':
    # a página autenticada do SIGP também tem um elemento com esse id.)
    try:
        WebDriverWait(driver, 20).until(ec.staleness_of(submit_button))
    except TimeoutException:
        pass
    if driver.find_elements(By.ID, 'senha'):
        raise Exception('Falha no login do SIGP: usuário ou senha inválidos.')


def rejeita_todos(mes, ano, driver, c, usuario):
    rejeitadas_d = RelatorioBatidasRejeitadas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                             tipo='D').values()

    if rejeitadas_d:
        rejeitadas_d = pd.DataFrame(rejeitadas_d)
        pega_matricula(rejeitadas_d, mes, ano)

    diurnos = RelatorioRejeitarBatidas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                      tipo='D').order_by('nome').values()
    diurnos = pd.DataFrame(diurnos)
    diurnos.columns = diurnos.columns.str.replace('dia', '')
    diurnos = pega_matricula(diurnos, mes, ano)
    diurnos = diurnos.drop(columns={'id', 'empregado_id', 'importacao_id', 'importacao_id',
                                    'importado_por', 'importado_por_id', 'data_upload'})
    try:
        if not rejeitadas_d.empty:
            diurnos = diurnos[~diurnos['matricula'].isin(rejeitadas_d['matricula'])]
    except AttributeError:
        pass
    for a, b in diurnos.iterrows():
        c = 0
        for dia in b[2:33]:
            if dia != '':
                c += 1
        if c == 0:
            diurnos = diurnos[diurnos['matricula'] != b['matricula']]

    diurnos = diurnos.reset_index(drop=True)
    print(diurnos)
    c = Diurno(diurnos, driver, c, usuario)

    rejeitadas_n = RelatorioBatidasRejeitadas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                             tipo='N').values()
    if rejeitadas_n:
        rejeitadas_n = pd.DataFrame(rejeitadas_n)
        pega_matricula(rejeitadas_n, mes, ano)

    noturnos = RelatorioRejeitarBatidas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                       tipo='N').order_by('nome').values()
    noturnos = pd.DataFrame(noturnos)
    noturnos.columns = noturnos.columns.str.replace('dia', '')
    noturnos = pega_matricula(noturnos, mes, ano)
    noturnos = noturnos.drop(columns={'id', 'empregado_id', 'importacao_id', 'importacao_id',
                                      'importado_por', 'importado_por_id', 'data_upload'})

    try:
        if not rejeitadas_n.empty:
            noturnos = noturnos[~noturnos['matricula'].isin(rejeitadas_n['matricula'])]
    except AttributeError:
        pass
    for a, b in noturnos.iterrows():
        c = 0
        for dia in b[2:33]:
            if dia != '':
                c += 1
        if c == 0:
            noturnos = noturnos[noturnos['matricula'] != b['matricula']]

    noturnos = noturnos.reset_index(drop=True)
    print(noturnos)
    c = Noturno(noturnos, driver, c, usuario)

    rejeitadas_dn = RelatorioBatidasRejeitadas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                              tipo='DN').values()
    if rejeitadas_dn:
        rejeitadas_dn = pd.DataFrame(rejeitadas_dn)
        pega_matricula(rejeitadas_dn, mes, ano)

    diurno_noturno = RelatorioRejeitarBatidas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                             tipo='DN').order_by('nome').values()
    diurno_noturno = pd.DataFrame(diurno_noturno)
    diurno_noturno.columns = diurno_noturno.columns.str.replace('dia', '')
    diurno_noturno = pega_matricula(diurno_noturno, mes, ano)
    diurno_noturno = diurno_noturno.drop(columns={'id', 'empregado_id', 'importacao_id', 'importacao_id',
                                                  'importado_por', 'importado_por_id', 'data_upload'})

    try:
        if not rejeitadas_dn.empty:
            diurno_noturno = diurno_noturno[~diurno_noturno['matricula'].isin(rejeitadas_dn['matricula'])]
    except AttributeError:
        pass

    for a, b in diurno_noturno.iterrows():
        c = 0
        for dia in b[2:33]:
            if dia != '':
                c += 1
        if c == 0:
            diurno_noturno = diurno_noturno[diurno_noturno['matricula'] != b['matricula']]
    diurno_noturno = diurno_noturno.reset_index(drop=True)

    print(diurno_noturno)
    c = VinteQuatroHoras(diurno_noturno, driver, c, usuario)


def rejeita_especifico(mes, ano, driver, c, matricula, usuario):
    diurnos = RelatorioRejeitarBatidas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                      tipo='D', empregado__matricula=matricula).values()
    diurnos = pd.DataFrame(diurnos)
    diurnos.columns = diurnos.columns.str.replace('dia', '')
    diurnos = pega_matricula(diurnos, mes, ano)
    diurnos = diurnos.drop(columns={'id', 'empregado_id', 'importacao_id', 'importacao_id',
                                    'importado_por', 'importado_por_id', 'data_upload'})
    print(diurnos)
    c = Diurno(diurnos, driver, c, usuario)

    noturnos = RelatorioRejeitarBatidas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                       tipo='N', empregado__matricula=matricula).values()
    noturnos = pd.DataFrame(noturnos)
    noturnos.columns = noturnos.columns.str.replace('dia', '')
    noturnos = pega_matricula(noturnos, mes, ano)
    noturnos = noturnos.drop(columns={'id', 'empregado_id', 'importacao_id', 'importacao_id',
                                      'importado_por', 'importado_por_id', 'data_upload'})
    print(noturnos)
    c = Noturno(noturnos, driver, c, usuario)

    diurno_noturno = RelatorioRejeitarBatidas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                             tipo='DN', empregado__matricula=matricula).values()
    diurno_noturno = pd.DataFrame(diurno_noturno)
    diurno_noturno.columns = diurno_noturno.columns.str.replace('dia', '')
    diurno_noturno = pega_matricula(diurno_noturno, mes, ano)
    diurno_noturno = diurno_noturno.drop(columns={'id', 'empregado_id', 'importacao_id', 'importacao_id',
                                                  'importado_por', 'importado_por_id', 'data_upload'})
    print(diurno_noturno)
    c = VinteQuatroHoras(diurno_noturno, driver, c, usuario)


def recalcula_todos(mes, ano, processo, usuario):
    if mes < 10:
        mes = f'0{mes}'

    mes_ano = f'{mes}{ano}'
    observacao = f'Recalculo do banco de horas após processamento de horas extras, processo SEI {processo}'
    confirmacoes = RelatorioConfirmacao.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                       saldo_banco_decimal__gte=0, saldo_mes_decimal__gte=0,
                                                       valor_total__gt=0).order_by('-nome').values()
    recalculados = RelatorioBancosRecalculados.objects.filter(importacao__mes=mes, importacao__ano=ano).values()
    recalculados = pd.DataFrame(recalculados)
    if confirmacoes:
        driver = inicia_driver()
        try:
            clica_banco(driver)
            confirmacoes = pd.DataFrame(confirmacoes)
            pega_matricula(confirmacoes, mes, ano)
            if not recalculados.empty:
                pega_matricula(recalculados, mes, ano)
                recalculados['matricula'] = recalculados['matricula'].astype(int)
                recalculados = recalculados['matricula']
                for i in recalculados:
                    confirmacoes = confirmacoes[confirmacoes['matricula'] != i]

            confirmacoes['matricula'] = confirmacoes['matricula'].astype(int)
            confirmacoes = confirmacoes[['matricula', 'nome']]
            RecalcularBanco(confirmacoes, driver, mes_ano, observacao, usuario)
            return 'ok'
        finally:
            driver.quit()
    else:
        return 'erro'


def recalcula_especifico(mes, ano, matricula, processo, usuario):
    if mes < 10:
        mes = f'0{mes}'

    mes_ano = f'{mes}{ano}'
    observacao = f'Recalculo do banco de horas após processamento de horas extras, processo SEI {processo}'
    print(observacao)
    confirmacoes = RelatorioConfirmacao.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                       saldo_banco_decimal__gte=0, saldo_mes_decimal__gte=0,
                                                       empregado__matricula=matricula, valor_total__gt=0).values()
    if confirmacoes:
        driver = inicia_driver()
        try:
            clica_banco(driver)
            confirmacoes = pd.DataFrame(confirmacoes)
            confirmacoes = pd.DataFrame(confirmacoes)
            pega_matricula(confirmacoes, mes, ano)
            confirmacoes['matricula'] = confirmacoes['matricula'].astype(int)
            confirmacoes = confirmacoes[['matricula', 'empregado_id']]
            RecalcularBanco(confirmacoes, driver, mes_ano, observacao, usuario)
            return 'ok'
        finally:
            driver.quit()
    else:
        return 'erro'


def lanca_todos(mes, ano, mes_folha, ano_folha, fator, processo, usuario):
    folha = f'Folha Normal {str(mes_folha)}/{ano_folha}'
    print(folha)
    observacao = f'Horas extras {mes}/{ano}.Processo SEI {processo}.'
    confirmacoes = RelatorioPagas.objects.filter(importacao__mes=mes, importacao__ano=ano).values()
    if confirmacoes:
        driver = inicia_driver()
        try:
            clica_folha(driver)
            confirmacoes = pd.DataFrame(confirmacoes)
            pega_matricula(confirmacoes, mes, ano)
            confirmacoes['matricula'] = confirmacoes['matricula'].astype(int)
            rubricas_lancadas = RelatorioRubricasLancadas.objects.filter(importacao__mes=mes,
                                                                         importacao__ano=ano).values()
            if rubricas_lancadas:
                rubricas_lancadas = pd.DataFrame(rubricas_lancadas)
                pega_matricula(rubricas_lancadas, mes, ano)
                for i, j in rubricas_lancadas.iterrows():
                    confirmacoes = confirmacoes[confirmacoes['matricula'] != j['matricula']]
            confirmacoes.reset_index(drop=True, inplace=True)
            confirmacoes['rubrica_diurna'] = ''
            confirmacoes['rubrica_noturna'] = ''
            for i, j in confirmacoes.iterrows():
                confirmacoes.at[i, 'rubrica_diurna'] = 81 if j['valor_diurnas'] > 0 else ''
                confirmacoes.at[i, 'rubrica_noturna'] = 878 if j['valor_noturnas'] > 0 else ''

            confirmacoes = confirmacoes.drop(columns={'id', 'cargo', 'empregado_id', 'importacao_id',
                                                      'data_upload', 'setor', 'qtd', 'valor_diurnas', 'valor_noturnas',
                                                      'total', 'importado_por', 'importado_por_id'})
            print(confirmacoes)

            LancarRubricas(confirmacoes, driver, mes, ano, folha, observacao, usuario, fator)
            return 'ok'
        finally:
            driver.quit()
    else:
        return 'erro'


def lanca_especifico(mes, ano, mes_folha, ano_folha, matricula, fator, processo, usuario):
    folha = f'Folha Normal {mes_folha}/{ano_folha}'
    observacao = f'Recalculo do banco de horas após processamento de horas extras, processo SEI {processo}'
    print(observacao)
    confirmacoes = RelatorioPagas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                 empregado__matricula=matricula).values()
    if confirmacoes:
        driver = inicia_driver()
        try:
            clica_folha(driver)
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

            LancarRubricas(confirmacoes, driver, mes, ano, folha, processo, usuario, fator)
            return 'ok'
        finally:
            driver.quit()
    else:
        return 'erro'


def voltar_todos(mes, ano, driver, c, usuario):
    voltar = VoltarNegativos.objects.filter(importacao__mes=mes, importacao__ano=ano).values()
    voltar = pd.DataFrame(voltar)
    print(voltar)
    pega_matricula(voltar, mes, ano)

    desrejeitadas_d = RelatorioBatidasDesrejeitadas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                                   tipo='D').values()

    if desrejeitadas_d:
        desrejeitadas_d = pd.DataFrame(desrejeitadas_d)
        pega_matricula(desrejeitadas_d, mes, ano)

    diurnos = RelatorioRejeitarBatidas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                      tipo='D').order_by('nome').values()
    diurnos = pd.DataFrame(diurnos)
    diurnos.columns = diurnos.columns.str.replace('dia', '')
    diurnos = pega_matricula(diurnos, mes, ano)
    diurnos = diurnos.drop(columns={'id', 'empregado_id', 'importacao_id', 'importacao_id',
                                    'importado_por', 'importado_por_id', 'data_upload'})
    try:
        diurnos = diurnos[diurnos['matricula'].isin(voltar['matricula'])]
        if not desrejeitadas_d.empty:
            diurnos = diurnos[~diurnos['matricula'].isin(desrejeitadas_d['matricula'])]
    except AttributeError:
        pass
    for a, b in diurnos.iterrows():
        c = 0
        for dia in b[2:33]:
            if dia != '':
                c += 1
        if c == 0:
            diurnos = diurnos[diurnos['matricula'] != b['matricula']]

    diurnos = diurnos.reset_index(drop=True)
    print(diurnos)
    c = VoltarDiurno(diurnos, driver, c, usuario)

    desrejeitadas_n = RelatorioBatidasDesrejeitadas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                                   tipo='N').values()

    if desrejeitadas_n:
        desrejeitadas_n = pd.DataFrame(desrejeitadas_n)
        pega_matricula(desrejeitadas_n, mes, ano)

    noturnos = RelatorioRejeitarBatidas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                       tipo='N').order_by('nome').values()
    noturnos = pd.DataFrame(noturnos)
    noturnos.columns = noturnos.columns.str.replace('dia', '')
    noturnos = pega_matricula(noturnos, mes, ano)
    noturnos = noturnos.drop(columns={'id', 'empregado_id', 'importacao_id', 'importacao_id',
                                      'importado_por', 'importado_por_id', 'data_upload'})

    try:
        noturnos = noturnos[noturnos['matricula'].isin(voltar['matricula'])]
        if not desrejeitadas_n.empty:
            noturnos = noturnos[~noturnos['matricula'].isin(desrejeitadas_n['matricula'])]
    except AttributeError:
        pass
    for a, b in noturnos.iterrows():
        c = 0
        for dia in b[2:33]:
            if dia != '':
                c += 1
        if c == 0:
            noturnos = noturnos[noturnos['matricula'] != b['matricula']]

    noturnos = noturnos.reset_index(drop=True)
    print(noturnos)
    c = VoltarNoturno(noturnos, driver, c, usuario)

    desrejeitadas_dn = RelatorioBatidasDesrejeitadas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                                    tipo='DN').values()

    if desrejeitadas_dn:
        desrejeitadas_dn = pd.DataFrame(desrejeitadas_dn)
        pega_matricula(desrejeitadas_dn, mes, ano)

    diurno_noturno = RelatorioRejeitarBatidas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                             tipo='DN').order_by('nome').values()
    diurno_noturno = pd.DataFrame(diurno_noturno)
    diurno_noturno.columns = diurno_noturno.columns.str.replace('dia', '')
    diurno_noturno = pega_matricula(diurno_noturno, mes, ano)
    diurno_noturno = diurno_noturno.drop(columns={'id', 'empregado_id', 'importacao_id', 'importacao_id',
                                                  'importado_por', 'importado_por_id', 'data_upload'})

    try:
        diurno_noturno = diurno_noturno[diurno_noturno['matricula'].isin(voltar['matricula'])]
        print(diurno_noturno)
        if not desrejeitadas_dn.empty:
            diurno_noturno = diurno_noturno[~diurno_noturno['matricula'].isin(desrejeitadas_dn['matricula'])]
    except AttributeError:
        pass

    for a, b in diurno_noturno.iterrows():
        c = 0
        for dia in b[2:33]:
            if dia != '':
                c += 1
        if c == 0:
            diurno_noturno = diurno_noturno[diurno_noturno['matricula'] != b['matricula']]
    diurno_noturno = diurno_noturno.reset_index(drop=True)

    print(diurno_noturno)
    c = VoltarVinteQuatroHoras(diurno_noturno, driver, c, usuario)


def recalcula_negativos(mes, ano, processo, usuario):
    observacao = f'Recalculo do banco de horas após processamento de horas extras, processo SEI {processo}'

    if mes < 10:
        mes = f'0{mes}'

    mes_ano = f'{mes}{ano}'
    negativos = RelatorioNegativos.objects.filter(importacao__mes=mes, importacao__ano=ano, tipo='confirmacao').values()
    negativos = pd.DataFrame(negativos)
    if negativos.empty:
        # Nenhum banco negativo de confirmação neste período: nada a recalcular.
        # Evita o KeyError 'matricula' e abrir o navegador à toa.
        return 'vazio'
    pega_matricula(negativos, mes, ano)
    negativos['matricula'] = negativos['matricula'].astype(int)
    negativos = negativos.sort_values(by='matricula', ascending=True)
    print(negativos)

    driver = inicia_driver()
    try:
        clica_banco(driver)
        RecalcularNegativos(negativos, driver, mes_ano, observacao, usuario)
        return 'ok'
    finally:
        driver.quit()
