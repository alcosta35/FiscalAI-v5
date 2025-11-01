# ==========================================
# CELL 5: Start Server
# ==========================================

print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║              🚀 INICIANDO FISCALAI v5.0                        ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
""")

import os

# Verificar se tem os CSVs necessários
print("📂 Verificando arquivos necessários...")
!mkdir -p data

required_files = {
    'data/CFOP.csv': 'Tabela de CFOPs',
    'data/202401_NFs_Cabecalho.csv': 'Cabeçalhos das Notas Fiscais',
    'data/202401_NFs_Itens.csv': 'Itens das Notas Fiscais'
}

missing_files = []
for file, desc in required_files.items():
    if os.path.exists(file):
        print(f"   ✅ {desc}")
    else:
        print(f"   ❌ {desc} - FALTANDO!")
        missing_files.append(file)

if missing_files:
    print("\n⚠️ ARQUIVOS FALTANDO:")
    print("   Você precisa fazer upload dos seguintes arquivos:\n")
    for f in missing_files:
        print(f"   • {f}")
    
    print("\n📤 Iniciando upload...")
    from google.colab import files
    uploaded = files.upload()
    
    # Mover arquivos para data/
    for filename in uploaded.keys():
        !mv {filename} data/
        print(f"   ✅ {filename} movido para data/")

print("\n✅ Todos os arquivos estão prontos!")
print("\n🚀 Iniciando servidor...\n")

!python main.py
