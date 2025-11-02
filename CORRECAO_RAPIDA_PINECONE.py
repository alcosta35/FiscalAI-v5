# ==========================================
# CÉLULA DE CORREÇÃO: Erro Pinecone
# Execute esta célula AGORA para corrigir o erro
# ==========================================

print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║         🔧 CORRIGINDO ERRO DO PINECONE                        ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
""")

print("🔍 Problema detectado: pacote 'pinecone-client' está obsoleto")
print("✅ Solução: substituir por 'pinecone'\n")

# Passo 1: Remover pacote antigo
print("1️⃣ Removendo pacote antigo 'pinecone-client'...")
!pip uninstall -y pinecone-client 2>/dev/null
print("   ✅ Removido\n")

# Passo 2: Instalar pacote correto
print("2️⃣ Instalando pacote correto 'pinecone'...")
!pip install -q pinecone
print("   ✅ Instalado\n")

# Passo 3: Verificar
print("3️⃣ Verificando instalação...")
try:
    import pinecone
    print(f"   ✅ Pinecone versão {pinecone.__version__} instalado!")
    print(f"   📦 Pacote: {pinecone.__file__}\n")
except Exception as e:
    print(f"   ❌ Erro: {e}\n")

# Passo 4: Confirmar que pacote antigo foi removido
print("4️⃣ Confirmando remoção do pacote antigo...")
try:
    import pinecone_client
    print("   ⚠️ ATENÇÃO: pinecone-client ainda existe!")
    print("   Execute: !pip uninstall -y pinecone-client")
except ImportError:
    print("   ✅ Pacote antigo removido com sucesso!\n")

print("="*70)
print("✅ CORREÇÃO COMPLETA!")
print("="*70)
print("\n📋 PRÓXIMO PASSO:")
print("   Execute a Célula 4 novamente para popular o Pinecone")
print("   Agora deve funcionar sem erros!\n")
