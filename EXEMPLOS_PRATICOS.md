# 💼 EXEMPLOS PRÁTICOS - FiscalAI v5.0

## 🎯 Casos de Uso Reais

### Exemplo 1: Validação Simples

**Pergunta:**
```
Valide o CFOP do primeiro item da nota 368082
```

**O Que Acontece:**
1. Sistema busca a nota 368082
2. Extrai dados do item 1
3. Gera query semântica
4. Busca no Pinecone
5. GPT-4 explica resultado

**Resposta:**
```
╔═══════════════════════════════════════════════════════════════════╗
║              🔍 VALIDAÇÃO SEMÂNTICA DE CFOP - V5.0                ║
╚═══════════════════════════════════════════════════════════════════╝

📋 DADOS DA OPERAÇÃO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Nota Fiscal: 368082
• Item: 1
• Natureza: VENDA DE MERCADORIA ADQUIRIDA OU RECEBIDA DE TERCEIROS
• Âmbito: SP → RJ
• Produto: CAMISETA BÁSICA 100% ALGODÃO TAMANHO M
• Consumidor Final: Não

📊 ANÁLISE SEMÂNTICA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 CFOP SUGERIDO: 6.102 (Confiança: 94.2%)

📋 APLICAÇÃO:
Venda de mercadoria adquirida ou recebida de terceiros em operação
interestadual, destinada a contribuinte do ICMS para comercialização
ou industrialização.

💡 ALTERNATIVAS CONSIDERADAS:
1. CFOP 6.108 (Score: 87.3%) - Venda para não contribuinte
2. CFOP 6.101 (Score: 82.1%) - Venda de produção própria

⚖️ COMPARAÇÃO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• CFOP Registrado: 6.102
• CFOP Sugerido:   6.102
• Confiança:       94.2%

✅ RESULTADO: CFOP CORRETO!
```

---

### Exemplo 2: Divergência Detectada

**Pergunta:**
```
Valide o CFOP do item 2 da nota com chave
35240134028316923228550010003680821895807710
```

**Resposta com Divergência:**
```
⚖️ COMPARAÇÃO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• CFOP Registrado: 5.102
• CFOP Sugerido:   6.102
• Confiança:       94.2%

⚠️ DIVERGÊNCIA DETECTADA!

🔍 ANÁLISE:
A operação é claramente INTERESTADUAL (SP → RJ), mas o CFOP 
registrado (5.102) é para operações INTERNAS.

💡 RECOMENDAÇÃO:
Alterar o CFOP de 5.102 para 6.102

📋 JUSTIFICATIVA:
- UF Emitente (SP) ≠ UF Destinatário (RJ)
- Operações interestaduais devem usar série 6xxx
- CFOP 6.102 = Venda interestadual de mercadoria de terceiros
```

---

### Exemplo 3: Análise de Múltiplos Itens

**Pergunta:**
```
Liste todos os itens da nota 368082 e valide cada CFOP
```

**Resposta:**
```
📦 ANÁLISE COMPLETA - NOTA 368082
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Item 1: CAMISETA BÁSICA
• CFOP Registrado: 6.102
• CFOP Sugerido:   6.102 (94.2%)
• Status: ✅ CORRETO

Item 2: CALÇA JEANS  
• CFOP Registrado: 6.102
• CFOP Sugerido:   6.102 (92.8%)
• Status: ✅ CORRETO

Item 3: TÊNIS ESPORTIVO
• CFOP Registrado: 5.102
• CFOP Sugerido:   6.102 (93.1%)
• Status: ⚠️ DIVERGÊNCIA

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 RESUMO:
• Total de itens: 3
• Corretos: 2 (66.7%)
• Divergências: 1 (33.3%)

🚨 ITENS PARA REVISÃO:
• Item 3 - Alterar de 5.102 para 6.102
```

---

### Exemplo 4: Busca por Contexto

**Pergunta:**
```
Qual CFOP usar para venda de computador de SP para empresa em MG
que vai revender?
```

**Resposta:**
```
🔍 ANÁLISE CONTEXTUAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 CONTEXTO IDENTIFICADO:
• Tipo: VENDA
• Âmbito: INTERESTADUAL (SP → MG)
• Produto: Computador (mercadoria)
• Destinatário: Empresa contribuinte
• Finalidade: Revenda (comercialização)

🎯 CFOP RECOMENDADO: 6.102 (Confiança: 96.5%)

📝 DESCRIÇÃO:
Venda de mercadoria adquirida ou recebida de terceiros em operação
interestadual.

✅ APLICAÇÃO:
Use este CFOP quando:
• Vender mercadoria que você comprou de terceiros
• Operação entre estados diferentes
• Destinatário é contribuinte do ICMS
• Finalidade é comercialização/industrialização

❌ NÃO USE quando:
• Venda dentro do mesmo estado (use 5.102)
• Produto industrializado por você (use 6.101)
• Destinatário não é contribuinte (use 6.108)
```

