# backend/routes/validacao.py
"""
Rotas relacionadas à validação de CFOP
"""
from fastapi import APIRouter, HTTPException, Depends
from models.schemas import ValidarCFOPRequest

router = APIRouter(prefix="/validacao", tags=["Validação"])

def get_agente():
    """Dependency para obter o agente"""
    from main import agente
    if agente is None:
        raise HTTPException(status_code=503, detail="Sistema não inicializado")
    return agente

@router.post("/cfop-item")
async def validar_cfop_item(
    request: ValidarCFOPRequest,
    agente = Depends(get_agente)
):
    """
    Valida o CFOP de um item específico usando chave de acesso
    """
    try:
        # Encontrar a ferramenta de validação
        tool_validar = None
        for tool in agente.tools:
            if tool.name == "validar_cfop_item_especifico":
                tool_validar = tool
                break
        
        if not tool_validar:
            raise HTTPException(status_code=500, detail="Ferramenta de validação não encontrada")
        
        # Executar validação
        resultado = tool_validar.func(request.chave_acesso, request.numero_item)
        
        return {"resultado": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao validar CFOP: {str(e)}")