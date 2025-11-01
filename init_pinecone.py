# init_pinecone.py
"""
Script de inicialização automática do Pinecone
Popula o índice se estiver vazio
"""
import os
import sys
from pathlib import Path

def inicializar_pinecone():
    """Inicializa e popula Pinecone se necessário"""
    
    try:
        from services.pinecone_service import PineconeVectorStore
        from config import settings, DATA_DIR
        import pandas as pd
        
        print("\n" + "="*70)
        print("🔧 VERIFICANDO PINECONE VECTOR STORE")
        print("="*70)
        
        # Inicializar Vector Store
        print("\n1️⃣ Conectando ao Pinecone...")
        vector_store = PineconeVectorStore()
        vector_store.criar_ou_conectar_indice()
        
        # Verificar se está populado
        stats = vector_store.index.describe_index_stats()
        print(f"   ✓ Vetores atuais no índice: {stats.total_vector_count}")
        
        if stats.total_vector_count == 0:
            print("\n⚠️  Índice vazio! Populando automaticamente...")
            
            # Verificar se arquivo CFOP existe
            cfop_path = DATA_DIR / "CFOP.csv"
            if not cfop_path.exists():
                print(f"\n❌ ERRO: Arquivo CFOP.csv não encontrado em {cfop_path}")
                print("\n📝 SOLUÇÃO:")
                print("   1. Faça upload do arquivo CFOP.csv via interface web, ou")
                print("   2. Coloque o arquivo em: data/CFOP.csv")
                return False
            
            # Carregar CFOP
            print(f"\n2️⃣ Carregando {cfop_path}...")
            df_cfop = pd.read_csv(cfop_path, encoding='utf-8-sig')
            print(f"   ✓ {len(df_cfop)} CFOPs carregados")
            
            # Popular
            print("\n3️⃣ Populando Vector Store...")
            print("⏳ Isso pode levar alguns minutos...")
            
            resultado = vector_store.popular_cfops(df_cfop)
            
            print("\n" + "="*70)
            print("✅ POPULAÇÃO CONCLUÍDA!")
            print("="*70)
            print(f"   ✓ CFOPs processados: {resultado['success']}")
            print(f"   ✗ Erros: {resultado['errors']}")
            print(f"   📍 Total de vetores: {resultado['total_vectors']}")
            print("="*70 + "\n")
            
            return True
        else:
            print(f"\n✅ Índice já populado com {stats.total_vector_count} vetores")
            print("="*70 + "\n")
            return True
            
    except Exception as e:
        print(f"\n❌ ERRO durante inicialização: {e}")
        import traceback
        traceback.print_exc()
        print("\n⚠️  O sistema pode não funcionar corretamente!")
        print("="*70 + "\n")
        return False

if __name__ == "__main__":
    sucesso = inicializar_pinecone()
    sys.exit(0 if sucesso else 1)
