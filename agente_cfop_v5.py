# agente_cfop_v5.py
"""
Agente Validador CFOP v5
Usa busca semântica com Pinecone para validação inteligente
"""
import pandas as pd
from typing import Dict, List, Optional
from services.pinecone_service import PineconeVectorStore
from config import settings

class AgenteValidadorCFOPv5:
    """
    Agente inteligente para validação de CFOP usando busca semântica
    """
    
    def __init__(
        self,
        cabecalho_path: str,
        itens_path: str,
        cfop_path: str,
        auto_popular: bool = True
    ):
        """
        Inicializa o agente validador
        
        Args:
            cabecalho_path: Caminho para CSV de cabeçalhos
            itens_path: Caminho para CSV de itens
            cfop_path: Caminho para CSV de CFOPs
            auto_popular: Se deve popular automaticamente o Pinecone
        """
        print("\n🚀 Inicializando FiscalAI v5 - Validação Semântica")
        print("=" * 70)
        
        # Carregar dados
        print("\n📂 Carregando dados...")
        self.df_cabecalho = pd.read_csv(cabecalho_path, encoding='utf-8-sig', low_memory=False)
        self.df_itens = pd.read_csv(itens_path, encoding='utf-8-sig', low_memory=False)
        self.df_cfop = pd.read_csv(cfop_path, encoding='utf-8-sig', low_memory=False)
        
        print(f"   ✓ Cabeçalhos: {len(self.df_cabecalho):,} registros")
        print(f"   ✓ Itens: {len(self.df_itens):,} registros")
        print(f"   ✓ CFOPs: {len(self.df_cfop):,} registros")
        
        # Inicializar Vector Store
        print("\n🔧 Inicializando Pinecone Vector Store...")
        self.vector_store = PineconeVectorStore()
        self.vector_store.criar_ou_conectar_indice()
        
        # Popular se necessário
        if auto_popular:
            stats = self.vector_store.index.describe_index_stats()
            if stats.total_vector_count == 0:
                print("\n📥 Índice vazio. Populando com CFOPs...")
                self.popular_vector_store()
            else:
                print(f"\n✅ Índice já contém {stats.total_vector_count} vetores")
        
        print("\n" + "=" * 70)
        print("✅ Sistema pronto para uso!")
        print("=" * 70 + "\n")
    
    def popular_vector_store(self) -> Dict:
        """
        Popula o Pinecone com embeddings dos CFOPs
        
        Returns:
            Dict com estatísticas da população
        """
        return self.vector_store.popular_cfops(self.df_cfop)
    
    def buscar_cfop_para_item(
        self,
        item_row: pd.Series,
        cabecalho_row: Optional[pd.Series] = None
    ) -> List[Dict]:
        """
        Busca CFOP adequado para um item usando busca semântica
        
        Args:
            item_row: Série pandas com dados do item
            cabecalho_row: Série pandas com dados do cabeçalho (opcional)
            
        Returns:
            Lista de CFOPs sugeridos com scores
        """
        # Obter dados do cabeçalho se não fornecido
        if cabecalho_row is None:
            chave = item_row.get('CHAVE DE ACESSO', '')
            cabecalho_row = self.df_cabecalho[
                self.df_cabecalho['CHAVE DE ACESSO'] == chave
            ].iloc[0] if not self.df_cabecalho[
                self.df_cabecalho['CHAVE DE ACESSO'] == chave
            ].empty else None
        
        # Extrair informações
        descricao = str(item_row.get('DESCRIÇÃO DO PRODUTO/SERVIÇO', ''))
        uf_emitente = str(cabecalho_row.get('UF EMITENTE', '')) if cabecalho_row is not None else ''
        uf_destinatario = str(cabecalho_row.get('UF DESTINATÁRIO', '')) if cabecalho_row is not None else ''
        consumidor_final = str(cabecalho_row.get('CONSUMIDOR FINAL', '0')) if cabecalho_row is not None else '0'
        
        # Buscar CFOPs
        return self.vector_store.buscar_cfop_semantico(
            descricao_item=descricao,
            uf_emitente=uf_emitente,
            uf_destinatario=uf_destinatario,
            consumidor_final=consumidor_final
        )
    
    def validar_item(
        self,
        item_row: pd.Series,
        cabecalho_row: Optional[pd.Series] = None
    ) -> Dict:
        """
        Valida o CFOP usado em um item
        
        Args:
            item_row: Série pandas com dados do item
            cabecalho_row: Série pandas com dados do cabeçalho (opcional)
            
        Returns:
            Dict com resultado da validação
        """
        # Obter dados do cabeçalho se não fornecido
        if cabecalho_row is None:
            chave = item_row.get('CHAVE DE ACESSO', '')
            cabecalho_match = self.df_cabecalho[
                self.df_cabecalho['CHAVE DE ACESSO'] == chave
            ]
            if not cabecalho_match.empty:
                cabecalho_row = cabecalho_match.iloc[0]
        
        # Extrair informações
        cfop_usado = str(item_row.get('CFOP', ''))
        descricao = str(item_row.get('DESCRIÇÃO DO PRODUTO/SERVIÇO', ''))
        uf_emitente = str(cabecalho_row.get('UF EMITENTE', '')) if cabecalho_row is not None else ''
        uf_destinatario = str(cabecalho_row.get('UF DESTINATÁRIO', '')) if cabecalho_row is not None else ''
        consumidor_final = str(cabecalho_row.get('CONSUMIDOR FINAL', '0')) if cabecalho_row is not None else '0'
        
        # Validar
        return self.vector_store.validar_cfop_usado(
            cfop_usado=cfop_usado,
            descricao_item=descricao,
            uf_emitente=uf_emitente,
            uf_destinatario=uf_destinatario,
            consumidor_final=consumidor_final
        )
    
    def validar_lote(
        self,
        num_amostras: int = 100
    ) -> Dict:
        """
        Valida um lote de itens aleatórios
        
        Args:
            num_amostras: Número de itens a validar
            
        Returns:
            Dict com estatísticas da validação
        """
        print(f"\n🔍 Validando {num_amostras} itens aleatórios...")
        
        # Amostrar itens
        amostra = self.df_itens.sample(n=min(num_amostras, len(self.df_itens)))
        
        resultados = {
            "total": len(amostra),
            "validos": 0,
            "invalidos": 0,
            "sem_resultado": 0,
            "detalhes": []
        }
        
        for idx, item in amostra.iterrows():
            try:
                resultado = self.validar_item(item)
                
                if resultado["valido"] is True:
                    resultados["validos"] += 1
                elif resultado["valido"] is False:
                    resultados["invalidos"] += 1
                else:
                    resultados["sem_resultado"] += 1
                
                resultados["detalhes"].append({
                    "chave": item.get('CHAVE DE ACESSO', ''),
                    "item": item.get('NÚMERO PRODUTO', ''),
                    "descricao": item.get('DESCRIÇÃO DO PRODUTO/SERVIÇO', '')[:50],
                    **resultado
                })
                
            except Exception as e:
                print(f"⚠️ Erro ao validar item: {e}")
                resultados["sem_resultado"] += 1
        
        # Calcular percentuais
        if resultados["total"] > 0:
            resultados["percentual_validos"] = round(
                (resultados["validos"] / resultados["total"]) * 100, 2
            )
            resultados["percentual_invalidos"] = round(
                (resultados["invalidos"] / resultados["total"]) * 100, 2
            )
        
        print(f"\n📊 Resultados:")
        print(f"   ✅ Válidos: {resultados['validos']} ({resultados.get('percentual_validos', 0)}%)")
        print(f"   ⚠️  Inválidos: {resultados['invalidos']} ({resultados.get('percentual_invalidos', 0)}%)")
        print(f"   ❓ Sem resultado: {resultados['sem_resultado']}")
        
        return resultados
    
    def obter_estatisticas(self) -> Dict:
        """
        Retorna estatísticas gerais do sistema
        
        Returns:
            Dict com estatísticas
        """
        stats = self.vector_store.index.describe_index_stats()
        
        return {
            "total_notas": len(self.df_cabecalho),
            "total_itens": len(self.df_itens),
            "total_cfops_cadastrados": len(self.df_cfop),
            "total_vetores_pinecone": stats.total_vector_count,
            "dimensao_embeddings": stats.dimension,
            "modelo_embeddings": settings.openai_embedding_model,
            "threshold_similaridade": settings.similarity_threshold
        }
