# backend/routes/chat.py
"""
Rotas relacionadas ao chat
"""
from fastapi import APIRouter, HTTPException, Depends
from models.schemas import ChatRequest, ChatResponse
from typing import Any

router = APIRouter(prefix="/chat", tags=["Chat"])

def get_agente():
    """Dependency para obter o agente"""
    from main import agente
    if agente is None:
        raise HTTPException(status_code=503, detail="Sistema não inicializado")
    return agente

@router.post("/perguntar", response_model=ChatResponse)
async def processar_pergunta(
    request: ChatRequest,
    agente = Depends(get_agente)
):
    """
    Processa uma pergunta do usuário através do agente inteligente
    """
    try:
        resposta = agente.processar_pergunta(request.pergunta)
        return ChatResponse(resposta=resposta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar pergunta: {str(e)}")