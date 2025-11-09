"""
Script de Configuração Automática da OpenAI
============================================

Este script configura automaticamente todo o ambiente necessário
para executar as análises de imóveis com IA:

1. Verifica chave da API OpenAI
2. Faz upload do edital.pdf
3. Cria novo assistente
4. Testa a configuração
5. Valida todo o pipeline

Uso:
    python setup_openai.py
"""

import os
import sys
import io
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class SetupOpenAI:
    """Configuração automática da OpenAI"""
    
    def __init__(self):
        self.config_path = Path("config.json")
        self.edital_path = Path("edital.pdf")
        self.env_path = Path(".env")
        self.client = None
        self.config = {}
        
    def log(self, message: str, status: str = "INFO"):
        """Log formatado com emojis"""
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "STEP": "🔹"
        }
        icon = icons.get(status, "•")
        print(f"{icon} {message}")
    
    def step_header(self, step: int, title: str):
        """Cabeçalho de passo"""
        print(f"\n{'='*60}")
        print(f"PASSO {step}: {title}")
        print(f"{'='*60}")
    
    def load_config(self):
        """Carrega ou cria config.json"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            self.log("Config.json carregado", "SUCCESS")
        else:
            self.config = {
                "estado": "GO",
                "cidade": "GOIANIA"
            }
            self.log("Novo config.json criado", "SUCCESS")
    
    def save_config(self):
        """Salva config.json"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
        self.log("Config.json salvo", "SUCCESS")
    
    def check_api_key(self) -> bool:
        """Verifica se a chave da API existe e é válida"""
        self.step_header(1, "Verificar Chave da API OpenAI")
        
        if not self.env_path.exists():
            self.log("Arquivo .env não encontrado!", "ERROR")
            self.log("Crie um arquivo .env com: OPENAI_API_KEY=sk-proj-...", "WARNING")
            return False
        
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            self.log("OPENAI_API_KEY não encontrada no .env", "ERROR")
            return False
        
        if not api_key.startswith("sk-"):
            self.log("Formato da API key inválido (deve começar com 'sk-')", "ERROR")
            return False
        
        # Testa a chave
        try:
            self.client = OpenAI(api_key=api_key)
            # Tenta listar modelos para validar a chave
            models = self.client.models.list()
            self.log(f"Chave da API válida! ({api_key[:15]}...)", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Erro ao validar API key: {e}", "ERROR")
            return False
    
    def upload_edital(self) -> bool:
        """Faz upload do edital.pdf"""
        self.step_header(2, "Upload do Edital PDF")
        
        if not self.edital_path.exists():
            self.log(f"Arquivo {self.edital_path} não encontrado!", "ERROR")
            self.log("Certifique-se de que o arquivo edital.pdf está na pasta atual", "WARNING")
            return False
        
        try:
            self.log("Fazendo upload do edital.pdf...", "STEP")
            file = self.client.files.create(
                file=open(self.edital_path, "rb"),
                purpose="assistants"
            )
            
            self.config["edital_file_id"] = file.id
            self.save_config()
            
            self.log(f"Upload concluído! File ID: {file.id}", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Erro no upload: {e}", "ERROR")
            return False
    
    def create_assistant(self) -> bool:
        """Cria novo assistente"""
        self.step_header(3, "Criar Assistente de Análise")
        
        try:
            self.log("Criando assistente com GPT-4o...", "STEP")
            
            assistant = self.client.beta.assistants.create(
                name="Leilão Bot",
                instructions="""
Tarefa:
Analise um edital em PDF, o texto da matrícula do imóvel (em PDF convertido) e um HTML com a descrição do imóvel para classificar a atratividade do imóvel para revenda em até 6 meses (flip).
Você deve extrair todos os dados relevantes, citar a fonte de cada informação e atribuir notas (0–10) a cinco critérios principais, calculando a nota final ponderada.

Entradas fornecidas:
- Edital (PDF): anexado
- Matrícula: texto integral ou PDF convertido
- Descrição (HTML): HTML extraído do site do leilão

Instruções de análise:
Extraia e liste todas as informações abaixo, sempre com "Fonte: …"
Use "Edital pág. X", "Matrícula AV-nº/Registro/Descrição", ou "Anúncio/HTML".
Se a informação não constar, marque "Não informado" (sem inferir).

Deve incluir, se existir no material:
- Nome do condomínio
- Habite-se (ou averbação equivalente)
- Apartamento e bloco
- Área privativa e total
- Quartos
- Matrícula e escritura registrada
- Pendências judiciais ou averbações de ações
- Processo judicial (número, vara ou tipo, se constar)
- Vaga(s) de garagem (nº ou fração ideal)
- Itens de lazer do condomínio (se descritos)
- Dados e endereço dos adquirentes anteriores
- Forma de título (compra e venda, alienação fiduciária, adjudicação etc.)
- Laudêmio (existência e tipo, se aplicável)
- Notícia de abertura de execução extrajudicial
- Decurso de prazo com purga de mora
- Documentos que instruíram o registro da execução
- Resultado / Código hash do CNIB
- DOI (Declaração sobre Operações Imobiliárias)
- Registro na matrícula (número, data, ato e natureza)
- Sequencial de registros e averbações
- Inscrição imobiliária
- Quitação da dívida / cancelamento da cédula
- Averbação de leilão negativo
- Outras observações de ônus ou restrições de disponibilidade

Critérios e notas (0–10):
Avalie exatamente 5 critérios com base nas informações coletadas.
Para cada um, dê nota (0–10), justifique em 2–4 linhas, e cite as fontes.

Critério | Peso | Descrição
1. Liquidez & Preço de Entrada | 0.30 | Considere deságio vs. avaliação, tipologia (quartos, área, vaga) e bairro.
2. Situação Registral & Risco Jurídico | 0.25 | Analise cadeia dominial, consolidação, cancelamento de ônus, pendências judiciais e regularidade registral.
3. Despesas Propter Rem | 0.20 | Regras de IPTU e condomínio (limites, repasses e riscos de passivo).
4. Prazos de Contratação & Registro | 0.15 | Compatibilidade entre prazos de pagamento, contratação e registro com o horizonte de 6 meses.
5. Velocidade de Liquidez | 0.10 | Potencial de revenda rápida em 6 meses considerando localização e perfil do imóvel.

Cálculo da nota final:
Use média ponderada: Nota_Final = (C1×0.30) + (C2×0.25) + (C3×0.20) + (C4×0.15) + (C5×0.10)
Apresente a fórmula e o resultado final com 1 casa decimal.

Sinalizadores de risco:
Liste 2 riscos práticos baseados nos documentos (ex.: passivo condominial acima do limite, atraso cartorial, pendência judicial, ausência de quitação).

Próximos passos objetivos:
Liste 2 ações diretas para mitigar riscos e acelerar a revenda (ex.: solicitar certidões, confirmar quitação, contato com síndico, preparar orçamento de reforma rápida).

Saída obrigatória:
A resposta final deve ser apenas o JSON abaixo (sem texto explicativo), seguindo exatamente esta estrutura:

{
  "imovel": {
    "empreendimento": "",
    "condominio": "",
    "habite_se": "",
    "apartamento": "",
    "bloco": "",
    "area_privativa_m2": "",
    "area_total_m2": "",
    "quartos": "",
    "vaga_garagem": "",
    "itens_lazer": "",
    "matricula": "",
    "oficio": "",
    "comarca": "",
    "inscricao_imobiliaria": "",
    "forma_titulo": "",
    "laudemio": "",
    "noticia_execucao_extrajudicial": "",
    "decurso_prazo_purga_mora": "",
    "documentos_instrucao": "",
    "codigo_cnib": "",
    "doi": "",
    "registro": "",
    "sequencial": "",
    "pendencias_judiciais": "",
    "processo_judicial": "",
    "restricoes_disponibilidade": "",
    "quitacao_divida": "",
    "averbacao_leilao_negativo": "",
    "avaliacao": "",
    "valor_minimo": "",
    "desconto_percent": "",
    "fonte_principal": ""
  },
  "criterios": [
    {"nome": "Liquidez & Preço de Entrada", "peso": 0.30, "nota": 0, "justificativa": "", "fontes": []},
    {"nome": "Situação Registral & Risco Jurídico", "peso": 0.25, "nota": 0, "justificativa": "", "fontes": []},
    {"nome": "Despesas Propter Rem", "peso": 0.20, "nota": 0, "justificativa": "", "fontes": []},
    {"nome": "Prazos de Contratação & Registro", "peso": 0.15, "nota": 0, "justificativa": "", "fontes": []},
    {"nome": "Velocidade de Liquidez", "peso": 0.10, "nota": 0, "justificativa": "", "fontes": []}
  ],
  "nota_final": {"metodo": "media_ponderada", "valor": 0.0},
  "riscos": [
    {"descricao": "", "fonte": ""},
    {"descricao": "", "fonte": ""}
  ],
  "proximos_passos": [
    "",
    ""
  ]
}

Regras finais:
- Português claro e técnico.
- Sem inferências: se não constar nos documentos, use "Não informado".
- Sem links externos.
- Cite "Fonte: …" em cada dado extraído.
- Resposta final deve ser SOMENTE o JSON.
""",
                model="gpt-4o",
                tools=[{"type": "file_search"}]
            )
            
            self.config["assistant_id"] = assistant.id
            self.save_config()
            
            self.log(f"Assistente criado! ID: {assistant.id}", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Erro ao criar assistente: {e}", "ERROR")
            return False
    
    def test_configuration(self) -> bool:
        """Testa a configuração completa"""
        self.step_header(4, "Testar Configuração")
        
        # Verifica se todos os IDs estão presentes
        required_keys = ["edital_file_id", "assistant_id"]
        missing = [k for k in required_keys if k not in self.config]
        
        if missing:
            self.log(f"Configuração incompleta. Faltam: {', '.join(missing)}", "ERROR")
            return False
        
        self.log("Verificando File ID...", "STEP")
        try:
            file_info = self.client.files.retrieve(self.config["edital_file_id"])
            self.log(f"  ✓ File ID válido: {file_info.filename} ({file_info.bytes} bytes)", "SUCCESS")
        except Exception as e:
            self.log(f"  ✗ File ID inválido: {e}", "ERROR")
            return False
        
        self.log("Verificando Assistant ID...", "STEP")
        try:
            assistant_info = self.client.beta.assistants.retrieve(self.config["assistant_id"])
            self.log(f"  ✓ Assistant ID válido: {assistant_info.name} (modelo: {assistant_info.model})", "SUCCESS")
        except Exception as e:
            self.log(f"  ✗ Assistant ID inválido: {e}", "ERROR")
            return False
        
        return True
    
    def show_summary(self):
        """Mostra resumo final"""
        print(f"\n{'='*60}")
        print("🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"{'='*60}")
        print(f"\n📋 Resumo da Configuração:")
        print(f"  • API Key: {os.getenv('OPENAI_API_KEY', '')[:15]}...")
        print(f"  • File ID: {self.config.get('edital_file_id', 'N/A')}")
        print(f"  • Assistant ID: {self.config.get('assistant_id', 'N/A')}")
        print(f"\n🚀 Próximos Passos:")
        print(f"  1. Testar análise individual:")
        print(f"     python query.py")
        print(f"\n  2. Executar automação completa:")
        print(f"     python automation.py --estado GO --cidade GOIANIA --max-imoveis 1")
        print(f"\n  3. Análise completa com filtro de nota:")
        print(f"     python automation.py --estado GO --cidade GOIANIA --min-nota 7")
        print(f"\n{'='*60}\n")
    
    def run(self):
        """Executa todo o processo de configuração"""
        print("\n" + "="*60)
        print("🤖 CONFIGURAÇÃO AUTOMÁTICA - OpenAI Assistant")
        print("="*60)
        
        # Carrega config existente
        self.load_config()
        
        # Passo 1: Verifica API key
        if not self.check_api_key():
            self.log("Configuração abortada: API key inválida", "ERROR")
            return False
        
        # Passo 2: Upload do edital
        if not self.upload_edital():
            self.log("Configuração abortada: falha no upload", "ERROR")
            return False
        
        # Passo 3: Cria assistente
        if not self.create_assistant():
            self.log("Configuração abortada: falha ao criar assistente", "ERROR")
            return False
        
        # Passo 4: Testa configuração
        if not self.test_configuration():
            self.log("Configuração abortada: teste falhou", "ERROR")
            return False
        
        # Mostra resumo
        self.show_summary()
        return True


def main():
    """Função principal"""
    setup = SetupOpenAI()
    
    try:
        success = setup.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Configuração interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

