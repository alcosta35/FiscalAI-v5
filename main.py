"""
FiscalAI v5.0 - Main Application
Servidor FastAPI com interface web para validação de CFOPs
"""
import os
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pandas as pd
from typing import List, Optional
import shutil
from datetime import datetime

from config import settings, IS_COLAB, DATA_DIR
from services.semantic_search_service import CFOPSemanticSearchService
from agente_cfop_v5 import AgenteValidadorCFOP_V5

# Inicializar FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema de validação inteligente de CFOPs usando IA"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Diretórios
TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

# Criar diretórios se não existirem
TEMPLATES_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True, parents=True)

# Static files e templates
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Variáveis globais
agente = None
uploaded_files = {
    "cabecalho": None,
    "itens": None,
    "cfop": None
}

# ============================================
# Inicialização
# ============================================

@app.on_event("startup")
async def startup_event():
    """Inicializar serviços na startup"""
    global agente
    
    print("\n" + "="*70)
    print(f"🚀 INICIANDO {settings.app_name}")
    print("="*70)
    
    try:
        # Verificar se Pinecone está configurado
        if not os.getenv("PINECONE_API_KEY"):
            print("⚠️  Pinecone não configurado. Busca semântica desabilitada.")
            settings.use_semantic_search = False
        
        # Inicializar agente se arquivos existirem
        if all([
            (DATA_DIR / "202401_NFs_Cabecalho.csv").exists(),
            (DATA_DIR / "202401_NFs_Itens.csv").exists(),
            (DATA_DIR / "CFOP.csv").exists()
        ]):
            print("📊 Arquivos CSV encontrados. Inicializando agente...")
            agente = AgenteValidadorCFOP_V5()
            print("✅ Agente inicializado!")
        else:
            print("⚠️  Arquivos CSV não encontrados. Faça upload pela interface.")
        
    except Exception as e:
        print(f"⚠️  Erro na inicialização: {e}")
        print("   O sistema continuará sem o agente. Faça upload dos arquivos.")
    
    print("="*70)
    print("✅ Servidor pronto!")
    print("="*70 + "\n")

# ============================================
# Rotas - Interface Web
# ============================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página principal"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "version": settings.app_version,
            "arquivos_carregados": all(uploaded_files.values()),
            "agente_inicializado": agente is not None
        }
    )

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "agente_inicializado": agente is not None,
        "arquivos_carregados": {
            "cabecalho": uploaded_files["cabecalho"] is not None,
            "itens": uploaded_files["itens"] is not None,
            "cfop": uploaded_files["cfop"] is not None
        }
    }

@app.get("/api/chat/status")
async def chat_status():
    """Status simples para o frontend do chat"""
    return {
        "inicializado": agente is not None,
        "agente_inicializado": agente is not None,  # compatibilidade
        "agente_ativo": agente is not None,  # compatibilidade v5
        "ready": agente is not None
    }

# ============================================
# Rotas - Upload de Arquivos
# ============================================

