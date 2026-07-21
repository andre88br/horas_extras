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
            wait = WebDriverWait(driver, 3)
            wait.until(ec.presence_of_element_located((By.ID, 'frame1')))

            frame1 = driver.find_element(By.ID, 'frame1')
            driver.switch_to.frame(frame1)
        except TimeoutException:
            pass
        wait = WebDriverWait(driver, 3)
        wait.until(ec.presence_of_element_located((By.ID, 'servMatricula')))
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
            wait = WebDriverWait(driver, 3)
            wait.until(ec.presence_of_element_located((By.ID, 'servMatricula')))
            campo_matricula = driver.find_element(By.ID, 'servMatricula')
            campo_matricula.send_keys(matricula)
            campo_matricula.send_keys(Keys.TAB)
    else:
        wait = WebDriverWait(driver, 3)
        wait.until(ec.presence_of_element_located((By.ID, 'servMatricula')))
        campo_matricula = driver.find_element(By.ID, 'servMatricula')
        campo_matricula.send_keys(matricula)
        campo_matricula.send_keys(Keys.TAB)


def RecalcularBanco(dados, driver, mes_ano, observacao, usuario):
    if len(dados) == 0:
        pass
    else:
        c = len(dados)
        for i, j in dados.iterrows():
            try:
                wait = WebDriverWait(driver, 3)
                wait.until(ec.presence_of_element_located((By.ID, 'frame1')))

                frame1 = driver.find_element(By.ID, 'frame1')
                driver.switch_to.frame(frame1)
            except TimeoutException:
                pass
            wait = WebDriverWait(driver, 5)
            wait.until(ec.presence_of_element_located((By.ID, 'MesAno')))
            campo_mes_ano = driver.find_element(By.ID, 'MesAno')
            campo_mes_ano.send_keys(mes_ano)
            campo_mes_ano.send_keys(Keys.TAB)

            matricula = int(j[0])
            index_as_int = int(str(i))

            ColarMatricula(matricula, index_as_int, driver)

            if 'Recalculo do banco de horas' not in str(driver.find_element(By.ID, 'observacao').get_attribute('value')):

                campo_observacao = driver.find_element(By.ID, 'observacao')
                campo_observacao.send_keys(observacao)
                campo_observacao.send_keys(Keys.TAB)

                recalcular = driver.find_element(By.LINK_TEXT, 'Recalcular')
                recalcular.click()

                # O SIGP passou a processar o recálculo em 2º plano: a barra de
                # progresso (ProgressBarFrame) não aparece mais. Após acionar
                # "Recalcular", dispensamos qualquer aviso (alerta/clique num ponto
                # neutro da página) e seguimos para a próxima matrícula.
                sleep(2)
                try:
                    driver.switch_to.alert.accept()
                except (NoAlertPresentException, UnexpectedAlertPresentException):
                    pass
                try:
                    driver.find_element(By.TAG_NAME, 'body').click()
                except Exception:
                    pass

                print(f'{c}-{matricula}: Banco enviado para recálculo!')
                c -= 1
                salva_banco_recalculado(j, usuario, mes_ano[:2], mes_ano[2:])
                driver.refresh()
            else:
                print(f'{c}-{matricula}: Banco já recalculado!')
                c -= 1
                salva_banco_recalculado(j, usuario, mes_ano[:2], mes_ano[2:])
