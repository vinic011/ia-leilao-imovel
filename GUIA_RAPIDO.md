# 🚀 Guia Rápido - Streamlit App

## ⚡ Início Rápido

### 1. Ativar ambiente

```bash
conda activate scrape-env
```

### 2. Executar aplicativo

```bash
cd ia-leilao-imovel
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`

## 📱 Navegação do App

### 🏠 Página Inicial
- Visão geral do projeto
- Estatísticas gerais
- Descrição dos critérios de avaliação

### 🔍 Buscar Imóveis
1. Configure **Estado** e **Cidade** na barra lateral
2. Clique em **"Executar Busca de Lista"**
   - ⏱️ Aguarde 1-2 minutos
   - ✅ Lista será salva em `data/list/`
3. Clique em **"Baixar Todos os Detalhes"**
   - ⏱️ Pode demorar 10-30 minutos dependendo da quantidade
   - ✅ Detalhes salvos em `data/detail/`

### 🤖 Analisar Imóvel
1. Selecione um imóvel da lista suspensa
2. Clique em **"Analisar com IA"**
   - ⏱️ Aguarde 1-3 minutos
   - 🤖 IA analisará o edital + matrícula + descrição
3. Veja os resultados:
   - 📊 Nota final (0-10)
   - 📋 Dados do imóvel
   - 🎯 Gráfico radar com 5 critérios
   - ⚠️ Riscos identificados
   - ✅ Próximos passos
4. Baixe o resultado em JSON se desejar

### 📊 Ranking
1. Visualize todos os imóveis analisados
2. Use **filtros** para refinar:
   - Nota mínima
   - Comarca
   - Número de quartos
3. Veja **gráfico de distribuição** de notas
4. Clique em um imóvel para ver detalhes completos
5. Exporte o ranking em CSV

## 🎨 Recursos Visuais

- **Gráfico Radar**: Mostra visualmente os 5 critérios
- **Cards coloridos**: Verde (≥7), Amarelo (5-7), Vermelho (<5)
- **Métricas em destaque**: Nota final grande e colorida
- **Alertas de risco**: Destacados em amarelo
- **Próximos passos**: Destacados em verde

## ⚙️ Configurações (Barra Lateral)

- **Estado**: Sigla (ex: PE, SP, RJ)
- **Cidade**: Nome completo em MAIÚSCULAS (ex: RECIFE)
- Clique em **"Salvar Configurações"** para persistir

## 🐛 Troubleshooting

### Erro: "Configuração Incompleta"
**Solução:**
```bash
python upload_edital.py
python create_assistent.py
```

### Erro: "Nenhum imóvel disponível"
**Solução:**
1. Vá para "Buscar Imóveis"
2. Execute o scraping primeiro

### Erro: Timeout no scraping
**Solução:**
- Verifique sua conexão com internet
- Execute novamente (pode ter havido problema temporário)
- Verifique se o site da Caixa está acessível

### Análise muito lenta
**Normal:**
- Primeira análise pode levar 2-3 minutos
- OCR da matrícula consome tempo
- API da OpenAI pode estar ocupada

### Gráficos não aparecem
**Solução:**
```bash
pip install --upgrade plotly
streamlit cache clear
```

## 💡 Dicas de Uso

### Para apresentação
1. Prepare 2-3 imóveis analisados previamente
2. Use a página de Ranking para comparação visual
3. Mostre o gráfico radar em tela cheia (botão expandir)
4. Destaque os riscos e próximos passos

### Para testes
1. Comece com uma cidade pequena (menos imóveis)
2. Analise 1-2 imóveis primeiro para testar
3. Depois faça análise em lote

### Para desenvolvimento
- Edite `app.py` e salve
- Streamlit recarrega automaticamente
- Use `st.write()` para debug

## 🔄 Atualizar Dependências

Se algo não funcionar após git pull:

```bash
conda env update -f env.yaml --prune
conda activate scrape-env
```

## 📞 Suporte

Problemas? Entre em contato com:
- 32 (Yuri) - ymarcal
- Frog - vinic011
- Delay

---

**Desenvolvido com ❤️ para TE-251 - ITA**

