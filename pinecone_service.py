# services/pinecone_service.py
"""
Serviço para gerenciamento do Pinecone Vector Store
Responsável por criar índice, popular com embeddings e realizar buscas semânticas
"""
import pandas as pd
from typing import List, Dict, Tuple, Optional
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
import time
from config import settings

class PineconeVectorStore:
    """Gerencia o Vector Store do Pinecone para CFOPs"""
    
    def __init__(self):
        """Inicializa cliente OpenAI e Pinecone"""
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        self.index_name = settings.pinecone_index_name
        self.index = None
        
    def _create_embedding(self, text: str) -> List[float]:
        """
        Cria embedding usando OpenAI
        
        Args:
            text: Texto para gerar embedding
            
        Returns:
            Lista de floats representando o embedding
        """
        try:
            response = self.openai_client.embeddings.create(
                model=settings.openai_embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Erro ao criar embedding: {e}")
            raise
    
    def criar_ou_conectar_indice(self) -> None:
        """
        Cria índice no Pinecone ou conecta a um existente
        """
        try:
            # Verificar se índice já existe
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                print(f"🔨 Criando índice '{self.index_name}'...")
                
                self.pc.create_index(
                    name=self.index_name,
                    dimension=settings.pinecone_dimension,
                    metric=settings.pinecone_metric,
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                
                # Aguardar índice ficar pronto
                while not self.pc.describe_index(self.index_name).status['ready']:
                    print("⏳ Aguardando índice ficar pronto...")
                    time.sleep(1)
                
                print(f"✅ Índice '{self.index_name}' criado com sucesso!")
            else:
                print(f"✅ Conectado ao índice existente '{self.index_name}'")
            
            # Conectar ao índice
            self.index = self.pc.Index(self.index_name)
            
        except Exception as e:
            print(f"❌ Erro ao criar/conectar índice: {e}")
            raise
    
    def popular_cfops(self, df_cfop: pd.DataFrame) -> Dict:
        """
        Popula o Pinecone com embeddings dos CFOPs
        
        Args:
            df_cfop: DataFrame com colunas CFOP, DESCRIÇÃO, APLICAÇÃO
            
        Returns:
            Dict com estatísticas do processo
        """
        if self.index is None:
            raise ValueError("Índice não inicializado. Execute criar_ou_conectar_indice() primeiro.")
        
        print("\n🚀 Iniciando população do Vector Store...")
        
        vectors_to_upsert = []
        success_count = 0
        error_count = 0
        
        # Limpar valores nulos
        df_cfop = df_cfop.dropna(subset=['APLICAÇÃO'])
        
        for idx, row in df_cfop.iterrows():
            try:
                cfop = str(row['CFOP']).strip()
                descricao = str(row['DESCRIÇÃO']).strip() if pd.notna(row['DESCRIÇÃO']) else ""
                aplicacao = str(row['APLICAÇÃO']).strip()
                
                # Pular linhas vazias ou inválidas
                if not cfop or not aplicacao or cfop == 'nan':
                    continue
                
                # Criar texto combinado para embedding (mais contexto)
                texto_completo = f"CFOP {cfop}: {descricao}. Aplicação: {aplicacao}"
                
                # Gerar embedding
                embedding = self._create_embedding(texto_completo)
                
                # Preparar metadata
                metadata = {
                    "cfop": cfop,
                    "descricao": descricao,
                    "aplicacao": aplicacao,
                    "primeiro_digito": cfop[0] if len(cfop) > 0 else "",
                    "grupo": cfop[:2] if len(cfop) >= 2 else ""
                }
                
                # Adicionar à lista de vetores
                vectors_to_upsert.append({
                    "id": f"cfop_{cfop}_{idx}",
                    "values": embedding,
                    "metadata": metadata
                })
                
                success_count += 1
                
                # Fazer upsert em lotes de 100
                if len(vectors_to_upsert) >= 100:
                    self.index.upsert(vectors=vectors_to_upsert)
                    print(f"📤 Enviados {success_count} CFOPs...")
                    vectors_to_upsert = []
                
            except Exception as e:
                error_count += 1
                print(f"⚠️ Erro ao processar CFOP {cfop}: {e}")
                continue
        
        # Enviar vetores restantes
        if vectors_to_upsert:
            self.index.upsert(vectors=vectors_to_upsert)
        
        # Aguardar indexação
        time.sleep(2)
        
        # Obter estatísticas
        stats = self.index.describe_index_stats()
        
        resultado = {
            "success": success_count,
            "errors": error_count,
            "total_vectors": stats.total_vector_count,
            "dimension": stats.dimension
        }
        
        print(f"\n✅ População concluída!")
        print(f"   ✓ Sucesso: {success_count}")
        print(f"   ✗ Erros: {error_count}")
        print(f"   📊 Total no índice: {stats.total_vector_count}")
        
        return resultado
    
    def buscar_cfop_semantico(
        self, 
        descricao_item: str,
        uf_emitente: str,
        uf_destinatario: str,
        consumidor_final: str = "0",
        top_k: int = None
    ) -> List[Dict]:
        """
        Busca CFOPs usando similaridade semântica
        
        Args:
            descricao_item: Descrição do produto/serviço
            uf_emitente: UF do emitente
            uf_destinatario: UF do destinatário
            consumidor_final: Se é consumidor final (0 ou 1)
            top_k: Número de resultados a retornar
            
        Returns:
            Lista de dicts com CFOP, score e metadata
        """
        if self.index is None:
            raise ValueError("Índice não inicializado.")
        
        if top_k is None:
            top_k = settings.top_k_results
        
        # Determinar primeiro dígito baseado na geografia
        # Operações de SAÍDA (5, 6, 7)
        if uf_emitente == uf_destinatario:
            primeiro_digito = "5"  # Dentro do estado
        else:
            primeiro_digito = "6"  # Interestadual
        
        # Criar query enriquecida
        query_text = f"""
        Descrição do produto: {descricao_item}
        Operação: {"venda para consumidor final" if consumidor_final == "1" else "venda normal"}
        Tipo: {"operação dentro do estado" if primeiro_digito == "5" else "operação interestadual"}
        """
        
        # Gerar embedding da query
        query_embedding = self._create_embedding(query_text)
        
        # Buscar no Pinecone com filtro de primeiro dígito
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k * 2,  # Buscar mais para depois filtrar
            include_metadata=True,
            filter={"primeiro_digito": primeiro_digito}
        )
        
        # Processar resultados
        cfops_encontrados = []
        for match in results.matches[:top_k]:
            cfops_encontrados.append({
                "cfop": match.metadata["cfop"],
                "descricao": match.metadata["descricao"],
                "aplicacao": match.metadata["aplicacao"],
                "similarity_score": round(match.score, 4),
                "confianca": self._calcular_confianca(match.score)
            })
        
        return cfops_encontrados
    
    def _calcular_confianca(self, score: float) -> str:
        """
        Calcula nível de confiança baseado no score de similaridade
        
        Args:
            score: Score de similaridade (0-1)
            
        Returns:
            String indicando nível de confiança
        """
        if score >= 0.90:
            return "MUITO ALTA"
        elif score >= 0.80:
            return "ALTA"
        elif score >= 0.70:
            return "MÉDIA"
        elif score >= 0.60:
            return "BAIXA"
        else:
            return "MUITO BAIXA"
    
    def validar_cfop_usado(
        self,
        cfop_usado: str,
        descricao_item: str,
        uf_emitente: str,
        uf_destinatario: str,
        consumidor_final: str = "0"
    ) -> Dict:
        """
        Valida se o CFOP usado está correto comparando com sugestão semântica
        
        Args:
            cfop_usado: CFOP que foi utilizado na NF-e
            descricao_item: Descrição do produto
            uf_emitente: UF do emitente
            uf_destinatario: UF do destinatário
            consumidor_final: Se é consumidor final
            
        Returns:
            Dict com resultado da validação
        """
        # Buscar CFOPs recomendados
        cfops_sugeridos = self.buscar_cfop_semantico(
            descricao_item=descricao_item,
            uf_emitente=uf_emitente,
            uf_destinatario=uf_destinatario,
            consumidor_final=consumidor_final,
            top_k=3
        )
        
        if not cfops_sugeridos:
            return {
                "valido": None,
                "cfop_usado": cfop_usado,
                "cfop_sugerido": None,
                "mensagem": "Não foi possível encontrar CFOPs similares",
                "confianca": "N/A"
            }
        
        # Verificar se CFOP usado está entre os sugeridos
        cfop_principal = cfops_sugeridos[0]
        cfops_match = [c for c in cfops_sugeridos if c["cfop"] == cfop_usado]
        
        if cfops_match:
            # CFOP usado está entre os sugeridos
            match = cfops_match[0]
            return {
                "valido": True,
                "cfop_usado": cfop_usado,
                "cfop_sugerido": cfop_usado,
                "similarity_score": match["similarity_score"],
                "confianca": match["confianca"],
                "mensagem": "✅ CFOP correto",
                "alternativas": cfops_sugeridos[1:] if len(cfops_sugeridos) > 1 else []
            }
        else:
            # CFOP usado difere da sugestão
            return {
                "valido": False,
                "cfop_usado": cfop_usado,
                "cfop_sugerido": cfop_principal["cfop"],
                "similarity_score": cfop_principal["similarity_score"],
                "confianca": cfop_principal["confianca"],
                "mensagem": f"⚠️ CFOP divergente. Sugestão: {cfop_principal['cfop']}",
                "justificativa": cfop_principal["aplicacao"],
                "alternativas": cfops_sugeridos[1:]
            }
    
    def limpar_indice(self) -> None:
        """Remove todos os vetores do índice"""
        if self.index:
            self.index.delete(delete_all=True)
            print("🗑️ Índice limpo com sucesso")
    
    def deletar_indice(self) -> None:
        """Deleta completamente o índice do Pinecone"""
        try:
            self.pc.delete_index(self.index_name)
            print(f"🗑️ Índice '{self.index_name}' deletado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao deletar índice: {e}")
