import pandas as pd
from selenium.common import TimeoutException, NoAlertPresentException, UnexpectedAlertPresentException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from empregados.models import Empregado
from pos_calculo.dbchanges import salva_escala_tirada
from pos_calculo.models import RelatorioEscalaTirada
from relatorios.models import RelatorioConfirmacao, RelatorioErros

escalas_codigos = {'M10': 500, 'M11': 501, 'M12': 502, 'M8': 503, 'T10': 504, 'T11': 505, 'T12': 506, 'T9': 507,
                   'M13': 513, 'M14': 516, 'M15': 518, 'M16': 520, 'M17': 522, 'M18': 524,
                   'N5': 526, 'T13': 527, 'T14': 529, 'T15': 531, 'T16': 533, 'T17': 535,
                   'T18': 537, 'T19': 539, 'MT15': 541, 'MT16': 542, 'MT17': 543, 'MT18': 544,
                   'MT19': 545, 'MT20': 546, 'MT21': 547, 'MT22': 548, 'MT23': 549, 'MT24': 550,
                   'MT25': 551, 'MT26': 552, 'MT27': 554, 'MT28': 556, 'MT29': 558, 'MT30': 560, 'MT31': 562,
                   'MT32': 564, 'MT33': 566, 'MT34': 568, 'MT35': 569, 'MT36': 570, 'MT37': 572, 'MT38': 574,
                   'MT39': 576, 'MT40': 578, 'MT41': 580, 'MT42': 582, 'MT43': 583, 'D5': 584, 'D6': 586,
                   'D7': 588, 'D8': 590, 'N6': 592, 'N7': 594, 'N8': 596, 'N9': 598, 'N10': 600, 'DN4': 602,
                   'DN5': 603, 'DN6': 604, 'M9': 605, 'N11': 607, 'TN1': 618, 'D9': 619, 'D10': 621, 'D11': 623}


def ColarMatricula(matricula, index_as_int, driver):
    if int(index_as_int) > 0:
        campo_matricula = driver.find_element(By.NAME, 'servMatr')
        try:
            wait = WebDriverWait(driver, 1)
            alert = wait.until(ec.alert_is_present())
            alert.accept()
        except UnexpectedAlertPresentException:
            driver.switch_to.alert.accept()
            pass
        except NoAlertPresentException:
            pass
        except TimeoutException:
            pass
        finally:
            campo_matricula.send_keys(matricula)
            campo_matricula.send_keys(Keys.TAB)
    else:
        campo_matricula = driver.find_element(By.NAME, 'servMatr')
        campo_matricula.send_keys(matricula)
        campo_matricula.send_keys(Keys.TAB)


def PegaDia(dia):
    if str(dia) != '':
        data = str(dia).split('/')
        data = data[0] + data[1] + data[2]
        return data
    else:
        return 'Campo Vazio'


def InsereData(data, driver):
    wait = WebDriverWait(driver, 120)
    wait.until(ec.presence_of_element_located((By.NAME, 'diaAnoMesI')))

    campo_data = driver.find_element(By.NAME, 'diaAnoMesI')
    campo_data.clear()
    campo_data.send_keys(data)
    campo_data.send_keys(Keys.TAB)

    pesquisar = driver.find_element(By.TAG_NAME, 'td').find_element(By.TAG_NAME, 'img')
    pesquisar.click()


def insere_data_inicial(data, driver):
    wait = WebDriverWait(driver, 120)
    wait.until(ec.presence_of_element_located((By.NAME, 'hrDataInicial')))
    campo_data = driver.find_element(By.NAME, 'hrDataInicial')
    campo_data.clear()
    campo_data.send_keys(data)
    campo_data.send_keys(Keys.TAB)


def insere_mes_ano(mes, ano, driver):
    mesAno = f'{mes}{ano}'

    wait = WebDriverWait(driver, 120)
    wait.until(ec.presence_of_element_located((By.NAME, 'mesAno')))

    campo_data = driver.find_element(By.NAME, 'mesAno')
    campo_data.clear()
    campo_data.send_keys(mesAno)
    campo_data.send_keys(Keys.TAB)


