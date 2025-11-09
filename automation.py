"""
Script de Automação Completa para Integração com n8n
=====================================================

Este script executa todo o pipeline de análise de imóveis de forma automatizada:
1. Busca lista de imóveis (scraping)
2. Baixa detalhes de todos os imóveis
3. Analisa cada imóvel com IA
4. Gera relatório consolidado
5. Retorna JSON para n8n processar

Uso:
    python automation.py --estado GO --cidade "RIO VERDE" --min-nota 7
    
Saída: JSON com lista de imóveis analisados e ranqueados
"""

import json
import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import time

class AutomationPipeline:
    """Pipeline completo de automação de análise de imóveis"""
    
    def __init__(self, estado: str, cidade: str, min_nota: float = 0.0, max_imoveis: Optional[int] = None):
        self.estado = estado.upper()
        self.cidade = cidade.upper()
        self.min_nota = min_nota
        self.max_imoveis = max_imoveis
        self.config_path = Path("config.json")
        self.data_dir = Path("data")
        self.analysis_dir = self.data_dir / "analysis"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "estado": self.estado,
            "cidade": self.cidade,
            "min_nota": self.min_nota,
            "imoveis_encontrados": 0,
            "imoveis_analisados": 0,
            "imoveis_aprovados": 0,
            "top_imoveis": [],
            "erros": []
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log formatado com timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}", flush=True)
    
    def update_config(self, imovel_id: Optional[str] = None):
        """Atualiza config.json com parâmetros atuais"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {}
            
            config["estado"] = self.estado
            config["cidade"] = self.cidade
            if imovel_id:
                config["imovel"] = imovel_id
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            self.log(f"Config atualizado: {self.estado}/{self.cidade}" + (f"/{imovel_id}" if imovel_id else ""))
            return True
        except Exception as e:
            self.log(f"Erro ao atualizar config: {e}", "ERROR")
            return False
    
    def run_scraping_list(self) -> bool:
        """Executa scraping da lista de imóveis"""
        self.log("Iniciando scraping de lista de imóveis...")
        try:
            # Atualiza config antes
            if not self.update_config():
                return False
            
            # Executa scraping
            result = subprocess.run(
                [sys.executable, "scrape_property_list.py"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos
            )
            
            if result.returncode == 0:
                self.log("✓ Scraping de lista concluído com sucesso")
                return True
            else:
                self.log(f"✗ Erro no scraping: {result.stderr}", "ERROR")
                self.results["erros"].append({
                    "etapa": "scraping_list",
                    "erro": result.stderr
                })
                return False
                
        except subprocess.TimeoutExpired:
            self.log("✗ Timeout no scraping de lista", "ERROR")
            self.results["erros"].append({
                "etapa": "scraping_list",
                "erro": "Timeout após 5 minutos"
            })
            return False
        except Exception as e:
            self.log(f"✗ Exceção no scraping: {e}", "ERROR")
            self.results["erros"].append({
                "etapa": "scraping_list",
                "erro": str(e)
            })
            return False
    
    def get_imoveis_list(self) -> List[str]:
        """Extrai lista de IDs de imóveis do HTML salvo"""
        try:
            from bs4 import BeautifulSoup
            
            html_path = self.data_dir / "list" / f"imoveis_{self.cidade.lower()}_{self.estado.lower()}.html"
            
            if not html_path.exists():
                self.log(f"✗ Arquivo de lista não encontrado: {html_path}", "ERROR")
                return []
            
            with open(html_path, 'r', encoding='utf-8') as f:
                html = f.read()
            
            soup = BeautifulSoup(html, 'html.parser')
            imoveis = []
            
            for tag in soup.find_all(text=lambda t: t and "Número do imóvel" in t):
                partes = tag.strip().split(":")
                if len(partes) > 1:
                    numero = partes[1].strip().split("<")[0].split()[0].replace("-", "")
                    if numero and numero not in imoveis:
                        imoveis.append(numero)
            
            self.log(f"✓ Encontrados {len(imoveis)} imóveis")
            self.results["imoveis_encontrados"] = len(imoveis)
            
            # Limita quantidade se especificado
            if self.max_imoveis:
                imoveis = imoveis[:self.max_imoveis]
                self.log(f"Limitando análise a {self.max_imoveis} imóveis")
            
            return imoveis
            
        except Exception as e:
            self.log(f"✗ Erro ao extrair lista de imóveis: {e}", "ERROR")
            self.results["erros"].append({
                "etapa": "extract_list",
                "erro": str(e)
            })
            return []
    
    def run_scraping_details(self) -> bool:
        """Executa scraping de detalhes de todos os imóveis"""
        self.log("Iniciando scraping de detalhes...")
        try:
            result = subprocess.run(
                [sys.executable, "scrape_detail.py"],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hora
            )
            
            if result.returncode == 0:
                self.log("✓ Scraping de detalhes concluído")
                return True
            else:
                self.log(f"✗ Erro no scraping de detalhes: {result.stderr}", "ERROR")
                self.results["erros"].append({
                    "etapa": "scraping_details",
                    "erro": result.stderr
                })
                return False
                
        except subprocess.TimeoutExpired:
            self.log("✗ Timeout no scraping de detalhes (1h)", "ERROR")
            self.results["erros"].append({
                "etapa": "scraping_details",
                "erro": "Timeout após 1 hora"
            })
            return False
        except Exception as e:
            self.log(f"✗ Exceção no scraping de detalhes: {e}", "ERROR")
            self.results["erros"].append({
                "etapa": "scraping_details",
                "erro": str(e)
            })
            return False
    
    def analyze_imovel(self, imovel_id: str) -> Optional[Dict]:
        """Analisa um imóvel específico com IA"""
        self.log(f"Analisando imóvel {imovel_id}...")
        
        try:
            # Verifica se já existe análise
            analysis_file = self.analysis_dir / f"{imovel_id}_analysis.json"
            if analysis_file.exists():
                self.log(f"  → Análise já existe, carregando do cache...")
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Atualiza config com imóvel atual
            if not self.update_config(imovel_id):
                return None
            
            # Executa análise
            self.log(f"  → Executando análise com IA (pode demorar 1-3 min)...")
            result = subprocess.run(
                [sys.executable, "query.py"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos
            )
            
            if result.returncode != 0:
                self.log(f"  ✗ Erro na análise: {result.stderr}", "ERROR")
                return None
            
            # Extrai JSON da saída
            output = result.stdout
            json_start = output.find('{')
            json_end = output.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                self.log(f"  ✗ JSON não encontrado na saída", "ERROR")
                return None
            
            analysis_json = json.loads(output[json_start:json_end])
            
            # Salva análise
            self.analysis_dir.mkdir(parents=True, exist_ok=True)
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_json, f, indent=2, ensure_ascii=False)
            
            self.log(f"  ✓ Análise concluída - Nota: {analysis_json['nota_final']['valor']:.1f}")
            return analysis_json
            
        except subprocess.TimeoutExpired:
            self.log(f"  ✗ Timeout na análise", "ERROR")
            return None
        except json.JSONDecodeError as e:
            self.log(f"  ✗ Erro ao decodificar JSON: {e}", "ERROR")
            return None
        except Exception as e:
            self.log(f"  ✗ Exceção na análise: {e}", "ERROR")
            return None
    
    def analyze_all_imoveis(self, imoveis: List[str]):
        """Analisa todos os imóveis da lista"""
        self.log(f"Iniciando análise de {len(imoveis)} imóveis...")
        
        for idx, imovel_id in enumerate(imoveis, 1):
            self.log(f"\n[{idx}/{len(imoveis)}] Processando imóvel {imovel_id}")
            
            analysis = self.analyze_imovel(imovel_id)
            
            if analysis:
                self.results["imoveis_analisados"] += 1
                nota = analysis["nota_final"]["valor"]
                
                # Verifica se passa no filtro de nota mínima
                if nota >= self.min_nota:
                    self.results["imoveis_aprovados"] += 1
                    
                    # Adiciona aos top imóveis
                    imovel_summary = {
                        "id": imovel_id,
                        "nota_final": nota,
                        "comarca": analysis["imovel"].get("comarca", "N/A"),
                        "condominio": analysis["imovel"].get("condominio", "N/A"),
                        "apartamento": analysis["imovel"].get("apartamento", "N/A"),
                        "quartos": analysis["imovel"].get("quartos", "N/A"),
                        "area_privativa_m2": analysis["imovel"].get("area_privativa_m2", "N/A"),
                        "valor_minimo": analysis["imovel"].get("valor_minimo", "N/A"),
                        "desconto_percent": analysis["imovel"].get("desconto_percent", "N/A"),
                        "criterios": [
                            {
                                "nome": c["nome"],
                                "nota": c["nota"]
                            } for c in analysis["criterios"]
                        ],
                        "riscos": [r["descricao"] for r in analysis.get("riscos", [])],
                        "proximos_passos": analysis.get("proximos_passos", [])
                    }
                    
                    self.results["top_imoveis"].append(imovel_summary)
                else:
                    self.log(f"  → Imóvel filtrado (nota {nota:.1f} < {self.min_nota})")
            else:
                self.results["erros"].append({
                    "etapa": "analysis",
                    "imovel": imovel_id,
                    "erro": "Falha na análise"
                })
            
            # Pequeno delay para não sobrecarregar a API
            if idx < len(imoveis):
                time.sleep(2)
        
        # Ordena top imóveis por nota (descendente)
        self.results["top_imoveis"].sort(key=lambda x: x["nota_final"], reverse=True)
    
    def generate_report(self) -> Dict:
        """Gera relatório final consolidado"""
        self.log("\n" + "="*60)
        self.log("RELATÓRIO FINAL DA AUTOMAÇÃO")
        self.log("="*60)
        self.log(f"Estado/Cidade: {self.estado} / {self.cidade}")
        self.log(f"Imóveis encontrados: {self.results['imoveis_encontrados']}")
        self.log(f"Imóveis analisados: {self.results['imoveis_analisados']}")
        self.log(f"Imóveis aprovados (nota ≥ {self.min_nota}): {self.results['imoveis_aprovados']}")
        self.log(f"Erros: {len(self.results['erros'])}")
        
        if self.results["top_imoveis"]:
            self.log("\nTOP 5 IMÓVEIS:")
            for idx, imovel in enumerate(self.results["top_imoveis"][:5], 1):
                self.log(f"  {idx}. ID: {imovel['id']} | Nota: {imovel['nota_final']:.1f} | {imovel['condominio']}")
        
        self.log("="*60)
        
        # Adiciona resumo executivo
        self.results["resumo_executivo"] = {
            "taxa_sucesso": f"{(self.results['imoveis_analisados'] / max(self.results['imoveis_encontrados'], 1)) * 100:.1f}%",
            "taxa_aprovacao": f"{(self.results['imoveis_aprovados'] / max(self.results['imoveis_analisados'], 1)) * 100:.1f}%",
            "melhor_nota": self.results["top_imoveis"][0]["nota_final"] if self.results["top_imoveis"] else 0,
            "nota_media": sum(i["nota_final"] for i in self.results["top_imoveis"]) / len(self.results["top_imoveis"]) if self.results["top_imoveis"] else 0
        }
        
        return self.results
    
    def run(self) -> Dict:
        """Executa pipeline completo"""
        self.log("="*60)
        self.log("INICIANDO PIPELINE DE AUTOMAÇÃO")
        self.log("="*60)
        
        # 1. Scraping de lista
        if not self.run_scraping_list():
            self.log("Pipeline abortado: erro no scraping de lista", "ERROR")
            return self.results
        
        # 2. Extrai lista de imóveis
        imoveis = self.get_imoveis_list()
        if not imoveis:
            self.log("Pipeline abortado: nenhum imóvel encontrado", "ERROR")
            return self.results
        
        # 3. Scraping de detalhes
        if not self.run_scraping_details():
            self.log("Pipeline abortado: erro no scraping de detalhes", "ERROR")
            return self.results
        
        # 4. Análise de todos os imóveis
        self.analyze_all_imoveis(imoveis)
        
        # 5. Gera relatório
        return self.generate_report()


def main():
    """Função principal para linha de comando"""
    parser = argparse.ArgumentParser(
        description="Automação completa de análise de imóveis para n8n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Análise completa em Rio Verde/GO, apenas imóveis com nota ≥ 7
  python automation.py --estado GO --cidade "RIO VERDE" --min-nota 7
  
  # Análise de teste com apenas 3 imóveis
  python automation.py --estado GO --cidade GOIANIA --max-imoveis 3
  
  # Análise sem filtro de nota
  python automation.py --estado SP --cidade "SAO PAULO"
        """
    )
    
    parser.add_argument(
        "--estado",
        required=True,
        help="Sigla do estado (ex: GO, SP, RJ)"
    )
    
    parser.add_argument(
        "--cidade",
        required=True,
        help="Nome da cidade em MAIÚSCULAS (ex: 'RIO VERDE', GOIANIA)"
    )
    
    parser.add_argument(
        "--min-nota",
        type=float,
        default=0.0,
        help="Nota mínima para incluir no relatório (0-10). Default: 0"
    )
    
    parser.add_argument(
        "--max-imoveis",
        type=int,
        help="Número máximo de imóveis para analisar (útil para testes)"
    )
    
    parser.add_argument(
        "--output",
        default="automation_result.json",
        help="Arquivo JSON de saída. Default: automation_result.json"
    )
    
    args = parser.parse_args()
    
    # Executa pipeline
    pipeline = AutomationPipeline(
        estado=args.estado,
        cidade=args.cidade,
        min_nota=args.min_nota,
        max_imoveis=args.max_imoveis
    )
    
    results = pipeline.run()
    
    # Salva resultado em arquivo
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Resultado salvo em: {output_path}")
    
    # Imprime JSON na stdout para n8n capturar
    print("\n--- JSON OUTPUT START ---")
    print(json.dumps(results, ensure_ascii=False))
    print("--- JSON OUTPUT END ---")
    
    # Retorna código de saída baseado em sucesso
    exit_code = 0 if results["imoveis_analisados"] > 0 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

