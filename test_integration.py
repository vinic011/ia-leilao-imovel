"""
Script de Teste da Integração n8n
==================================

Testa os componentes principais da integração antes de usar no n8n.

Uso:
    python test_integration.py
"""

import sys
import os
import json
from pathlib import Path
import subprocess

# Cores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    """Imprime cabeçalho colorido"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    """Imprime mensagem de sucesso"""
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    """Imprime mensagem de erro"""
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text):
    """Imprime mensagem de aviso"""
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_info(text):
    """Imprime mensagem informativa"""
    print(f"  {text}")

def test_env_file():
    """Testa se .env existe e tem OPENAI_API_KEY"""
    print_header("1. Testando Arquivo .env")
    
    env_path = Path(".env")
    
    if not env_path.exists():
        print_error(".env não encontrado")
        print_info("Crie um arquivo .env com:")
        print_info("OPENAI_API_KEY=sk-...")
        return False
    
    print_success(".env encontrado")
    
    # Verifica se tem OPENAI_API_KEY
    with open(env_path, 'r') as f:
        content = f.read()
        if "OPENAI_API_KEY" in content:
            print_success("OPENAI_API_KEY presente")
            
            # Verifica se não está vazio
            for line in content.split('\n'):
                if line.startswith('OPENAI_API_KEY='):
                    key_value = line.split('=', 1)[1].strip()
                    if key_value and key_value != 'sk-...':
                        print_success("OPENAI_API_KEY configurada")
                        return True
                    else:
                        print_error("OPENAI_API_KEY está vazia ou é placeholder")
                        return False
        else:
            print_error("OPENAI_API_KEY não encontrada no .env")
            return False
    
    return True

def test_dependencies():
    """Testa se todas as dependências estão instaladas"""
    print_header("2. Testando Dependências Python")
    
    required_packages = [
        ('beautifulsoup4', 'bs4'),
        ('selenium', 'selenium'),
        ('openai', 'openai'),
        ('requests', 'requests'),
        ('pandas', 'pandas'),
        ('python-dotenv', 'dotenv'),
        ('pytesseract', 'pytesseract'),
        ('pdf2image', 'pdf2image'),
        ('streamlit', 'streamlit'),
        ('plotly', 'plotly'),
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('pydantic', 'pydantic')
    ]
    
    missing = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print_success(f"{package_name}")
        except ImportError:
            print_error(f"{package_name} - NÃO INSTALADO")
            missing.append(package_name)
    
    if missing:
        print_warning(f"\n{len(missing)} pacote(s) faltando")
        print_info("Instale com: pip install " + " ".join(missing))
        return False
    
    print_success("\nTodas as dependências instaladas!")
    return True