def tirar_escala(mes, ano, driver, c, usuario):
    if mes < 10:
        mes = f'0{mes}'

    tiradas = RelatorioEscalaTirada.objects.filter(importacao__mes=mes, importacao__ano=ano).values()
    erros = RelatorioErros.objects.filter(importacao__mes=mes, importacao__ano=ano).values()

    escalas = (RelatorioConfirmacao.objects.filter(importacao__mes=mes, importacao__ano=ano, valor_total__gt=0,
                                                   saldo_mes_decimal__gte=0, saldo_banco_decimal__gte=0, ).
               exclude(empregado__matricula__in=erros.values_list('empregado__matricula', flat=True)).
               exclude(empregado__matricula__in=tiradas.values_list('empregado__matricula', flat=True)).values())

    escalas = pd.DataFrame(escalas)
    escalas = pega_matricula(escalas, mes, ano)

    escalas = escalas[['matricula', 'nome', 'dia1', 'dia2', 'dia3', 'dia4', 'dia5', 'dia6', 'dia7', 'dia8', 'dia9',
                       'dia10', 'dia11', 'dia12', 'dia13', 'dia14', 'dia15', 'dia16', 'dia17', 'dia18', 'dia19',
                       'dia20', 'dia21', 'dia22', 'dia23', 'dia24', 'dia25', 'dia26', 'dia27', 'dia28', 'dia29',
                       'dia30', 'dia31', 'setor']]

    escalas = escalas.reset_index(drop=True)
    print(escalas)

    for i, j in escalas.iterrows():
        c = 1
        for dia in j[2:33]:
            if dia != '':
                escalas.at[i, f'dia{c}'] = escalas_codigos[str(dia)]
            c += 1

    for i, j in escalas.iterrows():
        matricula = int(j['matricula'])
        dias = 0
        for dia in j[2:33]:
            if str(dia) != '':
                dias += 1
        if dias > 0:
            insere_mes_ano(mes, ano, driver)
            try:
                ColarMatricula(matricula, i, driver)
            except Exception as error:
                if (
                        'O empregado não possui Cadastro' or 'Não disponível para consulta por este usuário' or 'Informe a matrícula') in str(
                        error):
                    print(f'{matricula} - {j["nome"]}: Movimentado')
                    continue

            pesquisar = driver.find_element(By.XPATH, '/html/body/form/table[2]/tbody/tr/td/table/tbody/tr/td[9]/img')
            pesquisar.click()
            for dia, escala in j[2:33].items():
                if str(escala) != '':
                    dia = str(dia).split('dia')[1]
                    if int(dia) < 10:
                        dia = f'0{dia}'
                    data = str(f'{dia}{mes}{ano}')
                    print(f"{i} - {matricula} - {j['nome']}: {dia}/{mes}/{ano} - {escala}")
                    try:
                        sem_jornada = ''
                        classe2 = ''
                        wait = WebDriverWait(driver, 1)
                        linha = wait.until(
                            ec.presence_of_element_located((By.XPATH, f"//div[contains(text(), '{dia}/{mes}/{ano}')]")))

                        classe = f"{linha.get_attribute('id')}x"

                        if '.item:1x' in str(classe):
                            classe2 = classe.replace('.item:1x', '.item:2')
                            sem_jornada = classe.replace('.item:1x', '.item:5')
                            classe = classe.replace('.item:1x', '.item:1')
                        elif '.item:2x' in str(classe):
                            classe2 = classe.replace('.item:2x', '.item:2')
                            sem_jornada = classe.replace('.item:2x', '.item:5')
                            classe = classe.replace('.item:2x', '.item:1')

                        if driver.find_element(By.ID, sem_jornada).text == "Sem Jornada":
                            print(f"Escala já está sem jornada!")
                            salva_escala_tirada(j, escala, usuario, mes, ano, data)
                            continue

                        if (driver.find_element(By.ID, classe).text == f'{dia}/{mes}/{ano}' and
                                driver.find_element(By.ID, classe2).text == f'{dia}/{mes}/{ano}'):

                            linha.click()

                            excluir = driver.find_element(By.XPATH,
                                                          '/html/body/form/table[4]/tbody/tr/td[2]/a[2]/img')
                            excluir.click()

                            wait = WebDriverWait(driver, 1)
                            alert = wait.until(ec.alert_is_present())
                            alert.accept()

                            insere_data_inicial(data, driver)

                            select = Select(driver.find_element(By.ID, 'Ocorrencia'))
                            select.select_by_value('1')

                            wait = WebDriverWait(driver, 120)
                            wait.until(ec.presence_of_element_located((By.NAME, 'horarioTabCodigo')))

                            campo_data = driver.find_element(By.NAME, 'horarioTabCodigo')
                            campo_data.clear()
                            campo_data.send_keys(str(escala))
                            campo_data.send_keys(Keys.TAB)

                            incluir = driver.find_element(By.XPATH,
                                                          '/html/body/form/table[4]/tbody/tr/td[2]/a[1]/img')
                            incluir.click()
                            wait = WebDriverWait(driver, 1)
                            alert = wait.until(ec.alert_is_present())
                            alert.accept()

                            print(f"Sem jornada  incluída com sucesso")
                            data = str(f'{dia}/{mes}/{ano}')
                            salva_escala_tirada(j, escala, usuario, mes, ano, data)
                        else:
                            print(f"Não foi possível incluir sem jornada")
                            data = str(f'{dia}/{mes}/{ano}')
                            salva_escala_tirada(j, escala, usuario, mes, ano, data)
                    except:
                        try:
                            insere_data_inicial(data, driver)

                            select = Select(driver.find_element(By.ID, 'Ocorrencia'))
                            select.select_by_value('1')

                            wait = WebDriverWait(driver, 120)
                            wait.until(ec.presence_of_element_located((By.NAME, 'horarioTabCodigo')))

                            campo_data = driver.find_element(By.NAME, 'horarioTabCodigo')
                            campo_data.clear()
                            campo_data.send_keys(str(escala))
                            campo_data.send_keys(Keys.TAB)

                            incluir = driver.find_element(By.XPATH, '/html/body/form/table[4]/tbody/tr/td[2]/a[1]/img')
                            incluir.click()

                            try:
                                wait = WebDriverWait(driver, 1)
                                alert = wait.until(ec.alert_is_present())
                                if "Sobreposição de período" in alert.text:
                                    alert.accept()
                                    raise Exception
                            except:
                                pass

                            print(f"Sem jornada  incluída com sucesso")
                            data = str(f'{dia}/{mes}/{ano}')
                            salva_escala_tirada(j, escala, usuario, mes, ano, data)
                        except Exception as error:
                            print(f"Erro: {error}")
                            data = str(f'{dia}/{mes}/{ano}')
                            salva_escala_tirada(j, escala, usuario, mes, ano, data)
                            continue

        c += 1
    return c


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
