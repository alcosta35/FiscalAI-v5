# pinecone_setup.py
"""
Script para configurar e popular o Pinecone Vector Store com CFOPs
FiscalAI v5 - Validação Semântica de CFOP
"""
import pandas as pd
import os
from typing import List, Dict
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
import time

class PineconeCFOPSetup:
    """Classe para configurar o Pinecone Vector Store com dados de CFOP"""
    
    def __init__(
        self, 
        cfop_csv_path: str,
        pinecone_api_key: str = None,
        openai_api_key: str = None,
        index_name: str = "fiscalai-cfop"
    ):
        """
        Inicializa o setup do Pinecone
        
        Args:
            cfop_csv_path: Caminho para o arquivo CFOP.csv
            pinecone_api_key: Chave API do Pinecone (ou usar variável de ambiente)
            openai_api_key: Chave API da OpenAI (ou usar variável de ambiente)
            index_name: Nome do índice no Pinecone
        """
        self.cfop_csv_path = cfop_csv_path
        self.index_name = index_name
        
        # Configurar APIs
        self.pinecone_api_key = pinecone_api_key or os.getenv("PINECONE_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY não configurada")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY não configurada")
        
        # Inicializar clientes
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        
        # Configuração de embeddings
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimension = 1536
        
        print("✅ Clientes Pinecone e OpenAI inicializados")
    
    def load_cfop_data(self) -> pd.DataFrame:
        """Carrega e processa dados do CFOP.csv"""
        print(f"\n📂 Carregando {self.cfop_csv_path}...")
        
        df = pd.read_csv(self.cfop_csv_path, encoding='utf-8-sig')
        
        # Limpar dados
        df = df.dropna(subset=['CFOP', 'APLICAÇÃO'])
        df['CFOP'] = df['CFOP'].astype(str).str.strip()
        df['DESCRIÇÃO'] = df['DESCRIÇÃO'].fillna('').astype(str)
        df['APLICAÇÃO'] = df['APLICAÇÃO'].astype(str)
        
        # Filtrar apenas CFOPs válidos (numéricos)
        df = df[df['CFOP'].str.replace('.', '').str.isdigit()]
        
        print(f"✅ {len(df)} CFOPs carregados")
        return df
    
    def create_embedding_text(self, row: pd.Series) -> str:
        """
        Cria texto otimizado para embedding a partir da linha do CFOP
        
        Combina APLICAÇÃO + DESCRIÇÃO para contexto rico
        """
        cfop = row['CFOP']
        descricao = row['DESCRIÇÃO']
        aplicacao = row['APLICAÇÃO']
        
        # Texto para embedding (rico em contexto)
        text = f"""
        CFOP: {cfop}
        Descrição: {descricao}
        
        Aplicação e Contexto:
        {aplicacao}
        """.strip()
        
        return text
    
    def generate_embeddings(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Gera embeddings usando OpenAI API em lotes
        
        Args:
            texts: Lista de textos para gerar embeddings
            batch_size: Tamanho do lote
        """
        print(f"\n🧠 Gerando embeddings para {len(texts)} textos...")
        
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                response = self.openai_client.embeddings.create(
                    input=batch,
                    model=self.embedding_model
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                print(f"  ✓ Processados {min(i + batch_size, len(texts))}/{len(texts)} textos")
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  ❌ Erro no lote {i}: {e}")
                raise
        
        print("✅ Embeddings gerados com sucesso")
        return all_embeddings
    
    def create_index(self, dimension: int = 1536):
        """Cria índice no Pinecone se não existir"""
        print(f"\n🔧 Configurando índice '{self.index_name}'...")
        
        # Verificar se índice já existe
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        if self.index_name in existing_indexes:
            print(f"⚠️  Índice '{self.index_name}' já existe")
            
            # Perguntar se quer deletar
            delete = input("Deseja deletar e recriar? (s/n): ").lower()
            if delete == 's':
                self.pc.delete_index(self.index_name)
                print("🗑️  Índice deletado")
                time.sleep(5)  # Aguardar propagação
            else:
                print("ℹ️  Usando índice existente")
                return
        
        # Criar novo índice
        self.pc.create_index(
            name=self.index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        
        print(f"✅ Índice '{self.index_name}' criado")
        
        # Aguardar índice ficar pronto
        print("⏳ Aguardando índice ficar pronto...")
        time.sleep(10)
    
    def upsert_vectors(self, df: pd.DataFrame, embeddings: List[List[float]]):
        """Faz upload dos vetores para o Pinecone"""
        print(f"\n📤 Fazendo upload de {len(embeddings)} vetores...")
        
        # Conectar ao índice
        index = self.pc.Index(self.index_name)
        
        # Preparar dados para upsert
        vectors = []
        for idx, (_, row) in enumerate(df.iterrows()):
            vector_data = {
                "id": f"cfop_{row['CFOP']}_{idx}",
                "values": embeddings[idx],
                "metadata": {
                    "cfop": row['CFOP'],
                    "descricao": row['DESCRIÇÃO'][:500],  # Limitar tamanho
                    "aplicacao": row['APLICAÇÃO'][:1000]  # Limitar tamanho
                }
            }
            vectors.append(vector_data)
        
        # Upsert em lotes
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            index.upsert(vectors=batch)
            print(f"  ✓ Upload {min(i + batch_size, len(vectors))}/{len(vectors)}")
            time.sleep(0.5)
        
        print("✅ Upload concluído")
        
        # Verificar estatísticas
        stats = index.describe_index_stats()
        print(f"\n📊 Estatísticas do índice:")
        print(f"   Total de vetores: {stats['total_vector_count']}")
    
    def setup_complete(self) -> Dict:
        """
        Executa o setup completo:
        1. Carrega CFOPs
        2. Gera embeddings
        3. Cria índice
        4. Faz upload dos vetores
        """
        print("\n" + "="*70)
        print("🚀 FISCALAI v5 - SETUP PINECONE VECTOR STORE")
        print("="*70)
        
        # 1. Carregar dados
        df = self.load_cfop_data()
        
        # 2. Criar textos para embedding
        print("\n📝 Preparando textos para embedding...")
        texts = [self.create_embedding_text(row) for _, row in df.iterrows()]
        print(f"✅ {len(texts)} textos preparados")
        
        # 3. Gerar embeddings
        embeddings = self.generate_embeddings(texts)
        
        # 4. Criar índice
        self.create_index(dimension=self.embedding_dimension)
        
        # 5. Upload vetores
        self.upsert_vectors(df, embeddings)
        
        print("\n" + "="*70)
        print("✅ SETUP CONCLUÍDO COM SUCESSO!")
        print("="*70)
        
        return {
            "status": "success",
            "index_name": self.index_name,
            "total_cfops": len(df),
            "embedding_dimension": self.embedding_dimension,
            "embedding_model": self.embedding_model
        }


def main():
    """Função principal para executar o setup"""
    import sys
    
    # Configurar paths
    if len(sys.argv) > 1:
        cfop_csv_path = sys.argv[1]
    else:
        # Default para Colab
        cfop_csv_path = "/content/FiscalAI-v4/data/CFOP.csv"
    
    # Verificar se arquivo existe
    if not os.path.exists(cfop_csv_path):
        print(f"❌ Arquivo não encontrado: {cfop_csv_path}")
        print("\n💡 Use: python pinecone_setup.py <caminho_do_cfop.csv>")
        return
    
    # Executar setup
    setup = PineconeCFOPSetup(cfop_csv_path=cfop_csv_path)
    result = setup.setup_complete()
    
    print("\n📋 Resultado:")
    for key, value in result.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    main()
