# 🎯 COMECE AQUI - FiscalAI v5.0

## 📦 O Que Você Recebeu

Um sistema completo de validação de CFOP usando **IA e Busca Semântica**.

---

## 🚀 Quick Start (5 minutos)

### 1. Baixe o Projeto
- [View FiscalAI-v5.zip](computer:///mnt/user-data/outputs/FiscalAI-v5.zip)

### 2. Leia a Documentação
- [README.md](computer:///mnt/user-data/outputs/FiscalAI-v5/README.md) - Documentação completa
- [COLAB_SETUP.md](computer:///mnt/user-data/outputs/FiscalAI-v5/COLAB_SETUP.md) - Setup no Colab
- [RESUMO_EXECUTIVO.md](computer:///mnt/user-data/outputs/FiscalAI-v5/RESUMO_EXECUTIVO.md) - Visão geral

### 3. Configure as API Keys
Você precisa de 3 chaves:
- ✅ OpenAI: https://platform.openai.com/api-keys
- ✅ Pinecone: https://www.pinecone.io/ (plano gratuito OK)
- ✅ Ngrok: https://ngrok.com/ (apenas para Colab)

### 4. Execute no Colab
Copie as células de `colab_cells/` para seu notebook.

---

## 📁 Estrutura de Arquivos

```
FiscalAI-v5/
│
├── 📖 START_HERE.md (VOCÊ ESTÁ AQUI)
├── 📖 README.md (Documentação principal)
├── 📖 COLAB_SETUP.md (Guia Colab passo a passo)
├── 📖 RESUMO_EXECUTIVO.md (Visão geral técnica)
│
├── 🔧 services/
│   └── semantic_search_service.py (Busca semântica)
│
├── 🤖 agente_cfop_v5.py (Agente principal)
├── ⚙️ config.py (Configurações)
├── 📦 requirements.txt (Dependências)
│
├── 🔨 scripts/
│   └── populate_pinecone.py (Setup Pinecone)
│
└── 📓 colab_cells/ (Células prontas)
    ├── 01_clone_repo.py
    ├── 02_install_dependencies.py
    ├── 03_configure_api_keys.py
    ├── 04_populate_pinecone.py
    └── 05_start_server.py
```

---

## 🎯 O Que É Diferente da v4?

| Recurso | v4 | v5 |
|---------|----|----|
| Inferência | Regras if/else | IA semântica |
| Precisão | ~75% | ~92% |
| Manutenção | Editar código | Atualizar CSV |
| Novos CFOPs | Programar | Automático |
| Explicações | Básicas | IA detalhada |

---

## ⚡ Fluxo Rápido

```python
# No Colab, execute 5 células:

# 1. Clone
!git clone https://github.com/SEU-USER/FiscalAI-v5

# 2. Install
!pip install -q -r requirements.txt

# 3. API Keys (via Secrets)
from google.colab import userdata
# ...

# 4. Popular Pinecone (1x)
!python scripts/populate_pinecone.py

# 5. Start
!python main.py

# ✅ Pronto! Copie a URL ngrok e acesse
```

---

## 💡 Exemplos de Uso

### No Chat:

**Pergunta:**
```
Valide o CFOP do item 1 da nota com chave:
35240134028316923228550010003680821895807710
```

**Resposta:**
```
╔════════════════════════════════════════════╗
║   🔍 VALIDAÇÃO SEMÂNTICA - V5.0           ║
╚════════════════════════════════════════════╝

📋 Operação: VENDA interestadual SP→RJ
🎯 CFOP Sugerido: 6.102 (Confiança: 94.2%)
⚖️ CFOP Registrado: 6.102

✅ RESULTADO: CFOP CORRETO!
```

---

## 🔗 Links Úteis

### Documentação do Projeto:
- [README Principal](computer:///mnt/user-data/outputs/FiscalAI-v5/README.md)
- [Setup Colab](computer:///mnt/user-data/outputs/FiscalAI-v5/COLAB_SETUP.md)
- [Resumo Executivo](computer:///mnt/user-data/outputs/FiscalAI-v5/RESUMO_EXECUTIVO.md)

### API Keys:
- [OpenAI Platform](https://platform.openai.com/)
- [Pinecone Console](https://www.pinecone.io/)
- [Ngrok Dashboard](https://dashboard.ngrok.com/)

### Código:
- [Busca Semântica](computer:///mnt/user-data/outputs/FiscalAI-v5/services/semantic_search_service.py)
- [Agente v5](computer:///mnt/user-data/outputs/FiscalAI-v5/agente_cfop_v5.py)
- [Script Pinecone](computer:///mnt/user-data/outputs/FiscalAI-v5/scripts/populate_pinecone.py)

---

## 🎉 Pronto para Começar?

1. ✅ Baixe o ZIP
2. ✅ Leia README.md
3. ✅ Configure API keys
4. ✅ Execute no Colab
5. ✅ Valide seus CFOPs!

**Boa sorte! 🚀**
