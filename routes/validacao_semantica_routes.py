# routes/validacao_semantica_routes.py
"""
Rotas para validação semântica de CFOP usando Pinecone
FiscalAI v5
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Optional
import pandas as pd
from io import StringIO

from services.validacao_semantica import ValidadorCFOPSemantico

router = APIRouter(prefix="/validacao-semantica", tags=["Validação Semântica"])

# Instância global do validador
validador: Optional[ValidadorCFOPSemantico] = None


class ItemValidacao(BaseModel):
    """Modelo para validação de item individual"""
    uf_emitente: str
    uf_destinatario: str
    descricao_produto: str
    ncm: Optional[str] = ""
    consumidor_final: str = "0"
    indicador_ie: str = "1"
    cfop_informado: Optional[str] = None


class ResultadoValidacao(BaseModel):
    """Modelo de resposta da validação"""
    status: str
    mensagem: str
    cfop_informado: Optional[str]
    total_sugestoes: int
    sugestoes: List[Dict]
    query_gerada: str


@router.post("/inicializar")
async def inicializar_validador():
    """
    Inicializa o validador semântico conectando ao Pinecone
    """
    global validador
    
    try:
        validador = ValidadorCFOPSemantico()
        
        # Testar conexão
        stats = validador.index.describe_index_stats()
        
        return {
            "status": "success",
            "mensagem": "Validador semântico inicializado",
            "index_name": validador.index_name,
            "total_vetores": stats.get('total_vector_count', 0)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao inicializar validador: {str(e)}"
        )


@router.get("/status")
async def status_validador():
    """Retorna status do validador semântico"""
    if validador is None:
        return {
            "inicializado": False,
            "mensagem": "Validador não inicializado"
        }
    
    try:
        stats = validador.index.describe_index_stats()
        return {
            "inicializado": True,
            "index_name": validador.index_name,
            "total_vetores": stats.get('total_vector_count', 0),
            "embedding_model": validador.embedding_model
        }
    except Exception as e:
        return {
            "inicializado": True,
            "erro": str(e)
        }


@router.post("/validar-item", response_model=ResultadoValidacao)
async def validar_item_individual(item: ItemValidacao):
    """
    Valida CFOP de um item individual
    """
    if validador is None:
        raise HTTPException(
            status_code=400,
            detail="Validador não inicializado. Use /inicializar primeiro."
        )
    
    try:
        # Preparar dados do item
        item_data = {
            'UF EMITENTE': item.uf_emitente,
            'UF DESTINATÁRIO': item.uf_destinatario,
            'DESCRIÇÃO DO PRODUTO/SERVIÇO': item.descricao_produto,
            'NCM/SH (TIPO DE PRODUTO)': item.ncm,
            'CONSUMIDOR FINAL': item.consumidor_final,
            'INDICADOR IE DESTINATÁRIO': item.indicador_ie
        }
        
        # Validar
        resultado = validador.validar_cfop_item(
            item_data=item_data,
            cfop_informado=item.cfop_informado,
            top_k=5
        )
        
        return resultado
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na validação: {str(e)}"
        )


@router.post("/validar-lote")
async def validar_lote_itens(arquivo: UploadFile = File(...)):
    """
    Valida lote de itens a partir de CSV
    
    O CSV deve conter as colunas:
    - UF EMITENTE
    - UF DESTINATÁRIO
    - DESCRIÇÃO DO PRODUTO/SERVIÇO
    - NCM/SH (TIPO DE PRODUTO)
    - CONSUMIDOR FINAL
    - INDICADOR IE DESTINATÁRIO
    - CFOP (opcional, para comparação)
    """
    if validador is None:
        raise HTTPException(
            status_code=400,
            detail="Validador não inicializado"
        )
    
    if not arquivo.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Apenas arquivos CSV são aceitos"
        )
    
    try:
        # Ler CSV
        contents = await arquivo.read()
        df = pd.read_csv(StringIO(contents.decode('utf-8-sig')))
        
        # Validar lote
        df_resultado = validador.validar_lote(df, top_k=3)
        
        # Gerar relatório
        relatorio = validador.gerar_relatorio_validacao(df_resultado)
        
        # Converter resultados para dict
        resultados_list = df_resultado.to_dict('records')
        
        return {
            "status": "success",
            "total_processado": len(df_resultado),
            "relatorio": relatorio,
            "resultados": resultados_list[:100]  # Limitar para não sobrecarregar resposta
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar lote: {str(e)}"
        )


@router.get("/buscar-cfop")
async def buscar_cfop_por_contexto(
    query: str,
    top_k: int = 5
):
    """
    Busca CFOPs por descrição/contexto usando busca semântica
    
    Args:
        query: Descrição da operação fiscal
        top_k: Número de resultados
    """
    if validador is None:
        raise HTTPException(
            status_code=400,
            detail="Validador não inicializado"
        )
    
    try:
        # Buscar CFOPs similares
        resultados = validador.buscar_cfops_similares(
            query_text=query,
            top_k=top_k,
            min_score=0.6
        )
        
        return {
            "query": query,
            "total_resultados": len(resultados),
            "cfops": resultados
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na busca: {str(e)}"
        )


@router.post("/comparar-validacoes")
async def comparar_validacoes(arquivo: UploadFile = File(...)):
    """
    Compara validação semântica com CFOPs informados
    Útil para avaliar acurácia do modelo
    """
    if validador is None:
        raise HTTPException(
            status_code=400,
            detail="Validador não inicializado"
        )
    
    try:
        # Ler CSV
        contents = await arquivo.read()
        df = pd.read_csv(StringIO(contents.decode('utf-8-sig')))
        
        # Validar lote
        df_resultado = validador.validar_lote(df, top_k=5)
        
        # Gerar relatório detalhado
        relatorio = validador.gerar_relatorio_validacao(df_resultado)
        
        # Análise de divergências
        divergentes = df_resultado[df_resultado['status'] == 'DIVERGENTE']
        
        divergencias_detalhadas = []
        for _, row in divergentes.head(20).iterrows():  # Limitar a 20
            divergencias_detalhadas.append({
                'cfop_informado': row['cfop_informado'],
                'cfop_sugerido': row['sugestoes'][0]['cfop'] if row['sugestoes'] else None,
                'score': row['sugestoes'][0]['score'] if row['sugestoes'] else None,
                'numero_item': row['numero_item']
            })
        
        return {
            "status": "success",
            "relatorio_geral": relatorio,
            "total_divergencias": len(divergentes),
            "amostra_divergencias": divergencias_detalhadas
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na comparação: {str(e)}"
        )
