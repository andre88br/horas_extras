# Imports
from time import sleep

from selenium.common import TimeoutException, NoAlertPresentException, UnexpectedAlertPresentException, \
    NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from pos_calculo.dbchanges import salva_banco_recalculado


def ColarMatricula(matricula, index_as_int, driver):
    if int(index_as_int) > 0:
        try:
            wait = WebDriverWait(driver, 1)
            wait.until(ec.presence_of_element_located((By.ID, 'frame1')))

            frame1 = driver.find_element(By.ID, 'frame1')
            driver.switch_to.frame(frame1)
        except TimeoutException:
            pass
        campo_matricula = driver.find_element(By.ID, 'servMatricula')
        campo_matricula.clear()
        try:
            wait = WebDriverWait(driver, 2)
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
            campo_matricula = driver.find_element(By.ID, 'servMatricula')
            campo_matricula.send_keys(matricula)
            campo_matricula.send_keys(Keys.TAB)
    else:
        campo_matricula = driver.find_element(By.ID, 'servMatricula')
        campo_matricula.send_keys(matricula)
        campo_matricula.send_keys(Keys.TAB)


def RecalcularNegativos(dados, driver, mes_ano, observacao, usuario):
    if len(dados) == 0:
        pass
    else:
        campo_mes_ano = driver.find_element(By.ID, 'MesAno')
        campo_mes_ano.send_keys(mes_ano)
        campo_mes_ano.send_keys(Keys.TAB)
        c = 0
        for i, j in dados.iterrows():

            matricula = int(j['matricula'])
            index_as_int = int(str(i))

            ColarMatricula(matricula, index_as_int, driver)

            if 'banco de horas' not in str(driver.find_element(By.ID, 'observacao').get_attribute('value')):

                campo_observacao = driver.find_element(By.ID, 'observacao')
                campo_observacao.send_keys(observacao)
                campo_observacao.send_keys(Keys.TAB)

            recalcular = driver.find_element(By.LINK_TEXT, 'Recalcular')
            recalcular.click()

            wait = WebDriverWait(driver, 3)
            wait.until(ec.presence_of_element_located((By.ID, 'ProgressBarFrame')))

            frame_progresso = driver.find_element(By.ID, 'ProgressBarFrame')
            driver.switch_to.frame(frame_progresso)

            sleep(3)

            try:
                fechar_erro = driver.find_element(By.ID, 'closeButton')
                fechar_erro.click()

                fechar = driver.find_element(By.ID, 'progressCloseButton')
                fechar.click()
                print(f'{c+1}-{matricula}: Banco recalculado com sucesso!')
                c += 1
                salva_banco_recalculado(j, usuario, mes_ano[:2], mes_ano[2:])
                continue
            except NoSuchElementException:
                pass

            concluido = driver.find_element(By.CLASS_NAME, 'progress').find_element(By.TAG_NAME, 'spam').text

            while concluido != 'Concluído':
                sleep(2)
                concluido = driver.find_element(By.CLASS_NAME, 'progress').find_element(By.TAG_NAME, 'spam').text

            fechar = driver.find_element(By.ID, 'progressCloseButton')
            fechar.click()
            print(f'{c+1}-{matricula}: Banco recalculado com sucesso!')
            c += 1
            salva_banco_recalculado(j, usuario, mes_ano[:2], mes_ano[2:])

