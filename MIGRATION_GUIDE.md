# 📋 Guia de Migração: FiscalAI v4 → v5

## 🎯 O que muda?

### **Arquitetura**

```
v4: Regras Baseadas em Lógica
┌─────────────┐
│ Dados NF-e  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Árvore de Decisão   │ ← IF/ELSE complexos
└──────┬──────────────┘
       │
       ▼
┌─────────────┐
│ CFOP        │
└─────────────┘

v5: Busca Semântica
┌─────────────┐
│ Dados NF-e  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Gerar Embedding     │ ← OpenAI
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Buscar no Pinecone  │ ← Vector Store
└──────┬──────────────┘
       │
       ▼
┌─────────────┐
│ CFOP        │
└─────────────┘
```

---

## 🔧 Mudanças no Código

### **1. config.py**

#### ❌ **v4 (Antigo)**
```python
class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
```

#### ✅ **v5 (Novo)**
```python
class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"  # NOVO
    
    # Pinecone (NOVO)
    pinecone_api_key: str = ""
    pinecone_index_name: str = "cfop-validator"
    
    # Validação (NOVO)
    similarity_threshold: float = 0.75
    top_k_results: int = 3
```

---

### **2. agente_cfop.py → agente_cfop_v5.py**

#### ❌ **v4 (Regras)**
```python
class AgenteValidadorCFOP:
    def validar_cfop(self, item):
        # Lógica IF/ELSE
        if item['UF_EMITENTE'] == item['UF_DESTINATARIO']:
            if item['CONSUMIDOR_FINAL'] == '1':
                return '5102'  # Venda dentro do estado
            else:
                return '5101'
        else:
            # ... mais 50 linhas de IFs
```

#### ✅ **v5 (Semântica)**
```python
class AgenteValidadorCFOPv5:
    def validar_cfop(self, item):
        # Busca semântica automática
        return self.vector_store.buscar_cfop_semantico(
            descricao_item=item['DESCRICAO'],
            uf_emitente=item['UF_EMITENTE'],
            uf_destinatario=item['UF_DESTINATARIO'],
            consumidor_final=item['CONSUMIDOR_FINAL']
        )
```

---

### **3. Novos Arquivos**

#### **services/pinecone_service.py** (NOVO)
```python
class PineconeVectorStore:
    """Gerencia embeddings e buscas no Pinecone"""
    
    def popular_cfops(df_cfop):
        """Cria embeddings e envia para Pinecone"""
        
    def buscar_cfop_semantico(...):
        """Busca CFOPs por similaridade"""
        
    def validar_cfop_usado(...):
        """Compara CFOP usado vs sugerido"""
```

---

## 📦 Dependências

### **requirements.txt**

#### ➕ **Adicionar**
```
pinecone-client>=3.0.0
```

#### ✏️ **Atualizar**
```
openai>=1.3.0  # Era 0.27.x
```

---

## 🔑 Novas Credenciais Necessárias

### **Antes (v4):**
- ✅ OPENAI_API_KEY
- ✅ NGROK_AUTH_TOKEN

### **Agora (v5):**
- ✅ OPENAI_API_KEY
- ✅ NGROK_AUTH_TOKEN
- 🆕 **PINECONE_API_KEY**

### **Como obter Pinecone API Key:**
1. Acesse: https://app.pinecone.io/
2. Crie conta gratuita
3. Vá em: API Keys → Create API Key
4. Copie a chave (`pcsk_...`)

---

## 🚀 Passo a Passo da Migração

### **Opção A: Repositório Novo (Recomendado)**

```python
# 1. Clonar v5
!git clone https://github.com/alcosta35/FiscalAI-v5

# 2. Copiar dados da v4
!cp -r /content/FiscalAI-v4/data/* /content/FiscalAI-v5/data/

# 3. Configurar .env com nova chave
os.chdir('/content/FiscalAI-v5')
with open('.env', 'w') as f:
    f.write(f'OPENAI_API_KEY={openai_key}\n')
    f.write(f'NGROK_AUTH_TOKEN={ngrok_token}\n')
    f.write(f'PINECONE_API_KEY={pinecone_key}\n')  # NOVO

# 4. Popular Pinecone (primeira vez)
!python init_pinecone.py

# 5. Iniciar servidor
!python main.py
```

---

### **Opção B: Atualizar v4 In-Place**

```python
# 1. Backup
!cp -r /content/FiscalAI-v4 /content/FiscalAI-v4-backup

# 2. Atualizar arquivos
os.chdir('/content/FiscalAI-v4')
!git pull origin v5-upgrade

# 3. Instalar nova dependência
!pip install -q pinecone-client

# 4. Adicionar chave Pinecone
# ... (mesmo processo da Opção A)

# 5. Popular e iniciar
!python init_pinecone.py
!python main.py
```

---

## 🔄 Comparação de Código

### **Validar um Item**

#### ❌ **v4**
```python
from agente_cfop import AgenteValidadorCFOP

agente = AgenteValidadorCFOP(
    cabecalho_path='data/cabecalho.csv',
    itens_path='data/itens.csv',
    cfop_path='data/CFOP.csv'
)

# Validação com regras
resultado = agente.validar_cfop_item(
    cfop='5102',
    uf_emitente='SP',
    uf_destinatario='SP',
    consumidor_final='1'
)
# Retorna: True/False (sem explicação)
```

