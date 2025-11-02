# 🔧 CONFIGURAÇÃO DO PINECONE - FiscalAI v5.0

## 📋 Parâmetros Essenciais

### 1. API Key
```python
PINECONE_API_KEY=pcsk_xxxxxx  # Obtenha em pinecone.io
```

### 2. Nome do Índice
```python
PINECONE_INDEX_NAME=cfop-fiscal  # Nome único do seu índice
```
**Importante**: O índice será criado automaticamente se não existir.

### 3. Namespace
```python
PINECONE_NAMESPACE=cfop-production  # Organiza vetores dentro do índice
```
**Por que usar?**
- Separar ambientes (prod, dev, test)
- Múltiplas versões de dados
- Rollback facilitado

### 4. Dimensões do Vetor
```python
PINECONE_DIMENSION=1536  # DEVE corresponder ao modelo de embedding
```

**Modelos OpenAI e suas dimensões:**
| Modelo | Dimensão |
|--------|----------|
| text-embedding-3-small | 1536 |
| text-embedding-3-large | 3072 |
| text-embedding-ada-002 | 1536 |

⚠️ **CRÍTICO**: A dimensão DEVE ser a mesma do modelo de embedding!

### 5. Modelo de Embedding
```python
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

**Recomendações:**
- `text-embedding-3-small` - Barato e rápido (RECOMENDADO)
- `text-embedding-3-large` - Mais preciso, mais caro
- `text-embedding-ada-002` - Legado, ainda funciona

### 6. Métrica de Similaridade
```python
PINECONE_METRIC=cosine  # cosine, euclidean, ou dotproduct
```

**Qual usar?**
- `cosine` - **RECOMENDADO** para texto
- `euclidean` - Para dados numéricos
- `dotproduct` - Para casos especiais

### 7. Cloud e Região
```python
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
```

**Opções de Cloud:**
- `aws` - Amazon Web Services
- `gcp` - Google Cloud Platform
- `azure` - Microsoft Azure

**Regiões AWS:**
- `us-east-1` - Virginia (RECOMENDADO - mais barato)
- `us-west-2` - Oregon
- `eu-west-1` - Irlanda

**Dica**: Escolha a região mais próxima do seu usuário.

---

## 🎯 Configuração Completa Recomendada

### Para Produção:
```python
# .env
OPENAI_API_KEY=sk-proj-...
PINECONE_API_KEY=pcsk_...

# Opcional (valores padrão já são bons)
PINECONE_INDEX_NAME=cfop-fiscal
PINECONE_NAMESPACE=cfop-production
PINECONE_DIMENSION=1536
PINECONE_METRIC=cosine
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### Para Desenvolvimento/Testes:
```python
# .env.dev
OPENAI_API_KEY=sk-proj-...
PINECONE_API_KEY=pcsk_...
PINECONE_INDEX_NAME=cfop-fiscal
PINECONE_NAMESPACE=cfop-development  # ← Namespace diferente!
```

---

## 📊 Como Obter a API Key do Pinecone

1. **Criar conta**: https://www.pinecone.io/
2. **Login** no dashboard
3. **API Keys** → Create API Key
4. **Copiar** a key (começa com `pcsk_`)

### Planos:
- **Starter (Gratuito)**: 
  - 100k vetores
  - 1 índice
  - Suficiente para ~800 CFOPs!
  
- **Standard ($70/mês)**:
  - 5M vetores
  - Múltiplos índices
  
**Recomendação**: Comece com gratuito!

---

## 🔍 Verificar Configuração

Execute este script Python para validar:

```python
from services.semantic_search_service import CFOPSemanticSearchService

# Inicializar (vai mostrar todas as configs)
service = CFOPSemanticSearchService()

# Ver estatísticas
stats = service.get_index_stats()
print("\n📊 Configuração Atual:")
for key, value in stats.items():
    print(f"   • {key}: {value}")
```

**Output esperado:**
```
🔍 INICIALIZANDO SERVIÇO DE BUSCA SEMÂNTICA
==================================================================
🔑 OpenAI API Key: sk-proj-...Xyz
🔑 Pinecone API Key: pcsk_...Abc

📊 CONFIGURAÇÕES DO PINECONE:
   • Índice: cfop-fiscal
   • Namespace: cfop-production
   • Cloud: aws
   • Região: us-east-1
   • Dimensão: 1536
   • Métrica: cosine
   • Embedding Model: text-embedding-3-small

📊 Configurando índice: cfop-fiscal
   ✅ Conectado ao índice existente: cfop-fiscal
   📈 Vetores totais: 0
   📦 Vetores no namespace 'cfop-production': 0
==================================================================
✅ SERVIÇO DE BUSCA SEMÂNTICA INICIALIZADO!
==================================================================
```

---

## ⚠️ Troubleshooting

### Erro: "Index already exists with different dimensions"
**Causa**: Tentando criar índice com dimensão diferente da existente.

**Solução**:
```python
# Deletar índice antigo
from pinecone import Pinecone
pc = Pinecone(api_key="sua-key")
pc.delete_index("cfop-fiscal")

# Recriar com dimensões corretas
service = CFOPSemanticSearchService()
```

### Erro: "Namespace not found"
**Causa**: Namespace vazio ou não populado.

**Solução**:
```python
# Popular o namespace
!python scripts/populate_pinecone.py
```

### Erro: "Rate limit exceeded"
**Causa**: Muitas requisições (plano gratuito tem limites).

**Solução**:
- Aguarde alguns segundos
- Adicione delays no código
- Upgrade para plano pago

### Erro: "Vector dimension mismatch"
**Causa**: Embedding gerado tem dimensão diferente do índice.

**Solução**:
1. Verifique o modelo de embedding em `config.py`
2. Garanta que `PINECONE_DIMENSION` corresponde ao modelo
3. Recrie o índice se necessário

---

## 📚 Referências

- [Pinecone Docs](https://docs.pinecone.io/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [Pinecone Pricing](https://www.pinecone.io/pricing/)

---

## 🎯 Checklist de Configuração

- [ ] API Key do Pinecone obtida
- [ ] API Key do OpenAI obtida
- [ ] Arquivo `.env` criado
- [ ] Dimensões corretas configuradas
- [ ] Namespace definido
- [ ] Região escolhida
- [ ] Script de teste executado
- [ ] Índice populado

---

**✅ Com essas configurações, o Pinecone está pronto para uso!**
