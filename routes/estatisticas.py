# backend/routes/estatisticas.py
"""
Rotas relacionadas às estatísticas e dashboard
"""
from fastapi import APIRouter, HTTPException, Depends
from models.schemas import (
    ResumoEstatisticas,
    CFOPDistribuicaoResponse,
    DivergenciasTipoResponse,
    OperacoesUFResponse,
    TendenciaMensalResponse,
    TopDivergenciasResponse
)
from services import EstatisticasService
from config import settings

router = APIRouter(prefix="/estatisticas", tags=["Estatísticas"])

def get_estatisticas_service():
    """Dependency para obter o serviço de estatísticas"""
    from main import agente
    if agente is None:
        raise HTTPException(status_code=503, detail="Sistema não inicializado")
    return EstatisticasService(agente)

@router.get("/resumo", response_model=ResumoEstatisticas)
async def obter_resumo(service: EstatisticasService = Depends(get_estatisticas_service)):
    """
    Retorna estatísticas gerais do sistema
    """
    try:
        return service.obter_resumo(sample_size=settings.MAX_SAMPLE_SIZE)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cfop-distribuicao", response_model=CFOPDistribuicaoResponse)
async def obter_distribuicao_cfop(service: EstatisticasService = Depends(get_estatisticas_service)):
    """
    Retorna distribuição dos CFOPs mais utilizados
    """
    try:
        cfops = service.obter_distribuicao_cfop(top_n=10)
        return {"cfops": cfops}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/divergencias-tipo", response_model=DivergenciasTipoResponse)
async def obter_divergencias_por_tipo(service: EstatisticasService = Depends(get_estatisticas_service)):
    """
    Retorna divergências agrupadas por tipo
    """
    try:
        divergencias = service.obter_divergencias_por_tipo(sample_size=settings.MAX_SAMPLE_SIZE)
        return {"divergencias": divergencias}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/operacoes-uf", response_model=OperacoesUFResponse)
async def obter_operacoes_por_uf(service: EstatisticasService = Depends(get_estatisticas_service)):
    """
    Retorna distribuição de operações por UF
    """
    try:
        operacoes = service.obter_operacoes_por_uf(top_n=10)
        return {"operacoes": operacoes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tendencia-mensal", response_model=TendenciaMensalResponse)
async def obter_tendencia_mensal(service: EstatisticasService = Depends(get_estatisticas_service)):
    """
    Retorna tendência de notas ao longo do tempo
    """
    try:
        tendencia = service.obter_tendencia_mensal()
        return {"tendencia": tendencia}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-divergencias", response_model=TopDivergenciasResponse)
async def obter_top_divergencias(service: EstatisticasService = Depends(get_estatisticas_service)):
    """
    Retorna top 10 notas com mais problemas
    """
    try:
        top = service.obter_top_divergencias(
            sample_size=settings.MAX_SAMPLE_SIZE,
            top_n=10
        )
        return {"top_divergencias": top}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))