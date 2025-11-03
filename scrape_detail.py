from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from var import vars
import os
from selenium.webdriver.chrome.options import Options

# Caminho onde quer salvar os PDFs
download_dir = f"{os.getcwd()}/data/detail/{vars['cidade'].lower()}_{vars['estado'].lower()}"

# Configurações do Chrome
options = Options()
options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True  # Abre PDF fora do Chrome
})

path = f"data/detail/{vars['cidade'].lower()}_{vars['estado'].lower()}"
os.makedirs(path, exist_ok=True)

html = open(f"data/list/imoveis_{vars['cidade'].lower()}_{vars['estado'].lower()}.html", "r", encoding="utf-8").read()  # ou use a string HTML direto
soup = BeautifulSoup(html, "html.parser")

# Pega todos os <font> ou <span> que contêm "Número do imóvel"
imoveis = []
for tag in soup.find_all(text=lambda t: "Número do imóvel" in t):
    # o texto vem com "Número do imóvel: 144440974810-5"
    partes = tag.strip().split(":")
    if len(partes) > 1:
        numero = partes[1].strip().split("<")[0].split()[0].replace("-", "")  # extrai o número e remove o hífen
        imoveis.append(numero)

for imovel in imoveis:
    print(imovel)

    driver = webdriver.Chrome(options=options)
    driver.get("https://venda-imoveis.caixa.gov.br/sistema/busca-imovel.asp")

    wait = WebDriverWait(driver, 10)

    # Espera até o select de estado estar presente no DOM
    estado_select = wait.until(EC.presence_of_element_located((By.ID, "cmb_estado")))

    time.sleep(5)

    # Seleciona o estado (ex:x Pernambuco)
    Select(estado_select).select_by_visible_text(vars["estado"])

    time.sleep(5)

    # Espera o campo de cidade ser atualizado
    cidade_select = wait.until(EC.presence_of_element_located((By.ID, "cmb_cidade")))

    # Seleciona a cidade (ex: RECIFE)
    Select(cidade_select).select_by_visible_text(vars["cidade"])

    # Extrai todas as opções de cidade
    time.sleep(2)
    driver.find_element(By.ID, "btn_next0").click()
    time.sleep(2)
    driver.find_element(By.ID, "btn_next1").click()

    time.sleep(2)

    # salvar detalhe:
    driver.execute_script(f"detalhe_imovel({imovel})")
    detalhe = wait.until(EC.presence_of_element_located((By.ID, "dadosImovel")))

    with open(f"{path}/{imovel}.html", "w", encoding="utf-8") as f:
        f.write(detalhe.get_attribute("outerHTML"))

    driver.execute_script(f"ExibeDoc('/editais/matricula/{vars['estado']}/{imovel}.pdf')")

    time.sleep(2)  # espera o PDF carregar

    driver.quit()

