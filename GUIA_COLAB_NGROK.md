# 🌐 Guia Completo - Google Colab + ngrok

## Por que usar Colab + ngrok?

✅ **Vantagens:**
- Não precisa de servidor próprio
- Acesso público via URL https://
- Funciona de qualquer lugar do mundo
- Gratuito
- Não precisa instalar nada no computador
- GPU disponível (se necessário no futuro)

## 📋 Pré-requisitos

1. Conta Google (para usar Colab)
2. API Key da OpenAI (com créditos)
3. Arquivos CSV das notas fiscais
4. Arquivo `fiscalai-v2.tar.gz`

## 🚀 Passo a Passo Completo

### Passo 1: Abrir o Google Colab

1. Acesse: https://colab.research.google.com
2. Clique em "File" → "Upload notebook"
3. Faça upload do arquivo `FiscalAI_Colab.ipynb`

**OU**

1. Clique em "New notebook"
2. Copie e cole o conteúdo do notebook

### Passo 2: Fazer Upload do Projeto

1. No menu lateral esquerdo, clique no ícone 📁 (Files)
2. Clique em "Upload to session storage"
3. Selecione o arquivo `fiscalai-v2.tar.gz`
4. Aguarde o upload completar

### Passo 3: Executar as Células

#### Célula 1: Instalar Dependências
```python
!pip install -q fastapi uvicorn[standard] pydantic pydantic-settings python-dotenv
!pip install -q openai langchain langchain-openai langchain-community
!pip install -q pandas openpyxl
!pip install -q pyngrok nest-asyncio
```

**Tempo:** ~30 segundos  
**Resultado esperado:** Instalação silenciosa (flag `-q`)

#### Célula 2: Configurar API Key
```python
import os

# ⚠️ SUBSTITUA PELA SUA API KEY!
os.environ['OPENAI_API_KEY'] = 'sk-proj-xxxxx...'

# Verificar
if os.environ['OPENAI_API_KEY'] == 'sua-api-key-aqui':
    print('⚠️ ATENÇÃO: Configure sua API Key!')
else:
    print('✅ API Key configurada!')
```

**IMPORTANTE:** 
- Substitua `sua-api-key-aqui` pela sua chave real
- Mantenha a chave em segredo (não compartilhe o notebook com a chave)

#### Célula 3: Extrair Projeto
```python
!tar -xzf fiscalai-v2.tar.gz
%cd fiscalai-v2
!ls -la
```

**Resultado esperado:**
```
main.py
config.py
agente_cfop.py
requirements.txt
models/
routes/
services/
static/
templates/
```

#### Célula 4: Iniciar Servidor
```python
!mkdir -p data
!python main.py
```

**Resultado esperado:**
```
╔══════════════════════════════════════════════════════════════╗
║          FiscalAI - Auditor Fiscal Inteligente              ║
║                     v2.0.0                                   ║
╚══════════════════════════════════════════════════════════════╝

🌐 NGROK TUNNEL ATIVO
══════════════════════════════════════════════════════════════
📡 URL Pública: https://xxxx-xx-xx-xx-xx.ngrok-free.app
🔗 Acesse: https://xxxx-xx-xx-xx-xx.ngrok-free.app
══════════════════════════════════════════════════════════════

INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**⚠️ IMPORTANTE:**
- **Copie a URL do ngrok** (a que começa com `https://`)
- Esta URL é pública - qualquer pessoa com o link pode acessar
- A URL muda cada vez que você reinicia

### Passo 4: Acessar o Sistema

1. Abra uma nova aba no navegador
2. Cole a URL do ngrok
3. Você verá a página inicial do FiscalAI! 🎉

### Passo 5: Fazer Upload dos CSVs

1. Na página inicial, clique nas áreas de upload
2. Selecione os 3 arquivos:
   - `202401_NFs_Cabecalho.csv`
   - `202401_NFs_Itens.csv`
   - `CFOP.csv`
3. Aguarde o upload de cada arquivo (✓ verde)
4. Clique em "Iniciar Processamento"
5. Aguarde ~20-30 segundos

### Passo 6: Usar o Sistema

Após a inicialização, navegue pelas páginas:

- 📊 **Estatísticas** - Ver dashboard com gráficos
- 💬 **Chat IA** - Fazer perguntas sobre as notas
- ✓ **Validação** - Validar CFOPs específicos

## 🔄 Workflow Típico

```
1. Abrir Colab
2. Executar células (1-4)
3. Copiar URL do ngrok
4. Acessar no navegador
5. Fazer upload dos CSVs
6. Inicializar sistema
7. Usar as funcionalidades
8. [Trabalhar...]
9. Quando terminar: Stop no Colab
```

