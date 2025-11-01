# test_semantic_search.py
"""
Script de teste para validação semântica de CFOP
Execute este script para testar a funcionalidade antes de rodar o servidor completo
"""
import os
os.environ['OPENAI_API_KEY'] = 'sua-chave-aqui'
os.environ['PINECONE_API_KEY'] = 'sua-chave-aqui'

from services.pinecone_service import PineconeVectorStore
import pandas as pd

def testar_busca_semantica():
    """Testa a busca semântica de CFOPs"""
    
    print("\n" + "="*70)
    print("🧪 TESTE DE BUSCA SEMÂNTICA DE CFOP")
    print("="*70)
    
    # Inicializar Vector Store
    print("\n1️⃣ Inicializando Pinecone...")
    vector_store = PineconeVectorStore()
    vector_store.criar_ou_conectar_indice()
    
    # Verificar se está populado
    stats = vector_store.index.describe_index_stats()
    print(f"   ✓ Vetores no índice: {stats.total_vector_count}")
    
    if stats.total_vector_count == 0:
        print("\n⚠️  Índice vazio! Execute a célula de população primeiro.")
        return
    
    # Casos de teste
    casos_teste = [
        {
            "descricao": "Venda de notebook Dell Inspiron 15",
            "uf_emitente": "SP",
            "uf_destinatario": "SP",
            "consumidor_final": "1",
            "cfop_esperado": "5102"
        },
        {
            "descricao": "Transferência de mercadoria para filial",
            "uf_emitente": "SP",
            "uf_destinatario": "RJ",
            "consumidor_final": "0",
            "cfop_esperado": "6152"
        },
        {
            "descricao": "Venda de produto industrializado",
            "uf_emitente": "SP",
            "uf_destinatario": "MG",
            "consumidor_final": "0",
            "cfop_esperado": "6101"
        },
        {
            "descricao": "Devolução de compra de mercadoria para revenda",
            "uf_emitente": "RJ",
            "uf_destinatario": "RJ",
            "consumidor_final": "0",
            "cfop_esperado": "5202"
        }
    ]
    
    print("\n2️⃣ Executando casos de teste...\n")
    
    acertos = 0
    total = len(casos_teste)
    
    for i, caso in enumerate(casos_teste, 1):
        print(f"\n{'─'*70}")
        print(f"📝 TESTE {i}/{total}")
        print(f"{'─'*70}")
        print(f"Descrição: {caso['descricao']}")
        print(f"Rota: {caso['uf_emitente']} → {caso['uf_destinatario']}")
        print(f"Consumidor Final: {'Sim' if caso['consumidor_final'] == '1' else 'Não'}")
        print(f"CFOP Esperado: {caso['cfop_esperado']}")
        
        # Buscar
        resultados = vector_store.buscar_cfop_semantico(
            descricao_item=caso['descricao'],
            uf_emitente=caso['uf_emitente'],
            uf_destinatario=caso['uf_destinatario'],
            consumidor_final=caso['consumidor_final'],
            top_k=3
        )
        
        if resultados:
            print(f"\n🔍 Resultados encontrados:")
            for j, res in enumerate(resultados, 1):
                icon = "✅" if res['cfop'] == caso['cfop_esperado'] else "➡️"
                print(f"\n   {icon} {j}º lugar:")
                print(f"      CFOP: {res['cfop']}")
                print(f"      Descrição: {res['descricao'][:60]}...")
                print(f"      Similaridade: {res['similarity_score']} ({res['confianca']})")
            
            # Verificar acerto
            if resultados[0]['cfop'] == caso['cfop_esperado']:
                print(f"\n   ✅ ACERTO! CFOP correto na primeira posição")
                acertos += 1
            elif any(r['cfop'] == caso['cfop_esperado'] for r in resultados):
                print(f"\n   ⚠️  CFOP esperado encontrado, mas não na primeira posição")
            else:
                print(f"\n   ❌ CFOP esperado não encontrado nos top 3")
        else:
            print("\n   ❌ Nenhum resultado encontrado")
    
    # Resultado final
    print(f"\n{'='*70}")
    print(f"📊 RESULTADO FINAL")
    print(f"{'='*70}")
    print(f"Total de testes: {total}")
    print(f"Acertos: {acertos}")
    print(f"Taxa de acerto: {(acertos/total)*100:.1f}%")
    print(f"{'='*70}\n")

def testar_validacao():
    """Testa a validação de CFOP usado"""
    
    print("\n" + "="*70)
    print("🧪 TESTE DE VALIDAÇÃO DE CFOP")
    print("="*70)
    
    # Inicializar Vector Store
    print("\n1️⃣ Inicializando Pinecone...")
    vector_store = PineconeVectorStore()
    vector_store.criar_ou_conectar_indice()
    
    # Casos de teste
    casos = [
        {
            "nome": "CFOP Correto",
            "cfop_usado": "5102",
            "descricao": "Venda de notebook para consumidor final",
            "uf_emitente": "SP",
            "uf_destinatario": "SP",
            "consumidor_final": "1",
            "deve_ser_valido": True
        },
        {
            "nome": "CFOP Incorreto",
            "cfop_usado": "5101",  # Usando 5101 quando deveria ser 5102
            "descricao": "Venda de notebook para consumidor final",
            "uf_emitente": "SP",
            "uf_destinatario": "SP",
            "consumidor_final": "1",
            "deve_ser_valido": False
        }
    ]
    
    print("\n2️⃣ Executando validações...\n")
    
    for caso in casos:
        print(f"\n{'─'*70}")
        print(f"📝 {caso['nome']}")
        print(f"{'─'*70}")
        
        resultado = vector_store.validar_cfop_usado(
            cfop_usado=caso['cfop_usado'],
            descricao_item=caso['descricao'],
            uf_emitente=caso['uf_emitente'],
            uf_destinatario=caso['uf_destinatario'],
            consumidor_final=caso['consumidor_final']
        )
        
        print(f"CFOP Usado: {resultado['cfop_usado']}")
        print(f"CFOP Sugerido: {resultado['cfop_sugerido']}")
        print(f"Resultado: {resultado['mensagem']}")
        print(f"Confiança: {resultado.get('confianca', 'N/A')}")
        
        if resultado['valido'] == caso['deve_ser_valido']:
            print(f"✅ Validação funcionou conforme esperado")
        else:
            print(f"❌ Validação não funcionou como esperado")
    
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    print("\n🚀 Iniciando testes da FiscalAI v5")
    
    try:
        # Teste 1: Busca Semântica
        testar_busca_semantica()
        
        # Teste 2: Validação
        testar_validacao()
        
        print("\n✅ Todos os testes concluídos!")
        
    except Exception as e:
        print(f"\n❌ Erro durante testes: {e}")
        import traceback
        traceback.print_exc()
