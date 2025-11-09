# 📧 Configuração de Email para n8n

## 🎯 Visão Geral

Para receber os relatórios automáticos do n8n, você precisa configurar credenciais SMTP (Simple Mail Transfer Protocol). Este guia mostra como configurar para os provedores mais comuns.

---

## ⭐ Gmail (Recomendado)

### Por que Gmail?
- ✅ Gratuito
- ✅ Confiável
- ✅ Fácil de configurar
- ✅ Alta taxa de entrega

### Passo a Passo Completo

#### 1. Ativar Verificação em 2 Etapas

1. **Acesse**: https://myaccount.google.com/security
2. **Encontre**: "Verificação em duas etapas"
3. **Clique**: "Ativar"
4. **Siga**: os passos (vai usar seu celular)

**Importante**: A verificação em 2 etapas é **obrigatória** para gerar senhas de app.

#### 2. Gerar Senha de App

⚠️ **ATENÇÃO**: Você NÃO usará sua senha normal do Gmail!

1. **Acesse**: https://myaccount.google.com/apppasswords
   
   *Caminho alternativo: Conta Google > Segurança > Verificação em duas etapas > Senhas de app*

2. **Faça login** se solicitado

3. **Digite um nome** para o app: `n8n-ia-leilao-imovel`

4. **Clique**: "Criar"

5. **Copie a senha** de 16 dígitos:
   
   ```
   Exemplo: abcd efgh ijkl mnop
   ```
   
   ⚠️ **IMPORTANTE**: 
   - Copie AGORA, você só verá uma vez
   - Guarde em local seguro
   - Use ESTA senha no n8n, não sua senha normal

#### 3. Credenciais para n8n

Use estas configurações no n8n:

```
📋 CREDENCIAIS SMTP GMAIL

Host: smtp.gmail.com
Porta: 587
Segurança: STARTTLS (não SSL)
Usuário: seu-email@gmail.com
Senha: [senha de app de 16 dígitos]

Email remetente: seu-email@gmail.com
Email destinatário: seu-email@gmail.com (ou outro)
```

---

## 📨 Outlook/Hotmail

### Configuração

```
Host: smtp-mail.outlook.com
Porta: 587
Segurança: STARTTLS
Usuário: seu-email@outlook.com OU seu-email@hotmail.com
Senha: sua senha normal do Outlook
```

### Observações

- ✅ Não precisa de senha de app
- ✅ Usa senha normal da conta
- ⚠️ Pode ter limite de emails por dia (300/dia)

---

## 🏢 Office 365 (Email Corporativo)

### Configuração

```
Host: smtp.office365.com
Porta: 587
Segurança: STARTTLS
Usuário: seu-email@sua-empresa.com
Senha: sua senha corporativa
```

### Observações

- ⚠️ Pode precisar de permissão do administrador
- ⚠️ Algumas empresas bloqueiam SMTP externo

---

## 🌐 Yahoo Mail

### Configuração

```
Host: smtp.mail.yahoo.com
Porta: 587
Segurança: STARTTLS
Usuário: seu-email@yahoo.com
Senha: [senha de app]
```

### Gerar Senha de App (Yahoo)

1. Acesse: https://login.yahoo.com/account/security
2. Clique em "Gerar senha de app"
3. Selecione "Outro app"
4. Digite: "n8n"
5. Copie a senha gerada

---

## 🔧 Configuração no n8n

### No Navegador (depois de iniciar n8n)

1. **Abra o workflow** importado

2. **Clique** no node **"Enviar Email"**

3. **Credential**: Clique em "Select Credential"

4. **Clique**: "Create New Credential"

5. **Preencha**:

   | Campo | Valor |
   |-------|-------|
   | **Credential Name** | `Gmail - IA Leilão` |
   | **Host** | `smtp.gmail.com` |
   | **Port** | `587` |
   | **Secure** | `false` (desmarque) |
   | **User** | seu-email@gmail.com |
   | **Password** | senha de app (16 dígitos) |

6. **Teste**: Clique em "Test" (se disponível)

7. **Salve**: Clique em "Save"

---

## 🧪 Testar Configuração SMTP (Antes do n8n)

### Teste Rápido com Python

Crie um arquivo `test_email.py`:

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# CONFIGURAÇÃO - ALTERE AQUI
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "seu-email@gmail.com"
SMTP_PASSWORD = "abcd efgh ijkl mnop"  # Senha de app
EMAIL_TO = "seu-email@gmail.com"

print("🔍 Testando configuração SMTP...")

try:
    # Criar mensagem
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = EMAIL_TO
    msg['Subject'] = '✅ Teste n8n - IA Leilão Imóveis'
    
    body = """
    <html>
        <body>
            <h1>🎉 Sucesso!</h1>
            <p>Se você recebeu este email, sua configuração SMTP está correta!</p>
            <p>Você pode prosseguir com a configuração do n8n.</p>
            <hr>
            <small>Teste enviado de test_email.py</small>
        </body>
    </html>
    """
    
    msg.attach(MIMEText(body, 'html'))
    
    # Conectar e enviar
    print(f"📡 Conectando ao {SMTP_HOST}:{SMTP_PORT}...")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        print("🔐 Iniciando STARTTLS...")
        server.starttls()
        
        print("🔑 Fazendo login...")
        server.login(SMTP_USER, SMTP_PASSWORD)
        
        print("📧 Enviando email...")
        server.send_message(msg)
    
    print("✅ EMAIL ENVIADO COM SUCESSO!")
    print(f"📬 Verifique {EMAIL_TO}")
    
