"""
Serviço de busca semântica de CFOP usando Pinecone Vector Store
"""
import os
from pinecone import Pinecone
from openai import OpenAI
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class CFOPMatch:
    """Representa um match de CFOP da busca semântica"""
    cfop: str
    descricao: str
    aplicacao: str
    score: float
    texto_completo: str
    
    def __str__(self):
        return f"CFOP {self.cfop} (Score: {self.score:.4f})"


class CFOPSemanticSearch:
    """Serviço de busca semântica de CFOP"""
    
    def __init__(self):
        """Inicializa o serviço de busca"""
        print("\n🔍 Inicializando CFOPSemanticSearch...")
        
        # Verificar API Keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("❌ OPENAI_API_KEY não encontrada!")
        if not self.pinecone_api_key:
            raise ValueError("❌ PINECONE_API_KEY não encontrada!")
        
        # Inicializar clientes
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        
        # Conectar ao índice
        self.index_name = "fiscalai-cfop"
        try:
            self.index = self.pc.Index(self.index_name)
            # Testar conexão
            stats = self.index.describe_index_stats()
            print(f"✅ Conectado ao índice '{self.index_name}'")
            print(f"   Total de vetores: {stats.total_vector_count}")
        except Exception as e:
            raise RuntimeError(f"❌ Erro ao conectar ao índice Pinecone: {e}")
    
    def _gerar_embedding(self, texto: str) -> List[float]:
        """
        Gera embedding para um texto usando OpenAI
        
        Args:
            texto: Texto para gerar embedding
            
        Returns:
            Lista com valores do embedding
        """
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texto
            )
            return response.data[0].embedding
        except Exception as e:
            raise RuntimeError(f"Erro ao gerar embedding: {e}")
    
    def construir_query_de_contexto(
        self,
        natureza_operacao: str,
        uf_emitente: str,
        uf_destinatario: str,
        descricao_produto: Optional[str] = None,
        indicador_ie: Optional[str] = None,
        consumidor_final: Optional[str] = None
    ) -> str:
        """
        Constrói uma query rica baseada no contexto da operação
        
        Args:
            natureza_operacao: Natureza da operação (ex: "VENDA", "COMPRA")
            uf_emitente: UF do emitente
            uf_destinatario: UF do destinatário
            descricao_produto: Descrição do produto/serviço
            indicador_ie: Indicador de IE (1=contribuinte, 2=isento, 9=não contribuinte)
            consumidor_final: Se é consumidor final (0=não, 1=sim)
            
        Returns:
            Query formatada para busca semântica
        """
        # Determinar tipo de operação (entrada/saída)
        natureza_lower = natureza_operacao.lower()
        tipo_operacao = ""
        if any(palavra in natureza_lower for palavra in ['venda', 'remessa', 'saída']):
            tipo_operacao = "saída (venda/remessa)"
        elif any(palavra in natureza_lower for palavra in ['compra', 'entrada', 'aquisição']):
            tipo_operacao = "entrada (compra/aquisição)"
        elif 'devolução' in natureza_lower or 'dev' in natureza_lower:
            if 'venda' in natureza_lower:
                tipo_operacao = "entrada (devolução de venda)"
            else:
                tipo_operacao = "saída (devolução de compra)"
        
        # Determinar âmbito da operação
        if uf_emitente == uf_destinatario:
            ambito = f"operação interna (dentro do estado {uf_emitente})"
        else:
            ambito = f"operação interestadual (de {uf_emitente} para {uf_destinatario})"
        
        # Determinar tipo de destinatário
        tipo_destinatario = ""
        if indicador_ie == "1":
            tipo_destinatario = "destinatário é contribuinte do ICMS"
        elif indicador_ie == "9":
            tipo_destinatario = "destinatário não é contribuinte do ICMS"
        elif indicador_ie == "2":
            tipo_destinatario = "destinatário é isento de inscrição estadual"
        
        # Consumidor final
        info_consumidor = ""
        if consumidor_final == "1":
            info_consumidor = "operação para consumidor final"
        
        # Construir query
        query_parts = [
            f"Natureza: {natureza_operacao}",
            f"Tipo: {tipo_operacao}" if tipo_operacao else "",
            f"Âmbito: {ambito}",
            tipo_destinatario,
            info_consumidor
        ]
        
        if descricao_produto:
            query_parts.append(f"Produto: {descricao_produto}")
        
        # Juntar todas as partes não vazias
        query = ". ".join([p for p in query_parts if p])
        
        return query
    
    def buscar_cfop_por_contexto(
        self,
        natureza_operacao: str,
        uf_emitente: str,
        uf_destinatario: str,
        descricao_produto: Optional[str] = None,
        indicador_ie: Optional[str] = None,
        consumidor_final: Optional[str] = None,
        top_k: int = 5
    ) -> List[CFOPMatch]:
        """
        Busca CFOPs usando contexto da operação
        
        Args:
            natureza_operacao: Natureza da operação
            uf_emitente: UF do emitente
            uf_destinatario: UF do destinatário
            descricao_produto: Descrição do produto
            indicador_ie: Indicador de IE
            consumidor_final: Se é consumidor final
            top_k: Número de resultados
            
        Returns:
            Lista de CFOPMatch ordenada por relevância
        """
        # Construir query
        query_texto = self.construir_query_de_contexto(
            natureza_operacao=natureza_operacao,
            uf_emitente=uf_emitente,
            uf_destinatario=uf_destinatario,
            descricao_produto=descricao_produto,
            indicador_ie=indicador_ie,
            consumidor_final=consumidor_final
        )
        
        print(f"\n🔍 Query construída: {query_texto}")
        
        # Buscar
        return self.buscar_cfop(query_texto, top_k=top_k)
    
    def buscar_cfop(self, query: str, top_k: int = 5) -> List[CFOPMatch]:
        """
        Busca CFOPs usando query de texto livre
        
        Args:
            query: Texto da busca
            top_k: Número de resultados
            
        Returns:
            Lista de CFOPMatch ordenada por relevância
        """
        try:
            # Gerar embedding da query
            query_embedding = self._gerar_embedding(query)
            
            # Buscar no Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Converter para CFOPMatch
            matches = []
            for match in results.matches:
                cfop_match = CFOPMatch(
                    cfop=match.metadata.get('cfop', ''),
                    descricao=match.metadata.get('descricao', ''),
                    aplicacao=match.metadata.get('aplicacao', ''),
                    score=match.score,
                    texto_completo=match.metadata.get('texto_completo', '')
                )
                matches.append(cfop_match)
            
            return matches
            
        except Exception as e:
            print(f"❌ Erro na busca semântica: {e}")
            return []
    
    def validar_cfop_com_contexto(
        self,
        cfop_informado: str,
        natureza_operacao: str,
        uf_emitente: str,
        uf_destinatario: str,
        descricao_produto: Optional[str] = None,
        indicador_ie: Optional[str] = None,
        consumidor_final: Optional[str] = None,
        threshold: float = 0.85
    ) -> Dict:
        """
        Valida um CFOP informado contra busca semântica
        
        Args:
            cfop_informado: CFOP que foi informado
            natureza_operacao: Natureza da operação
            uf_emitente: UF emitente
            uf_destinatario: UF destinatário
            descricao_produto: Descrição do produto
            indicador_ie: Indicador de IE
            consumidor_final: Se é consumidor final
            threshold: Score mínimo para considerar válido
            
        Returns:
            Dict com resultado da validação
        """
        # Normalizar CFOP informado
        cfop_informado = str(cfop_informado).strip().replace('.', '').replace(',', '')
        if len(cfop_informado) == 4:
            cfop_informado = f"{cfop_informado[0]}.{cfop_informado[1:]}"
        
        # Buscar CFOPs sugeridos
        matches = self.buscar_cfop_por_contexto(
            natureza_operacao=natureza_operacao,
            uf_emitente=uf_emitente,
            uf_destinatario=uf_destinatario,
            descricao_produto=descricao_produto,
            indicador_ie=indicador_ie,
            consumidor_final=consumidor_final,
            top_k=5
        )
        
        if not matches:
            return {
                "valido": False,
                "confianca": 0.0,
                "mensagem": "Não foi possível determinar CFOP adequado (erro na busca)",
                "cfop_informado": cfop_informado,
                "cfop_sugerido": None,
                "matches": []
            }
        
        # Verificar se CFOP informado está nos resultados
        cfop_encontrado = False
        posicao = -1
        melhor_match = matches[0]
        
        for i, match in enumerate(matches):
            if match.cfop == cfop_informado:
                cfop_encontrado = True
                posicao = i
                break
        
        # Determinar resultado
        if cfop_encontrado and posicao == 0 and melhor_match.score >= threshold:
            # CFOP informado é o melhor match
            return {
                "valido": True,
                "confianca": melhor_match.score,
                "mensagem": f"✅ CFOP {cfop_informado} está correto (confiança: {melhor_match.score:.2%})",
                "cfop_informado": cfop_informado,
                "cfop_sugerido": cfop_informado,
                "matches": matches[:3]
            }
        
        elif cfop_encontrado and melhor_match.score >= threshold:
            # CFOP informado está nos resultados mas não é o melhor
            return {
                "valido": False,
                "confianca": melhor_match.score,
                "mensagem": f"⚠️ CFOP {cfop_informado} pode estar incorreto. Sugestão: {melhor_match.cfop} (confiança: {melhor_match.score:.2%})",
                "cfop_informado": cfop_informado,
                "cfop_sugerido": melhor_match.cfop,
                "matches": matches[:3]
            }
        
        else:
            # CFOP informado não está nos resultados ou score muito baixo
            return {
                "valido": False,
                "confianca": melhor_match.score,
                "mensagem": f"❌ CFOP {cfop_informado} provavelmente incorreto. Sugestão: {melhor_match.cfop} (confiança: {melhor_match.score:.2%})",
                "cfop_informado": cfop_informado,
                "cfop_sugerido": melhor_match.cfop,
                "matches": matches[:3]
            }
    
    def formatar_resultado_validacao(self, resultado: Dict) -> str:
        """
        Formata resultado de validação para exibição
        
        Args:
            resultado: Dict com resultado da validação
            
        Returns:
            String formatada
        """
        output = []
        output.append("="*70)
        output.append("🔍 RESULTADO DA VALIDAÇÃO SEMÂNTICA")
        output.append("="*70)
        output.append(f"\nCFOP Informado: {resultado['cfop_informado']}")
        output.append(f"Status: {resultado['mensagem']}")
        output.append(f"Confiança: {resultado['confianca']:.2%}")
        
        if resultado.get('cfop_sugerido') and resultado['cfop_sugerido'] != resultado['cfop_informado']:
            output.append(f"\n💡 CFOP Sugerido: {resultado['cfop_sugerido']}")
        
        output.append("\n📊 Top 3 CFOPs mais relevantes:")
        for i, match in enumerate(resultado.get('matches', [])[:3], 1):
            output.append(f"\n{i}. CFOP {match.cfop} (Score: {match.score:.4f})")
            output.append(f"   {match.descricao}")
            if len(match.aplicacao) > 0:
                aplicacao_preview = match.aplicacao[:150]
                if len(match.aplicacao) > 150:
                    aplicacao_preview += "..."
                output.append(f"   Aplicação: {aplicacao_preview}")
        
        output.append("\n" + "="*70)
        
        return "\n".join(output)


