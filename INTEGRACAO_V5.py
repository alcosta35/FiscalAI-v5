# INTEGRAÇÃO FISCALAI V5 - VALIDAÇÃO SEMÂNTICA
# ==============================================

"""
Este arquivo contém as instruções para integrar a validação semântica
com Pinecone no FiscalAI v4, criando a versão v5.
"""

# ==============================================
# 1. ADICIONAR IMPORT NO main.py
# ==============================================

# No início do arquivo main.py, adicionar:
from routes.validacao_semantica_routes import router as validacao_semantica_router

# ==============================================
# 2. INCLUIR ROUTER NO main.py
# ==============================================

# Depois das outras inclusões de routers, adicionar:
app.include_router(validacao_semantica_router, prefix="/api")

# Exemplo de como ficaria:
"""
app.include_router(chat_router, prefix="/api")
app.include_router(estatisticas_router, prefix="/api")
app.include_router(validacao_router, prefix="/api")
app.include_router(validacao_semantica_router, prefix="/api")  # NOVO
"""

# ==============================================
# 3. ATUALIZAR .env.example
# ==============================================

# Adicionar no arquivo .env.example:
"""
# OpenAI API Key
OPENAI_API_KEY=sk-your-key-here

# Ngrok Auth Token
NGROK_AUTH_TOKEN=your-token-here

# Pinecone API Key (NOVO)
PINECONE_API_KEY=your-pinecone-key-here
"""

# ==============================================
# 4. CRIAR ESTRUTURA DE PASTAS
# ==============================================

"""
FiscalAI-v5/
├── main.py (atualizado)
├── config.py
├── requirements.txt (atualizado)
├── pinecone_setup.py (NOVO)
├── .env.example (atualizado)
├── models/
│   └── schemas.py
├── routes/
│   ├── chat_router.py
│   ├── estatisticas_router.py
│   ├── validacao_router.py
│   └── validacao_semantica_routes.py (NOVO)
├── services/
│   └── validacao_semantica.py (NOVO)
├── static/
│   └── (arquivos existentes)
└── templates/
    ├── index.html
    ├── chat.html
    ├── estatisticas.html
    ├── validacao.html
    └── validacao_semantica.html (NOVO - opcional)
"""

# ==============================================
# 5. ENDPOINTS DISPONÍVEIS APÓS INTEGRAÇÃO
# ==============================================

"""
NOVOS ENDPOINTS:

POST /api/validacao-semantica/inicializar
  - Inicializa o validador conectando ao Pinecone
  - Response: { "status": "success", "total_vetores": 450 }

GET /api/validacao-semantica/status
  - Verifica status do validador
  - Response: { "inicializado": true, "total_vetores": 450 }

POST /api/validacao-semantica/validar-item
  - Valida CFOP de um item individual
  - Body: { "uf_emitente": "SP", "uf_destinatario": "RJ", ... }
  - Response: { "status": "CORRETO", "sugestoes": [...] }

POST /api/validacao-semantica/validar-lote
  - Valida lote de itens via CSV upload
  - Body: CSV file
  - Response: { "relatorio": {...}, "resultados": [...] }

GET /api/validacao-semantica/buscar-cfop?query=...&top_k=5
  - Busca CFOPs por descrição livre
  - Response: { "cfops": [...] }

POST /api/validacao-semantica/comparar-validacoes
  - Compara validação semântica vs CFOPs informados
  - Body: CSV file
  - Response: { "relatorio_geral": {...}, "divergencias": [...] }
"""

# ==============================================
# 6. FLUXO DE USO
# ==============================================

"""
SETUP INICIAL (uma única vez):

1. Obter chave da Pinecone:
   - Criar conta em: https://app.pinecone.io/
   - Copiar API key do dashboard

2. Executar setup do Pinecone:
   $ python pinecone_setup.py /path/to/CFOP.csv
   
   Isso irá:
   - Carregar o CFOP.csv
   - Gerar embeddings de ~450 CFOPs
   - Criar índice "fiscalai-cfop" no Pinecone
   - Popular o Vector Store
   
   Tempo: ~5-10 minutos
   Custo: $0 (Pinecone free tier)

USO DIÁRIO:

1. Iniciar servidor:
   $ python main.py

2. Na interface web ou via API:
   - POST /api/validacao-semantica/inicializar
   - POST /api/validacao-semantica/validar-item
   - ou POST /api/validacao-semantica/validar-lote
"""

# ==============================================
# 7. EXEMPLO DE USO VIA CÓDIGO
# ==============================================

exemplo_uso = """
# Inicializar validador
import requests

BASE_URL = "http://localhost:8000"

# 1. Inicializar
response = requests.post(f"{BASE_URL}/api/validacao-semantica/inicializar")
print(response.json())

# 2. Validar item
item = {
    "uf_emitente": "SP",
    "uf_destinatario": "RJ",
    "descricao_produto": "Notebook para revenda",
    "ncm": "84713012",
    "consumidor_final": "0",
    "indicador_ie": "1",
    "cfop_informado": "6102"
}

response = requests.post(
    f"{BASE_URL}/api/validacao-semantica/validar-item",
    json=item
)

resultado = response.json()
print(f"Status: {resultado['status']}")
print(f"Sugestões: {resultado['sugestoes']}")

# 3. Busca livre
response = requests.get(
    f"{BASE_URL}/api/validacao-semantica/buscar-cfop",
    params={
        "query": "venda de produto para consumidor final em outro estado",
        "top_k": 5
    }
)

cfops = response.json()['cfops']
for cfop in cfops:
    print(f"CFOP {cfop['cfop']} - Score: {cfop['score']}")
"""

# ==============================================
# 8. VANTAGENS DA VERSÃO V5
# ==============================================

vantagens = """
✅ VALIDAÇÃO INTELIGENTE
   - Busca semântica baseada em contexto real
   - Não depende de regras fixas
   - Aprende com descrições naturais

✅ PRECISÃO MELHORADA
   - Score de confiança para cada sugestão
   - Top-K sugestões (não apenas 1)
   - Identifica divergências automaticamente

✅ FLEXIBILIDADE
   - Funciona mesmo com dados incompletos
   - Busca livre por descrição
   - Fácil de expandir/atualizar

✅ ESCALABILIDADE
   - Pinecone gerencia infraestrutura
   - Busca instantânea (ms)
   - Free tier suficiente para até 100k vetores

✅ AUDITORIA
   - Relatórios de acurácia
   - Comparação com CFOPs informados
   - Análise de divergências
"""

print(vantagens)
