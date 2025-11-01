# ==============================================================================
# CÉLULA 3: INICIAR SERVIDOR
# ==============================================================================
import os

print("🚀 Iniciando FiscalAI V5")
print("="*70)

os.chdir('/content/FiscalAI-v5')

# Criar diretório data se não existir
!mkdir -p data

# Iniciar servidor
print("\n⏳ Aguarde o ngrok gerar o link público...")
print("   Isso pode levar 10-20 segundos...\n")

!python main.py
