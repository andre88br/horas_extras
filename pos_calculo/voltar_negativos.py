from time import sleep

import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
from selenium.common import TimeoutException, NoAlertPresentException, UnexpectedAlertPresentException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from empregados.models import Empregado
from pos_calculo.dbchanges import salva_desrejeitada, salva_escala_voltada
from pos_calculo.models import RelatorioBatidasDesrejeitadas, RelatorioEscalaVoltada
from relatorios.models import VoltarNegativos


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


# def ColarMatricula(matricula, index_as_int, driver):
#     wait = WebDriverWait(driver, 30)
#     wait.until(ec.presence_of_element_located((By.NAME, 'servMatr')))
#     campo_matricula = driver.find_element(By.NAME, 'servMatr')
#     campo_matricula.clear()
#     try:
#         wait = WebDriverWait(driver, 2)
#         alert = wait.until(ec.alert_is_present())
#         alert.accept()
#     except TimeoutException:
#         pass
#
#     campo_matricula.send_keys(matricula)
#     campo_matricula.send_keys(Keys.TAB)


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


def dois_cliques(l, linha, linha_texto, driver, data, dia, j, usuario, c):
    mes, ano = int(str(data[2:4])), int(str(data[4:]))
    try:
        batida1 = RelatorioBatidasDesrejeitadas.objects.filter(empregado__matricula=j['matricula'],
                                                               data=dia, batida=1,
                                                               tipo=j['tipo'])
        batida2 = RelatorioBatidasDesrejeitadas.objects.filter(empregado__matricula=j['matricula'],
                                                               data=dia, batida=2,
                                                               tipo=j['tipo'])
        if batida1 and batida2:
            raise ObjectDoesNotExist
        else:
            rejeitado = driver.find_element(By.ID, linha_texto[:23] + '7').text
            if rejeitado == 'Sim':
                ActionChains(driver).double_click(linha).perform()

                ActionChains(driver) \
                    .send_keys(Keys.TAB * 6) \
                    .send_keys(Keys.ARROW_LEFT) \
                    .perform()

                ActionChains(driver) \
                    .send_keys(Keys.TAB * 8) \
                    .send_keys(Keys.ENTER) \
                    .perform()
                Excecao(driver)
                print(f'{c}-{j["matricula"]}: Batida {l} do dia {dia} desrejeitada com sucesso!')
                salva_desrejeitada(j, usuario, mes, ano, dia)
                InsereData(data, driver)
            else:
                print(f'{c}-{j["matricula"]}: Batida {l} do dia {dia} não estava rejeitada!')
                salva_desrejeitada(j, usuario, mes, ano, dia)
    except ObjectDoesNotExist:
        print(f'{c}-{j["matricula"]}: Batida {l} do dia {dia} não estava rejeitada!')
        salva_desrejeitada(j, usuario, mes, ano, dia)


def ValidaNoturno(dia, data, driver, j, usuario, c):
    l = 0
    for i in range(4):
        hora1 = driver.find_element(By.ID, 'grid1.data.item:' + str(l) + '.item:2').text
        hora1 = int(hora1.split(':')[0])
        data1 = driver.find_element(By.ID, 'grid1.data.item:' + str(l + 1) + '.item:1').text
        data1 = data1.split('-')[0]

        if hora1 >= 17 and data1 != dia:
            cancelado = driver.find_element(By.ID, 'grid1.data.item:' + str(l) + '.item:6').text
            if cancelado != 'Sim':
                linha = driver.find_element(By.ID, 'grid1.data.item:' + str(l) + '.item:1')
                linha_texto = 'grid1.data.item:' + str(l) + '.item:1'
                dois_cliques(1, linha, linha_texto, driver, data, dia, j, usuario, c)
                linha = driver.find_element(By.ID, 'grid1.data.item:' + str(l + 1) + '.item:1')
                linha_texto = 'grid1.data.item:' + str(l + 1) + '.item:1'
                dois_cliques(2, linha, linha_texto, driver, data, dia, j, usuario, c)
                break
            else:
                l += 1
                continue
        else:
            l += 1
            continue


def ValidaDiurno(dia, data, driver, j, usuario, c):
    for l in range(2):
        if l == 0:
            cancelado = driver.find_element(By.ID, 'grid1.data.item:' + str(l) + '.item:6').text
            if cancelado != 'Sim':
                linha = driver.find_element(By.ID, 'grid1.data.item:' + str(l) + '.item:1')
                linha_texto = 'grid1.data.item:' + str(l) + '.item:1'
                dois_cliques(l + 1, linha, linha_texto, driver, data, dia, j, usuario, c)
            else:
                linha = driver.find_element(By.ID, 'grid1.data.item:' + str(l + 1) + '.item:1')
                linha_texto = 'grid1.data.item:' + str(l + 1) + '.item:1'
                dois_cliques(l + 1, linha, linha_texto, driver, data, dia, j, usuario, c)
        else:
            cancelado = driver.find_element(By.ID, 'grid1.data.item:' + str(l) + '.item:6').text
            if cancelado != 'Sim':
                linha = driver.find_element(By.ID, 'grid1.data.item:' + str(l) + '.item:1')
                linha_texto = 'grid1.data.item:' + str(l) + '.item:1'
                dois_cliques(l + 1, linha, linha_texto, driver, data, dia, j, usuario, c)
            else:
                linha = driver.find_element(By.ID, 'grid1.data.item:' + str(l + 1) + '.item:1')
                linha_texto = 'grid1.data.item:' + str(l + 1) + '.item:1'
                dois_cliques(l + 1, linha, linha_texto, driver, data, dia, j, usuario, c)


