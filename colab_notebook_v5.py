# ==========================================
# FISCALAI v5 - COLAB NOTEBOOK
# Validação Semântica de CFOP com Pinecone
# ==========================================

# ==========================================
# CELL 1: Clone Repository
# ==========================================
!git clone https://github.com/alcosta35/FiscalAI-v5

# ==========================================
# CELL 2: Install Dependencies
# ==========================================
print("\n📦 Installing dependencies for FiscalAI v5...")
try:
    !pip install -q -r /content/FiscalAI-v5/requirements.txt
    print("✅ All dependencies installed!")
except Exception as e:
    print(f"⚠️ Some packages had conflicts, trying individual install...")
    # Install critical packages individually
    !pip install -q fastapi uvicorn pydantic pydantic-settings python-dotenv
    !pip install -q openai>=1.0.0 langchain langchain-openai langchain-community
    !pip install -q pinecone-client>=3.0.0
    !pip install -q pandas openpyxl numpy
    !pip install -q pyngrok nest-asyncio python-multipart
    print("✅ Dependencies installed!")

print("\n✅ Setup complete!")

# ==========================================
# CELL 3: Configure API Keys (OpenAI, Ngrok, Pinecone)
# ==========================================
from google.colab import userdata
import os

print("🔑 Configuring API Keys for FiscalAI v5")
print("=" * 60)

os.chdir('/content/FiscalAI-v5')

# Get API keys from Colab Secrets
try:
    openai_key = userdata.get('OPENAI_API_KEY')
    ngrok_token = userdata.get('NGROK_AUTH_TOKEN')
    pinecone_key = userdata.get('PINECONE_API_KEY')
    
    # Write all keys to .env file
    with open('.env', 'w') as f:
        f.write(f'OPENAI_API_KEY={openai_key}\n')
        f.write(f'NGROK_AUTH_TOKEN={ngrok_token}\n')
        f.write(f'PINECONE_API_KEY={pinecone_key}\n')
    
    # Show masked keys
    openai_masked = openai_key[:10] + "..." + openai_key[-4:]
    ngrok_masked = ngrok_token[:10] + "..." + ngrok_token[-4:]
    pinecone_masked = pinecone_key[:10] + "..." + pinecone_key[-4:]
    
    print(f"✅ OpenAI API Key: {openai_masked}")
    print(f"✅ Ngrok Auth Token: {ngrok_masked}")
    print(f"✅ Pinecone API Key: {pinecone_masked}")
    print("✅ Configuration complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n⚠️  Please add secrets to Colab:")
    print("   1. Click 🔑 icon on left sidebar")
    print("   2. Add THREE secrets:")
    print("      - Name: OPENAI_API_KEY")
    print("        Value: sk-...")
    print("      - Name: NGROK_AUTH_TOKEN")
    print("        Value: 2...")
    print("      - Name: PINECONE_API_KEY")
    print("        Value: (your pinecone key)")
    print("   3. Enable 'Notebook access' for all")
    print("   4. Rerun this cell")

# ==========================================
# CELL 4: Upload CFOP.csv and Setup Pinecone (ONE TIME ONLY)
# ==========================================
from google.colab import files
import os

print("=" * 70)
print("📤 SETUP INICIAL - PINECONE VECTOR STORE")
print("=" * 70)
print("\n⚠️  ATENÇÃO: Execute esta célula APENAS UMA VEZ!")
print("   Ela irá:")
print("   1. Fazer upload do CFOP.csv")
print("   2. Gerar embeddings de todos os CFOPs")
print("   3. Criar índice no Pinecone")
print("   4. Popular o Vector Store")
print("\n   Tempo estimado: 5-10 minutos")
print("\n" + "=" * 70)

resposta = input("\n🤔 Deseja continuar? (sim/não): ").lower()

if resposta in ['sim', 's', 'yes', 'y']:
    print("\n📂 Faça upload do arquivo CFOP.csv:")
    uploaded = files.upload()
    
    if 'CFOP.csv' in uploaded or any('cfop' in f.lower() for f in uploaded.keys()):
        # Encontrar o arquivo
        cfop_file = [f for f in uploaded.keys() if 'cfop' in f.lower()][0]
        
        # Mover para data/
        !mkdir -p /content/FiscalAI-v5/data
        !cp {cfop_file} /content/FiscalAI-v5/data/CFOP.csv
        
        print(f"\n✅ Arquivo carregado: {cfop_file}")
        
        # Executar setup do Pinecone
        print("\n🚀 Iniciando setup do Pinecone...")
        print("   (Isso pode levar alguns minutos...)\n")
        
        os.chdir('/content/FiscalAI-v5')
        !python pinecone_setup.py /content/FiscalAI-v5/data/CFOP.csv
        
        print("\n" + "=" * 70)
        print("✅ SETUP CONCLUÍDO!")
        print("=" * 70)
        print("\n💡 Agora você pode:")
        print("   1. Executar a célula 5 para iniciar o servidor")
        print("   2. Fazer upload dos CSVs de NFs")
        print("   3. Usar a validação semântica!")
    else:
        print("❌ Arquivo CFOP.csv não encontrado no upload")
else:
    print("\n⏭️  Setup cancelado. Você pode executar esta célula mais tarde.")

# ==========================================
# CELL 5: Start Server
# ==========================================
import os
os.chdir('/content/FiscalAI-v5')

!mkdir -p data
!python main.py

# ==========================================
# CELL 6 (OPTIONAL): Test Semantic Validation
# ==========================================
import requests
import json

# Assumindo que o servidor está rodando
BASE_URL = "http://localhost:8000"

print("🧪 Testando Validação Semântica")
print("=" * 60)

# 1. Inicializar validador
print("\n1️⃣ Inicializando validador semântico...")
response = requests.post(f"{BASE_URL}/api/validacao-semantica/inicializar")
print(f"   Status: {response.json()}")

# 2. Validar item individual
print("\n2️⃣ Validando item individual...")
item_teste = {
    "uf_emitente": "SP",
    "uf_destinatario": "RJ",
    "descricao_produto": "Notebook Dell Inspiron para revenda",
    "ncm": "84713012",
    "consumidor_final": "0",
    "indicador_ie": "1",
    "cfop_informado": "6102"
}

response = requests.post(
    f"{BASE_URL}/api/validacao-semantica/validar-item",
    json=item_teste
)

resultado = response.json()
print(f"\n   Status: {resultado['status']}")
print(f"   Mensagem: {resultado['mensagem']}")
print(f"\n   Top 3 Sugestões:")
for i, sug in enumerate(resultado['sugestoes'][:3], 1):
    print(f"   {i}. CFOP {sug['cfop']} - Score: {sug['score']}")
    print(f"      {sug['descricao'][:100]}...")

print("\n✅ Teste concluído!")

# ==========================================
# CELL 7 (OPTIONAL): Busca Livre por Contexto
# ==========================================
import requests

BASE_URL = "http://localhost:8000"

# Buscar CFOP por descrição livre
query = "venda de produto importado para consumidor final em outro estado"

print(f"🔍 Buscando CFOPs para: '{query}'")
print("=" * 60)

response = requests.get(
    f"{BASE_URL}/api/validacao-semantica/buscar-cfop",
    params={"query": query, "top_k": 5}
)

resultado = response.json()

print(f"\n📊 {resultado['total_resultados']} resultados encontrados:\n")

for i, cfop in enumerate(resultado['cfops'], 1):
    print(f"{i}. CFOP {cfop['cfop']} - Score: {cfop['score']} ({cfop['confianca']})")
    print(f"   {cfop['descricao']}")
    print()
