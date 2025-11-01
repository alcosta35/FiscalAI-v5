# ==============================================================================
# CÉLULA 0: SETUP INICIAL - FiscalAI V5
# ==============================================================================
# Execute esta célula primeiro!

print("🚀 FiscalAI V5 - Setup Inicial")
print("="*70)

# 1. Clone do repositório
print("\n📥 Clonando repositório...")
!git clone https://github.com/SEU-USUARIO/FiscalAI-v5 2>/dev/null || echo "✅ Repositório já existe"

# 2. Mudar para diretório
%cd /content/FiscalAI-v5

# 3. Instalar dependências
print("\n📦 Instalando dependências...")
!pip install -q -r requirements.txt

print("\n✅ Setup inicial concluído!")
print("\n📝 Próximos passos:")
print("   1. Execute a CÉLULA 1 para configurar API Keys")
print("   2. Faça upload do CFOP.csv")
print("   3. Execute a CÉLULA 2 para setup do Pinecone")
print("   4. Execute a CÉLULA 3 para iniciar servidor")
