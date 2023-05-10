from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


def TestaSenha(username, senha):
    service = Service("chromedriver.exe")
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=service, options=options)

    url = "https://sigp.ebserh.gov.br/csp/ebserh/index.csp"

    try:
        driver.get(url)

        username_input = driver.find_element(By.ID, 'login')
        username_input.send_keys(username)

        # Find the password input by inspecting on password input
        password_input = driver.find_element(By.ID, 'senha')
        password_input.send_keys(senha)

        # Click on submit
        submit_button = driver.find_element(By.CLASS_NAME, 'btn-primary')
        submit_button.click()

        wait = WebDriverWait(driver, 20)
        wait.until(ec.presence_of_element_located((By.XPATH, "/html/body/div[1]/span[1]")))

        fechar_erro = driver.find_element(By.XPATH, "/html/body/div[1]/span[1]")
        fechar_erro.click()

        ActionChains(driver).click().perform()

        username_input = driver.find_element(By.ID, 'login')
        username_input.clear()

        # Find the password input by inspecting on password input
        password_input = driver.find_element(By.ID, 'senha')
        password_input.clear()
        return 'erro'
    except TimeoutException:
        # hwnd = win32gui.FindWindow(None, 'MENTORH')  # Insira o título da página
        # win32gui.ShowWindow(hwnd, 0)
        driver.quit()
        return 'ok'
