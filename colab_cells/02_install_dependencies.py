# ==========================================
# CELL 2: Install Dependencies
# ==========================================

print("📦 Instalando dependências do FiscalAI v5.0...")
print("   Isso pode levar 2-3 minutos...\n")

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
    
    packages = [
        "fastapi", "uvicorn", "pydantic", "pydantic-settings",
        "python-dotenv", "openai", "langchain", "langchain-openai",
        "langchain-community", "pandas", "openpyxl",
        "pyngrok", "nest-asyncio", "pinecone-client"
    ]
    
    for pkg in packages:
        !pip install -q {pkg}
    
    print("✅ Instalação manual concluída!")

print("\n🎉 Setup completo!")
