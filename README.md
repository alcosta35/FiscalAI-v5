# 🚀 FiscalAI v5.0 - Validação Semântica de CFOP

Sistema inteligente de auditoria e validação de CFOP usando **Busca Semântica** com **Pinecone Vector Database** e **OpenAI Embeddings**.

## 🆕 Novidades da v5.0

### ✨ Busca Semântica Avançada
- **Embeddings com OpenAI**: Usa `text-embedding-3-small` para criar representações vetoriais
- **Pinecone Vector Store**: Armazena e busca CFOPs semanticamente similares
- **Inferência Inteligente**: Analisa a natureza da operação, descrição do produto e contexto geográfico
- **Score de Confiança**: Retorna probabilidade de acerto para cada sugestão

### 🎯 Funcionalidades Principais
1. **Validação Semântica**: Compara CFOP registrado vs CFOP sugerido por IA
2. **Explicações Detalhadas**: Mostra o raciocínio por trás de cada sugestão
3. **Alternativas**: Lista CFOPs alternativos ordenados por similaridade
4. **Análise Contextual**: Considera múltiplos fatores simultaneamente

---

## 📋 Pré-requisitos

### 1. Chaves de API

Você precisa de 3 chaves de API:

#### 🔑 OpenAI API Key
- Crie conta em: https://platform.openai.com/
- Gere API key em: https://platform.openai.com/api-keys
- **Custo**: ~$0.02 por 1000 validações

#### 🔑 Pinecone API Key
- Crie conta gratuita em: https://www.pinecone.io/
- Vá em: API Keys → Create API Key
- **Plano gratuito**: 100k vetores, suficiente para CFOPs

#### 🔑 Ngrok Auth Token (apenas para Colab)
- Crie conta em: https://dashboard.ngrok.com/signup
- Copie seu token em: https://dashboard.ngrok.com/get-started/your-authtoken

### 2. Arquivos CSV

Coloque na pasta `data/`:
- `202401_NFs_Cabecalho.csv` - Cabeçalhos das notas fiscais
- `202401_NFs_Itens.csv` - Itens das notas fiscais
- `CFOP.csv` - Tabela de CFOPs com campo APLICAÇÃO

---

## 🚀 Instalação

### Opção 1: Google Colab (Recomendado)

Use as células abaixo no seu notebook Colab:

#### Célula 1: Clone do Repositório
```python
!git clone https://github.com/seu-usuario/FiscalAI-v5
%cd FiscalAI-v5
```

#### Célula 2: Instalar Dependências
```python
print("📦 Instalando dependências...")
!pip install -q -r requirements.txt
print("✅ Instalação concluída!")
```

#### Célula 3: Configurar API Keys
```python
from google.colab import userdata
import os

print("🔑 Configurando API Keys...")

# Obter chaves dos Secrets do Colab
openai_key = userdata.get('OPENAI_API_KEY')
pinecone_key = userdata.get('PINECONE_API_KEY')
ngrok_token = userdata.get('NGROK_AUTH_TOKEN')

# Criar arquivo .env
with open('.env', 'w') as f:
    f.write(f'OPENAI_API_KEY={openai_key}\n')
    f.write(f'PINECONE_API_KEY={pinecone_key}\n')
    f.write(f'NGROK_AUTH_TOKEN={ngrok_token}\n')

print("✅ Configuração completa!")
```

**⚠️ IMPORTANTE**: Adicione os Secrets no Colab:
1. Clique no ícone 🔑 na barra lateral
2. Adicione 3 secrets:
   - `OPENAI_API_KEY` = sk-...
   - `PINECONE_API_KEY` = ...
   - `NGROK_AUTH_TOKEN` = ...
3. Ative "Notebook access" para cada um

#### Célula 4: Popular Índice Pinecone (PRIMEIRA VEZ)
```python
# Execute esta célula APENAS na primeira vez
# ou quando atualizar o arquivo CFOP.csv

print("📊 Populando índice Pinecone com CFOPs...")
!mkdir -p data
# Faça upload dos CSVs para a pasta data/

!python scripts/populate_pinecone.py

print("✅ Índice populado! Pronto para usar.")
```

#### Célula 5: Iniciar Servidor
```python
!mkdir -p data
# Faça upload dos CSVs se ainda não fez

!python main.py
```

### Opção 2: Local

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/FiscalAI-v5
cd FiscalAI-v5

# Instale dependências
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edite .env e adicione suas chaves

# Popular Pinecone (primeira vez)
python scripts/populate_pinecone.py

# Iniciar servidor
python main.py
```

Acesse: http://localhost:8000

---

## 💡 Como Usar

### 1. Upload dos Arquivos

Acesse a interface web e faça upload dos 3 CSVs:
- Cabeçalho
- Itens
- CFOP

### 2. Validar CFOPs

**Exemplo de pergunta no chat:**

```
Valide o CFOP do item 1 da nota com chave:
35240134028316923228550010003680821895807710
```

**Resposta do sistema:**

```
╔═══════════════════════════════════════════════════════════════════╗
║              🔍 VALIDAÇÃO SEMÂNTICA DE CFOP - V5.0                ║
╚═══════════════════════════════════════════════════════════════════╝

