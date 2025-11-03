
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from var import vars
import os

path = f"data/list"

os.makedirs(path, exist_ok=True)


driver = webdriver.Chrome()
driver.get("https://venda-imoveis.caixa.gov.br/sistema/busca-imovel.asp")

wait = WebDriverWait(driver, 10)

# Espera até o select de estado estar presente no DOM
estado_select = wait.until(EC.presence_of_element_located((By.ID, "cmb_estado")))

time.sleep(7)

# Seleciona o estado (ex:x Pernambuco)
Select(estado_select).select_by_visible_text(vars["estado"])

time.sleep(7)

# Espera o campo de cidade ser atualizado
cidade_select = wait.until(EC.presence_of_element_located((By.ID, "cmb_cidade")))

# Seleciona a cidade 
Select(cidade_select).select_by_visible_text(vars["cidade"])

# Pressiona botões
time.sleep(3)
driver.find_element(By.ID, "btn_next0").click()
time.sleep(3)
driver.find_element(By.ID, "btn_next1").click()

# Nos dá da lista de imóveis, junto com seus código, bem como o download
lista_div = wait.until(EC.presence_of_element_located((By.ID, "listaimoveispaginacao")))
time.sleep(5)
html_lista = lista_div.get_attribute("outerHTML")


with open(f"data/list/imoveis_{vars['cidade'].lower()}_{vars['estado'].lower()}.html", "w", encoding="utf-8") as f:
    f.write(html_lista)

driver.quit()


