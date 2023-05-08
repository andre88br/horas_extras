
from django.core.exceptions import ObjectDoesNotExist
from selenium.common import TimeoutException, NoAlertPresentException, UnexpectedAlertPresentException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from pos_calculo.dbchanges import salva_rejeitada
from pos_calculo.models import RelatorioBatidasRejeitadas


def ColarMatricula(matricula, index_as_int, driver):
    if int(index_as_int) > 0:
        campo_matricula = driver.find_element(By.NAME, 'servMatr')
        campo_matricula.clear()
        try:
            wait = WebDriverWait(driver, 5)
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
            campo_matricula = driver.find_element(By.NAME, 'servMatr')
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


def dois_cliques(l, linha, linha_texto, driver, data, dia, j, usuario, c):
    mes, ano = int(str(data[2:4])), int(str(data[4:]))
    try:
        batida1 = RelatorioBatidasRejeitadas.objects.filter(empregado__matricula=j['matricula'],
                                                            data=dia, batida=1,
                                                            tipo=j['tipo'])
        batida2 = RelatorioBatidasRejeitadas.objects.filter(empregado__matricula=j['matricula'],
                                                            data=dia, batida=2,
                                                            tipo=j['tipo'])
        if batida1 and batida2:
            raise ObjectDoesNotExist
        else:
            rejeitado = driver.find_element(By.ID, linha_texto[:23] + '7').text
            if rejeitado != 'Sim':
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
                print(f'{c}-{j["matricula"]}: Batida {l} do dia {dia} rejeitada com sucesso!')
                salva_rejeitada(j, usuario, mes, ano, dia)
                InsereData(data, driver)
            else:
                print(f'{c}-{j["matricula"]}: Batida {l} do dia {dia} já estava rejeitada!')
                salva_rejeitada(j, usuario, mes, ano, dia)
    except ObjectDoesNotExist:
        print(f'{c}-{j["matricula"]}: Batida {l} do dia {dia} já estava rejeitada!')
        salva_rejeitada(j, usuario, mes, ano, dia)


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


def Noturno(dados, driver, c, usuario):
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


def Diurno(dados, driver, c, usuario):
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


def VinteQuatroHoras(dados, driver, c, usuario):
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
