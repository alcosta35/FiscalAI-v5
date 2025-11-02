# routes/__init__.py
from routes.chat import router as chat_router
from routes.estatisticas import router as estatisticas_router
from routes.validacao import router as validacao_router

__all__ = ['chat_router', 'estatisticas_router', 'validacao_router']
