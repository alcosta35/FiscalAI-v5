#!/usr/bin/env python3
"""
Script para popular o índice Pinecone com dados de CFOPs
"""
import os
import sys
import pandas as pd
from pathlib import Path
from pinecone import Pinecone
from openai import OpenAI
from dotenv import load_dotenv
import time

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "cfop-fiscal"
PINECONE_NAMESPACE = "default"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Determinar caminho do arquivo
IS_COLAB = 'COLAB_GPU' in os.environ
if IS_COLAB:
    DATA_DIR = Path('/content/data')
else:
    DATA_DIR = Path(__file__).parent.parent / 'data'

CFOP_CSV = DATA_DIR / "CFOP.csv"

def criar_embedding(texto: str, client: OpenAI) -> list:
    """Cria embedding usando OpenAI"""
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=texto
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Erro ao criar embedding: {e}")
        return None

def main():
    print("="*70)
    print("📊 POPULAR ÍNDICE PINECONE COM CFOPs")
    print("="*70)
    
    # Verificar API Keys
    if not PINECONE_API_KEY:
        print("❌ PINECONE_API_KEY não encontrada!")
        print("   Configure no arquivo .env ou como variável de ambiente")
        return
    
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY não encontrada!")
        print("   Configure no arquivo .env ou como variável de ambiente")
        return
    
    print(f"✅ API Keys encontradas")
    print(f"✅ Pinecone Key: {PINECONE_API_KEY[:10]}...{PINECONE_API_KEY[-4:]}")
    print(f"✅ OpenAI Key: {OPENAI_API_KEY[:10]}...{OPENAI_API_KEY[-4:]}")
    
    # Verificar arquivo CSV
    if not CFOP_CSV.exists():
        print(f"❌ Arquivo não encontrado: {CFOP_CSV}")
        return
    
    print(f"\n📂 Carregando: {CFOP_CSV}")
    
    try:
        # Carregar CSV
        df_cfop = pd.read_csv(CFOP_CSV)
        print(f"✅ {len(df_cfop)} CFOPs carregados")
        print(f"📋 Colunas: {', '.join(df_cfop.columns.tolist())}")
        
        # Inicializar clientes
        print("\n🔧 Inicializando Pinecone...")
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)
        
        print("🔧 Inicializando OpenAI...")
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Preparar dados para indexação
        print(f"\n🔄 Processando {len(df_cfop)} CFOPs...")
        vectors = []
        
        for idx, row in df_cfop.iterrows():
            cfop = str(row['CFOP'])
            descricao = str(row['DESCRIÇÃO'])
            aplicacao = str(row.get('APLICAÇÃO', ''))
            
            # Criar texto para embedding
            texto_completo = f"CFOP {cfop}: {descricao}"
            if aplicacao and aplicacao != 'nan':
                texto_completo += f" - Aplicação: {aplicacao}"
            
            # Criar embedding
            embedding = criar_embedding(texto_completo, openai_client)
            
            if embedding:
                # Preparar metadados
                metadata = {
                    'cfop': cfop,
                    'descricao': descricao,
                    'texto': texto_completo
                }
                
                if aplicacao and aplicacao != 'nan':
                    metadata['aplicacao'] = aplicacao
                
                # Adicionar à lista de vetores
                vectors.append({
                    'id': f"cfop_{cfop.replace('.', '_')}",
                    'values': embedding,
                    'metadata': metadata
                })
                
                print(f"   ✅ [{idx+1}/{len(df_cfop)}] CFOP {cfop} processado")
            
            # Pequeno delay para evitar rate limits
            time.sleep(0.1)
        
        # Fazer upsert no Pinecone em lotes
        print(f"\n📤 Enviando {len(vectors)} vetores para Pinecone...")
        batch_size = 100
        
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i+batch_size]
            index.upsert(
                vectors=batch,
                namespace=PINECONE_NAMESPACE
            )
            print(f"   ✅ Batch {i//batch_size + 1}/{(len(vectors)-1)//batch_size + 1} enviado")
        
        # Verificar estatísticas do índice
        print("\n📊 Estatísticas do índice:")
        stats = index.describe_index_stats()
        print(f"   Total de vetores: {stats['total_vector_count']}")
        print(f"   Namespace '{PINECONE_NAMESPACE}': {stats['namespaces'].get(PINECONE_NAMESPACE, {}).get('vector_count', 0)} vetores")
        
        print("\n" + "="*70)
        print("✅ INDEXAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Erro durante a indexação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
