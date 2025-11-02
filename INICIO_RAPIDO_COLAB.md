# ⚡ Início Rápido - Google Colab (3 minutos)

## 🎯 Para Começar AGORA

### 1️⃣ Abrir Colab
```
https://colab.research.google.com
```

### 2️⃣ Criar Novo Notebook
- Clique em "New notebook"

### 3️⃣ Copiar e Colar

**Célula 1:** Instalar tudo
```python
!pip install -q fastapi uvicorn[standard] pydantic pydantic-settings python-dotenv openai langchain langchain-openai langchain-community pandas openpyxl pyngrok nest-asyncio
```

**Célula 2:** Configurar API Keys (IMPORTANTE!)
```python
import os

# ⚠️ MUDAR PARA SUAS CHAVES!

# OpenAI API Key
os.environ['OPENAI_API_KEY'] = 'sk-proj-sua-chave-aqui'

# ngrok Authtoken (NOVO - Obrigatório!)
os.environ['NGROK_AUTHTOKEN'] = 'seu-ngrok-token-aqui'

print('✅ Configurado!')
```

**🔑 Como obter o ngrok authtoken:**
1. Cadastre-se grátis: https://dashboard.ngrok.com/signup
2. Copie seu token: https://dashboard.ngrok.com/get-started/your-authtoken
3. Cole no código acima

**Célula 3:** Upload e Extrair
```python
# Faça upload do fiscalai-v2-colab.tar.gz via menu Files (📁)
!tar -xzf fiscalai-v2-colab.tar.gz
%cd fiscalai-v2-colab
!mkdir -p data
```

**Célula 4:** RODAR!
```python
!python main.py
```

### 4️⃣ Copiar URL
```
Procure no output:
📡 URL Pública: https://xxxx.ngrok-free.app
```

### 5️⃣ Abrir no Navegador
- Cole a URL no navegador
- Pronto! 🎉

## 📸 Screenshot do Output Esperado

```
╔══════════════════════════════════════════════════════════════╗
║          FiscalAI - Auditor Fiscal Inteligente              ║
║                     v2.0.0                                   ║
╚══════════════════════════════════════════════════════════════╝

🌐 NGROK TUNNEL ATIVO
══════════════════════════════════════════════════════════════
📡 URL Pública: https://1234-56-78-90-12.ngrok-free.app
🔗 Acesse: https://1234-56-78-90-12.ngrok-free.app
══════════════════════════════════════════════════════════════

🚀 Rodando no Google Colab
🌐 Acesse a aplicação em: https://1234-56-78-90-12.ngrok-free.app

INFO:     Started server process [1234]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## ✅ Checklist

- [ ] Colab aberto
- [ ] Células executadas
- [ ] API Key configurada
- [ ] Projeto extraído
- [ ] Servidor rodando
- [ ] URL do ngrok copiada
- [ ] Navegador aberto
- [ ] Página carregou

**Se todos ✅, você está pronto!**

## 🎬 Próximos Passos

### Na Interface Web:

1. **Upload CSVs** (Página Inicial)
   - 202401_NFs_Cabecalho.csv
   - 202401_NFs_Itens.csv
   - CFOP.csv

2. **Inicializar** 
   - Clicar "Iniciar Processamento"
   - Aguardar ~30 segundos

3. **Usar!**
   - 📊 Ver estatísticas
   - 💬 Fazer perguntas
   - ✓ Validar CFOPs

## ⚠️ Problemas Comuns

### "OPENAI_API_KEY não encontrada"
```python
# Execute novamente a Célula 2 com sua chave
os.environ['OPENAI_API_KEY'] = 'sk-proj-XXXXX'
```

### "ngrok authentication failed"
```python
# Você precisa configurar o ngrok authtoken!
# 1. Cadastre-se: https://dashboard.ngrok.com/signup
# 2. Copie token: https://dashboard.ngrok.com/get-started/your-authtoken
# 3. Configure:
import os
os.environ['NGROK_AUTHTOKEN'] = 'seu-token-aqui'
# 4. Execute o servidor novamente
```

### "No such file: fiscalai-v2-colab.tar.gz"
```
1. Clique em 📁 (Files) no menu esquerdo
2. Clique em ↑ (Upload)
3. Selecione o arquivo .tar.gz
4. Aguarde upload completar
5. Execute Célula 3 novamente
```

### "ngrok não funciona"
```python
# Reiniciar runtime:
# Runtime > Restart runtime
# Execute tudo novamente
```

### "Página não carrega"
```
1. Verifique URL copiada está completa
2. Aguarde 10 segundos (pode demorar)
3. Tente em aba anônima
4. Limpe cache do navegador
```

## 💡 Dicas Rápidas

✅ **DO:**
- Use API Key com créditos
- Copie URL completa
- Aguarde servidor iniciar
- Mantenha Colab aberto

❌ **DON'T:**
- Não feche o Colab
- Não pare a célula do servidor
- Não compartilhe API Key
- Não deixe inativo >90min

## 🔄 Para Reiniciar

```python
# Se algo deu errado:
# 1. Stop na célula 4 (botão ⏹️)
# 2. Execute célula 4 novamente
# 3. Nova URL será gerada
```

## 📱 No Mobile

✅ Funciona perfeitamente!
- Interface responsiva
- Todos os recursos funcionam
- Upload de arquivos funciona

## 👥 Compartilhar com Equipe

```
1. Copie URL do ngrok
2. Envie para colegas
3. Todos podem acessar simultaneamente
4. ⚠️ Todos veem os mesmos dados!
```

## ⏱️ Tempo Estimado

| Etapa | Tempo |
|-------|-------|
| Setup Colab | 1 min |
| Upload projeto | 30 seg |
| Instalar deps | 30 seg |
| Iniciar server | 30 seg |
| **TOTAL** | **3 min** |

## 🎁 Bônus: One-Liner

Cole tudo de uma vez no Colab:

```python
# Instalar
!pip install -q fastapi uvicorn[standard] pydantic pydantic-settings python-dotenv openai langchain langchain-openai langchain-community pandas openpyxl pyngrok nest-asyncio

# Configurar
import os
os.environ['OPENAI_API_KEY'] = 'sk-proj-SUA-CHAVE-AQUI'

# Após upload do .tar.gz:
!tar -xzf fiscalai-v2-colab.tar.gz && cd fiscalai-v2-colab && mkdir -p data && python main.py
```

## 📞 Precisa de Ajuda?

Consulte:
- 📚 **GUIA_COLAB_NGROK.md** - Guia completo
- 🧪 **GUIA_TESTE.md** - Como testar
- 📖 **README.md** - Documentação

---

## 🎉 Pronto em 3 Minutos!

1. ⚡ Abrir Colab
2. ⚡ Executar células
3. ⚡ Copiar URL
4. ⚡ USAR!

**Simples assim!** 🚀

---

**FiscalAI v2.0** - Do Colab para produção em minutos! 🌐
