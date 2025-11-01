# FiscalAI v5 - Quick Start Guide 🚀

## Setup em 5 Minutos

### 1️⃣ Obter API Keys (2 min)

**OpenAI** (para embeddings):
- Crie conta: https://platform.openai.com
- Vá em API Keys → Create new key
- Copie: `sk-...`

**Pinecone** (Vector Store - GRÁTIS):
- Crie conta: https://app.pinecone.io
- Após login, copie API Key do dashboard
- Copie: `xxx-xxx-xxx`

**Ngrok** (apenas Colab):
- Crie conta: https://dashboard.ngrok.com
- Copie auth token

---

### 2️⃣ Google Colab - Notebook Completo

#### Célula 1: Clone + Install
```python
# Clone
!git clone https://github.com/alcosta35/FiscalAI-v5
%cd FiscalAI-v5

# Install
!pip install -q pinecone-client openai fastapi uvicorn pandas pyngrok
```

#### Célula 2: Configure Keys
```python
from google.colab import userdata
import os

# Adicione 3 Secrets no Colab (🔑 ícone lateral):
# - OPENAI_API_KEY
# - PINECONE_API_KEY
# - NGROK_AUTH_TOKEN

with open('.env', 'w') as f:
    f.write(f'OPENAI_API_KEY={userdata.get("OPENAI_API_KEY")}\n')
    f.write(f'PINECONE_API_KEY={userdata.get("PINECONE_API_KEY")}\n')
    f.write(f'NGROK_AUTH_TOKEN={userdata.get("NGROK_AUTH_TOKEN")}\n')

print("✅ Keys configuradas")
```

#### Célula 3: Upload CFOP.csv + Setup Pinecone (UMA VEZ APENAS)
```python
from google.colab import files

# Upload CFOP.csv
print("📤 Faça upload do CFOP.csv:")
uploaded = files.upload()

# Mover para data/
!mkdir -p data
!cp CFOP.csv data/

# Setup Pinecone (5-10 min)
print("🚀 Configurando Pinecone...")
!python pinecone_setup.py data/CFOP.csv

print("✅ Setup concluído!")
```

#### Célula 4: Iniciar Servidor
```python
!python main.py
# Acesse a URL do ngrok exibida
```

---

### 3️⃣ Testar (API ou Web)

#### Opção A: Interface Web
1. Abra URL do ngrok
2. Faça upload dos CSVs de NFs
3. Use validação semântica na página de validação

#### Opção B: Via API
```python
import requests

BASE = "http://localhost:8000"  # ou URL do ngrok

# 1. Inicializar
requests.post(f"{BASE}/api/validacao-semantica/inicializar")

# 2. Validar item
item = {
    "uf_emitente": "SP",
    "uf_destinatario": "RJ",
    "descricao_produto": "Notebook Dell para revenda",
    "ncm": "84713012",
    "consumidor_final": "0",
    "indicador_ie": "1",
    "cfop_informado": "6102"
}

response = requests.post(
    f"{BASE}/api/validacao-semantica/validar-item",
    json=item
)

resultado = response.json()
print(f"Status: {resultado['status']}")
print(f"CFOP Sugerido: {resultado['sugestoes'][0]['cfop']}")
print(f"Confiança: {resultado['sugestoes'][0]['confianca']}")
print(f"Score: {resultado['sugestoes'][0]['score']}")
```

---

## Resultado Esperado

```json
{
  "status": "CORRETO",
  "mensagem": "CFOP informado está correto (#1 nas sugestões)",
  "cfop_informado": "6102",
  "sugestoes": [
    {
      "cfop": "6.102",
      "descricao": "Venda de mercadoria adquirida ou recebida de terceiros",
      "score": 0.9234,
      "confianca": "ALTA"
    }
  ]
}
```

---

## Validar Lote

