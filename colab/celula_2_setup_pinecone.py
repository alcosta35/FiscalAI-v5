# ==============================================================================
# CÉLULA 2: SETUP PINECONE (EXECUTAR APENAS UMA VEZ!)
# ==============================================================================
import os

print("🚀 Setup do Pinecone Vector Store")
print("="*70)

os.chdir('/content/FiscalAI-v5')

# Verificar se diretório data existe
if not os.path.exists('data'):
    print("📁 Criando diretório data/")
    os.makedirs('data')

# Verificar se CFOP.csv existe
cfop_path = 'data/CFOP.csv'
if not os.path.exists(cfop_path):
    print(f"\n❌ Arquivo {cfop_path} não encontrado!")
    print("\n📝 Para continuar:")
    print("   1. Clique no ícone 📁 (arquivos) na barra lateral")
    print("   2. Navegue até a pasta 'data/'")
    print("   3. Clique no botão de upload")
    print("   4. Selecione o arquivo CFOP.csv")
    print("   5. Execute esta célula novamente")
else:
    print(f"✅ Arquivo encontrado: {cfop_path}")
    
    # Executar setup do Pinecone
    print("\n🔄 Iniciando setup do Pinecone...")
    print("⏳ Este processo pode levar 5-10 minutos...")
    print("\n" + "="*70)
    
    !python pinecone_setup.py data/CFOP.csv
    
    print("\n" + "="*70)
    print("✅ Setup do Pinecone concluído!")
    print("\n📝 Próximo passo:")
    print("   • Execute a CÉLULA 3 para iniciar o servidor")
    print("\n💡 Dica: Este setup precisa ser executado apenas UMA VEZ!")
    print("   O índice fica salvo no Pinecone e pode ser reutilizado.")