---

### Exemplo 5: Comparação de Alternativas

**Pergunta:**
```
Quais CFOPs possíveis para devolução de compra de mercadoria
recebida de SP, estou no RJ?
```

**Resposta:**
```
🔍 BUSCA SEMÂNTICA - TOP 5 CFOPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🥇 OPÇÃO 1: CFOP 6.202 (Score: 95.3%)
📋 Devolução de compra para comercialização
✅ Melhor opção para devolver mercadoria adquirida para revenda

🥈 OPÇÃO 2: CFOP 6.201 (Score: 89.7%)
📋 Devolução de compra para industrialização
⚠️ Use apenas se a mercadoria seria usada na produção

🥉 OPÇÃO 3: CFOP 6.411 (Score: 72.1%)
📋 Devolução de venda de produção do estabelecimento
❌ Não aplicável - este é para VENDA, não compra

🏅 OPÇÃO 4: CFOP 6.556 (Score: 65.2%)
📋 Devolução de compra de material de uso/consumo
⚠️ Use apenas para material não destinado a revenda

🏅 OPÇÃO 5: CFOP 5.202 (Score: 60.8%)
📋 Devolução interna de compra
❌ Não aplicável - operação é interestadual (SP→RJ)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 RECOMENDAÇÃO FINAL:
Use CFOP 6.202 se a mercadoria era para comercialização
Use CFOP 6.201 se era para industrialização
```

---

### Exemplo 6: Análise Estatística

**Pergunta:**
```
Quais os 10 CFOPs mais usados nas notas carregadas?
```

**Resposta:**
```
📊 TOP 10 CFOPs MAIS UTILIZADOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 5.102 - 3,254 itens (32.5%)
   Venda interna de mercadoria de terceiros

2. 6.102 - 2,187 itens (21.9%)
   Venda interestadual de mercadoria de terceiros

3. 5.101 - 1,543 itens (15.4%)
   Venda interna de produção própria

4. 6.108 - 982 itens (9.8%)
   Venda interestadual a não contribuinte

5. 5.405 - 654 itens (6.5%)
   Venda interna de produção própria para não contribuinte

6. 6.101 - 421 itens (4.2%)
   Venda interestadual de produção própria

7. 5.202 - 298 itens (3.0%)
   Devolução interna de compra

8. 6.202 - 187 itens (1.9%)
   Devolução interestadual de compra

9. 5.556 - 143 itens (1.4%)
   Compra de material para uso ou consumo

10. 6.556 - 98 itens (1.0%)
    Compra interestadual de material para uso

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 ANÁLISE:
• Total de itens analisados: 10,000
• CFOPs únicos encontrados: 87
• Concentração: Top 3 representam 69.8% das operações
```

---

## 🎓 Dicas de Uso

### ✅ Melhores Práticas:

1. **Seja Específico:**
   ```
   ✅ "Valide o CFOP do item 3 da nota 368082"
   ❌ "Valide essa nota"
   ```

2. **Use Chave Completa:**
   ```
   ✅ "nota com chave 35240134028316923228550010003680821895807710"
   ❌ "nota 35240..."
   ```

3. **Contexto Completo:**
   ```
   ✅ "venda interestadual de computador para revenda"
   ❌ "venda de produto"
   ```

### ⚡ Atalhos:

- "primeira nota" = índice 0
- "quinta nota" = índice 4  
- "item 1" = primeiro item
- "últimos 10 CFOPs" = tail(10)

---

## 💡 Casos Especiais

### Devolução de Venda:
```
Operação original: 5.102 (venda interna)
Devolução: 1.202 (devolução de venda interna)

Operação original: 6.102 (venda interestadual)
Devolução: 2.202 (devolução de venda interestadual)
```

### Consumidor Final:
```
Contribuinte ICMS → 6.102
Não contribuinte → 6.108
Consumidor final → 6.108
```

### Produção Própria vs Terceiros:
```
Fabricou o produto → X.101
Comprou para revender → X.102
```

---

## 🔍 Comandos Úteis

```python
# Validar item específico
"Valide o CFOP do item 2 da nota 123456"

# Listar todos os itens
"Liste os itens da nota 123456"

# Buscar por chave
"Busque a nota com chave 352401340283..."

# Análise estatística
"Mostre os CFOPs mais usados"

# Validação em lote
"Valide todos os itens da nota 123456"

# Busca semântica
"Qual CFOP para venda de equipamento para indústria no PR?"
```

---

**🎉 Pronto para usar!**
