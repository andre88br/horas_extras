from datetime import datetime
from time import sleep

from selenium.common import TimeoutException, NoAlertPresentException, UnexpectedAlertPresentException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


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
    sleep(3)
    campo_data = driver.find_element(By.NAME, 'diaAnoMesI')
    campo_data.clear()
    campo_data.send_keys(data)
    campo_data.send_keys(Keys.TAB)

    pesquisar = driver.find_element(By.TAG_NAME, 'td').find_element(By.TAG_NAME, 'img')
    pesquisar.click()


def dois_cliques(l, linha, linha_texto, driver, data, dia):
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
        print(f'Batida {l + 1} do dia {dia} rejeitada com sucesso!')
        InsereData(data, driver)
    else:
        print(f'Batida {l + 1} do dia {dia} já estava rejeitada!')


def ValidaNoturno(dia, data, driver):
    hora = ''
    for l in range(2):
        if l == 0:
            hora = driver.find_element(By.ID, 'grid1.data.item:' + str(l) + '.item:2').text
            hora = hora.split(':')

        if l == 0 and int(hora[0]) >= 17:
            cancelado = driver.find_element(By.ID, 'grid1.data.item:' + str(l) + '.item:6').text
            if cancelado != 'Sim':
                linha = driver.find_element(By.ID, 'grid1.data.item:' + str(l) + '.item:1')
                linha_texto = 'grid1.data.item:' + str(l) + '.item:1'
                dois_cliques(l, linha, linha_texto, driver, data, dia)
            else:
                linha = driver.find_element(By.ID, 'grid1.data.item:' + str(l + 1) + '.item:1')
                linha_texto = 'grid1.data.item:' + str(l + 1) + '.item:1'
                dois_cliques(l, linha, linha_texto, driver, data, dia)
        elif l == 1 and int(hora[0]) >= 17:
            cancelado = driver.find_element(By.ID, 'grid1.data.item:' + str(l) + '.item:6').text
            if cancelado != 'Sim':
                linha = driver.find_element(By.ID, 'grid1.data.item:' + str(l) + '.item:1')
                linha_texto = 'grid1.data.item:' + str(l) + '.item:1'
                dois_cliques(l, linha, linha_texto, driver, data, dia)
            else:
                linha = driver.find_element(By.ID, 'grid1.data.item:' + str(l + 1) + '.item:1')
                linha_texto = 'grid1.data.item:' + str(l + 1) + '.item:1'
                dois_cliques(l, linha, linha_texto, driver, data, dia)
        else:
            cancelado = driver.find_element(By.ID, 'grid1.data.item:' + str(l + 1) + '.item:6').text
            if cancelado != 'Sim':
                linha = driver.find_element(By.ID, 'grid1.data.item:' + str(l + 1) + '.item:1')
                linha_texto = 'grid1.data.item:' + str(l + 1) + '.item:1'
                dois_cliques(l, linha, linha_texto, driver, data, dia)
            else:
                linha = driver.find_element(By.ID, 'grid1.data.item:' + str(l + 2) + '.item:1')
                linha_texto = 'grid1.data.item:' + str(l + 2) + '.item:1'
                dois_cliques(l, linha, linha_texto, driver, data, dia)


def ValidaDiurno(dia, data, driver):
    for l in range(2):
        if l == 0:
            cancelado = driver.find_element(By.ID, 'grid1.data.item:' + str(l) + '.item:6').text
            if cancelado != 'Sim':
                linha = driver.find_element(By.ID, 'grid1.data.item:' + str(l) + '.item:1')
                linha_texto = 'grid1.data.item:' + str(l) + '.item:1'
                dois_cliques(l, linha, linha_texto, driver, data, dia)
            else:
                linha = driver.find_element(By.ID, 'grid1.data.item:' + str(l + 1) + '.item:1')
                linha_texto = 'grid1.data.item:' + str(l + 1) + '.item:1'
                dois_cliques(l, linha, linha_texto, driver, data, dia)
        else:
            cancelado = driver.find_element(By.ID, 'grid1.data.item:' + str(l) + '.item:6').text
            if cancelado != 'Sim':
                linha = driver.find_element(By.ID, 'grid1.data.item:' + str(l) + '.item:1')
                linha_texto = 'grid1.data.item:' + str(l) + '.item:1'
                dois_cliques(l, linha, linha_texto, driver, data, dia)
            else:
                linha = driver.find_element(By.ID, 'grid1.data.item:' + str(l + 1) + '.item:1')
                linha_texto = 'grid1.data.item:' + str(l + 1) + '.item:1'
                dois_cliques(l, linha, linha_texto, driver, data, dia)


def Excecao(driver):
    while True:
        try:
            wait = WebDriverWait(driver, 10)
            alert = wait.until(ec.alert_is_present())
            alert.accept()

            wait2 = WebDriverWait(driver, 10)
            alert2 = wait2.until(ec.alert_is_present())
            alert2.accept()
        except UnexpectedAlertPresentException:
            driver.switch_to.alert.accept()
            break
        except NoAlertPresentException:
            break
        except TimeoutException:
            break


def Noturno(dados, driver, c):
    for i, j in dados.iterrows():
        matricula = int(j[0])

        ColarMatricula(matricula, c, driver)

        for dia in j[2:33]:
            data = PegaDia(dia)
            if data != 'Campo Vazio':
                InsereData(data, driver)
                ValidaNoturno(dia, data, driver)
        c += 1
    return c


def Diurno(dados, driver, c):
    for i, j in dados.iterrows():

        matricula = int(j[0])
        ColarMatricula(matricula, c, driver)
        for dia in j[2:33]:
            data = PegaDia(dia)
            if data != 'Campo Vazio':
                InsereData(data, driver)
                ValidaDiurno(dia, data, driver)
        c += 1
    return c


def VinteQuatroHoras(dados, driver, c):
    for i, j in dados.iterrows():
        matricula = int(j[0])
        ColarMatricula(matricula, c, driver)

        for dia in j[2:33]:
            data = PegaDia(dia)
            if data != 'Campo Vazio':
                InsereData(data, driver)
                ValidaDiurno(dia, data, driver)
        c += 1
    return c
