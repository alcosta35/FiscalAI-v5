# scripts/populate_pinecone.py
"""
Script para popular o índice Pinecone com os CFOPs
"""
import sys
from pathlib import Path

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.semantic_search_service import CFOPSemanticSearchService
from config import settings, DATA_DIR
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║          📊 POPULAR ÍNDICE PINECONE COM CFOPs                 ║
    ║                 FiscalAI v5.0                                  ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Verificar arquivo CFOP
    cfop_path = settings.cfop_csv
    if not Path(cfop_path).exists():
        print(f"❌ Arquivo CFOP não encontrado: {cfop_path}")
        print(f"   Por favor, coloque o arquivo CFOP.csv em: {DATA_DIR}")
        return
    
    # Verificar API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY não encontrada!")
        print("   Configure no arquivo .env")
        return
    
    if not os.getenv("PINECONE_API_KEY"):
        print("❌ PINECONE_API_KEY não encontrada!")
        print("   Configure no arquivo .env")
        return
    
    try:
        # Inicializar serviço
        print("\n🔄 Inicializando serviço de busca semântica...")
        service = CFOPSemanticSearchService()
        
        # Popular índice
        print(f"\n📥 Populando índice com CFOPs de: {cfop_path}")
        service.populate_index_from_csv(cfop_path, batch_size=100)
        
        # Mostrar estatísticas finais
        stats = service.get_index_stats()
        print("\n" + "="*70)
        print("✅ INDEXAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*70)
        print(f"📊 Total de vetores no índice: {stats['total_vectors']}")
        print(f"📏 Dimensão dos vetores: {stats['dimension']}")
        print(f"📇 Nome do índice: {stats['index_name']}")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Erro durante a indexação: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()
