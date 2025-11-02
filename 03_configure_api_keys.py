# ==========================================
# CELL 3: Configure API Keys
# ==========================================

from google.colab import userdata
import os

print("🔑 Configurando API Keys para FiscalAI v5.0")
print("="*70)

# IMPORTANTE: Adicione seus secrets no Colab primeiro!
# 1. Clique no ícone 🔑 na barra lateral esquerda
# 2. Adicione 3 secrets:
#    - OPENAI_API_KEY (começa com sk-)
#    - PINECONE_API_KEY (da dashboard Pinecone)
#    - NGROK_AUTH_TOKEN (da dashboard Ngrok)
# 3. Ative "Notebook access" para cada secret

try:
    # Obter secrets do Colab
    openai_key = userdata.get('OPENAI_API_KEY')
    pinecone_key = userdata.get('PINECONE_API_KEY')
    ngrok_token = userdata.get('NGROK_AUTH_TOKEN')
    
    # Validar formato
    if not openai_key.startswith('sk-'):
        raise ValueError("OpenAI key inválida (deve começar com 'sk-')")
    
    # Criar arquivo .env
    with open('.env', 'w') as f:
        f.write(f'OPENAI_API_KEY={openai_key}\n')
        f.write(f'PINECONE_API_KEY={pinecone_key}\n')
        f.write(f'NGROK_AUTH_TOKEN={ngrok_token}\n')
    
    # Mostrar keys mascaradas
    def mask_key(key):
        if len(key) > 15:
            return key[:10] + "..." + key[-4:]
        return "***"
    
    print("✅ Configuração completa!\n")
    print(f"   • OpenAI Key: {mask_key(openai_key)}")
    print(f"   • Pinecone Key: {mask_key(pinecone_key)}")
    print(f"   • Ngrok Token: {mask_key(ngrok_token)}")
    print("\n💾 Arquivo .env criado com sucesso!")
    
except Exception as e:
    print(f"❌ Erro ao configurar: {e}\n")
    print("⚠️  AÇÃO NECESSÁRIA:")
    print("="*70)
    print("1. Clique no ícone 🔑 (Secrets) na barra lateral esquerda")
    print("2. Adicione 3 secrets:")
    print("\n   Secret 1:")
    print("   • Name: OPENAI_API_KEY")
    print("   • Value: sk-proj-...")
    print("   • Notebook access: ✅ ATIVADO")
    print("\n   Secret 2:")
    print("   • Name: PINECONE_API_KEY")
    print("   • Value: (sua key do pinecone.io)")
    print("   • Notebook access: ✅ ATIVADO")
    print("\n   Secret 3:")
    print("   • Name: NGROK_AUTH_TOKEN")
    print("   • Value: (token do ngrok.com)")
    print("   • Notebook access: ✅ ATIVADO")
    print("\n3. Execute esta célula novamente")
    print("="*70)

print("\n📋 PRÓXIMO PASSO:")
print("   Execute a célula 4 para popular o índice Pinecone")
print("   (necessário apenas na primeira vez)")