```python
# CSV deve ter colunas:
# - UF EMITENTE
# - UF DESTINATÁRIO
# - DESCRIÇÃO DO PRODUTO/SERVIÇO
# - NCM/SH (TIPO DE PRODUTO)
# - CONSUMIDOR FINAL
# - INDICADOR IE DESTINATÁRIO
# - CFOP (opcional)

import pandas as pd

df = pd.read_csv('notas_fiscais.csv')

# Upload
files = {'arquivo': open('notas_fiscais.csv', 'rb')}
response = requests.post(
    f"{BASE}/api/validacao-semantica/validar-lote",
    files=files
)

relatorio = response.json()['relatorio']
print(f"Taxa de Acerto: {relatorio['taxa_acerto']}%")
print(f"Divergências: {relatorio['divergentes']}")
```

---

## Busca Livre

```python
# Buscar CFOP por descrição natural
response = requests.get(
    f"{BASE}/api/validacao-semantica/buscar-cfop",
    params={
        "query": "venda de mercadoria importada para consumidor final fora do estado",
        "top_k": 3
    }
)

cfops = response.json()['cfops']
for cfop in cfops:
    print(f"{cfop['cfop']} - Score: {cfop['score']}")
```

---

## Custos

### Setup Inicial (UMA VEZ)
- OpenAI: ~$0.07 (450 embeddings)
- Pinecone: $0 (free tier até 100K vetores)

### Uso Mensal (10.000 validações)
- OpenAI: ~$1.50
- Pinecone: $0

**Total: ~$1.50/mês** 🎉

---

## Troubleshooting

### ❌ "PINECONE_API_KEY não configurada"
```bash
# Verificar .env
cat .env

# Deve conter:
PINECONE_API_KEY=xxx
```

### ❌ "Índice não encontrado"
```bash
# Executar setup
python pinecone_setup.py data/CFOP.csv
```

### ❌ Scores baixos (<0.7)
- Enriqueça o campo "APLICAÇÃO" no CFOP.csv
- Textos mais detalhados = melhores resultados
- Considere adicionar exemplos de uso

---

## Endpoints Principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/validacao-semantica/inicializar` | Conecta ao Pinecone |
| POST | `/api/validacao-semantica/validar-item` | Valida 1 item |
| POST | `/api/validacao-semantica/validar-lote` | Valida CSV |
| GET | `/api/validacao-semantica/buscar-cfop` | Busca livre |
| GET | `/api/validacao-semantica/status` | Status do sistema |

---

## Estrutura de Resposta

```python
{
  "status": "CORRETO" | "DIVERGENTE" | "SUGERIDO" | "SEM_SUGESTAO",
  "mensagem": "...",
  "cfop_informado": "6102",
  "sugestoes": [
    {
      "cfop": "6.102",
      "descricao": "...",
      "aplicacao": "...",
      "score": 0.9234,
      "confianca": "ALTA" | "MÉDIA" | "BAIXA"
    }
  ],
  "query_gerada": "..."
}
```

---

## Níveis de Confiança

| Score | Confiança | Ação |
|-------|-----------|------|
| ≥ 0.90 | ALTA | ✅ Pode confiar |
| 0.75-0.89 | MÉDIA | ⚠️ Revisar se crítico |
| < 0.75 | BAIXA | 🔍 Análise manual |

---

## Próximos Passos

1. ✅ **Setup básico** (você está aqui)
2. 📊 **Testar com dados reais**
3. 🎯 **Ajustar threshold de confiança**
4. 🚀 **Integrar com seu sistema**
5. 📈 **Monitorar acurácia**

---

## Recursos

- 📚 **Docs completos**: README_V5.md
- 🎥 **Vídeo tutorial**: [em breve]
- 💬 **Suporte**: issues no GitHub
- 📧 **Email**: contato@fiscalai.com

---

**FiscalAI v5** - Validação Fiscal Inteligente 🚀

Pronto em 5 minutos. Acurácia de 90%+. Custo de ~$1.50/mês.
