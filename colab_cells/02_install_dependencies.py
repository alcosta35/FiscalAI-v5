# ==========================================
# CELL 2: Install Dependencies
# ==========================================

print("📦 Instalando dependências do FiscalAI v5.0...")
print("   Isso pode levar 2-3 minutos...\n")

# IMPORTANTE: Remover pinecone-client antigo se existir
print("🔧 Verificando e removendo pacote antigo 'pinecone-client'...")
try:
    !pip uninstall -y pinecone-client 2>/dev/null
    print("   ✅ Pacote antigo removido (se existia)")
except:
    print("   ✅ Sem pacote antigo para remover")

print("\n📥 Instalando dependências...")

try:
    !pip install -q -r requirements.txt
    print("✅ Todas as dependências instaladas com sucesso!")
    
    # Verificar instalações críticas
    import pinecone
    import openai
    import langchain
    print("\n✅ Verificação:")
    print(f"   • Pinecone: {pinecone.__version__}")
    print(f"   • OpenAI: {openai.__version__}")
    print(f"   • LangChain: {langchain.__version__}")
    
except Exception as e:
    print(f"⚠️ Alguns pacotes tiveram conflitos: {e}")
    print("   Tentando instalação individual...")
    
    # Remover pinecone-client explicitamente
    !pip uninstall -y pinecone-client 2>/dev/null
    
    packages = [
        "fastapi", "uvicorn", "pydantic", "pydantic-settings",
        "python-dotenv", "openai", "langchain", "langchain-openai",
        "langchain-community", "pandas", "openpyxl",
        "pyngrok", "nest-asyncio"
    ]
    
    for pkg in packages:
        !pip install -q {pkg}
    
    # Instalar pinecone por último (versão correta)
    print("\n📌 Instalando Pinecone (pacote oficial)...")
    !pip install -q pinecone
    
    print("✅ Instalação manual concluída!")

# Verificar versão final do Pinecone
print("\n🔍 Verificando Pinecone...")
import pinecone
print(f"✅ Pinecone instalado: versão {pinecone.__version__}")
print(f"   Pacote correto: 'pinecone' (não 'pinecone-client')")

print("\n🎉 Setup completo!")
