# ==========================================
# CORREÇÃO RÁPIDA - Mover CFOP.csv para lugar correto
# Execute esta célula AGORA para corrigir o erro
# ==========================================

print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║         🔧 CORRIGINDO CAMINHO DO CFOP.CSV                     ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
""")

import os
import shutil

print("🔍 Problema detectado: Arquivo no caminho errado")
print("✅ Solução: Mover para /content/data/\n")

# Passo 1: Criar diretório correto
data_dir = "/content/data"
os.makedirs(data_dir, exist_ok=True)
print(f"1️⃣ Diretório criado: {data_dir}")

# Passo 2: Procurar o arquivo
print(f"\n2️⃣ Procurando CFOP.csv...")

found = False
possible_locations = [
    "CFOP.csv",
    "data/CFOP.csv",
    "/content/FiscalAI-v5/data/CFOP.csv",
    f"{data_dir}/CFOP.csv"
]

for location in possible_locations:
    if os.path.exists(location):
        print(f"   ✅ Encontrado em: {location}")
        
        # Se não está no lugar correto, mover
        if location != f"{data_dir}/CFOP.csv":
            print(f"   📂 Movendo para {data_dir}/...")
            shutil.move(location, f"{data_dir}/CFOP.csv")
            print(f"   ✅ Movido com sucesso!")
        else:
            print(f"   ✅ Já está no lugar correto!")
        
        found = True
        break

# Passo 3: Se não encontrou, fazer upload
if not found:
    print("   ❌ Arquivo não encontrado!")
    print("\n3️⃣ Fazendo upload do arquivo...")
    
    from google.colab import files
    uploaded = files.upload()
    
    if 'CFOP.csv' in uploaded:
        shutil.move('CFOP.csv', f"{data_dir}/CFOP.csv")
        print(f"   ✅ Arquivo movido para {data_dir}/CFOP.csv")
        found = True

# Passo 4: Verificar final
print(f"\n4️⃣ Verificação final...")
if os.path.exists(f"{data_dir}/CFOP.csv"):
    size = os.path.getsize(f"{data_dir}/CFOP.csv")
    print(f"   ✅ Arquivo está em: {data_dir}/CFOP.csv")
    print(f"   📏 Tamanho: {size:,} bytes")
else:
    print(f"   ❌ Erro: Arquivo ainda não está no lugar correto!")

print("\n" + "="*70)
if found and os.path.exists(f"{data_dir}/CFOP.csv"):
    print("✅ CORREÇÃO COMPLETA!")
    print("="*70)
    print("\n📋 PRÓXIMO PASSO:")
    print("   Execute a Célula 4 novamente para popular o Pinecone")
    print("   Agora deve funcionar sem erros!")
else:
    print("⚠️ CORREÇÃO INCOMPLETA")
    print("="*70)
    print("\n📋 AÇÃO NECESSÁRIA:")
    print("   Faça upload do arquivo CFOP.csv novamente")
    print("   e execute esta célula mais uma vez")

print()