# =============================================================================
# TESTES
# =============================================================================

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🧪 Testando CFOPSemanticSearch...")
    
    try:
        # Inicializar serviço
        search_service = CFOPSemanticSearch()
        
        # Teste 1: Busca simples
        print("\n" + "="*70)
        print("TESTE 1: Busca por texto livre")
        print("="*70)
        
        matches = search_service.buscar_cfop(
            "venda de mercadoria para revenda dentro do mesmo estado",
            top_k=3
        )
        
        print(f"\n✅ Encontrados {len(matches)} resultados:")
        for i, match in enumerate(matches, 1):
            print(f"\n{i}. {match}")
            print(f"   {match.descricao}")
        
        # Teste 2: Busca por contexto
        print("\n" + "="*70)
        print("TESTE 2: Busca por contexto")
        print("="*70)
        
        matches = search_service.buscar_cfop_por_contexto(
            natureza_operacao="VENDA DE MERCADORIAS",
            uf_emitente="SP",
            uf_destinatario="RJ",
            descricao_produto="Produtos para revenda",
            indicador_ie="1",
            consumidor_final="0",
            top_k=3
        )
        
        print(f"\n✅ Encontrados {len(matches)} resultados:")
        for i, match in enumerate(matches, 1):
            print(f"\n{i}. {match}")
            print(f"   {match.descricao}")
        
        # Teste 3: Validação
        print("\n" + "="*70)
        print("TESTE 3: Validação de CFOP")
        print("="*70)
        
        resultado = search_service.validar_cfop_com_contexto(
            cfop_informado="6102",
            natureza_operacao="VENDA DE MERCADORIAS",
            uf_emitente="SP",
            uf_destinatario="RJ",
            descricao_produto="Produtos para revenda",
            indicador_ie="1",
            consumidor_final="0"
        )
        
        print(search_service.formatar_resultado_validacao(resultado))
        
        print("\n✅ Todos os testes concluídos!")
        
    except Exception as e:
        print(f"\n❌ Erro nos testes: {e}")
        import traceback
        traceback.print_exc()
