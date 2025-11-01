# FiscalAI v5 - Validação Semântica de CFOP com Pinecone

## 🚀 Visão Geral

O **FiscalAI v5** é uma evolução do sistema de auditoria fiscal que implementa **validação semântica de CFOP** usando **Pinecone Vector Store** e **OpenAI Embeddings**.

### O que mudou?

**v4 (anterior)**: Validação baseada em regras fixas e lógica programática
**v5 (nova)**: Validação baseada em busca semântica com IA, entendendo o **contexto** da operação

---

## 🎯 Como Funciona

### Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                         FiscalAI v5                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. CFOP.csv (campo "APLICAÇÃO")                               │
│     ↓                                                           │
│  2. OpenAI API (gera embeddings)                               │
│     ↓                                                           │
│  3. Pinecone Vector Store (armazena vetores + metadata)        │
│     ↓                                                           │
│  4. Item da NF (campos contextuais)                            │
│     ↓                                                           │
│  5. Query semântica (busca similares)                          │
│     ↓                                                           │
│  6. Top-K CFOPs + Score de confiança                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Fluxo de Validação

1. **Setup Inicial** (uma única vez):
   - Carrega CFOP.csv
   - Gera embeddings do campo "APLICAÇÃO"
   - Cria índice no Pinecone
   - Popula Vector Store

2. **Validação** (uso contínuo):
   - Recebe dados do item da NF
   - Cria query contextual combinando campos
   - Busca CFOPs mais similares semanticamente
   - Retorna sugestões com score de confiança

---

## 📋 Pré-requisitos

### 1. Contas e API Keys

