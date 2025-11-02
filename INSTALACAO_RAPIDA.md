# 🚀 Guia de Instalação Rápida - FiscalAI v2.0

## Passo 1: Preparar o Ambiente

```bash
# Criar e ativar ambiente virtual (recomendado)
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

## Passo 2: Instalar Dependências

```bash
pip install -r requirements.txt
```

## Passo 3: Configurar API Key

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar o arquivo .env e adicionar sua API Key
# OPENAI_API_KEY=sk-sua-chave-aqui
```

## Passo 4: Executar o Sistema

```bash
python main.py
```

O sistema será iniciado em: **http://localhost:8000**

## Passo 5: Usar o Sistema

1. Acesse http://localhost:8000 no navegador
2. Faça upload dos 3 arquivos CSV:
   - 202401_NFs_Cabecalho.csv
   - 202401_NFs_Itens.csv
   - CFOP.csv
3. Clique em "Iniciar Processamento"
4. Navegue pelas funcionalidades:
   - 📊 Estatísticas
   - 💬 Chat IA
   - ✓ Validação CFOP

## ⚠️ Troubleshooting

### Erro: "OPENAI_API_KEY não encontrada"
- Verifique se o arquivo `.env` existe
- Verifique se a chave está correta

### Erro ao instalar dependências
```bash
# Atualizar pip
pip install --upgrade pip

# Instalar novamente
pip install -r requirements.txt
```

### Porta 8000 já em uso
Edite o arquivo `main.py` e altere a porta:
```python
uvicorn.run("main:app", host="0.0.0.0", port=8001)  # Usar porta 8001
```

## 📞 Suporte

Para mais informações, consulte o README.md completo.

---

**FiscalAI v2.0** - Sistema pronto em menos de 5 minutos! 🚀
