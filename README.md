# FiscalAI - Auditor Fiscal Inteligente v2.0

Sistema inteligente para auditoria fiscal usando IA com interface web moderna.

## 🆕 Novidades da Versão 2.0

- ✨ **Interface Web Completa** - Substituiu o SwaggerUI por páginas web modernas
- 📤 **Upload de Arquivos** - Usuário faz upload dos CSVs diretamente pelo navegador
- 📊 **Dashboard de Estatísticas** - Gráficos interativos e indicadores visuais
- 💬 **Chat IA Interativo** - Interface de chat para perguntas sobre as notas fiscais
- ✓ **Validação CFOP** - Página dedicada para validação de CFOPs específicos
- 🎨 **Design Moderno** - Interface verde com gradientes e animações suaves

## 🚀 Como Executar

### Opção 1: Google Colab + ngrok (Recomendado para Produção)

1. Abra o notebook: [FiscalAI_Colab.ipynb](FiscalAI_Colab.ipynb)
2. Faça upload do arquivo `fiscalai-v2.tar.gz`
3. Configure sua API Key da OpenAI
4. Execute as células em ordem
5. Copie o link público do ngrok
6. Acesse no navegador

**Vantagens:**
- ✅ Acesso público via ngrok
- ✅ Não precisa de servidor próprio
- ✅ Funciona de qualquer lugar
- ✅ Gratuito

### Opção 2: Local (Desenvolvimento)

#### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

#### 2. Configurar API Key

Crie um arquivo `.env` na raiz do projeto:

```bash
OPENAI_API_KEY=sk-sua-chave-aqui
```

#### 3. Executar o Sistema

```bash
python main.py
```

O sistema será iniciado em: **http://localhost:8000**

## 📋 Como Usar

### Passo 1: Upload dos Arquivos CSV

1. Acesse http://localhost:8000
2. Faça upload dos 3 arquivos CSV:
   - `202401_NFs_Cabecalho.csv`
   - `202401_NFs_Itens.csv`
   - `CFOP.csv`
3. Clique em **"Iniciar Processamento"**

### Passo 2: Navegar pelas Funcionalidades

Após a inicialização, você terá acesso a:

- **📊 Estatísticas**: Dashboard com gráficos e indicadores
- **💬 Chat IA**: Faça perguntas sobre suas notas fiscais
- **✓ Validação CFOP**: Valide CFOPs de itens específicos

## 🎯 Funcionalidades

### Dashboard de Estatísticas

- Total de notas e itens processados
- Taxa de conformidade fiscal
- Divergências críticas
- CFOPs mais utilizados
- Distribuição de divergências por tipo
- Operações por UF
- Tendência mensal
- Top 10 notas com mais problemas

### Chat com IA

Exemplos de perguntas:
- "Quantas notas fiscais temos no sistema?"
- "Valide o CFOP do item 2 da nota 35240134028316923228550010003680821895807710"
- "Quais são os CFOPs mais utilizados?"
- "Mostre a quinta nota fiscal"
- "Explique o CFOP 5102"

### Validação de CFOP

- Valida CFOP de itens específicos
- Infere o CFOP correto baseado na natureza da operação
- Identifica divergências críticas
- Fornece justificativa detalhada

## 📁 Estrutura do Projeto

```
FiscalAI/
├── main.py                 # FastAPI app principal
├── config.py               # Configurações
├── agente_cfop.py          # Agente validador (LangChain + OpenAI)
├── requirements.txt        # Dependências
├── .env                    # API Keys (não commitar)
├── models/                 # Modelos Pydantic
│   └── schemas.py
├── routes/                 # Endpoints da API
│   ├── chat.py
│   ├── estatisticas.py
│   └── validacao.py
├── services/               # Lógica de negócio
│   └── estatisticas_service.py
├── static/                 # Arquivos estáticos
│   └── css/
│       └── style.css
├── templates/              # Páginas HTML
│   ├── index.html          # Upload de arquivos
│   ├── estatisticas.html   # Dashboard
│   ├── chat.html           # Chat IA
│   └── validacao.html      # Validação CFOP
└── data/                   # Arquivos CSV (criado automaticamente)
```

## 🔑 API Endpoints

### Upload e Inicialização
- `POST /api/upload-csv` - Upload de arquivo CSV
- `POST /api/inicializar` - Inicializar sistema
- `POST /api/resetar` - Resetar sistema
- `GET /api/status-arquivos` - Status dos arquivos

### Estatísticas
- `GET /api/estatisticas/resumo` - Resumo geral
- `GET /api/estatisticas/cfop-distribuicao` - Distribuição de CFOPs
- `GET /api/estatisticas/divergencias-tipo` - Divergências por tipo
- `GET /api/estatisticas/operacoes-uf` - Operações por UF
- `GET /api/estatisticas/tendencia-mensal` - Tendência mensal
- `GET /api/estatisticas/top-divergencias` - Top divergências

### Chat
- `POST /api/chat/perguntar` - Enviar pergunta ao agente

### Validação
- `POST /api/validacao/cfop-item` - Validar CFOP de item

## 🛠️ Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web moderno e rápido
- **LangChain** - Framework para aplicações com LLM
- **OpenAI GPT-4** - Modelo de linguagem
- **Pandas** - Análise de dados
- **Pydantic** - Validação de dados

### Frontend
- **HTML5/CSS3** - Estrutura e estilos
- **JavaScript Vanilla** - Interatividade
- **Chart.js** - Gráficos interativos
- **Design Responsivo** - Funciona em mobile e desktop

## 📊 Requisitos do Sistema

- Python 3.10+
- OpenAI API Key
- 4GB RAM mínimo
- Navegador moderno (Chrome, Firefox, Edge, Safari)

## 🔒 Segurança

- Nunca commite o arquivo `.env` com suas API Keys
- Use HTTPS em produção
- Configure CORS adequadamente para seu domínio
- Valide e sanitize inputs do usuário

## 📝 Notas de Desenvolvimento

### Para adicionar novas funcionalidades:

1. **Nova página HTML**: Adicione em `/templates/`
2. **Nova rota de página**: Adicione em `main.py`
3. **Nova API**: Crie um router em `/routes/`
4. **Nova lógica de negócio**: Adicione em `/services/`

### Logs

O sistema gera logs detalhados no console para debug.

## 🐛 Troubleshooting

**Sistema não inicializa:**
- Verifique se a API Key está correta no `.env`
- Verifique se todos os arquivos CSV foram carregados

**Erro ao fazer upload:**
- Verifique se o arquivo é CSV válido
- Verifique se o arquivo não está corrompido

**Chat não responde:**
- Verifique a conexão com a API OpenAI
- Verifique se ainda tem créditos na conta OpenAI

## 📄 Licença

Este projeto é para uso educacional e interno.

## 👥 Contato

Para dúvidas e suporte, consulte a documentação ou entre em contato com a equipe de desenvolvimento.

---

**FiscalAI v2.0** - Auditoria Fiscal Inteligente com IA 🚀