@app.post("/api/upload/cabecalho")
async def upload_cabecalho(file: UploadFile = File(...)):
    """Upload do arquivo de cabeçalhos"""
    try:
        file_path = DATA_DIR / "202401_NFs_Cabecalho.csv"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Validar CSV
        df = pd.read_csv(file_path)
        uploaded_files["cabecalho"] = {
            "filename": file.filename,
            "rows": len(df),
            "uploaded_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "message": f"Arquivo carregado: {len(df)} notas fiscais",
            "rows": len(df)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar arquivo: {str(e)}")

@app.post("/api/upload/itens")
async def upload_itens(file: UploadFile = File(...)):
    """Upload do arquivo de itens"""
    try:
        file_path = DATA_DIR / "202401_NFs_Itens.csv"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Validar CSV
        df = pd.read_csv(file_path)
        uploaded_files["itens"] = {
            "filename": file.filename,
            "rows": len(df),
            "uploaded_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "message": f"Arquivo carregado: {len(df)} itens",
            "rows": len(df)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar arquivo: {str(e)}")

@app.post("/api/upload/cfop")
async def upload_cfop(file: UploadFile = File(...)):
    """Upload do arquivo de CFOPs"""
    try:
        file_path = DATA_DIR / "CFOP.csv"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Validar CSV
        df = pd.read_csv(file_path)
        uploaded_files["cfop"] = {
            "filename": file.filename,
            "rows": len(df),
            "uploaded_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "message": f"Arquivo carregado: {len(df)} CFOPs",
            "rows": len(df)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar arquivo: {str(e)}")

@app.post("/api/inicializar")
async def inicializar_agente():
    """Inicializar o agente após upload dos arquivos"""
    global agente
    
    try:
        # Verificar se todos os arquivos foram enviados
        if not all(uploaded_files.values()):
            faltando = [k for k, v in uploaded_files.items() if not v]
            raise HTTPException(
                status_code=400,
                detail=f"Arquivos faltando: {', '.join(faltando)}"
            )
        
        # Inicializar agente
        print("🔄 Inicializando agente...")
        agente = AgenteValidadorCFOP_V5()
        
        return {
            "success": True,
            "message": "Agente inicializado com sucesso!",
            "arquivos": uploaded_files
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao inicializar agente: {str(e)}")

# ============================================
# Rotas - Chat e Validação
# ============================================

@app.post("/api/chat")
async def chat(request: Request):
    """Endpoint do chat"""
    try:
        data = await request.json()
        mensagem = data.get("mensagem", "")
        
        if not agente:
            return JSONResponse({
                "success": False,
                "error": "Agente não inicializado. Faça upload dos arquivos primeiro."
            }, status_code=400)
        
        # Processar mensagem
        resposta = agente.processar_mensagem(mensagem)
        
        return {
            "success": True,
            "resposta": resposta
        }
        
    except Exception as e:
        print(f"\n❌ ERRO no chat:")
        print(f"   Mensagem: {mensagem if 'mensagem' in locals() else 'N/A'}")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.get("/api/estatisticas")
async def estatisticas():
    """Retornar estatísticas das notas fiscais"""
    if not agente:
        raise HTTPException(status_code=400, detail="Agente não inicializado")
    
    try:
        stats = agente.obter_estatisticas()
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/validar_cfop")
async def validar_cfop(request: Request):
    """Validar um CFOP específico"""
    if not agente:
        raise HTTPException(status_code=400, detail="Agente não inicializado")
    
    try:
        data = await request.json()
        chave_nf = data.get("chave_nf")
        numero_item = data.get("numero_item")
        
        if not chave_nf or not numero_item:
            raise HTTPException(status_code=400, detail="chave_nf e numero_item são obrigatórios")
        
        resultado = agente.validar_item(chave_nf, numero_item)
        
        return {"success": True, "resultado": resultado}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cfops_populares")
async def cfops_populares():
    """Retornar CFOPs mais utilizados"""
    if not agente:
        raise HTTPException(status_code=400, detail="Agente não inicializado")
    
    try:
        cfops = agente.obter_cfops_populares(top_n=10)
        return {"success": True, "data": cfops}
    except Exception as e:
        print(f"\n❌ ERRO em cfops_populares:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# Função principal
# ============================================

def main():
    """Iniciar servidor"""
    print(f"""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║              🚀 FISCALAI v5.0 - SERVIDOR                       ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Configurar host e porta
    host = settings.host
    port = settings.port
    
    # No Colab, usar ngrok
    if IS_COLAB:
        print("📱 Executando no Google Colab")
        print("🔗 Configurando ngrok...\n")
        
        try:
            from pyngrok import ngrok
            import nest_asyncio
            
            nest_asyncio.apply()
            
            # Configurar ngrok
            ngrok_token = os.getenv("NGROK_AUTH_TOKEN")
            if ngrok_token:
                ngrok.set_auth_token(ngrok_token)
                public_url = ngrok.connect(port)
                print(f"\n🌐 URL PÚBLICA: {public_url}")
                print(f"📱 Acesse sua aplicação em: {public_url}\n")
            else:
                print("⚠️  NGROK_AUTH_TOKEN não encontrado")
                print("   A aplicação rodará apenas localmente\n")
                
        except Exception as e:
            print(f"⚠️  Erro ao configurar ngrok: {e}")
            print("   A aplicação rodará apenas localmente\n")
    
    # Iniciar servidor
    print(f"🚀 Iniciando servidor em http://{host}:{port}")
    print("="*70 + "\n")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()
