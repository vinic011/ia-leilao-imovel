# 🔄 Integração com n8n - Guia Completo

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Pré-requisitos](#pré-requisitos)
3. [Método 1: Script Standalone](#método-1-script-standalone)
4. [Método 2: API FastAPI](#método-2-api-fastapi)
5. [Workflows n8n Exemplo](#workflows-n8n-exemplo)
6. [Configuração de Email](#configuração-de-email)
7. [Agendamento Semanal](#agendamento-semanal)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

Esta integração permite automatizar completamente o pipeline de análise de imóveis:

```
┌──────────────────────────────────────────────────────────────┐
│                    AUTOMAÇÃO COMPLETA                         │
└──────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  n8n (Trigger)  │  ← Cron semanal (ex: toda segunda 8h)
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Executar       │  ← Chama automation.py OU API
│  Análise        │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Processar      │  ← Extrai top imóveis (nota ≥ 7)
│  Resultados     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Enviar Email   │  ← Relatório HTML com top 5
│  Notificação    │
└─────────────────┘
```

---

## 📦 Pré-requisitos

### 1. Instalar n8n

```bash
# Via npm (recomendado)
npm install -g n8n

# OU via Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### 2. Instalar Dependências do Projeto

```bash
cd ia-leilao-imovel
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente

Crie/atualize `.env` com:

```env
OPENAI_API_KEY=sk-...
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app
EMAIL_TO=destinatario@email.com
```

---

## 🚀 Método 1: Script Standalone

### Características
- ✅ Simples e direto
- ✅ Não requer servidor adicional
- ✅ Ideal para automações agendadas
- ⚠️ Bloqueante (espera conclusão)

### Como Usar

#### No Terminal

```bash
cd ia-leilao-imovel

# Exemplo: Análise em Rio Verde/GO, apenas nota ≥ 7
python automation.py --estado GO --cidade "RIO VERDE" --min-nota 7

# Exemplo: Teste com 3 imóveis apenas
python automation.py --estado GO --cidade GOIANIA --max-imoveis 3 --min-nota 0
```

#### No n8n

**Node: Execute Command**

```json
{
  "command": "python",
  "arguments": [
    "automation.py",
    "--estado",
    "GO",
    "--cidade",
    "RIO VERDE",
    "--min-nota",
    "7"
  ],
  "workdir": "/caminho/completo/para/ia-leilao-imovel"
}
```

**Saída:** JSON completo com resultados no `stdout`

---

## 🌐 Método 2: API FastAPI

### Características
- ✅ Assíncrono (não bloqueia)
- ✅ RESTful (padrão web)
- ✅ Healthcheck integrado
- ✅ Múltiplas análises simultâneas
- ⚠️ Requer servidor rodando

### 1. Iniciar API

```bash
cd ia-leilao-imovel

# Modo desenvolvimento
python api.py

# OU modo produção
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 2
```

**API estará disponível em:** `http://localhost:8000`

**Documentação interativa:** `http://localhost:8000/docs`

### 2. Endpoints Disponíveis

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/` | Informações da API |
| `GET` | `/health` | Healthcheck |
| `POST` | `/analyze` | Inicia análise |
| `GET` | `/status/{task_id}` | Status da análise |
| `GET` | `/result/{task_id}` | Resultado da análise |
| `GET` | `/ranking` | Lista imóveis analisados |
| `DELETE` | `/task/{task_id}` | Remove tarefa |

### 3. Exemplo de Uso

#### Iniciar Análise

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "estado": "GO",
    "cidade": "RIO VERDE",
    "min_nota": 7.0,
    "max_imoveis": 10
  }'
```

**Resposta:**
```json
{
  "task_id": "a1b2c3d4-...",
  "status": "pending",
  "message": "Análise iniciada",
  "status_url": "/status/a1b2c3d4-...",
  "result_url": "/result/a1b2c3d4-..."
}
```

#### Verificar Status

```bash
curl "http://localhost:8000/status/a1b2c3d4-..."
```

**Resposta:**
```json
{
  "task_id": "a1b2c3d4-...",
  "status": "running",  // ou: pending, completed, failed
  "created_at": "2025-11-09T10:00:00",
  "updated_at": "2025-11-09T10:05:00"
}
```

#### Obter Resultado

```bash
curl "http://localhost:8000/result/a1b2c3d4-..."
```

**Resposta:** JSON completo com análises

---

## 🔧 Workflows n8n Exemplo

### Workflow 1: Automação Simples (Script Standalone)

```
┌─────────────────┐
│  Cron (Trigger) │  ← Toda segunda 8h
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Execute Command │  ← python automation.py ...
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  JSON Parse     │  ← Extrai resultado
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   IF (Filtro)   │  ← Verifica se há imóveis
└─────────────────┘
         │
         ├─── SIM ──────┐
         │              ▼
         │      ┌─────────────────┐
         │      │  Format HTML    │  ← Cria email
         │      └─────────────────┘
         │              │
         │              ▼
         │      ┌─────────────────┐
         │      │  Send Email     │
         │      └─────────────────┘
         │
         └─── NÃO ──────┐
                        ▼
                ┌─────────────────┐
                │  Log (Skip)     │
                └─────────────────┘
```

### Workflow 2: API Assíncrona (Polling)

```
┌─────────────────┐
│  Cron (Trigger) │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  HTTP Request   │  ← POST /analyze
│  (POST)         │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Set Variable   │  ← Salva task_id
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Loop (Polling) │  ← A cada 5 min
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  HTTP Request   │  ← GET /status/{task_id}
│  (GET Status)   │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  IF (Completed?)│
└─────────────────┘
         │
         ├─── SIM ──────┐
         │              ▼
         │      ┌─────────────────┐
         │      │  HTTP Request   │  ← GET /result/{task_id}
         │      │  (GET Result)   │
         │      └─────────────────┘
         │              │
         │              ▼
         │      ┌─────────────────┐
         │      │  Format + Send  │
         │      └─────────────────┘
         │
         └─── NÃO ──────┐
                        ▼
                ┌─────────────────┐
                │  Wait 5min      │  ← Volta ao loop
                └─────────────────┘
```

---

## 📧 Configuração de Email

### Node: Send Email (n8n)

```json
{
  "authentication": "smtp",
  "smtp": {
    "host": "smtp.gmail.com",
    "port": 587,
    "secure": false,
    "user": "{{$env.SMTP_USER}}",
    "password": "{{$env.SMTP_PASSWORD}}"
  },
  "fromEmail": "{{$env.SMTP_USER}}",
  "toEmail": "{{$env.EMAIL_TO}}",
  "subject": "🏠 Novos Imóveis de Leilão - {{$json.cidade}}/{{$json.estado}}",
  "emailFormat": "html",
  "html": "{{$json.emailHtml}}"
}
```

### Template HTML de Email

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; }
    .header { background: #667eea; color: white; padding: 20px; text-align: center; }
    .imovel { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px; }
    .nota { font-size: 24px; font-weight: bold; }
    .nota-alta { color: #28a745; }
    .nota-media { color: #ffc107; }
    .nota-baixa { color: #dc3545; }
  </style>
</head>
<body>
  <div class="header">
    <h1>🏠 Análise de Imóveis de Leilão</h1>
    <p>{{$json.cidade}}/{{$json.estado}} - {{$json.timestamp}}</p>
  </div>
  
  <div style="padding: 20px;">
    <h2>📊 Resumo</h2>
    <ul>
      <li><strong>Imóveis Analisados:</strong> {{$json.imoveis_analisados}}</li>
      <li><strong>Imóveis Aprovados (≥7):</strong> {{$json.imoveis_aprovados}}</li>
      <li><strong>Melhor Nota:</strong> {{$json.resumo_executivo.melhor_nota}}</li>
    </ul>
    
    <h2>🏆 Top 5 Imóveis</h2>
    
    {{#each $json.top_imoveis}}
      {{#if (lte @index 4)}}
        <div class="imovel">
          <div class="nota nota-alta">{{this.nota_final}}</div>
          <h3>{{this.condominio}} - Apt {{this.apartamento}}</h3>
          <p><strong>Comarca:</strong> {{this.comarca}}</p>
          <p><strong>Quartos:</strong> {{this.quartos}} | <strong>Área:</strong> {{this.area_privativa_m2}} m²</p>
          <p><strong>Valor Mínimo:</strong> {{this.valor_minimo}}</p>
          <p><strong>Desconto:</strong> {{this.desconto_percent}}</p>
          
          <h4>⚠️ Riscos</h4>
          <ul>
            {{#each this.riscos}}
              <li>{{this}}</li>
            {{/each}}
          </ul>
          
          <h4>✅ Próximos Passos</h4>
          <ol>
            {{#each this.proximos_passos}}
              <li>{{this}}</li>
            {{/each}}
          </ol>
          
          <p><small><strong>ID:</strong> {{this.id}}</small></p>
        </div>
      {{/if}}
    {{/each}}
  </div>
  
  <div style="padding: 20px; background: #f0f2f6; text-align: center;">
    <p><small>Análise gerada automaticamente por IA | {{$now.format('DD/MM/YYYY HH:mm')}}</small></p>
  </div>
</body>
</html>
```

---

## ⏰ Agendamento Semanal

### Cron Node (n8n)

**Toda segunda-feira às 8h:**
```
0 8 * * 1
```

**Toda terça e quinta às 9h:**
```
0 9 * * 2,4
```

**Toda sexta às 18h:**
```
0 18 * * 5
```

**Configuração Completa:**

```json
{
  "mode": "everyWeek",
  "hour": 8,
  "minute": 0,
  "weekday": 1,
  "timezone": "America/Sao_Paulo"
}
```

---

## 🔍 Workflows JSON Completos

### 1. Workflow Simples (Execute Command)

Salve como: `workflow_simple.json`

```json
{
  "name": "IA Leilão - Automação Simples",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "0 8 * * 1"
            }
          ]
        }
      },
      "name": "Trigger Semanal",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "command": "python automation.py --estado GO --cidade 'RIO VERDE' --min-nota 7",
        "workdir": "/caminho/completo/para/ia-leilao-imovel"
      },
      "name": "Executar Análise",
      "type": "n8n-nodes-base.executeCommand",
      "typeVersion": 1,
      "position": [450, 300]
    },
    {
      "parameters": {
        "jsCode": "// Extrai JSON da saída\nconst output = $input.item.json.stdout;\nconst jsonStart = output.indexOf('--- JSON OUTPUT START ---');\nconst jsonEnd = output.indexOf('--- JSON OUTPUT END ---');\n\nif (jsonStart !== -1 && jsonEnd !== -1) {\n  const jsonStr = output.substring(jsonStart + 25, jsonEnd).trim();\n  return JSON.parse(jsonStr);\n}\n\nthrow new Error('JSON não encontrado na saída');"
      },
      "name": "Parse JSON",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [650, 300]
    },
    {
      "parameters": {
        "conditions": {
          "number": [
            {
              "value1": "={{$json.imoveis_aprovados}}",
              "operation": "larger",
              "value2": 0
            }
          ]
        }
      },
      "name": "Tem Imóveis?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [850, 300]
    },
    {
      "parameters": {
        "authentication": "smtp",
        "fromEmail": "={{$env.SMTP_USER}}",
        "toEmail": "={{$env.EMAIL_TO}}",
        "subject": "🏠 {{$json.imoveis_aprovados}} Novos Imóveis em {{$json.cidade}}/{{$json.estado}}",
        "emailFormat": "html",
        "html": "=<h1>Top Imóveis</h1><pre>{{JSON.stringify($json.top_imoveis, null, 2)}}</pre>"
      },
      "name": "Enviar Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 2.1,
      "position": [1050, 200]
    }
  ],
  "connections": {
    "Trigger Semanal": {
      "main": [[{"node": "Executar Análise", "type": "main", "index": 0}]]
    },
    "Executar Análise": {
      "main": [[{"node": "Parse JSON", "type": "main", "index": 0}]]
    },
    "Parse JSON": {
      "main": [[{"node": "Tem Imóveis?", "type": "main", "index": 0}]]
    },
    "Tem Imóveis?": {
      "main": [[{"node": "Enviar Email", "type": "main", "index": 0}]]
    }
  }
}
```

### 2. Workflow API (HTTP Request)

Salve como: `workflow_api.json`

```json
{
  "name": "IA Leilão - API Assíncrona",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "0 8 * * 1"
            }
          ]
        }
      },
      "name": "Trigger Semanal",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://localhost:8000/analyze",
        "jsonParameters": true,
        "options": {},
        "bodyParametersJson": "={\n  \"estado\": \"GO\",\n  \"cidade\": \"RIO VERDE\",\n  \"min_nota\": 7.0\n}"
      },
      "name": "POST /analyze",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [450, 300]
    },
    {
      "parameters": {
        "amount": 5,
        "unit": "minutes"
      },
      "name": "Aguardar 5min",
      "type": "n8n-nodes-base.wait",
      "typeVersion": 1,
      "position": [650, 300],
      "webhookId": "polling-wait"
    },
    {
      "parameters": {
        "url": "=http://localhost:8000/status/{{$json.task_id}}",
        "options": {}
      },
      "name": "GET /status",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [850, 300]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{$json.status}}",
              "operation": "equals",
              "value2": "completed"
            }
          ]
        }
      },
      "name": "Concluído?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [1050, 300]
    },
    {
      "parameters": {
        "url": "=http://localhost:8000/result/{{$json.task_id}}",
        "options": {}
      },
      "name": "GET /result",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [1250, 200]
    },
    {
      "parameters": {
        "authentication": "smtp",
        "fromEmail": "={{$env.SMTP_USER}}",
        "toEmail": "={{$env.EMAIL_TO}}",
        "subject": "🏠 Análise Concluída",
        "emailFormat": "html"
      },
      "name": "Enviar Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 2.1,
      "position": [1450, 200]
    }
  ],
  "connections": {
    "Trigger Semanal": {
      "main": [[{"node": "POST /analyze", "type": "main", "index": 0}]]
    },
    "POST /analyze": {
      "main": [[{"node": "Aguardar 5min", "type": "main", "index": 0}]]
    },
    "Aguardar 5min": {
      "main": [[{"node": "GET /status", "type": "main", "index": 0}]]
    },
    "GET /status": {
      "main": [[{"node": "Concluído?", "type": "main", "index": 0}]]
    },
    "Concluído?": {
      "main": [
        [{"node": "GET /result", "type": "main", "index": 0}],
        [{"node": "Aguardar 5min", "type": "main", "index": 0}]
      ]
    },
    "GET /result": {
      "main": [[{"node": "Enviar Email", "type": "main", "index": 0}]]
    }
  }
}
```

---

## 🐛 Troubleshooting

### Problema: "comando python não encontrado"

**Solução:**
```bash
# No n8n, use caminho completo do Python
which python  # Linux/Mac
where python  # Windows

