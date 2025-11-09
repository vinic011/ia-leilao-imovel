"""
API FastAPI para Integração com n8n
====================================

API REST para executar análises de imóveis de forma assíncrona e robusta.

Endpoints:
    POST /analyze - Inicia análise automatizada
    GET /status/{task_id} - Verifica status de análise
    GET /result/{task_id} - Obtém resultado de análise
    GET /ranking - Lista imóveis analisados com filtros
    GET /health - Healthcheck

Uso com n8n:
    1. POST /analyze com parâmetros
    2. Aguarda conclusão (polling em /status)
    3. GET /result para obter resultados

Executar:
    uvicorn api:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from pathlib import Path
import json
import uuid
import subprocess
import sys

app = FastAPI(
    title="IA Leilão Imóveis API",
    description="API para análise automatizada de imóveis de leilão",
    version="1.0.0"
)

# Armazena status de tarefas em memória (em produção, usar Redis/DB)
tasks_status: Dict[str, Dict] = {}

# Modelos Pydantic
class AnalyzeRequest(BaseModel):
    """Requisição para iniciar análise"""
    estado: str = Field(..., description="Sigla do estado (ex: GO, SP)", min_length=2, max_length=2)
    cidade: str = Field(..., description="Nome da cidade em MAIÚSCULAS")
    min_nota: float = Field(default=0.0, description="Nota mínima para filtro (0-10)", ge=0, le=10)
    max_imoveis: Optional[int] = Field(default=None, description="Limite de imóveis para análise")
    
    class Config:
        schema_extra = {
            "example": {
                "estado": "GO",
                "cidade": "RIO VERDE",
                "min_nota": 7.0,
                "max_imoveis": 10
            }
        }

class TaskStatus(BaseModel):
    """Status de uma tarefa"""
    task_id: str
    status: str  # pending, running, completed, failed
    created_at: str
    updated_at: str
    progress: Optional[Dict] = None
    error: Optional[str] = None

class AnalyzeResponse(BaseModel):
    """Resposta ao iniciar análise"""
    task_id: str
    status: str
    message: str
    status_url: str
    result_url: str

class ImovelSummary(BaseModel):
    """Resumo de imóvel analisado"""
    id: str
    nota_final: float
    comarca: str
    condominio: str
    quartos: str
    area_privativa_m2: str
    valor_minimo: str
    desconto_percent: str


# Funções auxiliares
def run_automation_task(task_id: str, estado: str, cidade: str, min_nota: float, max_imoveis: Optional[int]):
    """Executa automação em background"""
    try:
        # Atualiza status
        tasks_status[task_id]["status"] = "running"
        tasks_status[task_id]["updated_at"] = datetime.now().isoformat()
        
        # Monta comando
        cmd = [
            sys.executable,
            "automation.py",
            "--estado", estado,
            "--cidade", cidade,
            "--min-nota", str(min_nota),
            "--output", f"automation_result_{task_id}.json"
        ]
        
        if max_imoveis:
            cmd.extend(["--max-imoveis", str(max_imoveis)])
        
        # Executa
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=7200  # 2 horas
        )
        
        # Processa resultado
        if result.returncode == 0:
            # Carrega resultado do arquivo
            result_file = Path(f"automation_result_{task_id}.json")
            if result_file.exists():
                with open(result_file, 'r', encoding='utf-8') as f:
                    result_data = json.load(f)
                
                tasks_status[task_id]["status"] = "completed"
                tasks_status[task_id]["result"] = result_data
                tasks_status[task_id]["updated_at"] = datetime.now().isoformat()
            else:
                raise Exception("Arquivo de resultado não encontrado")
        else:
            raise Exception(f"Erro na automação: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        tasks_status[task_id]["status"] = "failed"
        tasks_status[task_id]["error"] = "Timeout após 2 horas"
        tasks_status[task_id]["updated_at"] = datetime.now().isoformat()
    except Exception as e:
        tasks_status[task_id]["status"] = "failed"
        tasks_status[task_id]["error"] = str(e)
        tasks_status[task_id]["updated_at"] = datetime.now().isoformat()


# Endpoints
@app.get("/", tags=["Info"])
async def root():
    """Informações da API"""
    return {
        "name": "IA Leilão Imóveis API",
        "version": "1.0.0",
        "description": "API para análise automatizada de imóveis de leilão",
        "endpoints": {
            "POST /analyze": "Inicia análise",
            "GET /status/{task_id}": "Verifica status",
            "GET /result/{task_id}": "Obtém resultado",
            "GET /ranking": "Lista imóveis analisados",
            "GET /health": "Healthcheck"
        }
    }

@app.get("/health", tags=["Info"])
async def health():
    """Healthcheck para n8n"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze", response_model=AnalyzeResponse, tags=["Análise"])
