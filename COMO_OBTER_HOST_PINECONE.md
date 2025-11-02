# 🔗 COMO OBTER O HOST URL DO PINECONE

## 📋 O Que é o Host URL?

O **Host URL** é o endereço específico do seu índice no Pinecone.

**Formato:**
```
https://[index-name]-[project-id].svc.[environment].pinecone.io
```

**Exemplo:**
```
https://cfop-x8q6et6.svc.aped-4627-b74a.pinecone.io
```

---

## 🎯 MÉTODO 1: Obter pelo Dashboard (MAIS FÁCIL)

### Passo a Passo:

1. **Acesse** https://app.pinecone.io/
2. **Faça login** na sua conta
3. **Clique no seu índice** (ex: "cfop")
4. Na página do índice, procure por **"Host"** ou **"Endpoint"**
5. **Copie** a URL completa

**Exemplo de onde encontrar:**
```
Index Details
├── Name: cfop
├── Environment: us-east-1
├── Dimensions: 1536
└── Host: https://cfop-x8q6et6.svc.aped-4627-b74a.pinecone.io  ← COPIE ISSO
```

---

## 🎯 MÉTODO 2: Obter via Python

Se você já tem um índice criado:

```python
from pinecone import Pinecone
import os

# Inicializar
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Obter informações do índice
index_info = pc.describe_index("cfop")

# Mostrar host
print(f"Host URL: {index_info.host}")
```

**Output:**
```
Host URL: https://cfop-x8q6et6.svc.aped-4627-b74a.pinecone.io
```

---

## 🎯 MÉTODO 3: Obter via API REST

```bash
curl -X GET "https://api.pinecone.io/indexes/cfop" \
  -H "Api-Key: YOUR_PINECONE_API_KEY"
```

**Response:**
```json
{
  "name": "cfop",
  "dimension": 1536,
  "metric": "cosine",
  "host": "https://cfop-x8q6et6.svc.aped-4627-b74a.pinecone.io",
  ...
}
```

---

## 🎯 MÉTODO 4: Obter Automaticamente no Código

O serviço já faz isso automaticamente se você não fornecer o host:

```python
from services.semantic_search_service import CFOPSemanticSearchService

# SEM fornecer host - ele obtém automaticamente
service = CFOPSemanticSearchService(
    index_name="cfop"
)

# Verificar o host obtido
print(f"Host: {service.host}")
```

---

## 📝 Como Usar no Seu .env

Depois de obter o host URL, adicione no `.env`:

```bash
PINECONE_HOST=https://cfop-x8q6et6.svc.aped-4627-b74a.pinecone.io
```

---

## 🎯 PARA SEU CASO ESPECÍFICO

Baseado no que você forneceu:

```python
# Na Célula 3 do Colab:

PINECONE_INDEX_NAME = "cfop"
PINECONE_NAMESPACE = "default"
PINECONE_HOST = "https://cfop-x8q6et6.svc.aped-4627-b74a.pinecone.io"
```

---

## ✅ Verificar se o Host Está Correto

Execute este código para testar:

```python
from pinecone import Pinecone
import os

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Conectar usando o host
index = pc.Index(
    name="cfop",
    host="https://cfop-x8q6et6.svc.aped-4627-b74a.pinecone.io"
)

# Testar conexão
stats = index.describe_index_stats()
print(f"✅ Conexão OK! Total de vetores: {stats.total_vector_count}")
```

---

## 🤔 E Se Eu Não Souber o Host?

**Não tem problema!** O sistema funciona sem o host:

```python
# Opção 1: Sem host (Pinecone resolve automaticamente)
service = CFOPSemanticSearchService(
    index_name="cfop"
)

# Opção 2: Sistema obtém automaticamente
# O método _setup_index() busca o host se não fornecido
```

**Mas fornecer o host é mais rápido** porque evita uma chamada extra à API.

---

## 📊 Diferença: Com vs Sem Host

### Com Host (MAIS RÁPIDO):
```python
service = CFOPSemanticSearchService(
    index_name="cfop",
    host="https://cfop-x8q6et6.svc.aped-4627-b74a.pinecone.io"
)
```
✅ Conexão direta  
✅ Mais rápido (~100ms)

### Sem Host:
```python
service = CFOPSemanticSearchService(
    index_name="cfop"
)
```
✅ Funciona igual  
⚠️ Um pouco mais lento (~200ms) - precisa resolver o host

---

## 🎯 RECOMENDAÇÃO

**Para PRODUÇÃO**: Sempre forneça o host URL  
**Para DESENVOLVIMENTO**: Pode omitir (mais flexível)

---

## 📚 Referências

- [Pinecone Dashboard](https://app.pinecone.io/)
- [Pinecone API Docs](https://docs.pinecone.io/reference/api/introduction)
- [Describe Index API](https://docs.pinecone.io/reference/api/control-plane/describe_index)

---

## ✅ Checklist

- [ ] Acessei o dashboard Pinecone
- [ ] Encontrei meu índice
- [ ] Copiei o host URL
- [ ] Adicionei no .env ou na célula 3
- [ ] Testei a conexão

---

**🎉 Pronto! Agora você tem o host URL configurado corretamente!**
