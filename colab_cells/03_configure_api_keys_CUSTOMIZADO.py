# ==========================================
# CÉLULA 3: Configure API Keys + Pinecone
# ==========================================

from google.colab import userdata
import os

print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║         🔑 CONFIGURANDO FISCALAI v5.0 + PINECONE              ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
""")

# ============================================
# 1. OBTER API KEYS DOS SECRETS
# ============================================
print("📥 Carregando API Keys dos Secrets...")

try:
    openai_key = userdata.get('OPENAI_API_KEY')
    pinecone_key = userdata.get('PINECONE_API_KEY')
    ngrok_token = userdata.get('NGROK_AUTH_TOKEN')
    
    print(f"✅ OpenAI Key: {openai_key[:10]}...{openai_key[-4:]}")
    print(f"✅ Pinecone Key: {pinecone_key[:10]}...{pinecone_key[-4:]}")
    print(f"✅ Ngrok Token: {ngrok_token[:10]}...{ngrok_token[-4:]}")
    
except Exception as e:
    print(f"❌ Erro ao carregar Secrets: {e}")
    print("\n⚠️  AÇÃO NECESSÁRIA:")
    print("   1. Clique no ícone 🔑 (Secrets) na barra lateral")
    print("   2. Adicione os 3 secrets:")
    print("      • OPENAI_API_KEY")
    print("      • PINECONE_API_KEY")
    print("      • NGROK_AUTH_TOKEN")
    print("   3. Ative 'Notebook access' para cada um")
    print("   4. Execute esta célula novamente")
    raise

# ============================================
# 2. CONFIGURAR PINECONE
# ============================================
print("\n⚙️ Configurando Pinecone...")

# SUAS CONFIGURAÇÕES ⬇️⬇️⬇️
PINECONE_INDEX_NAME = "cfop-fiscal"
PINECONE_NAMESPACE = "default"
PINECONE_HOST = "https://cfop-fiscal-x8q6et6.svc.aped-4627-b74a.pinecone.io"
PINECONE_DIMENSION = 1536
PINECONE_METRIC = "cosine"

print(f"   • Índice: {PINECONE_INDEX_NAME}")
print(f"   • Namespace: {PINECONE_NAMESPACE}")
print(f"   • Host: {PINECONE_HOST}")
print(f"   • Dimensão: {PINECONE_DIMENSION}")
print(f"   • Métrica: {PINECONE_METRIC}")

# ============================================
# 3. CRIAR ARQUIVO .env
# ============================================
print("\n📝 Criando arquivo .env...")

with open('.env', 'w') as f:
    # API Keys
    f.write(f'OPENAI_API_KEY={openai_key}\n')
    f.write(f'PINECONE_API_KEY={pinecone_key}\n')
    f.write(f'NGROK_AUTH_TOKEN={ngrok_token}\n')
    f.write('\n')
    
    # Pinecone Configuration
    f.write(f'PINECONE_INDEX_NAME={PINECONE_INDEX_NAME}\n')
    f.write(f'PINECONE_NAMESPACE={PINECONE_NAMESPACE}\n')
    f.write(f'PINECONE_HOST={PINECONE_HOST}\n')
    f.write(f'PINECONE_DIMENSION={PINECONE_DIMENSION}\n')
    f.write(f'PINECONE_METRIC={PINECONE_METRIC}\n')
    f.write('\n')
    
    # OpenAI Embedding Model
    f.write('OPENAI_EMBEDDING_MODEL=text-embedding-3-small\n')

print("✅ Arquivo .env criado com sucesso!")

# ============================================
# 4. VERIFICAR CONFIGURAÇÃO
# ============================================
print("\n🔍 Verificando configuração...")

# Carregar .env para verificar
from dotenv import load_dotenv
load_dotenv()

print("\n📊 CONFIGURAÇÕES FINAIS:")
print("="*70)
print(f"OpenAI Key: {os.getenv('OPENAI_API_KEY')[:10]}...{os.getenv('OPENAI_API_KEY')[-4:]}")
print(f"Pinecone Key: {os.getenv('PINECONE_API_KEY')[:10]}...{os.getenv('PINECONE_API_KEY')[-4:]}")
print(f"Pinecone Index: {os.getenv('PINECONE_INDEX_NAME')}")
print(f"Pinecone Namespace: {os.getenv('PINECONE_NAMESPACE')}")
print(f"Pinecone Host: {os.getenv('PINECONE_HOST')}")
print(f"Pinecone Dimension: {os.getenv('PINECONE_DIMENSION')}")
print("="*70)

print("""
✅ CONFIGURAÇÃO COMPLETA!

📋 PRÓXIMOS PASSOS:
   1. Execute a Célula 4 para popular o Pinecone (apenas 1x)
   2. Execute a Célula 5 para iniciar o servidor
""")