# Use no Execute Command:
/usr/bin/python3 automation.py ...
```

### Problema: "Timeout na análise"

**Solução:**
- Aumente timeout no n8n (Settings > Execution Timeout)
- Use `--max-imoveis` para limitar análises iniciais
- Prefira API (método assíncrono)

### Problema: "OPENAI_API_KEY não encontrada"

**Solução:**
```bash
# Certifique-se de que .env está no diretório correto
cd ia-leilao-imovel
cat .env  # Deve mostrar OPENAI_API_KEY=...

# OU passe como variável de ambiente no n8n
export OPENAI_API_KEY=sk-...
```

### Problema: "Email não enviado"

**Solução (Gmail):**
1. Ative "Verificação em 2 etapas"
2. Gere "Senha de App" em https://myaccount.google.com/apppasswords
3. Use a senha gerada (não sua senha normal)

### Problema: "JSON parse error"

**Solução:**
```bash
# Teste manualmente primeiro
python automation.py --estado GO --cidade GOIANIA --max-imoveis 1

# Verifique se JSON aparece entre markers
--- JSON OUTPUT START ---
{ ... }
--- JSON OUTPUT END ---
```

---

## 📊 Monitoramento

### Logs do n8n

```bash
# Ver logs em tempo real
n8n --log-level debug

