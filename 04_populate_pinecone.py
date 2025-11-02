# ==========================================
# CÉLULA 4: Popular Pinecone (Opcional)
# ==========================================

print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║         📊 POPULAR ÍNDICE PINECONE COM CFOPs                  ║
║                  (Apenas se já tiver CFOP.csv)                ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
""")

import os

print("⚠️  IMPORTANTE:")
print("   Esta célula é OPCIONAL")
print("   Você pode fazer upload do CFOP.csv pela interface web\n")

resposta = input("Deseja popular o Pinecone agora? (s/n): ")

if resposta.lower() != 's':
    print("❌ Pulando indexação.")
    print("   Você pode fazer upload do CFOP.csv pela interface web depois")
else:
    # Verificar se arquivo existe
    cfop_path = "/content/data/CFOP.csv"
    
    if not os.path.exists(cfop_path):
        print(f"\n⚠️ Arquivo CFOP.csv não encontrado em: {cfop_path}")
        print("\n📤 Faça upload do arquivo:")
        
        from google.colab import files
        uploaded = files.upload()
        
        if 'CFOP.csv' in uploaded:
            import shutil
            os.makedirs("/content/data", exist_ok=True)
            shutil.move('CFOP.csv', cfop_path)
            print(f"✅ Arquivo movido para {cfop_path}")
        else:
            print("❌ Arquivo não enviado. Execute a célula 5 e faça upload pela interface.")
            import sys
            sys.exit(0)
    
    print("\n🔄 Iniciando indexação...")
    !python scripts/populate_pinecone.py
    
    print("\n✅ Indexação concluída!")

print("\n📋 PRÓXIMO PASSO:")
print("   Execute a célula 5 para iniciar o servidor web")
