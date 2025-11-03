# ia-leilao-imovel

# 1. Baixar dependências

```
conda env create -f env.yaml
```
```
brew install poppler
```

# 2. Scrapping de dados do site da caixa


```
python scrape_property_list.py
```

```
python scrape_datail.py
```

# 3. Upload do edital, create assistent and run query

```
Create a .env file and add your OpenAI Key, as shown in .envexample .
```

```
python upload_edital.py
```

```
python create_assistent.py
```

```
python query.py
```