# OU via Docker
docker logs -f n8n
```

### Logs da API

```bash
# Com uvicorn
uvicorn api:app --log-level info

# Logs aparecem no stdout
```

### Arquivos Gerados

```
ia-leilao-imovel/
├── automation_result.json          ← Resultado padrão
├── automation_result_{task_id}.json ← Resultados da API
├── data/
│   ├── analysis/
│   │   └── {imovel_id}_analysis.json
│   ├── list/
│   └── detail/
```

---

## 🎯 Resumo de Comandos

```bash
# Instalar n8n
npm install -g n8n

# Instalar dependências Python
pip install -r requirements.txt

# Testar automation.py
python automation.py --estado GO --cidade GOIANIA --max-imoveis 1

# Iniciar API
python api.py

# Iniciar n8n
n8n

# Importar workflow
# Na UI do n8n: Menu > Import from File > workflow_simple.json
```

---

## 📚 Recursos Adicionais

- **n8n Documentation**: https://docs.n8n.io
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **OpenAI API**: https://platform.openai.com/docs

---

## ✅ Checklist de Implementação

- [ ] Instalar n8n
- [ ] Instalar dependências Python (`pip install -r requirements.txt`)
- [ ] Configurar `.env` com chaves API e SMTP
- [ ] Testar `automation.py` manualmente
- [ ] (Opcional) Testar `api.py` com Postman/curl
- [ ] Importar workflow no n8n
- [ ] Configurar credenciais SMTP no n8n
- [ ] Testar workflow manualmente (botão "Execute Workflow")
- [ ] Ativar workflow e configurar trigger semanal
- [ ] Verificar primeiro email recebido
- [ ] Documentar e compartilhar com equipe

---

**Última atualização**: 09/11/2025  
**Desenvolvido por**: Yuri Marcal (32) - ymarcal  
**Projeto**: IA Leilão Imóveis - TE-251 ITA

