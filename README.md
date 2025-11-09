# 🏠 IA Leilão Imóveis

Sistema de análise automatizada de imóveis de leilão da Caixa Econômica Federal utilizando IA (GPT-4o).

## 📋 Pré-requisitos

- Python 3.10
- Conda
- Poppler (para OCR de PDFs)
- Conta OpenAI com API Key

## 🚀 Instalação

### 1. Criar ambiente Conda

```bash
conda env create -f env.yaml
conda activate scrape-env
```

### 2. Instalar Poppler (para OCR)

**macOS:**
```bash
brew install poppler
```

**Windows:**
- Baixe de: https://github.com/oschwartz10612/poppler-windows/releases
- Adicione ao PATH

**Linux:**
```bash
sudo apt-get install poppler-utils
```

### 3. Configurar API da OpenAI

Crie um arquivo `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sua_chave_aqui
```

### 4. Configurar assistente (primeira vez)

```bash
# Upload do edital
python upload_edital.py

# Criar assistente
python create_assistent.py
```

## 🎯 Uso

### Opção 1: Interface Streamlit (Recomendado) 🌟

Execute o aplicativo web:

```bash
streamlit run app.py
```

Acesse: `http://localhost:8501`

**Funcionalidades:**
- 🏠 **Início**: Visão geral do projeto
- 🔍 **Buscar Imóveis**: Web scraping automático do site da Caixa
- 🤖 **Analisar Imóvel**: Análise com IA de imóveis individuais
- 📊 **Ranking**: Compare e ranqueie múltiplos imóveis

### Opção 2: Linha de Comando

#### Passo 1: Coletar dados

```bash
# Buscar lista de imóveis
python scrape_property_list.py

# Baixar detalhes de cada imóvel
python scrape_detail.py
```

#### Passo 2: Analisar com IA

Edite o `config.json` com o ID do imóvel desejado e execute:

```bash
python query.py
```

## 📁 Estrutura do Projeto

```
ia-leilao-imovel/
├── app.py                      # 🌟 Aplicativo Streamlit
├── scrape_property_list.py     # Busca lista de imóveis
├── scrape_detail.py            # Baixa detalhes individuais
├── query.py                    # Análise com IA
├── upload_edital.py            # Upload do edital para OpenAI
├── create_assistent.py         # Cria assistente GPT
├── config.json                 # Configurações do projeto
├── edital.pdf                  # Edital do leilão
├── env.yaml                    # Dependências
└── data/
    ├── list/                   # HTMLs com listas de imóveis
    ├── detail/                 # Detalhes e matrículas (PDFs)
    └── analysis/               # Resultados das análises
```

## 🤖 Critérios de Avaliação da IA

O sistema avalia cada imóvel em 5 critérios principais:

1. **Liquidez & Preço de Entrada (30%)**
   - Deságio vs. avaliação, tipologia, localização

2. **Situação Registral & Risco Jurídico (25%)**
   - Cadeia dominial, pendências judiciais

3. **Despesas Propter Rem (20%)**
   - IPTU, condomínio, passivos

4. **Prazos de Contratação & Registro (15%)**
   - Compatibilidade com horizonte de 6 meses

5. **Velocidade de Liquidez (10%)**
   - Potencial de revenda rápida

**Nota Final:** Média ponderada de 0 a 10

## 📊 Output da Análise

A IA retorna um JSON estruturado com:
- ✅ Dados completos do imóvel (50+ campos)
- 📊 Notas de 0-10 para cada critério com justificativas
- ⚠️ Riscos identificados
- 📝 Próximos passos recomendados

## 🛠️ Tecnologias

- **Python 3.10**
- **Streamlit** - Interface web
- **Selenium** - Web scraping
- **BeautifulSoup** - Parsing HTML
- **OpenAI API** - GPT-4o com file_search
- **Pytesseract** - OCR de matrículas
- **Plotly** - Visualizações interativas
- **Pandas** - Manipulação de dados

## 👥 Desenvolvedores

- 🐸 **Frog** (vinic011) - Coleta de dados, prompts
- 🎯 **32** (ymarcal) - Fine-tuning, Streamlit, artigo
- ⏰ **Delay** - Avaliação, validação, integração

## 📝 Licença

Projeto acadêmico - ITA TE-251