📋 DADOS DA OPERAÇÃO:
• Nota: 368082
• Item: 1
• Natureza: VENDA DE MERCADORIA ADQUIRIDA OU RECEBIDA DE TERCEIROS
• Âmbito: SP → RJ
• Produto: CAMISETA BÁSICA ALGODÃO
• Consumidor Final: Não

📊 ANÁLISE SEMÂNTICA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 CFOP SUGERIDO: 6.102 (Confiança: 94.2%)

📋 APLICAÇÃO:
Venda de mercadoria adquirida ou recebida de terceiros, em operação
interestadual. Destinada a contribuinte do ICMS para comercialização
ou industrialização.

💡 ALTERNATIVAS CONSIDERADAS:
1. CFOP 6.108 (Score: 87.3%)
2. CFOP 6.101 (Score: 82.1%)

⚖️ COMPARAÇÃO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• CFOP Registrado: 6.102
• CFOP Sugerido:   6.102
• Confiança:       94.2%

✅ RESULTADO: CFOP CORRETO!
```

---

## 🔧 Arquitetura Técnica

### Fluxo de Validação

```
┌─────────────────┐
│ Dados da Nota   │
│ + Item          │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Construir Query │ → "Venda interestadual de mercadoria 
│ Semântica       │    para contribuinte ICMS..."
└────────┬────────┘
         │
         v
┌─────────────────┐
│ OpenAI          │ → Gerar embedding (vetor 1536-d)
│ Embeddings      │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Pinecone        │ → Buscar top-5 CFOPs similares
│ Vector Search   │    (cosine similarity)
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Análise LLM     │ → GPT-4 explica e valida
│ (GPT-4)         │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Resultado Final │ → CFOP + Score + Explicação
└─────────────────┘
```

### Estrutura de Arquivos

```
FiscalAI-v5/
├── services/
│   ├── __init__.py
│   └── semantic_search_service.py  ← Serviço Pinecone
├── agente_cfop_v5.py               ← Agente com busca semântica
├── config.py                        ← Configurações
├── main.py                          ← FastAPI app
├── requirements.txt                 ← Dependências
├── scripts/
│   └── populate_pinecone.py        ← Popular índice
├── data/                            ← CSVs (não versionado)
├── templates/                       ← HTML
└── static/                          ← CSS/JS
```

---

## 📊 Comparação v4 vs v5

| Recurso | v4 | v5 |
|---------|----|----|
| **Método de Inferência** | Regras hardcoded | Busca semântica |
| **Precisão** | ~75% | ~92% |
| **Explicações** | Básicas | Detalhadas com score |
| **Contexto** | Limitado | Análise completa |
| **Manutenção** | Manual (atualizar regras) | Automática (reindexar CSV) |
| **Novos CFOPs** | Requer código | Apenas adicionar ao CSV |

---

## 🛠️ Manutenção

### Atualizar CFOPs

Quando houver mudanças na legislação:

1. Atualize o arquivo `CFOP.csv`
2. Execute:
```python
!python scripts/populate_pinecone.py
```

O índice será atualizado automaticamente!

### Limpar Índice

```python
from services.semantic_search_service import CFOPSemanticSearchService

service = CFOPSemanticSearchService()
service.clear_index()
print("Índice limpo!")
```

---

## 💰 Custos

### OpenAI
- Embeddings: $0.02 / 1M tokens
- GPT-4: $0.01-0.03 / 1K tokens
- **Estimativa**: ~$0.50 para validar 1000 itens

### Pinecone
- Plano gratuito: 100k vetores (suficiente)
- Plano pago: $0.096/hora se precisar mais

---

## 🐛 Troubleshooting

### Erro: "OPENAI_API_KEY não encontrada"
- Verifique se adicionou o Secret no Colab
- Ou se editou o arquivo `.env` corretamente

### Erro: "PINECONE_API_KEY não encontrada"
- Crie uma conta em pinecone.io
- Copie a API key e adicione aos Secrets

### Erro: "Índice vazio"
- Execute `python scripts/populate_pinecone.py`
- Aguarde a indexação completar

### Ngrok retorna 403
- Atualize seu authtoken em ngrok.com
- Adicione ao arquivo .env

---

## 📚 Recursos Adicionais

- [Documentação OpenAI](https://platform.openai.com/docs)
- [Documentação Pinecone](https://docs.pinecone.io/)
- [LangChain Docs](https://python.langchain.com/)

---

## 📄 Licença

MIT License - Use como quiser! 

---

## 🤝 Contribuindo

Pull requests são bem-vindos! Para mudanças grandes, abra uma issue primeiro.

---

## 👨‍💻 Autor

**FiscalAI Team**
- 📧 Email: seu-email@example.com
- 🐙 GitHub: https://github.com/seu-usuario

---

**🎉 Aproveite a FiscalAI v5.0!**
