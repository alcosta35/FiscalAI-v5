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

# Usar caminho absoluto no Colab
data_dir = "/content/data"
os.makedirs(data_dir, exist_ok=True)

# Verificar se tem os CSVs necessários
print("📂 Verificando arquivos necessários...")

required_files = {
    f'{data_dir}/CFOP.csv': 'Tabela de CFOPs',
    f'{data_dir}/202401_NFs_Cabecalho.csv': 'Cabeçalhos das Notas Fiscais',
    f'{data_dir}/202401_NFs_Itens.csv': 'Itens das Notas Fiscais'
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
        filename = os.path.basename(f)
        print(f"   • {filename}")
    
    print("\n📤 Iniciando upload...")
    from google.colab import files
    uploaded = files.upload()
    
    # Mover arquivos para /content/data/
    import shutil
    for filename in uploaded.keys():
        dest_path = f"{data_dir}/{filename}"
        shutil.move(filename, dest_path)
        print(f"   ✅ {filename} movido para {dest_path}")

print("\n✅ Todos os arquivos estão prontos!")
print("\n🚀 Iniciando servidor...\n")

!python main.py
