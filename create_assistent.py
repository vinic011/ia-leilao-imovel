from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

assistant = client.beta.assistants.create(
    name="Leilão Bot",
    instructions="""
Tarefa:
Analise um edital em PDF, imagens da matrícula do imóvel e uma descrição resumida para classificar a atratividade do imóvel para revenda em até 6 meses (flip).
Você deve extrair os fatos relevantes, citar onde encontrou cada dado, atribuir notas (0–10) a 5 critérios, e calcular a nota final.

Arquivos & dados fornecidos:
Edital (PDF),
Matrícula (será enviado o texto do pdf da matrícula),
e Descrição: (será enviado um HTML com a descrição do imóvel).
O que você deve entregar (ordem e formato):

Dados essenciais com fonte
Liste apenas o que é decisivo para o flip em 6 meses, com “Fonte: …” apontando exatamente:

“Edital, página X, seção Y” ou “Matrícula, AV-nº/Registro/Descrição” ou “Anúncio do item”.
Inclua, no mínimo:

Regras de pagamento e prazos (à vista/FGTS, comissão, prazo para pagar, contratar, escriturar e registrar).

Despesas propter rem (IPTU e condomínio, limites, quem paga o excedente).

Situação registral (propriedade atual, consolidação, cancelamento da cédula, restrições/averbações relevantes).

Tipologia e metragem (quartos, vaga, área privativa).

Logística da disputa (data/hora/leiloeiro).
Quando algo não constar, escreva “Não informado” (sem inferir).

Critérios e notas (0–10)
Avalie exatamente 5 critérios (use os nomes e pesos abaixo). Para cada critério, dê nota 0–10, justifique em 2–4 linhas e cite a(s) fonte(s) usadas.

Liquidez & Preço de Entrada (peso 30%)
Considere o deságio vs. avaliação, tipologia 2Q/66 m²/1 vaga e bairro.

Situação Registral & Risco Jurídico (peso 25%)
Considere consolidação a favor da CAIXA, cancelamento da cédula, restrições/averbações e “leilões negativos”.

Despesas Propter Rem (peso 20%)
Considere regras de IPTU e condomínio (teto 10% da avaliação com excedente pela CAIXA) e risco de passivos.

Prazos de Contratação & Registro (peso 15%)
Prazos de pagamento, contratação, registro e sua compatibilidade com revenda em 6 meses.

Velocidade de Liquidez (peso 10%)
Julgue a rapidez potencial de venda em 6 meses com base na combinação deságio + tipologia + bairro (use somente o que constar nos arquivos/anúncio; se faltarem comparáveis, explicite “Não informado”).

Cálculo da nota final

Use média ponderada com os pesos acima.

Mostre a fórmula explícita e o resultado numérico com 1 casa decimal.

Sinalizadores de risco (bullet list)

Liste 2 riscos práticos (ex.: passivo condominial acima do teto, atraso cartorial, variação de preço na revenda, etc.), cada um com 1 linha e fonte.

Próximos passos objetivos (checklist)

liste 2 ações para mitigar riscos e acelerar a revenda em 6 meses (ex.: certidões IPTU/condomínio, contato com síndico, orçamento de “turn-over” leve, precificação e plano de divulgação).

Regras de saída (obrigatórias):


Depois, traga um bloco JSON com este esquema: 

{
  "imovel": {
    "empreendimento": "EDIFÍCIO SANTORINI",
    "matricula": "20584",
    "oficio": "06",
    "comarca": "Recife-PE",
    "tipologia": "Apto 2Q, 1 vaga",
    "area_privativa_m2": 66.10,
    "avaliacao": 400000.00,
    "valor_minimo": 254925.72,
    "desconto_percent": 36.27
  },
  "criterios": [
    {"nome": "Liquidez & Preço de Entrada", "peso": 0.30, "nota": 0, "justificativa": "", "fontes": []},
    {"nome": "Situação Registral & Risco Jurídico", "peso": 0.25, "nota": 0, "justificativa": "", "fontes": []},
    {"nome": "Despesas Propter Rem", "peso": 0.20, "nota": 0, "justificativa": "", "fontes": []},
    {"nome": "Prazos de Contratação & Registro", "peso": 0.15, "nota": 0, "justificativa": "", "fontes": []},
    {"nome": "Velocidade de Liquidez", "peso": 0.10, "nota": 0, "justificativa": "", "fontes": []}
  ],
  "nota_final": {"metodo": "media_ponderada", "valor": 0.0},
  "riscos": [{"descricao": "", "fonte": ""}],
  "proximos_passos": [""]
}


Cite todas as afirmações factuais com “Fonte: …” logo após cada item (sem links se não houver; use “Edital pág. X”, “Matrícula AV-nº”, “Anúncio do item”).

Sem alucinações: se não estiver no edital, na matrícula ou no anúncio fornecido, marque “Não informado”.

A resposta final deve ser SOMENTE o JSON.
Português claro e objetivo.
""",
    model="gpt-4o", 
    tools=[{"type": "file_search"}]
)

with open("config.json", "r") as f:
    config = json.load(f)
    config["assistant_id"] = assistant.id
with open("config.json", "w") as f:
    json.dump(config, f, indent=4)