def Excecao(driver):
    while True:
        try:
            wait = WebDriverWait(driver, 2)
            alert = wait.until(ec.alert_is_present())
            alert.accept()

            wait2 = WebDriverWait(driver, 2)
            alert2 = wait2.until(ec.alert_is_present())
            alert2.accept()
        except UnexpectedAlertPresentException:
            driver.switch_to.alert.accept()
            break
        except NoAlertPresentException:
            break
        except TimeoutException:
            break


def VoltarNoturno(dados, driver, c, usuario):
    for i, j in dados.iterrows():
        matricula = int(j[0])
        dias = 0
        for dia in j[2:33]:
            if str(dia) != '':
                dias += 1
        if dias > 0:
            ColarMatricula(matricula, c, driver)

        for dia in j[2:33]:
            if str(dia) != '':
                data = PegaDia(dia)
                InsereData(data, driver)
                ValidaNoturno(dia, data, driver, j, usuario, c)
        c += 1
    return c


def VoltarDiurno(dados, driver, c, usuario):
    for i, j in dados.iterrows():
        matricula = int(j[0])
        dias = 0
        for dia in j[2:33]:
            if str(dia) != '':
                dias += 1
        if dias > 0:
            ColarMatricula(matricula, c, driver)

        for dia in j[2:33]:
            if str(dia) != '':
                data = PegaDia(dia)
                InsereData(data, driver)
                ValidaDiurno(dia, data, driver, j, usuario, c)
        c += 1
    return c


def VoltarVinteQuatroHoras(dados, driver, c, usuario):
    for i, j in dados.iterrows():
        matricula = int(j[0])
        dias = 0
        for dia in j[2:33]:
            if str(dia) != '':
                dias += 1
        if dias > 0:
            ColarMatricula(matricula, c, driver)

        for dia in j[2:33]:
            if str(dia) != '':
                data = PegaDia(dia)
                InsereData(data, driver)
                ValidaDiurno(dia, data, driver, j, usuario, c)
        c += 1
    return c


def voltar_escala(mes, ano, driver, c, usuario):
    if mes < 10:
        mes = f'0{mes}'

    voltadas = RelatorioEscalaVoltada.objects.filter(importacao__mes=mes, importacao__ano=ano).values()

    escalas = (VoltarNegativos.objects.filter(importacao__mes=mes, importacao__ano=ano).
               exclude(empregado__matricula__in=voltadas.values_list('empregado__matricula', flat=True)).values())

    escalas = pd.DataFrame(escalas)
    escalas = pega_matricula(escalas, mes, ano)

    print(escalas)

    for i, j in escalas.iterrows():
        matricula = int(j['matricula'])
        dias = 0
        for dia in j[5:36]:
            if str(dia) != '':
                dias += 1
        if dias > 0:
            insere_mes_ano(mes, ano, driver)
            try:
                ColarMatricula(matricula, i, driver)
            except Exception as error:
                if (('O empregado não possui Cadastro' or 'Não disponível para consulta por este usuário' or
                    'Informe a matrícula')
                        in str(error)):
                    print(f'{matricula} - {j["nome"]}: Movimentado')
                    continue

            pesquisar = driver.find_element(By.XPATH, '/html/body/form/table[2]/tbody/tr/td/table/tbody/tr/td[9]/img')
            pesquisar.click()
            for dia, escala in j[5:36].items():
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

                        if driver.find_element(By.ID, sem_jornada).text != "Sem Jornada":
                            print(f"Escala já está incluída!")
                            salva_escala_voltada(j, escala, usuario, mes, ano, data)
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
                            select.select_by_value('')

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

                            print(f"Escala  incluída com sucesso")
                            data = str(f'{dia}/{mes}/{ano}')
                            salva_escala_voltada(j, escala, usuario, mes, ano, data)
                        else:
                            print(f"Não foi possível incluir escala")
                            data = str(f'{dia}/{mes}/{ano}')
                            salva_escala_voltada(j, escala, usuario, mes, ano, data)
                    except:
                        try:
                            insere_data_inicial(data, driver)

                            select = Select(driver.find_element(By.ID, 'Ocorrencia'))
                            select.select_by_value('')

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

                            print(f"Escala  incluída com sucesso")
                            data = str(f'{dia}/{mes}/{ano}')
                            salva_escala_voltada(j, escala, usuario, mes, ano, data)
                        except Exception as error:
                            print(f"Erro: {error}")
                            data = str(f'{dia}/{mes}/{ano}')
                            salva_escala_voltada(j, escala, usuario, mes, ano, data)
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
