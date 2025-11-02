# backend/models/schemas.py
"""
Schemas Pydantic para validação de dados
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ============================================================================
# SCHEMAS DE REQUEST
# ============================================================================

class ChatRequest(BaseModel):
    """Request do chat"""
    pergunta: str = Field(..., min_length=1, description="Pergunta do usuário")

class ValidarCFOPRequest(BaseModel):
    """Request para validação de CFOP"""
    chave_acesso: str = Field(..., min_length=44, max_length=44, description="Chave de acesso da nota")
    numero_item: str = Field(..., description="Número do item (1, 2, 3 ou 'primeiro', 'segundo')")

# ============================================================================
# SCHEMAS DE RESPONSE
# ============================================================================

class ChatResponse(BaseModel):
    """Response do chat"""
    resposta: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class ResumoEstatisticas(BaseModel):
    """Resumo geral das estatísticas"""
    total_notas: int
    total_itens: int
    taxa_conformidade: float
    divergencias_criticas: int
    divergencias_total: int
    ultima_analise: str

class CFOPDistribuicao(BaseModel):
    """Distribuição de um CFOP"""
    cfop: str
    quantidade: int
    percentual: float

class CFOPDistribuicaoResponse(BaseModel):
    """Response com distribuição de CFOPs"""
    cfops: List[CFOPDistribuicao]

class DivergenciaTipo(BaseModel):
    """Divergência por tipo"""
    tipo: str
    quantidade: int
    cor: str

class DivergenciasTipoResponse(BaseModel):
    """Response com divergências por tipo"""
    divergencias: List[DivergenciaTipo]

class OperacaoUF(BaseModel):
    """Operação por UF"""
    uf: str
    quantidade: int

class OperacoesUFResponse(BaseModel):
    """Response com operações por UF"""
    operacoes: List[OperacaoUF]

class TendenciaMensal(BaseModel):
    """Tendência mensal"""
    mes: str
    notas: int
    divergencias: int

class TendenciaMensalResponse(BaseModel):
    """Response com tendência mensal"""
    tendencia: List[TendenciaMensal]

class TopDivergencia(BaseModel):
    """Top divergência"""
    nota: str
    divergencias: int
    natureza: str
    valor: float

class TopDivergenciasResponse(BaseModel):
    """Response com top divergências"""
    top_divergencias: List[TopDivergencia]

# ============================================================================
# SCHEMAS DE STATUS
# ============================================================================

class HealthCheck(BaseModel):
    """Health check do sistema"""
    status: str
    mensagem: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class ErrorResponse(BaseModel):
    """Response de erro padrão"""
    erro: str
    detalhes: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())