| Serviço | Propósito | Link | Custo |
|---------|-----------|------|-------|
| OpenAI | Gerar embeddings | [platform.openai.com](https://platform.openai.com) | ~$0.02/1K itens |
| Pinecone | Vector Store | [app.pinecone.io](https://app.pinecone.io) | Free (até 100K vetores) |
| Ngrok | Túnel público (Colab) | [dashboard.ngrok.com](https://dashboard.ngrok.com) | Free |

### 2. Arquivo CFOP.csv

Deve conter as colunas:
- `CFOP`: Código do CFOP
- `DESCRIÇÃO`: Descrição breve
- `APLICAÇÃO`: **Texto detalhado** explicando quando usar (usado para embeddings)

Exemplo:
```csv
CFOP,DESCRIÇÃO,APLICAÇÃO
5.102,Venda de mercadoria adquirida ou recebida de terceiros,"Classificam-se neste código as vendas de mercadorias adquiridas ou recebidas de terceiros para industrialização ou comercialização, que não tenham sido objeto de qualquer processo industrial no estabelecimento..."
```

---

## 🛠️ Instalação

### Opção 1: Google Colab (Recomendado)

1. **Clone o repositório**:
```python
!git clone https://github.com/alcosta35/FiscalAI-v5
```

2. **Instale dependências**:
```python
!pip install -q -r /content/FiscalAI-v5/requirements.txt
```

3. **Configure API Keys** (Secrets do Colab):
   - Clique no ícone 🔑 (barra lateral)
   - Adicione 3 secrets:
     - `OPENAI_API_KEY`
     - `NGROK_AUTH_TOKEN`
     - `PINECONE_API_KEY`
   - Ative "Notebook access"

4. **Execute setup das keys**:
```python
from google.colab import userdata
import os

os.chdir('/content/FiscalAI-v5')

with open('.env', 'w') as f:
    f.write(f'OPENAI_API_KEY={userdata.get("OPENAI_API_KEY")}\n')
    f.write(f'NGROK_AUTH_TOKEN={userdata.get("NGROK_AUTH_TOKEN")}\n')
    f.write(f'PINECONE_API_KEY={userdata.get("PINECONE_API_KEY")}\n')
```

### Opção 2: Local

1. **Clone**:
```bash
git clone https://github.com/alcosta35/FiscalAI-v5
cd FiscalAI-v5
```

2. **Crie ambiente virtual**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Instale dependências**:
```bash
pip install -r requirements.txt
```

4. **Configure .env**:
```bash
cp .env.example .env
# Edite .env e adicione suas keys
```

---

## 🔧 Setup Inicial do Pinecone

**⚠️ Execute APENAS UMA VEZ** (ou quando atualizar o CFOP.csv)

### Passo 1: Upload do CFOP.csv

No Colab:
```python
from google.colab import files
uploaded = files.upload()  # Selecione CFOP.csv
!cp CFOP.csv /content/FiscalAI-v5/data/
```

Local:
```bash
cp /caminho/para/CFOP.csv ./data/
```

### Passo 2: Executar Setup

```bash
python pinecone_setup.py data/CFOP.csv
```

**O que acontece**:
- ✅ Carrega ~450 CFOPs do CSV
- ✅ Gera 450 embeddings (OpenAI)
- ✅ Cria índice "fiscalai-cfop" no Pinecone
- ✅ Upload dos vetores + metadata

**Tempo**: 5-10 minutos
**Custo**: ~$0.07 (OpenAI) + $0 (Pinecone free tier)

**Output esperado**:
```
🚀 FISCALAI v5 - SETUP PINECONE VECTOR STORE
==================================================
📂 Carregando data/CFOP.csv...
✅ 450 CFOPs carregados
🧠 Gerando embeddings para 450 textos...
  ✓ Processados 450/450 textos
✅ Embeddings gerados com sucesso
🔧 Configurando índice 'fiscalai-cfop'...
✅ Índice criado
📤 Fazendo upload de 450 vetores...
  ✓ Upload 450/450
✅ Upload concluído
📊 Total de vetores: 450
```

---

## 🚀 Iniciar Servidor

```bash
python main.py
```

**Colab**: Acesse a URL do ngrok exibida
**Local**: Acesse http://localhost:8000

---

## 📡 API - Endpoints

### 1. Inicializar Validador

**POST** `/api/validacao-semantica/inicializar`

Conecta ao Pinecone e prepara o validador.

```bash
curl -X POST http://localhost:8000/api/validacao-semantica/inicializar
```

Response:
```json
{
  "status": "success",
  "mensagem": "Validador semântico inicializado",
  "index_name": "fiscalai-cfop",
  "total_vetores": 450
}
```

---

### 2. Validar Item Individual

**POST** `/api/validacao-semantica/validar-item`

Valida CFOP de um item específico.

**Body**:
```json
{
  "uf_emitente": "SP",
  "uf_destinatario": "RJ",
  "descricao_produto": "Notebook Dell Inspiron 15 para revenda",
  "ncm": "84713012",
  "consumidor_final": "0",
  "indicador_ie": "1",
  "cfop_informado": "6102"
}
```

**Response**:
```json
{
  "status": "CORRETO",
  "mensagem": "CFOP informado está correto (#1 nas sugestões)",
  "cfop_informado": "6102",
  "total_sugestoes": 5,
  "sugestoes": [
    {
      "cfop": "6.102",
      "descricao": "Venda de mercadoria adquirida ou recebida de terceiros",
      "aplicacao": "Classificam-se neste código...",
      "score": 0.9234,
      "confianca": "ALTA"
    },
    {
      "cfop": "6.101",
      "score": 0.8876,
      "confianca": "ALTA"
    }
  ],
  "query_gerada": "Operação fiscal... (texto completo)"
}
```

**Status possíveis**:
- `CORRETO`: CFOP informado está nas top-K sugestões
- `DIVERGENTE`: CFOP informado difere das sugestões
- `SUGERIDO`: Apenas retornou sugestões (sem CFOP informado)
- `SEM_SUGESTAO`: Não encontrou sugestões com confiança adequada

---

### 3. Validar Lote (CSV)

**POST** `/api/validacao-semantica/validar-lote`

Valida múltiplos itens de uma vez.

**Body**: `multipart/form-data` com arquivo CSV

**CSV deve conter**:
- `UF EMITENTE`
- `UF DESTINATÁRIO`
- `DESCRIÇÃO DO PRODUTO/SERVIÇO`
- `NCM/SH (TIPO DE PRODUTO)`
- `CONSUMIDOR FINAL`
- `INDICADOR IE DESTINATÁRIO`
- `CFOP` (opcional, para comparação)

**Response**:
```json
{
  "status": "success",
  "total_processado": 150,
  "relatorio": {
    "total_validacoes": 150,
    "corretos": 132,
    "divergentes": 15,
    "sem_sugestao": 3,
    "taxa_acerto": 88.0,
    "taxa_divergencia": 10.0,
    "score_medio": 0.8756
  },
  "resultados": [...]
}
```

---

### 4. Busca Livre por Contexto

**GET** `/api/validacao-semantica/buscar-cfop`

Busca CFOPs por descrição natural.

**Query params**:
- `query`: Descrição da operação (string)
- `top_k`: Número de resultados (default: 5)

**Exemplo**:
```bash
curl "http://localhost:8000/api/validacao-semantica/buscar-cfop?\
query=venda%20de%20produto%20importado%20para%20consumidor%20final&top_k=3"
```

**Response**:
```json
{
  "query": "venda de produto importado para consumidor final",
  "total_resultados": 3,
  "cfops": [
    {
      "cfop": "6.107",
      "descricao": "Venda de mercadoria...",
      "score": 0.9145,
      "confianca": "ALTA"
    }
  ]
}
```

---

### 5. Comparar Validações

**POST** `/api/validacao-semantica/comparar-validacoes`

Compara validações semânticas com CFOPs informados (análise de acurácia).

**Body**: CSV com CFOP já preenchido

**Response**:
```json
{
  "status": "success",
  "relatorio_geral": {
    "taxa_acerto": 92.5,
    "score_medio": 0.8923
  },
  "total_divergencias": 12,
  "amostra_divergencias": [
    {
      "cfop_informado": "5102",
      "cfop_sugerido": "5101",
      "score": 0.8234,
      "numero_item": 5
    }
  ]
}
```

---

## 💡 Exemplos de Uso

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Inicializar
requests.post(f"{BASE_URL}/api/validacao-semantica/inicializar")

# 2. Validar item
item = {
    "uf_emitente": "SP",
    "uf_destinatario": "MG",
    "descricao_produto": "Mouse óptico USB para comercialização",
    "ncm": "84716060",
    "consumidor_final": "0",
    "indicador_ie": "1"
}

response = requests.post(
    f"{BASE_URL}/api/validacao-semantica/validar-item",
    json=item
)

resultado = response.json()
print(f"Status: {resultado['status']}")
print(f"CFOP Sugerido: {resultado['sugestoes'][0]['cfop']}")
print(f"Confiança: {resultado['sugestoes'][0]['confianca']}")
```

### JavaScript (Frontend)

```javascript
// Validar item
const validarCFOP = async (item) => {
  const response = await fetch('/api/validacao-semantica/validar-item', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(item)
  });
  
  const resultado = await response.json();
  
  if (resultado.status === 'CORRETO') {
    console.log('✅ CFOP correto!');
  } else {
    console.log(`⚠️ Sugestão: ${resultado.sugestoes[0].cfop}`);
  }
};
```

---

## 📊 Interpretando Resultados

### Score de Similaridade

| Score | Confiança | Interpretação |
|-------|-----------|---------------|
| ≥ 0.90 | ALTA | CFOP muito provável, pode confiar |
| 0.75-0.89 | MÉDIA | CFOP provável, revisar caso crítico |
| < 0.75 | BAIXA | CFOP incerto, precisa análise manual |

### Status de Validação

- **CORRETO**: CFOP informado coincide com as top-K sugestões
- **DIVERGENTE**: CFOP informado difere significativamente
- **SUGERIDO**: Sistema apenas sugeriu (sem CFOP para comparar)
- **SEM_SUGESTAO**: Dados insuficientes ou caso atípico

---

## 🔍 Como a Query é Construída

O sistema cria uma query contextual rica combinando:

```python
query = f"""
Operação fiscal com as seguintes características:

Geografia: operação interestadual
UF Origem: SP
UF Destino: RJ

Destinatário: contribuinte do ICMS, não é consumidor final

Produto: Notebook Dell Inspiron 15 para revenda
NCM: 84713012

Busco o CFOP apropriado para esta operação de venda/saída de mercadoria.
"""
```

Essa query é transformada em embedding e comparada com os embeddings dos CFOPs.

---

## 🧪 Testes e Validação

### Teste Básico

```bash
# Após iniciar servidor
curl -X POST http://localhost:8000/api/validacao-semantica/inicializar

curl -X POST http://localhost:8000/api/validacao-semantica/validar-item \
  -H "Content-Type: application/json" \
  -d '{
    "uf_emitente": "SP",
    "uf_destinatario": "SP",
    "descricao_produto": "Venda de produto próprio",
    "cfop_informado": "5101"
  }'
```

### Teste de Acurácia

1. Prepare CSV com CFOPs já validados manualmente
2. Execute validação em lote
3. Analise relatório de divergências
4. Ajuste threshold de confiança se necessário

---

## 🚨 Troubleshooting

### Erro: "PINECONE_API_KEY não configurada"
- Verifique se a key está no `.env` ou Colab Secrets
- Teste: `echo $PINECONE_API_KEY` (Linux) ou `echo %PINECONE_API_KEY%` (Windows)

### Erro: "Índice 'fiscalai-cfop' não encontrado"
- Execute o `pinecone_setup.py` primeiro
- Verifique no Pinecone dashboard se o índice existe

### Scores muito baixos (<0.7)
- Verifique qualidade do campo "APLICAÇÃO" no CFOP.csv
- Textos mais detalhados = melhores embeddings
- Considere enriquecer descrições dos CFOPs

### Rate limit da OpenAI
- Adicione `time.sleep()` entre chamadas
- Use tier pago da OpenAI para mais requisições/min

---

## 💰 Custos Estimados

### Setup Inicial (uma vez)
- OpenAI (450 embeddings): ~$0.07
- Pinecone (armazenamento): $0 (free tier)

### Uso Mensal (10.000 validações)
- OpenAI (10K queries): ~$1.50
- Pinecone (100K vetores): $0 (free tier)

**Total mensal: ~$1.50** 🎉

---

## 📈 Roadmap v5.1

- [ ] Cache de embeddings para queries repetidas
- [ ] Fine-tuning do modelo de embeddings
- [ ] Interface web para validação interativa
- [ ] Integração com ERP (SAP, TOTVS)
- [ ] Logs de auditoria (quem validou, quando)
- [ ] Relatórios executivos (dashboard)

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit (`git commit -am 'Add nova funcionalidade'`)
4. Push (`git push origin feature/nova-funcionalidade`)
5. Abra Pull Request

---

## 📄 Licença

MIT License - veja LICENSE para detalhes

---

## 👤 Autor

**André Costa**
- GitHub: [@alcosta35](https://github.com/alcosta35)
- Email: contato@fiscalai.com

---

## 🙏 Agradecimentos

- OpenAI pela API de embeddings
- Pinecone pelo Vector Store gratuito
- Comunidade Python/FastAPI

---

**FiscalAI v5** - Validação Fiscal Inteligente 🚀
