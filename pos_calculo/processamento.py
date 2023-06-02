import pandas as pd
from selenium import webdriver
from selenium.common import SessionNotCreatedException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from empregados.models import Empregado
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
    try:
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
    except SessionNotCreatedException:
        try:
            service = Service("chromedriver1.exe")
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
        except SessionNotCreatedException:
            service = Service("chromedriver2.exe")
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

    wait = WebDriverWait(driver, 10)
    wait.until(ec.presence_of_element_located((By.ID, 'login')))
    login(driver, 'andre.ribeiro.1', 'l6r7w588')
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
                                                       valor_total__gt=0).values()
    recalculados = RelatorioBancosRecalculados.objects.filter(importacao__mes=mes, importacao__ano=ano).values()
    recalculados = pd.DataFrame(recalculados)
    if confirmacoes:
        driver = inicia_driver()
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
        print(confirmacoes.shape[0])
        RecalcularBanco(confirmacoes, driver, mes_ano, observacao, usuario)
        return 'ok'
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
        clica_banco(driver)
        confirmacoes = pd.DataFrame(confirmacoes)
        confirmacoes = pd.DataFrame(confirmacoes)
        pega_matricula(confirmacoes, mes, ano)
        confirmacoes['matricula'] = confirmacoes['matricula'].astype(int)
        confirmacoes = confirmacoes[['matricula', 'empregado_id']]
        RecalcularBanco(confirmacoes, driver, mes_ano, observacao, usuario)
        return 'ok'
    else:
        return 'erro'


def lanca_todos(mes, ano, mes_folha, ano_folha, fator, processo, usuario):
    if mes_folha < 10:
        mes_folha = f'0{mes_folha}'
    folha = f'Folha Normal {mes_folha}/{ano_folha}'
    print(folha)
    observacao = f'Horas extras {mes}/{ano}.Processo SEI {processo}.'
    confirmacoes = RelatorioPagas.objects.filter(importacao__mes=mes, importacao__ano=ano).values()
    if confirmacoes:
        driver = inicia_driver()
        clica_folha(driver)
        confirmacoes = pd.DataFrame(confirmacoes)
        pega_matricula(confirmacoes, mes, ano)
        confirmacoes['matricula'] = confirmacoes['matricula'].astype(int)
        rubricas_lancadas = RelatorioRubricasLancadas.objects.filter(importacao__mes=mes, importacao__ano=ano).values()
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
    else:
        return 'erro'


def lanca_especifico(mes, ano, mes_folha, ano_folha, matricula, fator, processo, usuario):
    folha = f'{mes_folha}/{ano_folha}'
    observacao = f'Recalculo do banco de horas após processamento de horas extras, processo SEI {processo}'
    print(observacao)
    confirmacoes = RelatorioPagas.objects.filter(importacao__mes=mes, importacao__ano=ano,
                                                 empregado__matricula=matricula).values()
    if confirmacoes:
        driver = inicia_driver()
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
    else:
        return 'erro'


def voltar_todos(mes, ano, driver, c, usuario):
    voltar = VoltarNegativos.objects.filter(importacao__mes=mes, importacao__ano=ano).values()
    voltar = pd.DataFrame(voltar)
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
    pega_matricula(negativos, mes, ano)
    negativos['matricula'] = negativos['matricula'].astype(int)
    print(negativos)

    driver = inicia_driver()
    clica_banco(driver)

    RecalcularNegativos(negativos, driver, mes_ano, observacao, usuario)
    return 'ok'