async def analyze(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Inicia análise automatizada de imóveis
    
    Processo:
    1. Cria tarefa assíncrona
    2. Executa scraping + análise em background
    3. Retorna task_id para acompanhamento
    
    Use GET /status/{task_id} para acompanhar progresso
    """
    # Gera ID único para tarefa
    task_id = str(uuid.uuid4())
    
    # Registra tarefa
    tasks_status[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "params": {
            "estado": request.estado.upper(),
            "cidade": request.cidade.upper(),
            "min_nota": request.min_nota,
            "max_imoveis": request.max_imoveis
        }
    }
    
    # Adiciona tarefa ao background
    background_tasks.add_task(
        run_automation_task,
        task_id,
        request.estado.upper(),
        request.cidade.upper(),
        request.min_nota,
        request.max_imoveis
    )
    
    return AnalyzeResponse(
        task_id=task_id,
        status="pending",
        message="Análise iniciada. Use o task_id para acompanhar o progresso.",
        status_url=f"/status/{task_id}",
        result_url=f"/result/{task_id}"
    )

@app.get("/status/{task_id}", response_model=TaskStatus, tags=["Análise"])
async def get_status(task_id: str):
    """
    Verifica status de uma análise
    
    Status possíveis:
    - pending: Aguardando início
    - running: Em execução
    - completed: Concluída com sucesso
    - failed: Falhou (veja campo 'error')
    """
    if task_id not in tasks_status:
        raise HTTPException(status_code=404, detail="Task não encontrada")
    
    task = tasks_status[task_id]
    
    return TaskStatus(
        task_id=task["task_id"],
        status=task["status"],
        created_at=task["created_at"],
        updated_at=task["updated_at"],
        progress=task.get("progress"),
        error=task.get("error")
    )

@app.get("/result/{task_id}", tags=["Análise"])
async def get_result(task_id: str):
    """
    Obtém resultado de uma análise concluída
    
    Retorna JSON completo com:
    - Imóveis analisados
    - Top imóveis (ordenados por nota)
    - Resumo executivo
    - Erros (se houver)
    """
    if task_id not in tasks_status:
        raise HTTPException(status_code=404, detail="Task não encontrada")
    
    task = tasks_status[task_id]
    
    if task["status"] == "pending":
        raise HTTPException(status_code=425, detail="Análise ainda não iniciada")
    
    if task["status"] == "running":
        raise HTTPException(status_code=425, detail="Análise ainda em execução")
    
    if task["status"] == "failed":
        raise HTTPException(
            status_code=500,
            detail=f"Análise falhou: {task.get('error', 'Erro desconhecido')}"
        )
    
    return JSONResponse(content=task.get("result", {}))

@app.get("/ranking", tags=["Consulta"])
async def get_ranking(
    min_nota: float = Query(default=0.0, ge=0, le=10, description="Nota mínima"),
    max_results: int = Query(default=100, ge=1, le=1000, description="Limite de resultados"),
    comarca: Optional[str] = Query(default=None, description="Filtrar por comarca")
):
    """
    Lista imóveis analisados (de todas as análises salvas)
    
    Carrega todos os arquivos *_analysis.json e retorna ranking consolidado
    """
    try:
        analysis_dir = Path("data/analysis")
        
        if not analysis_dir.exists():
            return {
                "total": 0,
                "filtrado": 0,
                "imoveis": []
            }
        
        imoveis = []
        
        # Carrega todas as análises
        for analysis_file in analysis_dir.glob("*_analysis.json"):
            try:
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    analysis = json.load(f)
                
                nota = analysis["nota_final"]["valor"]
                imovel_comarca = analysis["imovel"].get("comarca", "")
                
                # Aplica filtros
                if nota < min_nota:
                    continue
                
                if comarca and comarca.upper() not in imovel_comarca.upper():
                    continue
                
                # Adiciona ao ranking
                imoveis.append({
                    "id": analysis_file.stem.replace("_analysis", ""),
                    "nota_final": nota,
                    "comarca": imovel_comarca,
                    "condominio": analysis["imovel"].get("condominio", "N/A"),
                    "apartamento": analysis["imovel"].get("apartamento", "N/A"),
                    "quartos": analysis["imovel"].get("quartos", "N/A"),
                    "area_privativa_m2": analysis["imovel"].get("area_privativa_m2", "N/A"),
                    "valor_minimo": analysis["imovel"].get("valor_minimo", "N/A"),
                    "desconto_percent": analysis["imovel"].get("desconto_percent", "N/A"),
                    "arquivo": str(analysis_file)
                })
            except Exception as e:
                print(f"Erro ao processar {analysis_file}: {e}")
                continue
        
        # Ordena por nota (descendente)
        imoveis.sort(key=lambda x: x["nota_final"], reverse=True)
        
        # Limita resultados
        total = len(imoveis)
        imoveis = imoveis[:max_results]
        
        return {
            "total": total,
            "filtrado": len(imoveis),
            "filtros": {
                "min_nota": min_nota,
                "comarca": comarca,
                "max_results": max_results
            },
            "imoveis": imoveis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar ranking: {str(e)}")

@app.delete("/task/{task_id}", tags=["Análise"])
async def delete_task(task_id: str):
    """Remove tarefa do sistema"""
    if task_id not in tasks_status:
        raise HTTPException(status_code=404, detail="Task não encontrada")
    
    # Remove arquivos relacionados
    result_file = Path(f"automation_result_{task_id}.json")
    if result_file.exists():
        result_file.unlink()
    
    # Remove do dicionário
    del tasks_status[task_id]
    
    return {"message": "Task removida com sucesso"}

@app.get("/tasks", tags=["Análise"])
async def list_tasks():
    """Lista todas as tarefas"""
    return {
        "total": len(tasks_status),
        "tasks": list(tasks_status.values())
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando API IA Leilão Imóveis...")
    print("📖 Documentação: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)

