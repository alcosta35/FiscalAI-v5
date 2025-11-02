# 🔑 Como Configurar o ngrok Authtoken (OBRIGATÓRIO)

## ⚠️ O que mudou?

O ngrok agora **exige autenticação** para usar. Não se preocupe, é **100% gratuito**!

## 📋 3 Passos Simples

### 1️⃣ Criar Conta no ngrok (Grátis)

```
🔗 Acesse: https://dashboard.ngrok.com/signup
```

- Use Google, GitHub ou email
- É rápido (30 segundos)
- Totalmente gratuito

### 2️⃣ Copiar seu Authtoken

Após criar a conta:

```
🔗 Acesse: https://dashboard.ngrok.com/get-started/your-authtoken
```

Você verá algo assim:
```
Your Authtoken
2a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
```

**Copie esse código!** ⬆️

### 3️⃣ Configurar no Colab

No seu notebook do Colab, **ANTES** de iniciar o servidor, adicione:

```python
import os
os.environ['NGROK_AUTHTOKEN'] = 'cole-seu-token-aqui'
```

**Exemplo:**
```python
import os
os.environ['NGROK_AUTHTOKEN'] = '2a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0'
```

Pronto! ✅

## 🎯 Configuração Completa no Colab

Cole isso em uma célula e execute:

```python
import os

# OpenAI API Key
os.environ['OPENAI_API_KEY'] = 'sk-proj-sua-chave-openai'

# ngrok Authtoken
os.environ['NGROK_AUTHTOKEN'] = 'seu-token-ngrok'

print('✅ Configurações salvas!')
```

## ✅ Como Saber se Funcionou?

Quando você executar o servidor, verá:

```
🌐 NGROK TUNNEL ATIVO
══════════════════════════════════════
📡 URL Pública: https://abc123.ngrok-free.app
🔗 Acesse: https://abc123.ngrok-free.app
══════════════════════════════════════
```

**Se aparecer a URL, funcionou!** 🎉

## ❌ Erros Comuns

### "authentication failed"

**Problema:** Token não configurado ou inválido

**Solução:**
1. Copie o token correto: https://dashboard.ngrok.com/get-started/your-authtoken
2. Configure com `os.environ['NGROK_AUTHTOKEN'] = 'seu-token'`
3. Execute o servidor novamente

### Token não funciona

**Verifique:**
- ✅ Copiou o token completo (sem espaços)
- ✅ Token está entre aspas simples `'token'`
- ✅ Executou a célula de configuração
- ✅ Token está correto (sem caracteres extras)

## 💡 Dicas

### Salvar para Sempre

Se você usa sempre o mesmo notebook, salve o token assim:

```python
# Cole isto no início do notebook
import os
os.environ['NGROK_AUTHTOKEN'] = 'seu-token-aqui'

# Pronto! Não precisa reconfigurar toda vez
```

### Segurança

- 🔒 Não compartilhe seu token
- 🔒 Não commite em repositórios públicos
- 🔒 Se vazar, gere um novo token

### Gerar Novo Token

Se perdeu ou quer trocar:

1. Acesse: https://dashboard.ngrok.com/tunnels/authtokens
2. Clique em "Revoke" no token antigo
3. Clique em "New Authtoken"
4. Copie o novo token

## 🆓 É Realmente Grátis?

**Sim!** O tier gratuito do ngrok inclui:

- ✅ Túneis ilimitados
- ✅ URLs https://
- ✅ 1 túnel simultâneo
- ✅ Sem limite de tráfego
- ✅ Perfeito para desenvolvimento

**Limitações:**
- ⏱️ URL muda a cada reinicialização
- 🔄 Precisa manter o Colab rodando

**Para produção séria** (opcional):
- 💰 Plano Pro: $8/mês
- 🌐 URL fixa
- 🔗 Múltiplos túneis

Mas para usar o FiscalAI, o **gratuito é perfeito**! ✅

## 📱 Funciona em Mobile?

Sim! Depois de configurar:
1. URL do ngrok funciona em qualquer dispositivo
2. Interface é responsiva
3. Acesse de celular, tablet, etc.

## 🎬 Resumo Visual

```
┌─────────────────────────────────────┐
│ 1. Criar conta ngrok (grátis)      │
│    https://dashboard.ngrok.com      │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 2. Copiar authtoken                 │
│    Dashboard > Your Authtoken       │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 3. Configurar no Colab              │
│    os.environ['NGROK_AUTHTOKEN']    │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 4. Rodar servidor                   │
│    !python main.py                  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ ✅ URL pública funcionando!         │
│    https://xxxx.ngrok-free.app      │
└─────────────────────────────────────┘
```

## 🆘 Ainda com Problemas?

### Teste Rápido

Execute isto no Colab para testar:

```python
from pyngrok import ngrok
import os

# Configure seu token
os.environ['NGROK_AUTHTOKEN'] = 'seu-token-aqui'
ngrok.set_auth_token(os.environ['NGROK_AUTHTOKEN'])

# Teste
try:
    tunnel = ngrok.connect(8000)
    print(f"✅ Funcionou! URL: {tunnel.public_url}")
    ngrok.disconnect(tunnel.public_url)
except Exception as e:
    print(f"❌ Erro: {e}")
```

Se aparecer "✅ Funcionou!", está configurado corretamente!

## 📞 Precisa de Ajuda?

1. **Token inválido?** → Gere novo token no dashboard
2. **Não recebeu email?** → Verifique spam
3. **Conta bloqueada?** → Entre em contato com suporte ngrok
4. **Outros problemas?** → Consulte docs: https://ngrok.com/docs

---

## 🎯 TL;DR (Muito Resumido)

```python
# 1. Criar conta: https://dashboard.ngrok.com/signup
# 2. Pegar token: https://dashboard.ngrok.com/get-started/your-authtoken
# 3. No Colab:

import os
os.environ['NGROK_AUTHTOKEN'] = 'seu-token-aqui'

# 4. Rodar servidor
!python main.py

# 5. Copiar URL e usar!
```

**Tempo total: 2 minutos** ⏱️

---

**FiscalAI v2.0** - Configuração do ngrok simplificada! 🔑

**Lembre-se:** Você só precisa fazer isso **uma vez**. Depois é só usar! 🚀
