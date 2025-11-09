# 🏠 IA Leilão Imóveis

Sistema de análise automatizada de imóveis de leilão da Caixa Econômica Federal utilizando IA (GPT-4o).

---

## 📋 Índice

1. [Visão Geral](#-visão-geral)
2. [Pré-requisitos](#-pré-requisitos)
3. [Instalação](#-instalação)
4. [Como Usar](#-como-usar)
5. [Automação com n8n](#-automação-com-n8n)
6. [Estrutura do Projeto](#-estrutura-do-projeto)
7. [Critérios de Avaliação](#-critérios-de-avaliação)
8. [Tecnologias](#-tecnologias)
9. [Documentação Adicional](#-documentação-adicional)
10. [Desenvolvedores](#-desenvolvedores)

---

## 🎯 Visão Geral

Este sistema automatiza a análise de imóveis de leilão, fornecendo:
- 🔍 **Web scraping** automático do site da Caixa
- 🤖 **Análise com IA** (GPT-4o) de cada imóvel
- 📊 **Nota de 0 a 10** baseada em 5 critérios ponderados
- 📧 **Notificações semanais** via email (opcional)
- 📱 **Interface web** para visualização e exploração

### Duas Formas de Usar

| Modo | Interface | Uso Ideal |
|------|-----------|-----------|
| **🌐 Streamlit** | Interface web interativa | Análise manual, exploração, visualização |
| **⚙️ Automação n8n** | Execução agendada com email | Notificações semanais, produção |

---

## 📦 Pré-requisitos

- **Python 3.10+**
- **Node.js 18+** (apenas para n8n)
- **Poppler** (para OCR de PDFs)
- **Conta OpenAI** com API Key

---

## 🚀 Instalação

### 1. Clonar/Baixar o Projeto

```bash
cd ia-leilao-imovel
```

### 2. Criar Ambiente Virtual

```bash
# Criar venv
python -m venv venv

# Ativar (Windows)
.\venv\Scripts\Activate.ps1

# Ativar (Linux/Mac)
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Instalar Poppler (para OCR)

**Windows:**
- Baixe de: https://github.com/oschwartz10612/poppler-windows/releases
- Adicione ao PATH ou use a pasta `poppler/` incluída

**macOS:**
```bash
brew install poppler
```

**Linux:**
```bash
sudo apt-get install poppler-utils
```

### 5. Configurar API da OpenAI

Crie um arquivo `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sk-sua-chave-aqui
```

### 6. Configurar Assistente (primeira vez)

```bash
# Upload do edital
python upload_edital.py

# Criar assistente
python create_assistent.py
```

---

## 🎯 Como Usar

### Opção 1: Interface Streamlit 🌟 (Recomendado para Exploração)

Execute o aplicativo web:

```bash
streamlit run app.py
```

Acesse: `http://localhost:8501`

#### Funcionalidades do Streamlit

**🏠 Início**
- Visão geral do projeto
- Estatísticas em tempo real
- Descrição dos critérios

**🔍 Buscar Imóveis**
- Web scraping automático por cidade/estado
- Download de lista e detalhes

**🤖 Analisar Imóvel**
- Selecionar imóvel e analisar com IA
- Visualização completa:
  - Nota final (0-10) com cores
  - Gráfico radar dos 5 critérios
  - Dados detalhados
  - Riscos identificados
  - Próximos passos
- Download em JSON

**📊 Ranking**
- Compare todos imóveis analisados
- Filtros avançados (nota, comarca, quartos)
- Gráfico de distribuição
- Exportar para CSV

**📖 Guia detalhado:** Consulte `GUIA_RAPIDO.md`

---

### Opção 2: Linha de Comando

#### Análise Completa Automatizada

```bash
# Análise completa: scraping + análise IA
python automation.py --estado GO --cidade "RIO VERDE" --min-nota 7

# Testar com poucos imóveis
python automation.py --estado GO --cidade GOIANIA --max-imoveis 3

# Ver todas opções
python automation.py --help
```

#### Passo a Passo Manual

```bash
# 1. Buscar lista de imóveis
python scrape_property_list.py

# 2. Baixar detalhes de cada imóvel
python scrape_detail.py

# 3. Analisar com IA (configure ID no config.json)
python query.py
```

---

## ⚙️ Automação com n8n

### O Que é?

**n8n** é uma ferramenta de automação workflow que permite executar o sistema automaticamente em horários agendados e enviar relatórios por email.

### Vantagens

- ✅ **Execução automática** semanal
- ✅ **Notificações por email** com top 5 imóveis
- ✅ **Zero intervenção manual**
- ✅ **Histórico completo** de análises
- ✅ **Gratuito e open source**

### Setup Rápido

#### 1. Instalar n8n

```bash
npm install -g n8n
```

#### 2. Iniciar n8n

```bash
n8n
# Acesse: http://localhost:5678
```

#### 3. Importar Workflow

1. No n8n, vá em **Menu > Import from File**
2. Selecione `workflow_n8n.json`
3. Configure credenciais SMTP (Gmail recomendado)
4. Configure variáveis de ambiente
5. Ative o workflow

#### 4. Configurar Email (Gmail)

1. Ative "Verificação em 2 etapas": https://myaccount.google.com/security
2. Gere "Senha de App": https://myaccount.google.com/apppasswords
3. Use no n8n:
   - Host: `smtp.gmail.com`
   - Port: `587`
   - User: seu-email@gmail.com
   - Password: senha-de-app-16-digitos

### O Que o Workflow Faz

```
⏰ Toda segunda-feira 8h
    ↓
🔍 Executa scraping + análise IA
    ↓
📊 Filtra imóveis com nota ≥ 7
    ↓
📧 Envia email HTML com top 5
    ↓
💾 Salva em data/analysis/
```

### Customizar

Edite o workflow para:
- Mudar cidade/estado: `--estado SP --cidade "SAO PAULO"`
- Mudar nota mínima: `--min-nota 8`
- Mudar horário: Edite cron expression (ex: `0 18 * * 5` = Sexta 18h)

### Documentação Completa

- **Setup detalhado:** `N8N_INTEGRATION.md`
- **Configuração de email:** `CONFIGURACAO_EMAIL.md`

---

## 📁 Estrutura do Projeto

```
ia-leilao-imovel/
├── 📱 Interface e Automação
│   ├── app.py                      # Interface Streamlit
│   ├── automation.py               # Pipeline de automação completo
│   ├── api.py                      # API REST FastAPI (opcional)
│
├── 🔍 Scripts de Coleta
│   ├── scrape_property_list.py     # Busca lista de imóveis
│   ├── scrape_detail.py            # Baixa detalhes individuais
│
├── 🤖 Scripts de Análise
│   ├── query.py                    # Análise com IA
│   ├── create_assistent.py         # Cria assistente GPT
│   ├── upload_edital.py            # Upload de edital
│   ├── setup_openai.py             # Configuração completa OpenAI
│
├── 📊 Dados
│   └── data/
│       ├── list/                   # HTMLs com listas de imóveis
│       ├── detail/                 # Detalhes e matrículas (HTML + PDF)
│       └── analysis/               # Resultados das análises (JSON)
│
├── ⚙️ Configuração
│   ├── config.json                 # Configurações do sistema
│   ├── requirements.txt            # Dependências Python
│   ├── env.yaml                    # Config ambiente conda
│   ├── .env                        # Chaves de API (criar)
│   └── workflow_n8n.json   # Workflow n8n pronto
│
├── 📚 Documentação
│   ├── README.md                   # Este arquivo
│   ├── GUIA_RAPIDO.md             # Como usar Streamlit
│   ├── N8N_INTEGRATION.md         # Guia completo n8n
│   ├── CONFIGURACAO_EMAIL.md      # Configurar email
│   ├── STREAMLIT_FEATURES.md      # Funcionalidades técnicas
│   └── PROXIMO_PASSOS.md          # Roadmap do projeto
│
└── 📄 Outros
    ├── edital.pdf                  # Edital exemplo
    └── poppler/                    # Biblioteca OCR
```

---

## 🤖 Critérios de Avaliação da IA

O sistema avalia cada imóvel em **5 critérios principais**:

| Critério | Peso | O Que Avalia |
|----------|------|--------------|
| **1. Liquidez & Preço de Entrada** | 30% | Deságio vs. avaliação, tipologia, localização |
| **2. Situação Registral & Risco Jurídico** | 25% | Cadeia dominial, pendências judiciais |
| **3. Despesas Propter Rem** | 20% | IPTU, condomínio, passivos |
| **4. Prazos de Contratação & Registro** | 15% | Compatibilidade com horizonte de 6 meses |
| **5. Velocidade de Liquidez** | 10% | Potencial de revenda rápida |

**Nota Final:** Média ponderada de 0 a 10

### Interpretação das Notas

| Faixa | Classificação | Recomendação |
|-------|---------------|--------------|
| **8.0 - 10.0** | 🟢 Excelente | Oportunidade muito boa, investigar imediatamente |
| **6.0 - 7.9** | 🟡 Boa | Potencial interessante, avaliar com cuidado |
| **4.0 - 5.9** | 🟠 Regular | Requer análise detalhada dos riscos |
| **0.0 - 3.9** | 🔴 Atenção | Muitos riscos, evitar ou investigar profundamente |

---

## 📊 Output da Análise

A IA retorna um JSON estruturado com:

```json
{
  "imovel": {
    "id": "1444427923",
    "comarca": "Rio Verde",
    "condominio": "Residencial Portal do Vale",
    "apartamento": "201",
    "quartos": "3",
    "area_privativa_m2": "75.00",
    "valor_minimo": "R$ 180.000,00",
    "valor_avaliacao": "R$ 250.000,00",
    "desconto_percent": "28%",
    ...
  },
  "criterios": [
    {
      "nome": "Liquidez & Preço de Entrada",
      "peso": 0.30,
      "nota": 8.5,
      "justificativa": "Desconto de 28% muito atrativo...",
      "fontes": ["edital_linha_45", "matricula_pagina_2"]
    },
    ...
  ],
  "nota_final": {
    "metodo": "media_ponderada",
    "valor": 8.2
  },
  "riscos": [
    {
      "descricao": "Condomínio em atraso (2 meses)",
      "fonte": "matricula_certidao"
    }
  ],
  "proximos_passos": [
    "1. Solicitar certidões negativas atualizadas",
    "2. Verificar quitação do condomínio",
    "3. Agendar visita presencial"
  ]
}
```

---

## 🛠️ Tecnologias

### Backend
- **Python 3.10**
- **OpenAI API** (GPT-4o com file_search)
- **Selenium** (Web scraping)
- **BeautifulSoup** (Parsing HTML)
- **Pytesseract** (OCR de matrículas)
- **FastAPI** (API REST opcional)

### Frontend
- **Streamlit** (Interface web)
- **Plotly** (Visualizações interativas)
- **Pandas** (Manipulação de dados)

### Automação
- **n8n** (Workflow automation)
- **Subprocess** (Execução de scripts)

---

## 📚 Documentação Adicional

### Guias de Uso
| Documento | Descrição | Quando Consultar |
|-----------|-----------|------------------|
| `GUIA_RAPIDO.md` | Como usar o Streamlit | Primeiro uso da interface |
| `N8N_INTEGRATION.md` | Guia completo de automação | Configurar n8n |
| `CONFIGURACAO_EMAIL.md` | Setup de email SMTP | Problemas com envio de email |

### Documentação Técnica
| Documento | Descrição |
|-----------|-----------|
| `STREAMLIT_FEATURES.md` | Funcionalidades e arquitetura do Streamlit |
| `PROXIMO_PASSOS.md` | Roadmap e próximas implementações |

### Arquivos de Configuração
| Arquivo | Descrição |
|---------|-----------|
| `workflow_n8n.json` | Workflow n8n pronto para importar |
| `config.json` | Configurações do sistema (IDs, cidades) |
| `.env` | Chaves de API (criar manualmente) |

---

## 🔧 Comandos Úteis

### Streamlit
```bash
# Iniciar aplicativo
streamlit run app.py

# Limpar cache
streamlit cache clear
```

### Análise
```bash
# Análise completa automatizada
python automation.py --estado GO --cidade GOIANIA --min-nota 7

# Testar com 1 imóvel
python automation.py --estado GO --cidade GOIANIA --max-imoveis 1

# Ver ajuda
python automation.py --help
```

### n8n
```bash
# Instalar
npm install -g n8n

# Iniciar
n8n

# Acesso: http://localhost:5678
```

### API (Opcional)
```bash
# Iniciar API REST
python api.py

# Docs: http://localhost:8000/docs
```

---

## 🐛 Troubleshooting

### Erro: "OPENAI_API_KEY not found"

**Solução:**
```bash
# Criar arquivo .env
echo OPENAI_API_KEY=sk-sua-chave > .env
```

### Erro: "No assistant found"

**Solução:**
```bash
# Reconfigurar OpenAI
python setup_openai.py
```

### Erro: Poppler não encontrado

**Solução (Windows):**
- Baixe de: https://github.com/oschwartz10612/poppler-windows/releases
- Extraia para `C:\poppler`
- Adicione `C:\poppler\Library\bin` ao PATH

### Streamlit não abre

**Solução:**
```bash
# Verificar instalação
streamlit --version

# Reinstalar se necessário
pip install --upgrade streamlit
```

### Análise muito lenta

**Normal:**
- Primeira análise: 2-3 minutos (inclui OCR)
- Análises subsequentes: 1-2 minutos (cache parcial)
- API OpenAI pode estar ocupada

**Dica:** Use `--max-imoveis 1` para testes rápidos

---

## 👥 Desenvolvedores

**Projeto TE-251 - ITA (2025)**

| Dev | GitHub | Responsabilidades |
|-----|--------|-------------------|
| 🐸 **Frog** | vinic011 | Coleta de dados (scraping), prompts |
| 🎯 **32** | ymarcal | Fine-tuning, Streamlit, n8n, artigo |
| ⏰ **Delay** | - | Avaliação, validação, integração |

---

## 📝 Licença

Projeto acadêmico desenvolvido para a disciplina TE-251 do ITA.

---

## 🏆 Status do Projeto

```
✅ Web scraping automatizado
✅ Prompts otimizados
✅ Análise com GPT-4o (file_search)
✅ Interface Streamlit completa
✅ Automação n8n implementada
✅ API REST funcional
✅ Documentação completa
⏳ Fine-tuning (em andamento)
⏳ Artigo IEEE (planejado)
```

---

## 🚀 Quick Start

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar OpenAI
echo OPENAI_API_KEY=sk-sua-chave > .env
python setup_openai.py

# 3. Iniciar Streamlit
streamlit run app.py

# 4. Acessar: http://localhost:8501
```

---

## 📞 Suporte

**Problemas?**
1. Consulte a seção [Troubleshooting](#-troubleshooting)
2. Verifique os guias em `📚 Documentação Adicional`
3. Execute `python setup_openai.py` para reconfigurar

---

**Última atualização:** 09/11/2025  
**Versão:** 2.0  
**Status:** ✅ Produção