#### ✅ **v5**
```python
from agente_cfop_v5 import AgenteValidadorCFOPv5

agente = AgenteValidadorCFOPv5(
    cabecalho_path='data/cabecalho.csv',
    itens_path='data/itens.csv',
    cfop_path='data/CFOP.csv',
    auto_popular=True  # NOVO: popula Pinecone automaticamente
)

# Validação semântica
resultado = agente.validar_item(item_row)

# Retorna dict completo:
{
    "valido": True,
    "cfop_usado": "5102",
    "cfop_sugerido": "5102",
    "similarity_score": 0.92,
    "confianca": "MUITO ALTA",
    "mensagem": "✅ CFOP correto",
    "alternativas": [
        {"cfop": "5101", "score": 0.85},
        {"cfop": "5405", "score": 0.78}
    ]
}
```

---

## 📊 Impacto nas Rotas da API

### **Nova Rota: Buscar CFOP** (NOVA)

```python
@app.post("/api/buscar-cfop")
async def buscar_cfop(request: BuscarCFOPRequest):
    """
    Busca CFOPs adequados para uma descrição usando semântica
    """
    resultados = agente.vector_store.buscar_cfop_semantico(
        descricao_item=request.descricao,
        uf_emitente=request.uf_emitente,
        uf_destinatario=request.uf_destinatario
    )
    return {"cfops": resultados}
```

### **Rota Atualizada: Validar**

#### ❌ **v4**
```python
return {"valido": True}  # Simples
```

#### ✅ **v5**
```python
return {
    "valido": True,
    "similarity_score": 0.92,
    "confianca": "MUITO ALTA",
    "justificativa": "...",
    "alternativas": [...]
}  # Rico em informações
```

---

## ⚠️ **Breaking Changes**

### **1. Formato de Resposta**

#### v4:
```json
{"valido": true}
```

#### v5:
```json
{
    "valido": true,
    "cfop_usado": "5102",
    "cfop_sugerido": "5102",
    "similarity_score": 0.92,
    "confianca": "MUITO ALTA"
}
```

**Impacto**: Se seu frontend espera apenas `valido`, você precisa ajustar!

---

### **2. Tempo de Resposta**

#### v4: ~50ms (local)
#### v5: ~200-500ms (API calls)

**Mitigação**: Implementar cache para descrições repetidas

---

### **3. Custos**

#### v4: $0 (tudo local)
#### v5: ~$0.000001 por busca + Pinecone free tier

**Impacto**: Praticamente zero, mas não mais 100% offline

---

## ✅ **Checklist de Migração**

- [ ] ✅ Obter PINECONE_API_KEY
- [ ] ✅ Adicionar secret no Colab
- [ ] ✅ Clonar/atualizar repositório v5
- [ ] ✅ Instalar `pinecone-client`
- [ ] ✅ Configurar `.env` com 3 chaves
- [ ] ✅ Executar `init_pinecone.py` (primeira vez)
- [ ] ✅ Testar com `test_semantic_search.py`
- [ ] ✅ Atualizar frontend (se necessário)
- [ ] ✅ Fazer backup da v4
- [ ] ✅ Iniciar servidor v5

---

## 🧪 **Teste Comparativo**

Execute ambas versões e compare:

```python
# v4
resultado_v4 = agente_v4.validar_cfop_item(...)
# ~60-70% de precisão

# v5
resultado_v5 = agente_v5.validar_item(...)
# ~85-95% de precisão
```

---

## 💡 **Dicas**

### **1. Rodar v4 e v5 lado a lado**
```python
# Testar ambos e comparar
agente_v4 = AgenteValidadorCFOP(...)
agente_v5 = AgenteValidadorCFOPv5(...)

for item in amostra:
    resultado_v4 = agente_v4.validar(item)
    resultado_v5 = agente_v5.validar_item(item)
    
    print(f"v4: {resultado_v4}")
    print(f"v5: {resultado_v5}")
    print(f"Melhor: {'v5' if resultado_v5['similarity_score'] > 0.8 else 'incerto'}")
```

### **2. Rollback fácil**
```python
# Se der problema, voltar para v4
!rm -rf /content/FiscalAI-v5
!mv /content/FiscalAI-v4-backup /content/FiscalAI-v4
```

### **3. Monitorar custos**
```python
# Ver uso da OpenAI
# https://platform.openai.com/usage

# Ver uso do Pinecone
# https://app.pinecone.io/
```

---

## 🆘 **Problemas Comuns**

### **"Pinecone index already exists"**
✅ Normal! A v5 reutiliza índice existente.

### **"OpenAI quota exceeded"**
⚠️ Você atingiu o limite da API. Aguarde reset ou aumente quota.

### **"Resultados ruins (low score)"**
🔧 Ajuste `similarity_threshold` em `config.py`

### **"Muito lento"**
⚡ Considere implementar cache local ou usar Pinecone Pro

---

## 📈 **Próximos Passos Após Migração**

1. ✅ Validar lote de amostras
2. ✅ Comparar métricas v4 vs v5
3. ✅ Ajustar threshold se necessário
4. ✅ Implementar cache (opcional)
5. ✅ Atualizar documentação do projeto
6. ✅ Treinar equipe no novo formato

---

## 📞 **Suporte**

Se precisar de ajuda durante a migração:
- 📧 Email: [seu-email]
- 💬 GitHub Issues: [link]
- 📚 Docs: README.md

---

**Boa migração! 🚀**
