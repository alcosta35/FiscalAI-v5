# 🔧 Configuração Avançada do ngrok (Opcional)

## Por que configurar o ngrok?

Por padrão, o ngrok funciona sem configuração, mas tem limitações:
- ⏱️ Túnel expira após 2 horas
- 🔄 URL muda sempre
- ⚡ Limite de conexões

Com uma conta ngrok gratuita, você pode:
- ⏱️ Túneis mais longos
- 🌐 URLs personalizadas (pago)
- ⚡ Mais conexões simultâneas
- 📊 Dashboard de métricas

## 📋 Como Configurar (Opcional)

### Passo 1: Criar Conta no ngrok

1. Acesse: https://ngrok.com
2. Clique em "Sign up"
3. Crie uma conta (gratuita)

### Passo 2: Obter Auth Token

1. Faça login no ngrok
2. Acesse: https://dashboard.ngrok.com/get-started/your-authtoken
3. Copie seu authtoken

### Passo 3: Configurar no Colab

Adicione esta célula **ANTES** de iniciar o servidor:

```python
# Configurar ngrok auth token (opcional)
from pyngrok import ngrok

# ⚠️ Substitua pelo seu token!
ngrok.set_auth_token("seu-token-aqui")

print("✅ ngrok configurado com auth token!")
```

## 🎯 Vantagens da Configuração

### Com Conta Gratuita:
- ✅ Túneis não expiram em 2 horas
- ✅ Dashboard com métricas
- ✅ Histórico de túneis
- ✅ 1 túnel simultâneo

### Com Plano Pago ($8/mês):
- ✅ URLs personalizadas (ex: fiscalai.ngrok.io)
- ✅ Múltiplos túneis simultâneos
- ✅ Reserva de domínio
- ✅ IP fixo
- ✅ Mais segurança

## 🚀 Exemplo Completo

```python
# Célula 1: Instalar dependências
!pip install -q fastapi uvicorn[standard] pydantic pydantic-settings python-dotenv
!pip install -q openai langchain langchain-openai langchain-community
!pip install -q pandas openpyxl
!pip install -q pyngrok nest-asyncio

# Célula 2: Configurar API Keys
import os
from pyngrok import ngrok

# OpenAI
os.environ['OPENAI_API_KEY'] = 'sk-proj-xxxxx'

# ngrok (opcional)
ngrok.set_auth_token("seu-token-ngrok")

print("✅ Configurações carregadas!")

# Célula 3: Extrair projeto
!tar -xzf fiscalai-v2.tar.gz
%cd fiscalai-v2

# Célula 4: Iniciar servidor
!mkdir -p data
!python main.py
```

## 💡 Dicas

### Para Desenvolvimento:
- Não precisa configurar ngrok token
- Use o free tier

### Para Produção/Apresentações:
- Configure o token para túneis mais estáveis
- Considere plano pago para URL fixa

### Para Equipes:
- Use URL fixa (plano pago)
- Configure autenticação básica
- Implemente controle de acesso

## ⚠️ Segurança

### Boas Práticas:
- 🔒 Não compartilhe seu auth token
- 🔑 Não commite tokens em notebooks públicos
- 🚫 Use túneis privados para dados sensíveis
- 🔐 Considere adicionar autenticação HTTP básica

### Adicionar Autenticação Básica (Avançado):

Edite `main.py`:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "senha123")
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Aplicar em rotas protegidas
@app.get("/estatisticas")
async def pagina_estatisticas(username: str = Depends(verify_credentials)):
    # ... resto do código
```

## 📊 Monitoramento

### Dashboard ngrok:
1. Acesse: https://dashboard.ngrok.com
2. Veja métricas em tempo real:
   - Número de requisições
   - Latência
   - Erros
   - Conexões ativas

### Logs no Colab:
```python
# Ver logs do ngrok
from pyngrok import ngrok

tunnels = ngrok.get_tunnels()
for tunnel in tunnels:
    print(f"Nome: {tunnel.name}")
    print(f"URL: {tunnel.public_url}")
    print(f"Protocolo: {tunnel.proto}")
```

## 🎯 Cenários de Uso

### Cenário 1: Demonstração Rápida
```
✅ Sem configuração
✅ URL temporária
✅ Free tier
```

### Cenário 2: Desenvolvimento Contínuo
```
✅ Com auth token
✅ Conta gratuita
✅ Túneis mais estáveis
```

### Cenário 3: Produção Interna
```
✅ Plano pago
✅ URL fixa
✅ Autenticação
✅ Monitoramento
```

## 🔄 Alternativas ao ngrok

Se ngrok não funcionar, considere:

### 1. Localtunnel
```bash
npm install -g localtunnel
lt --port 8000
```

### 2. Serveo
```bash
ssh -R 80:localhost:8000 serveo.net
```

### 3. Cloudflare Tunnel
```bash
cloudflared tunnel --url http://localhost:8000
```

### 4. VS Code Tunnels
```
Usar extensão do VS Code
```

## 📞 FAQ

**P: Preciso configurar o token?**  
R: Não, é opcional. O free tier sem token funciona bem.

**P: O token expira?**  
R: Não, o token é permanente para sua conta.

**P: Posso ter múltiplos tokens?**  
R: Sim, mas geralmente 1 é suficiente.

**P: O token é seguro no Colab?**  
R: Para uso pessoal sim, mas não compartilhe notebooks com tokens.

**P: Vale a pena pagar pelo ngrok?**  
R: Para produção ou uso frequente, sim. Para testes, não.

---

**Dica:** Para a maioria dos casos, o ngrok gratuito sem configuração é suficiente! 🚀
