# ==============================================================================
# CÉLULA 1: CONFIGURAR API KEYS
# ==============================================================================
from google.colab import userdata
import os

print("🔑 Configurando API Keys para FiscalAI V5")
print("="*70)

os.chdir('/content/FiscalAI-v5')

try:
    # Obter API keys dos secrets do Colab
    openai_key = userdata.get('OPENAI_API_KEY')
    pinecone_key = userdata.get('PINECONE_API_KEY')
    ngrok_token = userdata.get('NGROK_AUTH_TOKEN')
    
    # Criar arquivo .env
    with open('.env', 'w') as f:
        f.write(f'OPENAI_API_KEY={openai_key}\n')
        f.write(f'PINECONE_API_KEY={pinecone_key}\n')
        f.write(f'NGROK_AUTH_TOKEN={ngrok_token}\n')
    
    # Mostrar keys mascaradas
    openai_masked = openai_key[:8] + "..." + openai_key[-4:]
    pinecone_masked = pinecone_key[:8] + "..." + pinecone_key[-4:]
    ngrok_masked = ngrok_token[:8] + "..." + ngrok_token[-4:]
    
    print(f"✅ OpenAI API Key: {openai_masked}")
    print(f"✅ Pinecone API Key: {pinecone_masked}")
    print(f"✅ Ngrok Auth Token: {ngrok_masked}")
    print("\n✅ Configuração completa!")
    
    print("\n📝 Próximo passo:")
    print("   1. Use o botão 📁 (arquivos) na barra lateral")
    print("   2. Faça upload do CFOP.csv para a pasta 'data/'")
    print("   3. Execute a CÉLULA 2 para setup do Pinecone")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    print("\n⚠️  Configure os secrets no Colab:")
    print("   1. Clique no ícone 🔑 na barra lateral esquerda")
    print("   2. Adicione TRÊS secrets:")
    print("\n      Nome: OPENAI_API_KEY")
    print("      Valor: sk-... (seu OpenAI key)")
    print("\n      Nome: PINECONE_API_KEY")
    print("      Valor: p... (seu Pinecone key)")
    print("\n      Nome: NGROK_AUTH_TOKEN")
    print("      Valor: 2... (seu ngrok token)")
    print("\n   3. Ative 'Notebook access' para cada um")
    print("   4. Execute esta célula novamente")
    
    print("\n📚 Onde obter as API keys:")
    print("   • OpenAI: https://platform.openai.com/api-keys")
    print("   • Pinecone: https://app.pinecone.io/ → API Keys")
    print("   • Ngrok: https://dashboard.ngrok.com/get-started/your-authtoken")
