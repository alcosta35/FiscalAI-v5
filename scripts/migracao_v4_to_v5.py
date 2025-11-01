#!/usr/bin/env python3
"""
Script de Migração: FiscalAI v4 → v5
Automatiza a atualização para usar validação semântica com Pinecone
"""
import os
import shutil
from pathlib import Path
import subprocess
import sys

class MigracaoV4toV5:
    """Migração automatizada para FiscalAI v5"""
    
    def __init__(self, projeto_path: str = "."):
        self.projeto_path = Path(projeto_path).absolute()
        self.backup_path = self.projeto_path.parent / f"{self.projeto_path.name}_backup_v4"
        
    def verificar_estrutura_v4(self) -> bool:
        """Verifica se o projeto é v4 válido"""
        print("\n🔍 Verificando estrutura do projeto v4...")
        
        arquivos_necessarios = [
            "main.py",
            "config.py",
            "requirements.txt",
            "agente_cfop.py"
        ]
        
        for arquivo in arquivos_necessarios:
            if not (self.projeto_path / arquivo).exists():
                print(f"   ❌ Arquivo não encontrado: {arquivo}")
                return False
            print(f"   ✅ {arquivo}")
        
        return True
    
    def criar_backup(self):
        """Cria backup do projeto v4"""
        print(f"\n💾 Criando backup em: {self.backup_path}")
        
        if self.backup_path.exists():
            print(f"   ⚠️  Backup já existe, removendo...")
            shutil.rmtree(self.backup_path)
        
        shutil.copytree(self.projeto_path, self.backup_path)
        print("   ✅ Backup criado com sucesso")
    
    def atualizar_requirements(self):
        """Adiciona novas dependências"""
        print("\n📦 Atualizando requirements.txt...")
        
        req_file = self.projeto_path / "requirements.txt"
        
        with open(req_file, 'r') as f:
            conteudo = f.read()
        
        # Verificar se já tem Pinecone
        if 'pinecone' not in conteudo.lower():
            with open(req_file, 'a') as f:
                f.write("\n# FiscalAI v5 - Validação Semântica\n")
                f.write("pinecone-client>=3.0.0\n")
            print("   ✅ Pinecone adicionado")
        else:
            print("   ℹ️  Pinecone já presente")
    
    def criar_services_dir(self):
        """Cria diretório services/ se não existir"""
        print("\n📁 Criando estrutura de diretórios...")
        
        services_dir = self.projeto_path / "services"
        services_dir.mkdir(exist_ok=True)
        
        init_file = services_dir / "__init__.py"
        if not init_file.exists():
            init_file.touch()
        
        print("   ✅ services/ criado")
    
    def copiar_novos_arquivos(self, arquivos_v5_path: str):
        """Copia arquivos novos da v5"""
        print("\n📥 Copiando novos arquivos da v5...")
        
        arquivos_v5 = Path(arquivos_v5_path)
        
        # Lista de arquivos para copiar
        copias = [
            ("pinecone_setup.py", "pinecone_setup.py"),
            ("validacao_semantica.py", "services/validacao_semantica.py"),
            ("validacao_semantica_routes.py", "routes/validacao_semantica_routes.py")
        ]
        
        for origem, destino in copias:
            src = arquivos_v5 / origem
            dst = self.projeto_path / destino
            
            if src.exists():
                shutil.copy2(src, dst)
                print(f"   ✅ {destino}")
            else:
                print(f"   ⚠️  {origem} não encontrado em {arquivos_v5_path}")
    
    def atualizar_main_py(self):
        """Adiciona import e router no main.py"""
        print("\n✏️  Atualizando main.py...")
        
        main_file = self.projeto_path / "main.py"
        
        with open(main_file, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Adicionar import
        if 'validacao_semantica_routes' not in conteudo:
            # Encontrar linha de imports de routes
            linhas = conteudo.split('\n')
            idx_import = -1
            
            for i, linha in enumerate(linhas):
                if 'from routes' in linha and 'import' in linha:
                    idx_import = i
            
            if idx_import >= 0:
                novo_import = "from routes.validacao_semantica_routes import router as validacao_semantica_router"
                linhas.insert(idx_import + 1, novo_import)
                print("   ✅ Import adicionado")
            
            # Adicionar router
            idx_router = -1
            for i, linha in enumerate(linhas):
                if 'app.include_router' in linha:
                    idx_router = i
            
            if idx_router >= 0:
                novo_router = 'app.include_router(validacao_semantica_router, prefix="/api")'
                linhas.insert(idx_router + 1, novo_router)
                print("   ✅ Router adicionado")
            
            # Salvar
            with open(main_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(linhas))
        else:
            print("   ℹ️  main.py já atualizado")
    
    def atualizar_env_example(self):
        """Adiciona PINECONE_API_KEY no .env.example"""
        print("\n🔐 Atualizando .env.example...")
        
        env_file = self.projeto_path / ".env.example"
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                conteudo = f.read()
            
            if 'PINECONE_API_KEY' not in conteudo:
                with open(env_file, 'a') as f:
                    f.write("\n# Pinecone Vector Store (v5)\n")
                    f.write("PINECONE_API_KEY=your-pinecone-key-here\n")
                print("   ✅ PINECONE_API_KEY adicionado")
            else:
                print("   ℹ️  Já contém PINECONE_API_KEY")
        else:
            print("   ⚠️  .env.example não encontrado")
    
    def criar_readme_v5(self):
        """Cria README_V5.md com instruções"""
        print("\n📝 Criando README_V5.md...")
        
        readme = self.projeto_path / "README_V5.md"
        
        conteudo = """# FiscalAI v5 - Migração Concluída

## ✅ Migração bem-sucedida!

Seu projeto foi atualizado para a versão 5 com validação semântica.

## 🚀 Próximos Passos

### 1. Instalar novas dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Pinecone API Key

Adicione ao seu `.env`:
```
PINECONE_API_KEY=sua-chave-aqui
```

Para obter a chave:
1. Crie conta em: https://app.pinecone.io/
2. Copie API key do dashboard

### 3. Executar Setup do Pinecone (UMA VEZ)

```bash
python pinecone_setup.py data/CFOP.csv
```

Isso irá:
- Gerar embeddings dos CFOPs
- Criar índice no Pinecone
- Popular Vector Store

Tempo: ~5-10 minutos

### 4. Testar

```bash
python main.py
```

Acesse: http://localhost:8000

## 📡 Novos Endpoints

- `POST /api/validacao-semantica/inicializar`
- `POST /api/validacao-semantica/validar-item`
- `POST /api/validacao-semantica/validar-lote`
- `GET /api/validacao-semantica/buscar-cfop`

## 💡 Exemplo de Uso

```python
import requests

# Inicializar
requests.post("http://localhost:8000/api/validacao-semantica/inicializar")

# Validar item
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
    "http://localhost:8000/api/validacao-semantica/validar-item",
    json=item
)

print(response.json())
```

## 🔙 Rollback

Se precisar voltar para v4:
```bash
rm -rf {seu_projeto}/
cp -r {seu_projeto}_backup_v4/ {seu_projeto}/
```

## 📚 Documentação Completa

Veja `docs/V5_COMPLETE_GUIDE.md` para documentação detalhada.
"""
        
        with open(readme, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print("   ✅ README_V5.md criado")
    
    def executar_migracao(self, arquivos_v5_path: str = None):
        """Executa processo completo de migração"""
        print("\n" + "="*70)
        print("🚀 MIGRAÇÃO FISCALAI V4 → V5")
        print("="*70)
        
        # 1. Verificar estrutura
        if not self.verificar_estrutura_v4():
            print("\n❌ Projeto v4 inválido ou arquivos faltando")
            return False
        
        # 2. Criar backup
        self.criar_backup()
        
        # 3. Atualizar requirements
        self.atualizar_requirements()
        
        # 4. Criar diretórios
        self.criar_services_dir()
        
        # 5. Copiar novos arquivos (se path fornecido)
        if arquivos_v5_path:
            self.copiar_novos_arquivos(arquivos_v5_path)
        
        # 6. Atualizar main.py
        self.atualizar_main_py()
        
        # 7. Atualizar .env.example
        self.atualizar_env_example()
        
        # 8. Criar README
        self.criar_readme_v5()
        
        print("\n" + "="*70)
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*70)
        
        print("\n📋 PRÓXIMOS PASSOS:")
        print("   1. pip install -r requirements.txt")
        print("   2. Configurar PINECONE_API_KEY no .env")
        print("   3. python pinecone_setup.py data/CFOP.csv")
        print("   4. python main.py")
        print("\n   Veja README_V5.md para mais detalhes\n")
        
        return True


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migra FiscalAI v4 para v5'
    )
    parser.add_argument(
        '--projeto',
        default='.',
        help='Caminho do projeto v4 (default: diretório atual)'
    )
    parser.add_argument(
        '--arquivos-v5',
        help='Caminho dos arquivos da v5 (para copiar novos arquivos)'
    )
    
    args = parser.parse_args()
    
    # Executar migração
    migracao = MigracaoV4toV5(args.projeto)
    sucesso = migracao.executar_migracao(args.arquivos_v5)
    
    sys.exit(0 if sucesso else 1)


if __name__ == "__main__":
    main()
