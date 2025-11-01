# 📓 Setup Completo para Google Colab - FiscalAI v5.0

Execute as células abaixo em sequência no seu notebook Colab.

---

## ⚙️ Configuração Inicial (Uma vez só)

### 1️⃣ Adicionar Secrets no Colab

Antes de executar qualquer célula:

1. Clique no ícone **🔑 Secrets** na barra lateral esquerda
2. Adicione 3 secrets:

**Secret 1: OpenAI**
- Name: `OPENAI_API_KEY`
- Value: `sk-proj-...` (sua key da OpenAI)
- Notebook access: ✅ **ATIVADO**

**Secret 2: Pinecone**
- Name: `PINECONE_API_KEY`  
- Value: `pcsk_...` (sua key do Pinecone)
- Notebook access: ✅ **ATIVADO**

**Secret 3: Ngrok**
- Name: `NGROK_AUTH_TOKEN`
- Value: `2...` (seu token do Ngrok)
- Notebook access: ✅ **ATIVADO**

---

## 📋 Células do Notebook

Copie e cole cada célula abaixo no seu notebook Colab:

### Célula 1: Clone do Repositório

```python
# ==========================================
# FISCALAI v5.0 - Célula 1: Clone Repository
# ==========================================

print("""
╔════════════════════════════════════════════════════════════════╗
║                   🚀 FiscalAI v5.0                             ║
║            Validação Semântica de CFOP com IA                  ║
╚════════════════════════════════════════════════════════════════╝
""")

!git clone https://github.com/SEU-USUARIO/FiscalAI-v5
%cd FiscalAI-v5

print("✅ Repositório clonado!")
```

### Célula 2: Instalar Dependências

```python
# ==========================================
# FISCALAI v5.0 - Célula 2: Install Dependencies
# ==========================================

print("📦 Instalando dependências...")
!pip install -q -r requirements.txt

print("✅ Instalação completa!")

# Verificar
import pinecone, openai, langchain
print(f"\n✅ Versões:")
print(f"   • Pinecone: {pinecone.__version__}")
print(f"   • OpenAI: {openai.__version__}")
```

### Célula 3: Configurar API Keys

```python
# ==========================================
# FISCALAI v5.0 - Célula 3: Configure API Keys
# ==========================================

from google.colab import userdata

try:
    openai_key = userdata.get('OPENAI_API_KEY')
    pinecone_key = userdata.get('PINECONE_API_KEY')
    ngrok_token = userdata.get('NGROK_AUTH_TOKEN')
    
    with open('.env', 'w') as f:
        f.write(f'OPENAI_API_KEY={openai_key}\n')
        f.write(f'PINECONE_API_KEY={pinecone_key}\n')
        f.write(f'NGROK_AUTH_TOKEN={ngrok_token}\n')
    
    print("✅ API Keys configuradas!")
    print(f"   • OpenAI: {openai_key[:10]}...")
    print(f"   • Pinecone: {pinecone_key[:10]}...")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    print("\n⚠️  Adicione os Secrets no Colab (ícone 🔑)")
```

### Célula 4: Popular Pinecone (PRIMEIRA VEZ)

```python
# ==========================================
# FISCALAI v5.0 - Célula 4: Populate Pinecone
# ⚠️  Execute apenas UMA VEZ ou ao atualizar CFOP.csv
# ==========================================

print("📊 Populando índice Pinecone...")

!mkdir -p data

# Upload do CFOP.csv se não existir
import os
if not os.path.exists('data/CFOP.csv'):
    print("📤 Faça upload do arquivo CFOP.csv:")
    from google.colab import files
    uploaded = files.upload()
    !mv CFOP.csv data/

# Popular índice
!python scripts/populate_pinecone.py

print("✅ Índice populado!")
```

### Célula 5: Iniciar Servidor

```python
# ==========================================
# FISCALAI v5.0 - Célula 5: Start Server
# ==========================================

!mkdir -p data

# Upload dos CSVs se necessário
import os
required = ['CFOP.csv', '202401_NFs_Cabecalho.csv', '202401_NFs_Itens.csv']

for f in required:
    if not os.path.exists(f'data/{f}'):
        print(f"📤 Upload {f}:")
        from google.colab import files
        uploaded = files.upload()
        !mv {f} data/

# Iniciar servidor
!python main.py
```

---

## 🎯 Como Usar

Após a célula 5 executar:

1. **Copie a URL ngrok** que aparece no output:
   ```
   🌐 URL Pública: https://xxxx-xx-xxx-xxx-xx.ngrok.io
   ```

2. **Abra a URL no navegador**

3. **Faça upload dos CSVs** (se ainda não fez):
   - Cabeçalho
   - Itens  
   - CFOP

4. **Clique em "Chat"** e comece a validar:
   ```
   Valide o CFOP do primeiro item da nota 
   com chave 35240134028316923228550010003680821895807710
   ```

---

## 🔄 Próximas Execuções

Nas próximas vezes que abrir o Colab:

1. Execute apenas as células **1, 2, 3 e 5**
2. **Pule a célula 4** (índice já está populado)
3. A menos que tenha atualizado o CFOP.csv

---

## 💡 Dicas

- **Mantenha o Colab aberto**: O servidor para se você fechar
- **Timeout**: Colab fecha após ~90min de inatividade
- **Restart**: Se precisar reiniciar, execute todas as células novamente

---

## 🐛 Troubleshooting

**Erro: "OPENAI_API_KEY não encontrada"**
→ Verifique se adicionou o Secret e ativou "Notebook access"

**Erro: "Index not found"**
→ Execute a célula 4 para popular o Pinecone

**Ngrok retorna 403**
→ Atualize seu authtoken em ngrok.com

---

**🎉 Pronto! Agora você tem FiscalAI v5.0 rodando no Colab!**
