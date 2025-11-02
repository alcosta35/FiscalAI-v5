# backend/main.py
"""
Aplicação principal FastAPI - FiscalAI com Interface Web
Suporte para Google Colab + ngrok
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn
import sys
import os
import shutil
from pathlib import Path

# Importações locais
from config import settings, DATA_DIR, IS_COLAB
from models.schemas import HealthCheck
from routes import chat_router, estatisticas_router, validacao_router
from agente_cfop import AgenteValidadorCFOP

# ============================================================================
# INICIALIZAÇÃO DA APLICAÇÃO
# ============================================================================

app = FastAPI(
    title=settings.app_name,        
    version=settings.app_version,  
    description="Sistema inteligente de auditoria e validação de CFOP",
    docs_url="/api/docs",  # Mover docs para /api/docs
    redoc_url="/api/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criar diretórios necessários
STATIC_DIR = Path(__file__).parent / "static"
TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True, parents=True)

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Variável global para o agente
agente = None
arquivos_carregados = {
    "cabecalho": False,
    "itens": False,
    "cfop": False
}

# ============================================================================
# ROTAS DE PÁGINAS HTML
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def pagina_inicial():
    """Página inicial - Upload de arquivos"""
    html_path = TEMPLATES_DIR / "index.html"
    if html_path.exists():
        return FileResponse(html_path)
    return HTMLResponse(content="<h1>Página inicial não encontrada</h1>")

@app.get("/estatisticas", response_class=HTMLResponse)
async def pagina_estatisticas():
    """Página de estatísticas"""
    html_path = TEMPLATES_DIR / "estatisticas.html"
    if html_path.exists():
        return FileResponse(html_path)
    return HTMLResponse(content="<h1>Página de estatísticas não encontrada</h1>")

@app.get("/chat", response_class=HTMLResponse)
async def pagina_chat():
    """Página de chat"""
    html_path = TEMPLATES_DIR / "chat.html"
    if html_path.exists():
        return FileResponse(html_path)
    return HTMLResponse(content="<h1>Página de chat não encontrada</h1>")

@app.get("/validacao", response_class=HTMLResponse)
async def pagina_validacao():
    """Página de validação"""
    html_path = TEMPLATES_DIR / "validacao.html"
    if html_path.exists():
        return FileResponse(html_path)
    return HTMLResponse(content="<h1>Página de validação não encontrada</h1>")

# ============================================================================
# ROTAS DE API
# ============================================================================

@app.get("/api/health", response_model=HealthCheck)
async def health_check():
    """Health check do sistema"""
    status = "healthy" if agente is not None else "initializing"
    mensagem = "Sistema operacional" if agente is not None else "Sistema inicializando..."
    
    return HealthCheck(
        status=status,
        mensagem=mensagem
    )

@app.get("/api/status-arquivos")
async def status_arquivos():
    """Retorna status dos arquivos carregados"""
    return {
        "arquivos": arquivos_carregados,
        "todos_carregados": all(arquivos_carregados.values()),
        "agente_inicializado": agente is not None
    }

@app.post("/api/upload-csv")
async def upload_csv(
    tipo: str,
    arquivo: UploadFile = File(...)
):
    """
    Upload de arquivo CSV
    tipo: 'cabecalho', 'itens' ou 'cfop'
    """
    global arquivos_carregados
    
    tipos_validos = {
        "cabecalho": "202401_NFs_Cabecalho.csv",
        "itens": "202401_NFs_Itens.csv",
        "cfop": "CFOP.csv"
    }
    
    if tipo not in tipos_validos:
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo inválido. Use: {', '.join(tipos_validos.keys())}"
        )
    
    # Verificar se é arquivo CSV
    if not arquivo.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Apenas arquivos CSV são permitidos"
        )
    
    try:
        # Salvar arquivo
        file_path = DATA_DIR / tipos_validos[tipo]
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(arquivo.file, buffer)
        
        # Marcar como carregado
        arquivos_carregados[tipo] = True
        
        return {
            "status": "success",
            "mensagem": f"Arquivo {tipo} carregado com sucesso",
            "arquivo": tipos_validos[tipo],
            "path": str(file_path)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar arquivo: {str(e)}"
        )

@app.post("/api/inicializar")
async def inicializar_sistema():
    """
    Inicializa o agente CFOP com os arquivos CSV carregados
    """
    global agente, arquivos_carregados
    
    # Verificar se todos os arquivos foram carregados
    if not all(arquivos_carregados.values()):
        arquivos_faltando = [k for k, v in arquivos_carregados.items() if not v]
        raise HTTPException(
            status_code=400,
            detail=f"Arquivos não carregados: {', '.join(arquivos_faltando)}"
        )
    
    try:
        print("\n🚀 Inicializando sistema...")
        
        agente = AgenteValidadorCFOP(
            cabecalho_path=settings.cabecalho_csv,
            itens_path=settings.itens_csv,
            cfop_path=settings.cfop_csv
        )
        
        return {
            "status": "success",
            "mensagem": "Sistema inicializado com sucesso!",
            "total_notas": len(agente.df_cabecalho),
            "total_itens": len(agente.df_itens),
            "total_cfops": len(agente.df_cfop)
        }
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao inicializar: {str(e)}"
        )

@app.post("/api/resetar")
async def resetar_sistema():
    """Reseta o sistema para novo upload de arquivos"""
    global agente, arquivos_carregados
    
    agente = None
    arquivos_carregados = {
        "cabecalho": False,
        "itens": False,
        "cfop": False
    }
    
    # Limpar arquivos
    for arquivo in DATA_DIR.glob("*.csv"):
        try:
            arquivo.unlink()
        except:
            pass
    
    return {
        "status": "success",
        "mensagem": "Sistema resetado com sucesso"
    }

# ============================================================================
# INCLUIR ROTAS DA API
# ============================================================================

app.include_router(chat_router, prefix="/api")
app.include_router(estatisticas_router, prefix="/api")
app.include_router(validacao_router, prefix="/api")

# ============================================================================
# EXECUÇÃO LOCAL (DESENVOLVIMENTO)
# ============================================================================

def iniciar_ngrok():
    """Inicia ngrok se estiver no Colab"""
    if not IS_COLAB:
        return None
    
    try:
        from pyngrok import ngrok
        import nest_asyncio
        
        # Permitir nested event loops no Colab
        nest_asyncio.apply()
        
        # Verificar se authtoken está configurado
        authtoken = settings.ngrok_auth_token
        if authtoken:
            ngrok.set_auth_token(authtoken)
        
        # Configurar ngrok
        ngrok_tunnel = ngrok.connect(8000)
        public_url = ngrok_tunnel.public_url
        
        print("\n" + "="*70)
        print("🌐 NGROK TUNNEL ATIVO")
        print("="*70)
        print(f"📡 URL Pública: {public_url}")
        print(f"🔗 Acesse: {public_url}")
        print("="*70 + "\n")
        
        return public_url
        
    except Exception as e:
        error_msg = str(e)
        
        # Verificar se é erro de autenticação
        if "authentication failed" in error_msg or "authtoken" in error_msg:
            print("\n" + "="*70)
            print("🔑 NGROK REQUER AUTENTICAÇÃO")
            print("="*70)
            print("\n⚠️ O ngrok agora requer uma conta gratuita e authtoken.")
            print("\n📋 PASSOS PARA CONFIGURAR:")
            print("   1. Crie conta gratuita: https://dashboard.ngrok.com/signup")
            print("   2. Copie seu authtoken: https://dashboard.ngrok.com/get-started/your-authtoken")
            print("   3. No Colab, adicione ANTES de iniciar o servidor:")
            print("\n      import os")
            print("      os.environ['NGROK_AUTHTOKEN'] = 'seu-token-aqui'")
            print("\n   4. Execute novamente")
            print("\n💡 Ou configure diretamente no código:")
            print("      from pyngrok import ngrok")
            print("      ngrok.set_auth_token('seu-token-aqui')")
            print("="*70 + "\n")
        else:
            print(f"\n⚠️ Erro ao iniciar ngrok: {error_msg}")
            print("💡 Certifique-se de que pyngrok está instalado: pip install pyngrok\n")
        
        return None

if __name__ == "__main__":
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║          {settings.app_name}           ║
    ║                     v{settings.app_version}                          ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Iniciar ngrok se estiver no Colab
    public_url = iniciar_ngrok()
    
    if IS_COLAB:
        print("\n🚀 Rodando no Google Colab")
        if public_url:
            print(f"🌐 Acesse a aplicação em: {public_url}")
        print("\n")
    else:
        print("\n🚀 Rodando localmente")
        print("🌐 Acesse: http://localhost:8000\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False if IS_COLAB else True,
        log_level="info"
    )
