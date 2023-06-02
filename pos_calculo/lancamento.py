from time import sleep

from selenium.common import TimeoutException, NoAlertPresentException, UnexpectedAlertPresentException, \
    NoSuchElementException
from selenium.common.exceptions import JavascriptException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

from pos_calculo.dbchanges import salva_rubricas_lancadas


def ColarMatricula(matricula, c, driver):
    if c > 0:
        campo_matricula = driver.find_element(By.ID, 'servMatricula')
        campo_matricula.clear()
        campo_matricula.send_keys(Keys.TAB)
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


def SelecionarFolha(driver, folha):
    selecionar_folha = driver.find_element(By.LINK_TEXT, 'Seleção de Folha')
    selecionar_folha.click()

    wait = WebDriverWait(driver, 10)
    wait.until(ec.presence_of_element_located((By.ID, 'frame1')))

    frame1 = driver.find_element(By.ID, 'frame1')
    driver.switch_to.frame(frame1)

    wait = WebDriverWait(driver, 120)
    wait.until(ec.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/form/div[8]/table/tbody/tr[2]/td[7]")))

    ano = str(folha).split('/')
    ano = ano[1]
    select = Select(driver.find_element(By.ID, 'Ano'))
    select.select_by_value(ano)

    wait = WebDriverWait(driver, 120)
    wait.until(ec.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/form/div[8]/table/tbody/tr[2]/td[7]")))

    folha_selecionada = driver.find_element(By.XPATH, f"//td[contains(text(),'{folha}')]")
    ActionChains(driver).double_click(folha_selecionada).perform()

    try:
        fechar_erro = driver.find_element(By.ID, 'closeButton')
        fechar_erro.click()
        driver.back()
        sleep(2)
    except NoSuchElementException:
        sleep(2)
        pass


def InsereDados(j, driver, mes, ano, observacao, usuario, index, fator):
    for i in range(2 if j['rubrica_noturna'] == 878 else 1):
        # Limpa o campo e cola o código no campo Rubrica
        rubrica = ''
        if i == 0:
            rubrica = j['rubrica_diurna']
        if i == 1:
            rubrica = j['rubrica_noturna']
        campo_rubrica = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/form/div/div[1]/div["
                                                      "1]/table/tbody/tr[1]/td/table/tbody/tr[2]/td[1]/input")
        campo_rubrica.clear()
        campo_rubrica.send_keys(rubrica)

        # Limpa o campo e cola o código no campo Fator
        campo_fator = driver.find_element(By.XPATH, '//*[@id="T11"]/table/tbody/tr[1]/td/table/tbody/tr[2]/td[4]/input')
        campo_fator.clear()
        campo_fator.send_keys(fator)

        # Limpa o campo e cola o código no campo Mês/Ano Início Ocorrência
        mes_ano_ocorrencia = f'{mes}{ano}'
        inicio_ocorrencia = driver.find_element(By.XPATH, '/html/body/table/tbody/tr/td/form/div/div[1]/div['
                                                          '1]/table/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/input')
        inicio_ocorrencia.clear()
        if len(str(mes_ano_ocorrencia)) < 6:
            mes_ano_ocorrencia = f'0{mes_ano_ocorrencia}'
        inicio_ocorrencia.send_keys(mes_ano_ocorrencia)

        # Seleciona o operando (Valor ou Fórmula)
        operando = 'Fórmula'
        campo_operando = Select(driver.find_element(By.NAME, 'operando'))
        campo_operando.select_by_value(operando)

        # Limpa o campo e cola o o valor no campo Valor
        valor = ''
        if i == 0:
            valor = f'{str(j["hs_diurnas"]).split(".")[0]},{str(round(j["hs_diurnas"], 2)).split(".")[1]}' if \
                int(str(j["hs_diurnas"]).split(".")[0]) >= 10 else \
                f'0{str(j["hs_diurnas"]).split(".")[0]},{str(round(j["hs_diurnas"], 2)).split(".")[1]}'
        if i == 1:
            valor = f'{str(j["hs_noturnas"]).split(".")[0]},{str(round(j["hs_noturnas"], 2)).split(".")[1]}'
        if len(valor) < 5:
            valor = f'{valor}0'
        campo_valor = driver.find_element(By.XPATH, '/html/body/table/tbody/tr/td/form/div/div[1]/div['
                                                    '1]/table/tbody/tr[ '
                                                    '3]/td/table/tbody/tr[2]/td[3]/input')
        campo_valor.clear()
        campo_valor.send_keys(valor)

        # Limpa o campo e cola a observação no campo Observações
        campo_observacao = driver.find_element(By.NAME, 'obs')
        campo_observacao.clear()
        campo_observacao.send_keys(observacao)

        # Clica no botão Salvar e fecha a mensagem de Salvo com sucesso
        try:

            wait = WebDriverWait(driver, 2)
            wait.until(ec.presence_of_element_located((By.XPATH, '/html/body/table/tbody/tr/td/form/div/div[2]/input[1]'
                                                       )))

            botao_salvar = driver.find_element(By.XPATH, '/html/body/table/tbody/tr/td/form/div/div[2]/input[1]')
            action = ActionChains(driver)
            action.move_to_element(botao_salvar).click().perform()

            wait = WebDriverWait(driver, 2)
            wait.until(ec.presence_of_element_located((By.XPATH, "//span [text()='Dados salvos com "
                                                                 "sucesso.']")))

            fechar_mensagem = driver.find_element(By.ID, 'closeButton')
            fechar_mensagem.click()
            salva_rubricas_lancadas(j, usuario, mes, ano, rubrica, valor)
            print(f"{index} - {j['matricula']}: {rubrica} R$ {valor}")

        except JavascriptException:
            try:
                wait = WebDriverWait(driver, 2)
                wait.until(ec.presence_of_element_located((By.ID, 'closeButton')))
                fechar_mensagem = driver.find_element(By.ID, 'closeButton')
                fechar_mensagem.click()

                botao_salvar = driver.find_element(By.XPATH, '/html/body/table/tbody/tr/td/form/div/div[2]/input[1]')
                action = ActionChains(driver)
                action.move_to_element(botao_salvar).click().perform()

                wait = WebDriverWait(driver, 2)
                wait.until(ec.presence_of_element_located((By.XPATH, "//span [text()='Dados salvos com "
                                                                     "sucesso.']")))

                fechar_mensagem = driver.find_element(By.ID, 'closeButton')
                fechar_mensagem.click()
                salva_rubricas_lancadas(j, usuario, mes, ano, rubrica, valor)
                print(f"{index} - {j['matricula']}: {rubrica} - R$ {valor}")
            except TimeoutException:
                pass
        except TimeoutException:
            pass


def LancarRubricas(dados, driver, mes, ano, folha, observacao, usuario, fator):
    if len(dados) == 0:
        pass
    else:
        SelecionarFolha(driver, folha)

        wait = WebDriverWait(driver, 10)
        wait.until(ec.presence_of_element_located((By.ID, 'frame1')))

        frame1 = driver.find_element(By.ID, 'frame1')
        driver.switch_to.frame(frame1)

        matricula_anterior = None

        for i, j in dados.iterrows():
            try:
                matricula = j['matricula']
                index_as_int = int(str(i))

                if index_as_int == 0:
                    ColarMatricula(matricula, index_as_int, driver)

                    incluir = driver.find_element(By.LINK_TEXT, 'Incluir')
                    incluir.click()

                    InsereDados(j, driver, mes, ano, observacao, usuario, index_as_int + 1, fator)
                elif matricula_anterior == matricula:
                    InsereDados(j, driver, mes, ano, observacao, usuario, index_as_int, fator)
                else:
                    try:
                        wait = WebDriverWait(driver, 5)
                        wait.until(ec.presence_of_element_located((By.XPATH,
                                                                   "/html/body/table/tbody/tr/td/form/div/div[1]/div["
                                                                   "1]/table/tbody/tr[1]/td/table/tbody/tr[2]"
                                                                   "/td[1]/input")))
                        driver.back()

                        wait = WebDriverWait(driver, 10)
                        wait.until(ec.presence_of_element_located((By.ID, 'frame1')))

                        frame1 = driver.find_element(By.ID, 'frame1')
                        driver.switch_to.frame(frame1)

                        ColarMatricula(matricula, index_as_int, driver)

                        incluir = driver.find_element(By.LINK_TEXT, 'Incluir')
                        incluir.click()

                        InsereDados(j, driver, mes, ano, observacao, usuario, index_as_int + 1, fator)
                    except TimeoutException:

                        ColarMatricula(matricula, index_as_int, driver)

                        incluir = driver.find_element(By.LINK_TEXT, 'Incluir')
                        incluir.click()

                        InsereDados(j, driver, mes, ano, observacao, usuario, index_as_int + 1, fator)
                    finally:
                        matricula_anterior = matricula
            except UnexpectedAlertPresentException:
                matricula = j['matricula']
                index_as_int = int(str(i))
                print(f"{index_as_int +1} - {j['matricula']}: Movimentado")
                matricula_anterior = matricula
                continue


