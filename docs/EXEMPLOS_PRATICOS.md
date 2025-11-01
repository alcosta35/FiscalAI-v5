# FiscalAI v5 - Exemplos Práticos e Casos de Uso

## 📚 Índice

1. [Casos de Uso Comuns](#casos-de-uso-comuns)
2. [Exemplos de Validação](#exemplos-de-validação)
3. [Padrões de Query](#padrões-de-query)
4. [Análise de Divergências](#análise-de-divergências)
5. [Integração com ERP](#integração-com-erp)

---

## Casos de Uso Comuns

### 1. Venda Interestadual para Contribuinte

```python
item = {
    "uf_emitente": "SP",
    "uf_destinatario": "RJ",
    "descricao_produto": "Notebook Dell Inspiron 15 3000 para revenda",
    "ncm": "84713012",
    "consumidor_final": "0",  # Não é consumidor final
    "indicador_ie": "1",      # Contribuinte do ICMS
    "cfop_informado": "6102"
}

# Resultado esperado:
# CFOP 6.102 - Venda de mercadoria adquirida ou recebida de terceiros
# Score: 0.92+ (ALTA confiança)
```

### 2. Venda Interna para Não Contribuinte

```python
item = {
    "uf_emitente": "SP",
    "uf_destinatario": "SP",
    "descricao_produto": "Computador desktop montado para uso pessoal",
    "ncm": "84714190",
    "consumidor_final": "1",  # Consumidor final
    "indicador_ie": "9",      # Não contribuinte
    "cfop_informado": "5102"
}

# Resultado esperado:
# CFOP 5.102 - Venda de mercadoria para não contribuinte
# Score: 0.89+ (ALTA confiança)
```

### 3. Transferência Entre Filiais

```python
item = {
    "uf_emitente": "SP",
    "uf_destinatario": "MG",
    "descricao_produto": "Transferência de estoque de produtos acabados",
    "ncm": "84713012",
    "consumidor_final": "0",
    "indicador_ie": "1",
    "cfop_informado": "6152"
}

# Resultado esperado:
# CFOP 6.152 - Transferência para comercialização
# Score: 0.88+ (ALTA/MÉDIA confiança)
```

### 4. Devolução de Compra

```python
item = {
    "uf_emitente": "RJ",
    "uf_destinatario": "SP",
    "descricao_produto": "Devolução de mercadoria com defeito - Mouse USB",
    "ncm": "84716060",
    "consumidor_final": "0",
    "indicador_ie": "1",
    "cfop_informado": "6202"
}

# Resultado esperado:
# CFOP 6.202 - Devolução de compra para comercialização
# Score: 0.85+ (MÉDIA/ALTA confiança)
```

### 5. Venda de Ativo Imobilizado

```python
item = {
    "uf_emitente": "SP",
    "uf_destinatario": "RJ",
    "descricao_produto": "Venda de computador usado do escritório - ativo imobilizado",
    "ncm": "84713012",
    "consumidor_final": "0",
    "indicador_ie": "1",
    "cfop_informado": "6551"
}

# Resultado esperado:
# CFOP 6.551 - Venda de bem do ativo imobilizado
# Score: 0.87+ (ALTA confiança)
```

---

## Exemplos de Validação

### Exemplo 1: Validação com Alta Confiança ✅

```python
import requests

BASE = "http://localhost:8000"

item = {
    "uf_emitente": "SP",
    "uf_destinatario": "RJ",
    "descricao_produto": "Mouse óptico USB para revenda",
    "ncm": "84716060",
    "consumidor_final": "0",
    "indicador_ie": "1",
    "cfop_informado": "6102"
}

response = requests.post(
    f"{BASE}/api/validacao-semantica/validar-item",
    json=item
)

resultado = response.json()
```

**Resposta**:
```json
{
  "status": "CORRETO",
  "mensagem": "CFOP informado está correto (#1 nas sugestões)",
  "cfop_informado": "6102",
  "posicao_ranking": 1,
  "score": 0.9345,
  "sugestoes": [
    {
      "cfop": "6.102",
      "descricao": "Venda de mercadoria adquirida ou recebida de terceiros",
      "score": 0.9345,
      "confianca": "ALTA"
    },
    {
      "cfop": "6.101",
      "descricao": "Venda de produção do estabelecimento",
      "score": 0.8234,
      "confianca": "MÉDIA"
    }
  ]
}
```

**Interpretação**: ✅ CFOP correto, pode prosseguir

---

### Exemplo 2: Divergência Detectada ⚠️

```python
item = {
    "uf_emitente": "SP",
    "uf_destinatario": "SP",
    "descricao_produto": "Venda de notebook produzido pela empresa",
    "ncm": "84713012",
    "consumidor_final": "0",
    "indicador_ie": "1",
    "cfop_informado": "5102"  # INCORRETO
}

response = requests.post(
    f"{BASE}/api/validacao-semantica/validar-item",
    json=item
)
```

**Resposta**:
```json
{
  "status": "DIVERGENTE",
  "mensagem": "CFOP divergente. Sugestão: 5.101 (score: 0.9012)",
  "cfop_informado": "5102",
  "sugestoes": [
    {
      "cfop": "5.101",
      "descricao": "Venda de produção do estabelecimento",
      "score": 0.9012,
      "confianca": "ALTA"
    },
    {
      "cfop": "5.102",
      "descricao": "Venda de mercadoria adquirida ou recebida de terceiros",
      "score": 0.7823,
      "confianca": "MÉDIA"
    }
  ]
}
```

**Interpretação**: ⚠️ CFOP incorreto! Deveria ser 5.101 (produto próprio)

---

### Exemplo 3: Busca Sem CFOP Informado 🔍

```python
item = {
    "uf_emitente": "SP",
    "uf_destinatario": "RS",
    "descricao_produto": "Impressora HP LaserJet para comercialização",
    "ncm": "84433210",
    "consumidor_final": "0",
    "indicador_ie": "1"
    # cfop_informado ausente
}

response = requests.post(
    f"{BASE}/api/validacao-semantica/validar-item",
    json=item
)
```

**Resposta**:
```json
{
  "status": "SUGERIDO",
  "mensagem": "CFOP sugerido: 6.102",
  "cfop_informado": null,
  "sugestoes": [
    {
      "cfop": "6.102",
      "descricao": "Venda de mercadoria adquirida ou recebida de terceiros",
      "score": 0.9123,
      "confianca": "ALTA"
    }
  ]
}
```

**Interpretação**: 💡 Sistema sugere CFOP 6.102 com alta confiança

---

## Padrões de Query

### Como o Sistema Constrói Queries

```python
# Entrada do usuário:
item = {
    "uf_emitente": "SP",
    "uf_destinatario": "RJ",
    "descricao_produto": "Notebook Dell",
    "consumidor_final": "0",
    "indicador_ie": "1"
}

# Query gerada automaticamente:
"""
Operação fiscal com as seguintes características:

Geografia: operação interestadual
UF Origem: SP
UF Destino: RJ

Destinatário: contribuinte do ICMS, não é consumidor final

Produto: Notebook Dell
NCM: [vazio]

Busco o CFOP apropriado para esta operação de venda/saída de mercadoria.
"""
```

### Queries Otimizadas para Casos Específicos

#### 1. Venda com Detalhes Ricos
```python
# ✅ ÓTIMO
"Venda interestadual de notebook Dell Inspiron adquirido de terceiros 
para revenda para empresa contribuinte do ICMS"

# Resultado: Score alto (0.93+)
```

#### 2. Query Minimalista
```python
# ⚠️ ACEITÁVEL
"Venda notebook SP para RJ"

# Resultado: Score médio (0.78-0.85)
```

#### 3. Query Ambígua
```python
# ❌ RUIM
"Produto eletrônico"

# Resultado: Score baixo (<0.70), múltiplas sugestões
```

---

## Análise de Divergências

### Script para Analisar Lote

```python
import pandas as pd
import requests

BASE = "http://localhost:8000"

# 1. Carregar notas com CFOP informado
df = pd.read_csv('notas_fiscais_validadas.csv')

# 2. Validar lote
files = {'arquivo': open('notas_fiscais_validadas.csv', 'rb')}
response = requests.post(
    f"{BASE}/api/validacao-semantica/validar-lote",
    files=files
)

resultado = response.json()

# 3. Analisar divergências
relatorio = resultado['relatorio']

print(f"""
📊 RELATÓRIO DE VALIDAÇÃO
{'='*50}
Total de itens: {relatorio['total_validacoes']}
Corretos: {relatorio['corretos']} ({relatorio['taxa_acerto']}%)
Divergentes: {relatorio['divergentes']} ({relatorio['taxa_divergencia']}%)
Sem sugestão: {relatorio['sem_sugestao']}

Score médio: {relatorio.get('score_medio', 'N/A')}
""")

# 4. Exportar divergências para análise
divergentes = [r for r in resultado['resultados'] if r['status'] == 'DIVERGENTE']

df_divergentes = pd.DataFrame(divergentes)
df_divergentes.to_csv('divergencias_cfop.csv', index=False)

print(f"\n✅ {len(divergentes)} divergências exportadas para 'divergencias_cfop.csv'")
```

### Exemplo de Relatório

```
📊 RELATÓRIO DE VALIDAÇÃO
==================================================
Total de itens: 1.250
Corretos: 1.156 (92.5%)
Divergentes: 87 (7.0%)
Sem sugestão: 7 (0.5%)

Score médio: 0.8923
```

### Análise de Padrões de Divergência

```python
# Agrupar divergências por CFOP
df_div = pd.read_csv('divergencias_cfop.csv')

print("\n🔍 TOP 5 CFOPs DIVERGENTES:\n")
top_div = df_div['cfop_informado'].value_counts().head()

for cfop, count in top_div.items():
    print(f"CFOP {cfop}: {count} divergências")
    
    # Sugestões mais comuns para este CFOP
    sugestoes = df_div[df_div['cfop_informado'] == cfop]['sugestoes'].apply(
        lambda x: x[0]['cfop'] if x else None
    ).value_counts()
    
    print(f"  → Sugestão principal: {sugestoes.index[0]} ({sugestoes.values[0]}x)")
    print()
```

---

## Integração com ERP

### Exemplo: SAP

```python
from pyrfc import Connection

class FiscalAISAPIntegration:
    """Integração FiscalAI v5 com SAP"""
    
    def __init__(self, sap_config, fiscalai_url):
        self.sap = Connection(**sap_config)
        self.fiscalai = fiscalai_url
    
    def validar_nota_fiscal(self, nf_number):
        """Valida CFOP de uma NF no SAP"""
        
        # 1. Buscar dados da NF no SAP
        nf_data = self.sap.call('BAPI_INVOICING_DOCUMENT_READ', {
            'INVOICEDOCNUMBER': nf_number
        })
        
        # 2. Extrair itens
        items = nf_data['IT_ITEMS']
        
        resultados = []
        for item in items:
            # 3. Preparar dados para FiscalAI
            item_data = {
                "uf_emitente": item['UF_SENDER'],
                "uf_destinatario": item['UF_RECEIVER'],
                "descricao_produto": item['MATERIAL_DESC'],
                "ncm": item['NCM'],
                "consumidor_final": item['CONSUMER_FLAG'],
                "indicador_ie": item['IE_INDICATOR'],
                "cfop_informado": item['CFOP']
            }
            
            # 4. Validar no FiscalAI
            response = requests.post(
                f"{self.fiscalai}/api/validacao-semantica/validar-item",
                json=item_data
            )
            
            resultado = response.json()
            resultados.append({
                'item': item['ITEM_NUMBER'],
                'status': resultado['status'],
                'cfop_sap': item['CFOP'],
                'cfop_sugerido': resultado['sugestoes'][0]['cfop'],
                'score': resultado['sugestoes'][0]['score']
            })
        
        return resultados
    
    def atualizar_cfop_divergente(self, nf_number, item_number, novo_cfop):
        """Atualiza CFOP divergente no SAP"""
        
        result = self.sap.call('BAPI_INVOICING_DOCUMENT_CHANGE', {
            'INVOICEDOCNUMBER': nf_number,
            'ITEM_NUMBER': item_number,
            'CFOP': novo_cfop
        })
        
        return result

# Uso
sap_config = {
    'ashost': 'sap.empresa.com',
    'sysnr': '00',
    'client': '100',
    'user': 'user',
    'passwd': 'password'
}

integration = FiscalAISAPIntegration(sap_config, 'http://fiscalai.empresa.com')

# Validar NF
resultados = integration.validar_nota_fiscal('0000000123')

for r in resultados:
    if r['status'] == 'DIVERGENTE':
        print(f"⚠️ Item {r['item']}: CFOP {r['cfop_sap']} → {r['cfop_sugerido']}")
```

### Exemplo: TOTVS Protheus

```python
import requests

class FiscalAITOTVSIntegration:
    """Integração FiscalAI v5 com TOTVS Protheus"""
    
    def __init__(self, totvs_url, totvs_token, fiscalai_url):
        self.totvs_url = totvs_url
        self.totvs_token = totvs_token
        self.fiscalai = fiscalai_url
    
    def validar_pedido_venda(self, pedido_id):
        """Valida CFOPs de um pedido de venda"""
        
        # 1. Buscar pedido no Protheus
        headers = {'Authorization': f'Bearer {self.totvs_token}'}
        
        response = requests.get(
            f"{self.totvs_url}/rest/MATA410/{pedido_id}",
            headers=headers
        )
        
        pedido = response.json()
        
        # 2. Validar cada item
        resultados = []
        for item in pedido['items']:
            item_data = {
                "uf_emitente": pedido['C5_UFORIG'],
                "uf_destinatario": pedido['C5_UFDEST'],
                "descricao_produto": item['C6_DESCRI'],
                "ncm": item['B1_POSIPI'],
                "consumidor_final": pedido['C5_TPFRETE'],
                "indicador_ie": pedido['C5_TIPOCLI'],
                "cfop_informado": item['C6_CF']
            }
            
            # Validar
            response = requests.post(
                f"{self.fiscalai}/api/validacao-semantica/validar-item",
                json=item_data
            )
            
            resultado = response.json()
            resultados.append({
                'item': item['C6_ITEM'],
                'produto': item['C6_PRODUTO'],
                'status': resultado['status'],
                'cfop_atual': item['C6_CF'],
                'sugestao': resultado['sugestoes'][0]
            })
        
        return resultados

# Uso
integration = FiscalAITOTVSIntegration(
    totvs_url='https://totvs.empresa.com:8080',
    totvs_token='xxxx',
    fiscalai_url='http://fiscalai.empresa.com'
)

# Validar pedido
resultados = integration.validar_pedido_venda('000123')

# Exibir alertas
for r in resultados:
    if r['status'] == 'DIVERGENTE':
        print(f"""
        ⚠️ DIVERGÊNCIA DETECTADA
        Item: {r['item']} - {r['produto']}
        CFOP Atual: {r['cfop_atual']}
        Sugestão: {r['sugestao']['cfop']}
        Confiança: {r['sugestao']['confianca']}
        Score: {r['sugestao']['score']}
        """)
```

---

## Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                      FISCALAI v5 - ARQUITETURA                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────┐
│   ERP/SAP   │
│   TOTVS     │ ──────┐
│   Sistema   │       │
└─────────────┘       │
                      │ HTTP/REST
┌─────────────┐       │
│ Interface   │       │
│    Web      │ ──────┤
│  (Colab)    │       │
└─────────────┘       ▼
                 ┌──────────────────┐
                 │   FastAPI        │
                 │   (main.py)      │
                 └──────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌─────────────┐ ┌─────────────────┐
│ Validação    │ │ Chat        │ │ Estatísticas    │
│ Semântica    │ │ Router      │ │ Router          │
│ Router       │ │             │ │                 │
└──────────────┘ └─────────────┘ └─────────────────┘
        │
        ▼
┌──────────────────────┐
│ ValidadorCFOP        │
│ Semântico            │
│ (validacao_          │
│  semantica.py)       │
└──────────────────────┘
        │
        ├──────────────┬─────────────────┐
        │              │                 │
        ▼              ▼                 ▼
┌──────────────┐ ┌────────────┐ ┌──────────────────┐
│   OpenAI     │ │  Pinecone  │ │   Pandas         │
│  Embeddings  │ │   Vector   │ │   (Análise)      │
│              │ │   Store    │ │                  │
└──────────────┘ └────────────┘ └──────────────────┘
        │              │
        └──────┬───────┘
               │
        Busca Semântica
               │
               ▼
        ┌─────────────┐
        │  Resultado  │
        │  Top-K      │
        │  CFOPs      │
        └─────────────┘
```

---

## Fluxo de Dados

```
1. ENTRADA (Item NF)
   ├─ UF Emitente
   ├─ UF Destinatário
   ├─ Descrição Produto
   ├─ NCM
   ├─ Consumidor Final
   ├─ Indicador IE
   └─ CFOP Informado (opcional)
   
2. PROCESSAMENTO
   ├─ Construir query contextual
   ├─ Gerar embedding (OpenAI)
   └─ Buscar similares (Pinecone)
   
3. RESULTADO
   ├─ Top-K CFOPs
   ├─ Scores de confiança
   ├─ Status de validação
   └─ Metadata (descrição, aplicação)
```

---

**FiscalAI v5** - Exemplos e Integrações 🚀