except smtplib.SMTPAuthenticationError:
    print("❌ ERRO: Autenticação falhou")
    print("   Verifique:")
    print("   1. Usuário está correto")
    print("   2. Senha de app está correta")
    print("   3. Verificação em 2 etapas está ativa")
    
except smtplib.SMTPException as e:
    print(f"❌ ERRO SMTP: {e}")
    
except Exception as e:
    print(f"❌ ERRO: {e}")
```

**Execute:**

```bash
python test_email.py
```

**Se funcionar**, você verá:

```
🔍 Testando configuração SMTP...
📡 Conectando ao smtp.gmail.com:587...
🔐 Iniciando STARTTLS...
🔑 Fazendo login...
📧 Enviando email...
✅ EMAIL ENVIADO COM SUCESSO!
📬 Verifique seu-email@gmail.com
```

---

## 🐛 Troubleshooting Comum

### ❌ "Username and Password not accepted"

**Problema**: Usando senha normal ao invés de senha de app

**Solução**:
1. Gere uma senha de app em https://myaccount.google.com/apppasswords
2. Use ESTA senha, não sua senha normal

---

### ❌ "535 5.7.8 Username and Password not accepted"

**Problema**: Verificação em 2 etapas não está ativa

**Solução**:
1. Ative em https://myaccount.google.com/security
2. Depois gere a senha de app

---

### ❌ "Connection timeout"

**Problema**: Porta ou host incorretos

**Solução Gmail**:
- Host: `smtp.gmail.com` (sem https://)
- Porta: `587` (não 465 ou 25)

---

### ❌ "STARTTLS extension not supported by server"

**Problema**: Tentando usar SSL ao invés de STARTTLS

**Solução no n8n**:
- Marque **"Secure"** como `false`
- Use porta `587`

---

### ❌ Email não chega (sem erro)

**Verifique**:
1. **Caixa de spam** do destinatário
2. **Caixa de lixo** do destinatário
3. **"Todos os emails"** no Gmail
4. **Filtros** configurados que podem estar movendo o email

---

## 📊 Comparação de Provedores

| Provedor | Facilidade | Gratuito | Limite Diário | Requer Senha App |
|----------|-----------|----------|---------------|------------------|
| **Gmail** | ⭐⭐⭐⭐⭐ | ✅ | ~500 | ✅ Sim |
| **Outlook** | ⭐⭐⭐⭐ | ✅ | ~300 | ❌ Não |
| **Yahoo** | ⭐⭐⭐ | ✅ | ~100 | ✅ Sim |
| **Office 365** | ⭐⭐ | Depende | Varia | Depende |

---

## 📝 Template de Configuração

Copie e preencha suas informações:

```
╔════════════════════════════════════════════════════════╗
║           MINHAS CREDENCIAIS SMTP - n8n                ║
╚════════════════════════════════════════════════════════╝

Provedor: Gmail

Host: smtp.gmail.com
Porta: 587
Segurança: STARTTLS (SSL: desativado)

Email Remetente: _______________________________@gmail.com
Senha de App: ____ ____ ____ ____ (16 dígitos)

Email Destinatário: _______________________________@gmail.com

╔════════════════════════════════════════════════════════╗
║                  COMO USAR NO n8n                      ║
╚════════════════════════════════════════════════════════╝

1. Abrir workflow no navegador
2. Clicar no node "Enviar Email"
3. Credential > Create New
4. Preencher com as informações acima
5. Salvar
```

---

## ✅ Checklist de Configuração

Antes de usar no n8n, confirme:

- [ ] Verificação em 2 etapas ativada (Gmail/Yahoo)
- [ ] Senha de app gerada e copiada
- [ ] Host e porta corretos anotados
- [ ] Email destinatário definido
- [ ] Teste manual funcionou (test_email.py)
- [ ] Credencial criada no n8n
- [ ] Email de teste recebido

---

## 🔐 Segurança

### ⚠️ NUNCA Faça

- ❌ Compartilhe sua senha de app
- ❌ Commite senha de app no Git
- ❌ Use senha normal em scripts
- ❌ Exponha credenciais em código

### ✅ SEMPRE Faça

- ✅ Use senhas de app dedicadas
- ✅ Revogue senhas antigas não usadas
- ✅ Um app = uma senha de app
- ✅ Guarde senhas em gerenciador seguro

---

## 🎓 Entendendo SMTP

### O que é SMTP?

**SMTP** (Simple Mail Transfer Protocol) é o protocolo padrão para **envio** de emails.

### Porta 587 vs 465 vs 25

| Porta | Nome | Uso | Segurança |
|-------|------|-----|-----------|
| **587** | Submission | ⭐ Recomendado | STARTTLS |
| 465 | SMTPS | Legado | SSL/TLS |
| 25 | SMTP | Servidores | Nenhuma |

**Use sempre porta 587 com STARTTLS.**

### STARTTLS vs SSL/TLS

- **STARTTLS**: Começa sem criptografia, depois ativa (porta 587)
- **SSL/TLS**: Criptografado desde o início (porta 465)

**Gmail e maioria dos provedores**: Use STARTTLS (porta 587)

---

## 📚 Recursos Adicionais

- **Gmail App Passwords**: https://myaccount.google.com/apppasswords
- **Gmail SMTP Settings**: https://support.google.com/mail/answer/7126229
- **Outlook SMTP**: https://support.microsoft.com/en-us/office/pop-imap-and-smtp-settings
- **n8n Email Node**: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.emailsend/

---

**Última atualização**: 09/11/2025  
**Desenvolvido por**: Yuri Marcal (32) - ymarcal  
**Projeto**: IA Leilão Imóveis - TE-251 ITA


