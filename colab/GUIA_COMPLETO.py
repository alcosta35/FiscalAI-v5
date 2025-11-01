# ==============================================================================
# GUIA RÁPIDO: FiscalAI V5 no Google Colab
# ==============================================================================

"""
📚 GUIA COMPLETO DE EXECUÇÃO NO GOOGLE COLAB

═══════════════════════════════════════════════════════════════════════════════
🎯 OBJETIVO
═══════════════════════════════════════════════════════════════════════════════

Este notebook executa o FiscalAI V5 - um sistema de validação de CFOP com 
busca semântica usando Pinecone Vector Store e OpenAI Embeddings.

═══════════════════════════════════════════════════════════════════════════════
📋 REQUISITOS PRÉVIOS
═══════════════════════════════════════════════════════════════════════════════

Antes de começar, você precisa ter:

✅ 1. Conta OpenAI (https://platform.openai.com/)
   → Crie uma API key em: https://platform.openai.com/api-keys
   → Formato: sk-...

✅ 2. Conta Pinecone (https://www.pinecone.io/) - GRATUITA!
   → Crie conta e faça login
   → Vá em API Keys e copie sua key
   → Formato: p...

✅ 3. Conta Ngrok (https://ngrok.com/) - GRATUITA!
   → Crie conta em: https://dashboard.ngrok.com/signup
   → Copie authtoken em: https://dashboard.ngrok.com/get-started/your-authtoken
   → Formato: 2...

✅ 4. Arquivos CSV:
   → CFOP.csv (tabela de códigos CFOP)
   → 202401_NFs_Cabecalho.csv (opcional para testes)
   → 202401_NFs_Itens.csv (opcional para testes)

═══════════════════════════════════════════════════════════════════════════════
🚀 PASSO A PASSO
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│ PARTE 1: CONFIGURAÇÃO INICIAL (fazer uma vez)                              │
└─────────────────────────────────────────────────────────────────────────────┘

1️⃣ Adicionar Secrets no Colab

   a) Clique no ícone 🔑 (chave) na barra lateral esquerda
   
   b) Adicione 3 secrets:
   
      ┌──────────────────────────────────────────┐
      │ Nome: OPENAI_API_KEY                     │
      │ Valor: sk-...                            │
      │ [✓] Notebook access                      │
      └──────────────────────────────────────────┘
      
      ┌──────────────────────────────────────────┐
      │ Nome: PINECONE_API_KEY                   │
      │ Valor: p...                              │
      │ [✓] Notebook access                      │
      └──────────────────────────────────────────┘
      
      ┌──────────────────────────────────────────┐
      │ Nome: NGROK_AUTH_TOKEN                   │
      │ Valor: 2...                              │
      │ [✓] Notebook access                      │
      └──────────────────────────────────────────┘

2️⃣ Executar CÉLULA 0 (Setup Inicial)
   
   → Clona o repositório
   → Instala dependências
   → Tempo: ~30 segundos

3️⃣ Executar CÉLULA 1 (Configurar API Keys)
   
   → Lê os secrets do Colab
   → Cria arquivo .env
   → Tempo: ~1 segundo

4️⃣ Upload do CFOP.csv
   
   → Clique no ícone 📁 (arquivos) na barra lateral
   → Navegue até: FiscalAI-v5/data/
   → Clique no ícone de upload
   → Selecione CFOP.csv
   → Aguarde upload concluir

5️⃣ Executar CÉLULA 2 (Setup Pinecone) - APENAS UMA VEZ!
   
   → Cria índice no Pinecone
   → Gera embeddings de ~777 CFOPs
   → Popula o vector store
   → Executa testes
   → Tempo: ~5-10 minutos
   
   ⚠️ IMPORTANTE: Execute esta célula APENAS UMA VEZ!
      Depois, o índice fica salvo no Pinecone e não precisa refazer.

┌─────────────────────────────────────────────────────────────────────────────┐
│ PARTE 2: USAR O SISTEMA (toda vez que quiser usar)                         │
└─────────────────────────────────────────────────────────────────────────────┘

6️⃣ Executar CÉLULA 3 (Iniciar Servidor)
   
   → Inicia FastAPI com ngrok
   → Gera link público: https://xxxx.ngrok.io
   → Tempo: ~10-20 segundos
   
   ✨ Você verá algo como:
   
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🌐 NGROK TUNNEL ATIVO
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   📡 URL Pública: https://abcd-1234.ngrok.io
   🔗 Acesse: https://abcd-1234.ngrok.io
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7️⃣ Acessar a Interface Web
   
   → Clique no link do ngrok
   → Interface abre em nova aba
   → Pronto para usar!

═══════════════════════════════════════════════════════════════════════════════
💡 USO DO SISTEMA
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│ OPÇÃO 1: Via Interface Web                                                 │
└─────────────────────────────────────────────────────────────────────────────┘

1. Acesse o link do ngrok
2. Faça upload dos CSVs (cabeçalho, itens)
3. Clique em "Inicializar Sistema"
4. Use o chat para fazer perguntas:

   Exemplos:
   • "Valide o CFOP do item 2 da nota 35240134028316923228550010003680821895807710"
   • "Qual CFOP usar para venda interestadual para revenda?"
   • "Quais são os CFOPs mais usados?"

┌─────────────────────────────────────────────────────────────────────────────┐
│ OPÇÃO 2: Via API Python                                                    │
└─────────────────────────────────────────────────────────────────────────────┘

import requests

# Substituir pela URL do ngrok
BASE_URL = "https://sua-url.ngrok.io"

# Validar CFOP
response = requests.post(f"{BASE_URL}/api/chat", json={
    "mensagem": "Valide o item 1 da nota 35240134028316..."
})

print(response.json())

═══════════════════════════════════════════════════════════════════════════════
🔍 FUNCIONALIDADES DA BUSCA SEMÂNTICA
═══════════════════════════════════════════════════════════════════════════════

✨ O que a busca semântica faz:

• Analisa o CONTEXTO COMPLETO da operação
  → Natureza da operação
  → UFs origem/destino
  → Tipo de produto
  → Tipo de destinatário
  → Se é consumidor final

• Encontra os CFOPs MAIS SIMILARES
  → Usa inteligência artificial
  → Considera significado, não apenas palavras
  → Score de 0-100% de relevância

• Sugere ALTERNATIVAS
  → Top 5 CFOPs mais adequados
  → Explicação de cada um
  → Score de confiança

═══════════════════════════════════════════════════════════════════════════════
❓ PERGUNTAS FREQUENTES
═══════════════════════════════════════════════════════════════════════════════

Q: Preciso executar o setup do Pinecone toda vez?
A: NÃO! Execute apenas UMA VEZ. O índice fica salvo no Pinecone.

Q: O link do ngrok muda toda vez?
A: SIM. Cada vez que executar a CÉLULA 3, terá um novo link.

Q: Posso usar sem Pinecone?
A: SIM, mas perderá a busca semântica. Use FiscalAI V4.

Q: Quanto custa?
A: ~$0.10 por 10.000 validações (muito barato!)

Q: Preciso de GPU?
A: NÃO. Funciona perfeitamente na CPU gratuita do Colab.

Q: Posso usar localmente?
A: SIM! Veja instruções no README.md

═══════════════════════════════════════════════════════════════════════════════
🆘 PROBLEMAS COMUNS
═══════════════════════════════════════════════════════════════════════════════

❌ Erro: "PINECONE_API_KEY not found"
✅ Solução: Verifique se adicionou o secret no Colab e ativou "Notebook access"

❌ Erro: "authentication failed" (ngrok)
✅ Solução: Verifique se o NGROK_AUTH_TOKEN está correto

❌ Erro: "Index not found" (Pinecone)
✅ Solução: Execute a CÉLULA 2 (Setup Pinecone)

❌ Servidor não inicia
✅ Solução: Reinicie o runtime (Runtime → Restart runtime) e execute tudo novamente

═══════════════════════════════════════════════════════════════════════════════
📞 SUPORTE
═══════════════════════════════════════════════════════════════════════════════

• GitHub Issues: github.com/SEU-USUARIO/FiscalAI-v5/issues
• Documentação: README.md
• Email: seu-email@exemplo.com

═══════════════════════════════════════════════════════════════════════════════

✅ RESUMO RÁPIDO:

1. Adicionar 3 secrets no Colab (uma vez)
2. Executar CÉLULA 0 (setup)
3. Executar CÉLULA 1 (API keys)
4. Upload CFOP.csv
5. Executar CÉLULA 2 (Pinecone - uma vez!)
6. Executar CÉLULA 3 (servidor - toda vez)
7. Acessar link do ngrok
8. Usar o sistema! 🎉

═══════════════════════════════════════════════════════════════════════════════

Boa validação de CFOPs! 🚀
"""

print(__doc__)