def test_data_structure():
    """Testa se estrutura de diretórios existe"""
    print_header("3. Testando Estrutura de Diretórios")
    
    required_dirs = [
        'data',
        'data/list',
        'data/detail',
        'data/analysis'
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print_success(f"{dir_path}/")
        else:
            print_warning(f"{dir_path}/ não existe (será criado automaticamente)")
    
    return True

def test_config_json():
    """Testa se config.json existe"""
    print_header("4. Testando config.json")
    
    config_path = Path("config.json")
    
    if not config_path.exists():
        print_warning("config.json não encontrado")
        print_info("Será criado automaticamente ao executar scripts")
        return True
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print_success("config.json encontrado e válido")
        
        if 'estado' in config and 'cidade' in config:
            print_info(f"Cidade configurada: {config.get('cidade')}/{config.get('estado')}")
        
        return True
    except json.JSONDecodeError:
        print_error("config.json inválido (erro de sintaxe JSON)")
        return False

def test_automation_script():
    """Testa se automation.py funciona"""
    print_header("5. Testando automation.py")
    
    script_path = Path("automation.py")
    
    if not script_path.exists():
        print_error("automation.py não encontrado")
        return False
    
    print_success("automation.py encontrado")
    
    # Testa help
    print_info("Testando --help...")
    try:
        result = subprocess.run(
            [sys.executable, "automation.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print_success("automation.py --help funcionou")
            return True
        else:
            print_error("Erro ao executar automation.py --help")
            print_info(result.stderr)
            return False
    except Exception as e:
        print_error(f"Exceção ao testar: {e}")
        return False

def test_api_script():
    """Testa se api.py funciona"""
    print_header("6. Testando api.py")
    
    script_path = Path("api.py")
    
    if not script_path.exists():
        print_error("api.py não encontrado")
        return False
    
    print_success("api.py encontrado")
    
    print_info("Verificando sintaxe...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", "api.py"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print_success("api.py sem erros de sintaxe")
            return True
        else:
            print_error("Erro de sintaxe em api.py")
            print_info(result.stderr)
            return False
    except Exception as e:
        print_error(f"Exceção ao testar: {e}")
        return False

def test_workflow_json():
    """Testa se workflow JSON é válido"""
    print_header("7. Testando workflow_n8n_example.json")
    
    workflow_path = Path("workflow_n8n_example.json")
    
    if not workflow_path.exists():
        print_error("workflow_n8n_example.json não encontrado")
        return False
    
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        
        print_success("workflow_n8n_example.json válido")
        
        if 'nodes' in workflow:
            print_info(f"Workflow tem {len(workflow['nodes'])} nodes")
        
        if 'name' in workflow:
            print_info(f"Nome: {workflow['name']}")
        
        return True
    except json.JSONDecodeError as e:
        print_error(f"Erro no JSON do workflow: {e}")
        return False

def test_documentation():
    """Testa se documentação existe"""
    print_header("8. Testando Documentação")
    
    docs = [
        'N8N_INTEGRATION.md',
        'GUIA_N8N_RAPIDO.md',
        'README_N8N.md',
        'INTEGRACAO_N8N_RESUMO.md'
    ]
    
    for doc in docs:
        doc_path = Path(doc)
        if doc_path.exists():
            size_kb = doc_path.stat().st_size / 1024
            print_success(f"{doc} ({size_kb:.1f} KB)")
        else:
            print_warning(f"{doc} não encontrado")
    
    return True

def generate_report(results):
    """Gera relatório final"""
    print_header("RELATÓRIO FINAL")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\nTestes Executados: {total}")
    print(f"Sucessos: {GREEN}{passed}{RESET}")
    print(f"Falhas: {RED}{total - passed}{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}✓ TODOS OS TESTES PASSARAM!{RESET}")
        print(f"\n{GREEN}Sistema pronto para integração n8n!{RESET}")
        print(f"\n{BLUE}Próximos passos:{RESET}")
        print("  1. Instale n8n: npm install -g n8n")
        print("  2. Inicie n8n: n8n")
        print("  3. Importe workflow_n8n_example.json")
        print("  4. Configure credenciais SMTP")
        print("  5. Execute workflow de teste")
        print(f"\n{BLUE}Documentação:{RESET}")
        print("  - GUIA_N8N_RAPIDO.md - Setup em 5 minutos")
        print("  - N8N_INTEGRATION.md - Guia completo")
        return True
    else:
        print(f"\n{RED}✗ ALGUNS TESTES FALHARAM{RESET}")
        print("\nRevise os erros acima e corrija antes de usar no n8n.")
        return False

def main():
    """Função principal"""
    print(f"{BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     TESTE DE INTEGRAÇÃO N8N - IA LEILÃO IMÓVEIS           ║")
    print("║                                                            ║")
    print("║  Este script testa se tudo está configurado corretamente  ║")
    print("║  antes de usar a integração com n8n                       ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{RESET}\n")
    
    results = {
        'env_file': test_env_file(),
        'dependencies': test_dependencies(),
        'data_structure': test_data_structure(),
        'config_json': test_config_json(),
        'automation_script': test_automation_script(),
        'api_script': test_api_script(),
        'workflow_json': test_workflow_json(),
        'documentation': test_documentation()
    }
    
    success = generate_report(results)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

