# ==========================================
# CELL 4: Populate Pinecone (PRIMEIRA VEZ)
# ==========================================

print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║         📊 POPULAR ÍNDICE PINECONE COM CFOPs                  ║
║                  (Execute apenas 1x)                           ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
""")

print("⚠️  IMPORTANTE:")
print("   Esta célula precisa ser executada apenas UMA VEZ")
print("   ou quando você atualizar o arquivo CFOP.csv\n")

resposta = input("Deseja popular o índice Pinecone? (s/n): ")

if resposta.lower() != 's':
    print("❌ Operação cancelada.")
    print("   Se já populou antes, pode pular para a célula 5")
else:
    print("\n📂 Preparando ambiente...")
    
    # Criar diretório data
    !mkdir -p data
    
    # Verificar se arquivo CFOP.csv existe
    import os
    cfop_path = "data/CFOP.csv"
    
    if not os.path.exists(cfop_path):
        print(f"\n⚠️ Arquivo CFOP.csv não encontrado em: {cfop_path}")
        print("\n📤 AÇÃO NECESSÁRIA:")
        print("   1. Faça upload do arquivo CFOP.csv")
        print("   2. Coloque-o na pasta 'data/'")
        print("   3. Execute esta célula novamente")
        
        from google.colab import files
        print("\n📥 Fazendo upload do arquivo CFOP.csv...")
        uploaded = files.upload()
        
        if 'CFOP.csv' in uploaded:
            !mv CFOP.csv data/
            print("✅ Arquivo movido para data/CFOP.csv")
        else:
            print("❌ Arquivo CFOP.csv não foi enviado. Abortando.")
            import sys
            sys.exit(1)
    
    print("\n🔄 Iniciando indexação...")
    print("   Isso pode levar 2-5 minutos dependendo do tamanho do CSV\n")
    
    !python scripts/populate_pinecone.py
    
    print("\n" + "="*70)
    print("🎉 PRONTO! Índice Pinecone populado com sucesso!")
    print("="*70)
    print("\n📋 PRÓXIMO PASSO:")
    print("   Execute a célula 5 para iniciar o servidor")
