# services/semantic_search_service.py
"""
Serviço de Busca Semântica para CFOP usando Pinecone e OpenAI Embeddings
"""
import os
from typing import List, Dict, Optional, Tuple
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


class CFOPSemanticSearchService:
    """Serviço de busca semântica de CFOP usando embeddings"""
    
    def __init__(
        self,
        index_name: Optional[str] = None,
        namespace: Optional[str] = None,
        embedding_model: Optional[str] = None,
        dimension: Optional[int] = None,
        cloud: Optional[str] = None,
        region: Optional[str] = None,
        metric: Optional[str] = None
    ):
        """
        Inicializa o serviço de busca semântica
        
        Args:
            index_name: Nome do índice Pinecone (padrão do config.py)
            namespace: Namespace para organizar vetores
            embedding_model: Modelo de embedding OpenAI
            dimension: Dimensão dos vetores
            cloud: Cloud provider (aws, gcp, azure)
            region: Região do servidor
            metric: Métrica de similaridade (cosine, euclidean, dotproduct)
        """
        print("\n" + "="*70)
        print("🔍 INICIALIZANDO SERVIÇO DE BUSCA SEMÂNTICA")
        print("="*70)
        
        # Carregar configurações
        from config import settings
        
        # Configurar API keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("❌ OPENAI_API_KEY não encontrada!")
        if not self.pinecone_api_key:
            raise ValueError("❌ PINECONE_API_KEY não encontrada!")
        
        print(f"🔑 OpenAI API Key: {self.openai_api_key[:8]}...{self.openai_api_key[-4:]}")
        print(f"🔑 Pinecone API Key: {self.pinecone_api_key[:8]}...{self.pinecone_api_key[-4:]}")
        
        # Configurações do Pinecone (usar config.py como padrão)
        self.index_name = index_name or settings.pinecone_index_name
        self.namespace = namespace or settings.pinecone_namespace
        self.embedding_model = embedding_model or settings.openai_embedding_model
        self.embedding_dimension = dimension or settings.pinecone_dimension
        self.cloud = cloud or settings.pinecone_cloud
        self.region = region or settings.pinecone_region
        self.metric = metric or settings.pinecone_metric
        
        print(f"\n📊 CONFIGURAÇÕES DO PINECONE:")
        print(f"   • Índice: {self.index_name}")
        print(f"   • Namespace: {self.namespace}")
        print(f"   • Cloud: {self.cloud}")
        print(f"   • Região: {self.region}")
        print(f"   • Dimensão: {self.embedding_dimension}")
        print(f"   • Métrica: {self.metric}")
        print(f"   • Embedding Model: {self.embedding_model}")
        
        # Inicializar clientes
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        
        # Inicializar ou conectar ao índice
        self._setup_index()
        
        print("="*70)
        print("✅ SERVIÇO DE BUSCA SEMÂNTICA INICIALIZADO!")
        print("="*70 + "\n")
    
    def _setup_index(self):
        """Configura ou conecta ao índice Pinecone"""
        print(f"📊 Configurando índice: {self.index_name}")
        
        # Listar índices existentes
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            print(f"   ⚠️ Índice '{self.index_name}' não existe. Criando novo índice...")
            print(f"   • Dimensão: {self.embedding_dimension}")
            print(f"   • Métrica: {self.metric}")
            print(f"   • Cloud: {self.cloud}")
            print(f"   • Região: {self.region}")
            
            self.pc.create_index(
                name=self.index_name,
                dimension=self.embedding_dimension,
                metric=self.metric,
                spec=ServerlessSpec(
                    cloud=self.cloud,
                    region=self.region
                )
            )
            print(f"   ✅ Índice '{self.index_name}' criado com sucesso!")
        else:
            print(f"   ✅ Conectado ao índice existente: {self.index_name}")
        
        # Conectar ao índice
        self.index = self.pc.Index(self.index_name)
        
        # Mostrar estatísticas
        try:
            stats = self.index.describe_index_stats()
            total_vectors = stats.total_vector_count
            
            # Verificar namespace específico se configurado
            if self.namespace and hasattr(stats, 'namespaces'):
                namespace_count = stats.namespaces.get(self.namespace, {}).get('vector_count', 0)
                print(f"   📈 Vetores totais: {total_vectors}")
                print(f"   📦 Vetores no namespace '{self.namespace}': {namespace_count}")
            else:
                print(f"   📈 Vetores no índice: {total_vectors}")
        except Exception as e:
            print(f"   ⚠️ Não foi possível obter estatísticas: {e}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Gera embedding para um texto usando OpenAI
        
        Args:
            text: Texto para gerar embedding
            
        Returns:
            Lista de floats representando o embedding
        """
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Erro ao gerar embedding: {e}")
            raise
    
    def populate_index_from_csv(self, cfop_csv_path: str, batch_size: int = 100):
        """
        Popula o índice Pinecone com embeddings dos CFOPs do CSV
        
        Args:
            cfop_csv_path: Caminho para o arquivo CSV de CFOPs
            batch_size: Tamanho do batch para upload
        """
        print("\n" + "="*70)
        print("📥 POPULANDO ÍNDICE PINECONE COM CFOPs")
        print("="*70)
        
        # Carregar CSV
        print(f"📂 Carregando: {cfop_csv_path}")
        df_cfop = pd.read_csv(cfop_csv_path)
        print(f"   ✅ {len(df_cfop)} códigos CFOP carregados")
        
        # Filtrar apenas linhas com CFOP válido
        df_cfop_validos = df_cfop[df_cfop['CFOP'].notna()].copy()
        print(f"   ✅ {len(df_cfop_validos)} CFOPs válidos para indexação")
        
        vectors_to_upsert = []
        total_processed = 0
        
        for idx, row in df_cfop_validos.iterrows():
            try:
                cfop_code = str(row['CFOP']).strip()
                aplicacao = str(row.get('APLICAÇÃO', '')).strip()
                descricao = str(row.get('DESCRIÇÃO', '')).strip()
                
                # Pular linhas sem aplicação ou descrição
                if not aplicacao or aplicacao == 'nan' or len(aplicacao) < 10:
                    continue
                
                # Criar texto para embedding (concatenar aplicação e descrição)
                text_for_embedding = f"{aplicacao}\n\n{descricao}"
                
                # Gerar embedding
                embedding = self.generate_embedding(text_for_embedding)
                
                # Preparar metadata
                metadata = {
                    "cfop": cfop_code,
                    "aplicacao": aplicacao[:1000],  # Limitar tamanho
                    "descricao": descricao[:1000],
                    "texto_completo": text_for_embedding[:2000]
                }
                
                # Adicionar ao batch
                vectors_to_upsert.append({
                    "id": f"cfop_{cfop_code.replace('.', '_')}",
                    "values": embedding,
                    "metadata": metadata
                })
                
                total_processed += 1
                
                # Upload em batches
                if len(vectors_to_upsert) >= batch_size:
                    self.index.upsert(
                        vectors=vectors_to_upsert,
                        namespace=self.namespace
                    )
                    print(f"   ✅ Batch de {len(vectors_to_upsert)} vetores enviado ao namespace '{self.namespace}' ({total_processed}/{len(df_cfop_validos)})")
                    vectors_to_upsert = []
                
            except Exception as e:
                print(f"   ⚠️ Erro ao processar CFOP {cfop_code}: {e}")
                continue
        
        # Upload do último batch
        if vectors_to_upsert:
            self.index.upsert(
                vectors=vectors_to_upsert,
                namespace=self.namespace
            )
            print(f"   ✅ Último batch de {len(vectors_to_upsert)} vetores enviado ao namespace '{self.namespace}'")
        
        print("="*70)
        print(f"✅ INDEXAÇÃO CONCLUÍDA! Total: {total_processed} CFOPs")
        print(f"   Namespace: {self.namespace}")
        print("="*70 + "\n")
    
    def search_cfop(
        self, 
        query_text: str, 
        top_k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Busca CFOPs semanticamente similares à query
        
        Args:
            query_text: Texto descrevendo a operação fiscal
            top_k: Número de resultados a retornar
            filter_dict: Filtros opcionais para metadata
            
        Returns:
            Lista de dicionários com CFOP e score de similaridade
        """
        try:
            # Gerar embedding da query
            query_embedding = self.generate_embedding(query_text)
            
            # Buscar no Pinecone com namespace
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict,
                namespace=self.namespace
            )
            
            # Formatar resultados
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "cfop": match.metadata.get("cfop"),
                    "score": match.score,
                    "aplicacao": match.metadata.get("aplicacao"),
                    "descricao": match.metadata.get("descricao")
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Erro na busca: {e}")
            raise
    
    def infer_cfop_for_item(
        self,
        natureza_operacao: str,
        uf_emitente: str,
        uf_destinatario: str,
        descricao_produto: str,
        consumidor_final: str,
        indicador_ie: str = "1"
    ) -> Tuple[str, float, str]:
        """
        Infere o CFOP mais adequado para um item baseado em seus atributos
        
        Args:
            natureza_operacao: Natureza da operação (ex: "VENDA", "DEVOLUÇÃO")
            uf_emitente: UF do emitente
            uf_destinatario: UF do destinatário
            descricao_produto: Descrição do produto/serviço
            consumidor_final: Se é consumidor final ("0" ou "1")
            indicador_ie: Indicador de IE do destinatário
            
        Returns:
            Tupla (cfop_sugerido, score_confianca, explicacao)
        """
        print("\n" + "="*70)
        print("🔍 INFERINDO CFOP VIA BUSCA SEMÂNTICA")
        print("="*70)
        
        # Construir query semântica
        query_parts = []
        
        # Adicionar natureza da operação
        query_parts.append(f"Operação: {natureza_operacao}")
        
        # Adicionar âmbito geográfico
        if uf_emitente == uf_destinatario:
            query_parts.append("Operação interna (dentro do mesmo estado)")
        else:
            query_parts.append(f"Operação interestadual (de {uf_emitente} para {uf_destinatario})")
        
        # Adicionar informações do produto
        if descricao_produto and descricao_produto != 'nan':
            query_parts.append(f"Produto: {descricao_produto}")
        
        # Adicionar se é consumidor final
        if consumidor_final == "1":
            query_parts.append("Destinatário é consumidor final")
        else:
            query_parts.append("Destinatário não é consumidor final")
        
        # Adicionar informação de IE
        if indicador_ie == "1":
            query_parts.append("Destinatário é contribuinte do ICMS")
        elif indicador_ie == "9":
            query_parts.append("Destinatário não é contribuinte do ICMS")
        
        query_text = ". ".join(query_parts)
        
        print(f"📝 Query construída:\n{query_text}")
        print("-"*70)
        
        # Buscar CFOPs similares
        results = self.search_cfop(query_text, top_k=3)
        
        if not results:
            print("❌ Nenhum resultado encontrado")
            return ("INDEFINIDO", 0.0, "Nenhum CFOP correspondente encontrado")
        
        # Melhor match
        best_match = results[0]
        cfop_sugerido = best_match["cfop"]
        score = best_match["score"]
        
        # Criar explicação
        explicacao = f"""
🎯 CFOP SUGERIDO: {cfop_sugerido} (Confiança: {score:.2%})

📋 APLICAÇÃO:
{best_match['aplicacao'][:300]}...

💡 ALTERNATIVAS CONSIDERADAS:
"""
        for i, result in enumerate(results[1:], 1):
            explicacao += f"\n{i}. CFOP {result['cfop']} (Score: {result['score']:.2%})"
        
        print(f"\n✅ CFOP sugerido: {cfop_sugerido} (score: {score:.2%})")
        print("="*70 + "\n")
        
        return (cfop_sugerido, score, explicacao)
    
    def clear_index(self, namespace_only: bool = True):
        """
        Limpa vetores do índice
        
        Args:
            namespace_only: Se True, limpa apenas o namespace configurado.
                          Se False, limpa todo o índice.
        """
        if namespace_only:
            print(f"⚠️ Limpando namespace '{self.namespace}' do índice {self.index_name}...")
            self.index.delete(delete_all=True, namespace=self.namespace)
            print(f"✅ Namespace '{self.namespace}' limpo!")
        else:
            print(f"⚠️ Limpando TODO o índice {self.index_name}...")
            self.index.delete(delete_all=True)
            print("✅ Índice completamente limpo!")
    
    def get_index_stats(self) -> Dict:
        """Retorna estatísticas do índice"""
        stats = self.index.describe_index_stats()
        
        result = {
            "total_vectors": stats.total_vector_count,
            "dimension": self.embedding_dimension,
            "index_name": self.index_name,
            "namespace": self.namespace,
            "embedding_model": self.embedding_model,
            "metric": self.metric,
            "cloud": self.cloud,
            "region": self.region
        }
        
        # Adicionar info específica do namespace se disponível
        if hasattr(stats, 'namespaces') and self.namespace in stats.namespaces:
            result["namespace_vectors"] = stats.namespaces[self.namespace].vector_count
        
        return result