## 💡 Dicas Importantes

### Segurança
- 🔒 A URL do ngrok é pública - não compartilhe com desconhecidos
- 🔑 Não commite notebooks com API Keys
- 🚫 Não deixe o servidor rodando sem supervisão

### Performance
- ⏱️ Sessões do Colab expiram após ~90 minutos de inatividade
- 💾 Dados são temporários (perdidos ao resetar)
- 🔄 Para continuar trabalhando, execute tudo novamente

### Custos
- 🆓 Google Colab é gratuito
- 🆓 ngrok é gratuito (com limitações)
- 💰 OpenAI API cobra por uso (GPT-4)

### Produtividade
- 📱 O sistema funciona em mobile
- 🌍 Acesse de qualquer lugar
- 👥 Compartilhe a URL com colegas (com cuidado)

## 🛠️ Solução de Problemas

### Problema: "OPENAI_API_KEY não encontrada"

**Solução:**
1. Verifique se executou a célula 2
2. Verifique se substituiu a chave corretamente
3. Execute novamente a célula 2

### Problema: "Erro ao instalar dependências"

**Solução:**
```python
# Reiniciar runtime
# Runtime > Restart runtime
# Executar novamente a célula 1
```

### Problema: "ngrok não inicia"

**Solução:**
1. Verifique sua conexão com internet
2. Reinicie o runtime
3. Execute novamente todas as células

### Problema: "Sessão expirou"

**Solução:**
1. Execute novamente a célula 4 (servidor)
2. Nova URL do ngrok será gerada
3. Use a nova URL

### Problema: "Upload CSV muito lento"

**Solução:**
- Uploads no Colab são lentos
- Considere fazer o upload diretamente pela interface web
- Arquivos grandes (>10MB) podem demorar

### Problema: "Chat não responde"

**Solução:**
1. Verifique créditos na conta OpenAI
2. Verifique conexão com internet
3. Aguarde até 30 segundos (GPT-4 pode ser lento)

## 📊 Limites e Restrições

### Google Colab (Free)
- ⏱️ Tempo de execução: 12 horas máximo
- 💾 Armazenamento: Temporário
- 🔄 Inatividade: 90 minutos

### ngrok (Free)
- 🌐 URL pública temporária
- 🔄 URL muda a cada reinicialização
- ⚡ Limite de conexões simultâneas
- ⏱️ Túnel expira após 2 horas (precisa reiniciar)

### OpenAI API
- 💰 Cobra por token usado
- ⏱️ Rate limits aplicam-se
- 🔑 Precisa de créditos na conta

## 🎯 Melhor Prática

### Para Uso Diário:

```
1. Manhã:
   - Abrir Colab
   - Executar células
   - Copiar URL ngrok
   - Salvar URL em bookmark
   
2. Durante o dia:
   - Usar a URL salva
   - Fazer análises
   - Gerar relatórios
   
3. Noite:
   - Exportar dados importantes
   - Stop no Colab
```

### Para Apresentações:

```
1. Antes da apresentação:
   - Iniciar Colab 15 min antes
   - Testar URL
   - Fazer upload dos CSVs
   - Preparar exemplos
   
2. Durante apresentação:
   - Usar URL pública
   - Mostrar funcionalidades
   - Responder perguntas
   
3. Depois:
   - Exportar dados
   - Stop no Colab
```

## 🆘 FAQ

**P: Posso usar sem internet?**  
R: Não, o sistema precisa de conexão para OpenAI API e ngrok.

**P: Posso ter múltiplos usuários?**  
R: Sim, mas todos verão os mesmos dados. O sistema não tem autenticação.

**P: Os dados ficam salvos?**  
R: Não, dados no Colab são temporários. Faça backup se necessário.

**P: Posso usar GPU?**  
R: Não é necessário para o FiscalAI atual, mas está disponível no Colab.

**P: Quanto custa?**  
R: Colab e ngrok são gratuitos. OpenAI API cobra por uso (~$0.01-0.10 por consulta).

**P: É seguro?**  
R: Para desenvolvimento, sim. Para produção com dados sensíveis, considere servidor dedicado.

**P: Posso personalizar?**  
R: Sim! Edite os arquivos e reinicie o servidor.

---

## 📞 Suporte

- 📚 Documentação completa: README.md
- 🧪 Guia de testes: GUIA_TESTE.md
- 📦 Resumo do upgrade: RESUMO_UPGRADE.md

---

**FiscalAI v2.0** - Rodando no Colab com ngrok! 🚀
