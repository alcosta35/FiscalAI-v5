# services/validacao_semantica.py
"""
Serviço de Validação Semântica de CFOP usando Pinecone Vector Store
FiscalAI v5
"""
import os
from typing import List, Dict, Optional
from pinecone import Pinecone
from openai import OpenAI
import pandas as pd


class ValidadorCFOPSemantico:
    """Validador de CFOP usando busca semântica no Pinecone"""
    
    def __init__(
        self,
        pinecone_api_key: str = None,
        openai_api_key: str = None,
        index_name: str = "fiscalai-cfop"
    ):
        """
        Inicializa o validador semântico
        
        Args:
            pinecone_api_key: Chave API do Pinecone
            openai_api_key: Chave API da OpenAI
            index_name: Nome do índice no Pinecone
        """
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
        
        # Conectar ao índice
        try:
            self.index = self.pc.Index(self.index_name)
            print(f"✅ Conectado ao índice '{self.index_name}'")
        except Exception as e:
            raise ValueError(f"Erro ao conectar ao índice '{self.index_name}': {e}")
        
        # Modelo de embedding
        self.embedding_model = "text-embedding-3-small"
    
    def criar_query_contextual(self, item_data: Dict) -> str:
        """
        Cria uma query contextual a partir dos dados do item da NF
        
        Args:
            item_data: Dicionário com campos do item (pode vir do DataFrame)
        
        Returns:
            String formatada para busca semântica
        """
        # Extrair campos relevantes
        uf_emitente = item_data.get('UF EMITENTE', '')
        uf_destinatario = item_data.get('UF DESTINATÁRIO', '')
        descricao_produto = item_data.get('DESCRIÇÃO DO PRODUTO/SERVIÇO', '')
        ncm = item_data.get('NCM/SH (TIPO DE PRODUTO)', '')
        consumidor_final = item_data.get('CONSUMIDOR FINAL', '')
        indicador_ie = item_data.get('INDICADOR IE DESTINATÁRIO', '')
        
        # Determinar natureza geográfica
        if uf_emitente == uf_destinatario:
            natureza_geografica = "operação dentro do mesmo estado"
        elif uf_destinatario and uf_emitente:
            natureza_geografica = "operação interestadual"
        else:
            natureza_geografica = "operação indeterminada"
        
        # Determinar tipo de destinatário
        tipo_destinatario = ""
        if indicador_ie == '1':
            tipo_destinatario = "contribuinte do ICMS"
        elif indicador_ie == '2':
            tipo_destinatario = "isento de inscrição estadual"
        elif indicador_ie == '9':
            tipo_destinatario = "não contribuinte do ICMS"
        
        # Determinar se é consumidor final
        eh_consumidor_final = "consumidor final" if consumidor_final == '1' else "não é consumidor final"
        
        # Construir query rica em contexto
        query = f"""
        Operação fiscal com as seguintes características:
        
        Geografia: {natureza_geografica}
        UF Origem: {uf_emitente}
        UF Destino: {uf_destinatario}
        
        Destinatário: {tipo_destinatario}, {eh_consumidor_final}
        
        Produto: {descricao_produto}
        NCM: {ncm}
        
        Busco o CFOP apropriado para esta operação de venda/saída de mercadoria.
        """.strip()
        
        return query
    
    def gerar_embedding(self, text: str) -> List[float]:
        """Gera embedding para o texto usando OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            return response.data[0].embedding
        except Exception as e:
            raise ValueError(f"Erro ao gerar embedding: {e}")
    
    def buscar_cfops_similares(
        self, 
        query_text: str, 
        top_k: int = 5,
        min_score: float = 0.7
    ) -> List[Dict]:
        """
        Busca CFOPs mais similares no Pinecone
        
        Args:
            query_text: Texto da query (contexto do item)
            top_k: Número de resultados a retornar
            min_score: Score mínimo de similaridade (0-1)
        
        Returns:
            Lista de dicionários com CFOP, score e metadata
        """
        # Gerar embedding da query
        query_embedding = self.gerar_embedding(query_text)
        
        # Buscar no Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Processar resultados
        cfops_similares = []
        for match in results['matches']:
            score = match['score']
            
            # Filtrar por score mínimo
            if score < min_score:
                continue
            
            metadata = match['metadata']
            cfops_similares.append({
                'cfop': metadata.get('cfop', ''),
                'descricao': metadata.get('descricao', ''),
                'aplicacao': metadata.get('aplicacao', ''),
                'score': round(score, 4),
                'confianca': self._calcular_confianca(score)
            })
        
        return cfops_similares
    
    def _calcular_confianca(self, score: float) -> str:
        """
        Calcula nível de confiança baseado no score
        
        Args:
            score: Score de similaridade (0-1)
        
        Returns:
            Nível de confiança: 'ALTA', 'MÉDIA', 'BAIXA'
        """
        if score >= 0.90:
            return 'ALTA'
        elif score >= 0.75:
            return 'MÉDIA'
        else:
            return 'BAIXA'
    
    def validar_cfop_item(
        self, 
        item_data: Dict, 
        cfop_informado: str = None,
        top_k: int = 3
    ) -> Dict:
        """
        Valida o CFOP de um item usando busca semântica
        
        Args:
            item_data: Dados do item da NF
            cfop_informado: CFOP que foi informado na NF (opcional)
            top_k: Número de sugestões a retornar
        
        Returns:
            Dicionário com validação e sugestões
        """
        # Criar query contextual
        query_text = self.criar_query_contextual(item_data)
        
        # Buscar CFOPs similares
        sugestoes = self.buscar_cfops_similares(query_text, top_k=top_k)
        
        # Preparar resultado
        resultado = {
            'query_gerada': query_text,
            'cfop_informado': cfop_informado,
            'total_sugestoes': len(sugestoes),
            'sugestoes': sugestoes
        }
        
        # Se CFOP foi informado, validar
        if cfop_informado and sugestoes:
            melhor_sugestao = sugestoes[0]
            
            # Verificar se o CFOP informado está entre as sugestões
            cfops_sugeridos = [s['cfop'] for s in sugestoes]
            
            if cfop_informado in cfops_sugeridos:
                # Encontrar posição e score
                idx = cfops_sugeridos.index(cfop_informado)
                resultado['status'] = 'CORRETO'
                resultado['posicao_ranking'] = idx + 1
                resultado['score'] = sugestoes[idx]['score']
                resultado['mensagem'] = f"CFOP informado está correto (#{idx + 1} nas sugestões)"
            else:
                resultado['status'] = 'DIVERGENTE'
                resultado['mensagem'] = f"CFOP divergente. Sugestão: {melhor_sugestao['cfop']} (score: {melhor_sugestao['score']})"
        else:
            # Apenas retornar sugestão
            if sugestoes:
                resultado['status'] = 'SUGERIDO'
                resultado['mensagem'] = f"CFOP sugerido: {sugestoes[0]['cfop']}"
            else:
                resultado['status'] = 'SEM_SUGESTAO'
                resultado['mensagem'] = "Não foi possível encontrar sugestões com confiança adequada"
        
        return resultado
    
    def validar_lote(
        self, 
        df_itens: pd.DataFrame, 
        top_k: int = 3,
        progress_callback = None
    ) -> pd.DataFrame:
        """
        Valida um lote de itens
        
        Args:
            df_itens: DataFrame com itens a validar
            top_k: Número de sugestões por item
            progress_callback: Função para reportar progresso
        
        Returns:
            DataFrame com resultados da validação
        """
        resultados = []
        total = len(df_itens)
        
        for idx, row in df_itens.iterrows():
            # Preparar dados do item
            item_data = row.to_dict()
            cfop_informado = row.get('CFOP', None)
            
            # Validar
            resultado = self.validar_cfop_item(
                item_data=item_data,
                cfop_informado=cfop_informado,
                top_k=top_k
            )
            
            # Adicionar informações do item
            resultado['numero_item'] = row.get('NÚMERO PRODUTO', idx)
            resultado['chave_nfe'] = row.get('CHAVE DE ACESSO', '')
            
            resultados.append(resultado)
            
            # Callback de progresso
            if progress_callback:
                progress_callback(idx + 1, total)
        
        # Converter para DataFrame
        df_resultado = pd.DataFrame(resultados)
        
        return df_resultado
    
    def gerar_relatorio_validacao(self, df_resultado: pd.DataFrame) -> Dict:
        """
        Gera relatório estatístico da validação
        
        Args:
            df_resultado: DataFrame com resultados da validação
        
        Returns:
            Dicionário com estatísticas
        """
        total = len(df_resultado)
        
        # Contar por status
        status_counts = df_resultado['status'].value_counts().to_dict()
        
        # Calcular percentuais
        corretos = status_counts.get('CORRETO', 0)
        divergentes = status_counts.get('DIVERGENTE', 0)
        
        taxa_acerto = (corretos / total * 100) if total > 0 else 0
        taxa_divergencia = (divergentes / total * 100) if total > 0 else 0
        
        # Estatísticas de score (apenas para validações com CFOP informado)
        df_com_cfop = df_resultado[df_resultado['cfop_informado'].notna()]
        
        relatorio = {
            'total_validacoes': total,
            'corretos': corretos,
            'divergentes': divergentes,
            'sem_sugestao': status_counts.get('SEM_SUGESTAO', 0),
            'apenas_sugerido': status_counts.get('SUGERIDO', 0),
            'taxa_acerto': round(taxa_acerto, 2),
            'taxa_divergencia': round(taxa_divergencia, 2),
            'total_com_cfop_informado': len(df_com_cfop)
        }
        
        # Score médio das sugestões top-1
        if 'score' in df_resultado.columns:
            scores = df_resultado['score'].dropna()
            if len(scores) > 0:
                relatorio['score_medio'] = round(scores.mean(), 4)
                relatorio['score_min'] = round(scores.min(), 4)
                relatorio['score_max'] = round(scores.max(), 4)
        
        return relatorio


# Teste local
if __name__ == "__main__":
    print("🧪 Testando ValidadorCFOPSemantico...")
    
    # Exemplo de item para teste
    item_exemplo = {
        'UF EMITENTE': 'SP',
        'UF DESTINATÁRIO': 'RJ',
        'DESCRIÇÃO DO PRODUTO/SERVIÇO': 'Notebook Dell Inspiron 15',
        'NCM/SH (TIPO DE PRODUTO)': '84713012',
        'CONSUMIDOR FINAL': '0',
        'INDICADOR IE DESTINATÁRIO': '1'
    }
    
    try:
        validador = ValidadorCFOPSemantico()
        
        resultado = validador.validar_cfop_item(
            item_data=item_exemplo,
            cfop_informado='6102',
            top_k=3
        )
        
        print("\n📊 Resultado da Validação:")
        print(f"Status: {resultado['status']}")
        print(f"Mensagem: {resultado['mensagem']}")
        print(f"\nTop {len(resultado['sugestoes'])} Sugestões:")
        for i, sug in enumerate(resultado['sugestoes'], 1):
            print(f"{i}. CFOP {sug['cfop']} - Score: {sug['score']} - Confiança: {sug['confianca']}")
            print(f"   {sug['descricao']}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
