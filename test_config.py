#!/usr/bin/env python3
"""
Script de validação da configuração do Pinecone
Execute este script para verificar se tudo está configurado corretamente.
"""

import sys
import os
from pathlib import Path

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

load_dotenv()


def test_api_keys():
    """Testa se as API keys estão configuradas"""
    print("\n" + "="*70)
    print("🔑 TESTANDO API KEYS")
    print("="*70)
    
    openai_key = os.getenv("OPENAI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    
    if not openai_key:
        print("❌ OPENAI_API_KEY não encontrada!")
        print("   Adicione no arquivo .env: OPENAI_API_KEY=sk-...")
        return False
    
    if not pinecone_key:
        print("❌ PINECONE_API_KEY não encontrada!")
        print("   Adicione no arquivo .env: PINECONE_API_KEY=pcsk_...")
        return False
    
    print(f"✅ OpenAI Key: {openai_key[:10]}...{openai_key[-4:]}")
    print(f"✅ Pinecone Key: {pinecone_key[:10]}...{pinecone_key[-4:]}")
    
    return True


def test_config_settings():
    """Testa as configurações do config.py"""
    print("\n" + "="*70)
    print("⚙️ TESTANDO CONFIGURAÇÕES")
    print("="*70)
    
    try:
        from config import settings
        
        print(f"✅ Índice: {settings.pinecone_index_name}")
        print(f"✅ Namespace: {settings.pinecone_namespace}")
        print(f"✅ Dimensão: {settings.pinecone_dimension}")
        print(f"✅ Métrica: {settings.pinecone_metric}")
        print(f"✅ Cloud: {settings.pinecone_cloud}")
        print(f"✅ Região: {settings.pinecone_region}")
        print(f"✅ Embedding Model: {settings.openai_embedding_model}")
        
        # Validar dimensões
        embedding_models = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }
        
        expected_dim = embedding_models.get(settings.openai_embedding_model)
        if expected_dim and settings.pinecone_dimension != expected_dim:
            print(f"\n⚠️ AVISO: Dimensão incompatível!")
            print(f"   Modelo {settings.openai_embedding_model} usa {expected_dim} dimensões")
            print(f"   Mas PINECONE_DIMENSION está configurado como {settings.pinecone_dimension}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao carregar configurações: {e}")
        return False


def test_openai_connection():
    """Testa conexão com OpenAI"""
    print("\n" + "="*70)
    print("🤖 TESTANDO CONEXÃO OPENAI")
    print("="*70)
    
    try:
        from openai import OpenAI
        from config import settings
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Testar embedding
        print("   Gerando embedding de teste...")
        response = client.embeddings.create(
            input="Teste de conexão",
            model=settings.openai_embedding_model
        )
        
        embedding = response.data[0].embedding
        print(f"✅ Embedding gerado: {len(embedding)} dimensões")
        
        if len(embedding) != settings.pinecone_dimension:
            print(f"⚠️ AVISO: Embedding tem {len(embedding)} dimensões,")
            print(f"   mas Pinecone espera {settings.pinecone_dimension}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão OpenAI: {e}")
        return False


def test_pinecone_connection():
    """Testa conexão com Pinecone"""
    print("\n" + "="*70)
    print("📊 TESTANDO CONEXÃO PINECONE")
    print("="*70)
    
    try:
        from pinecone import Pinecone
        from config import settings
        
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        
        # Listar índices
        print("   Listando índices...")
        indexes = [index.name for index in pc.list_indexes()]
        print(f"✅ Índices encontrados: {len(indexes)}")
        
        if indexes:
            for idx in indexes:
                print(f"   • {idx}")
        
        # Verificar se índice configurado existe
        if settings.pinecone_index_name in indexes:
            print(f"\n✅ Índice '{settings.pinecone_index_name}' existe!")
            
            # Conectar e ver estatísticas
            index = pc.Index(settings.pinecone_index_name)
            stats = index.describe_index_stats()
            
            print(f"   📈 Total de vetores: {stats.total_vector_count}")
            
            if hasattr(stats, 'namespaces'):
                print(f"   📦 Namespaces:")
                for ns, info in stats.namespaces.items():
                    print(f"      • {ns}: {info.vector_count} vetores")
        else:
            print(f"\n⚠️ Índice '{settings.pinecone_index_name}' não existe")
            print("   Será criado automaticamente ao popular dados")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão Pinecone: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_semantic_search_service():
    """Testa o serviço de busca semântica"""
    print("\n" + "="*70)
    print("🔍 TESTANDO SERVIÇO DE BUSCA SEMÂNTICA")
    print("="*70)
    
    try:
        from services.semantic_search_service import CFOPSemanticSearchService
        
        print("   Inicializando serviço...")
        service = CFOPSemanticSearchService()
        
        # Ver estatísticas
        stats = service.get_index_stats()
        
        print("\n📊 Estatísticas do Serviço:")
        for key, value in stats.items():
            print(f"   • {key}: {value}")
        
        # Testar geração de embedding
        print("\n   Testando geração de embedding...")
        test_text = "Venda de mercadoria interestadual"
        embedding = service.generate_embedding(test_text)
        print(f"✅ Embedding gerado: {len(embedding)} dimensões")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no serviço: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes"""
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║       🧪 TESTE DE CONFIGURAÇÃO - FiscalAI v5.0                ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    results = []
    
    # Executar testes
    results.append(("API Keys", test_api_keys()))
    results.append(("Configurações", test_config_settings()))
    results.append(("OpenAI", test_openai_connection()))
    results.append(("Pinecone", test_pinecone_connection()))
    results.append(("Serviço", test_semantic_search_service()))
    
    # Resumo
    print("\n" + "="*70)
    print("📋 RESUMO DOS TESTES")
    print("="*70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False
    
    print("="*70)
    
    if all_passed:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("   Seu ambiente está configurado corretamente!")
        print("\n📋 Próximo passo:")
        print("   Execute: python scripts/populate_pinecone.py")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM")
        print("   Verifique os erros acima e corrija antes de continuar")
        print("\n📚 Consulte: PINECONE_CONFIG.md para ajuda")
    
    print()


if __name__ == "__main__":
    main()
