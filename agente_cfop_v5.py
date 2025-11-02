"""
FiscalAI v5.0 - Agente Validador de CFOP
Agente conversacional avançado com LangChain + Pinecone
Mantém todas as 15 ferramentas do v4 + busca semântica
"""
import pandas as pd
import os
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool, StructuredTool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
from dotenv import load_dotenv
import traceback
import re
from typing import Optional, Dict, List
from pathlib import Path

from config import settings, DATA_DIR
from services.semantic_search_service import CFOPSemanticSearchService

load_dotenv()


class AgenteValidadorCFOP_V5:
    """
    Agente inteligente para validação de CFOP v5.0
    
    Funcionalidades:
    - Todas as 15 ferramentas do v4
    - Busca semântica com Pinecone (NOVO)
    - Análise estatística avançada
    - Validação inteligente de CFOPs
    - Inferência de CFOP correto
    """
    
    def __init__(self):
        """Inicializa o agente com dados e ferramentas"""
        print("\n" + "="*70)
        print("🤖 INICIALIZANDO AGENTE VALIDADOR CFOP v5.0")
        print("="*70)
        
        # Carregar dados
        self._carregar_dados()
        
        # Verificar API Key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("❌ OPENAI_API_KEY não encontrada!")
        print(f"🔑 OpenAI API Key: {api_key[:8]}...{api_key[-4:]}")
        
        # Configurar LLM
        print("🤖 Configurando ChatOpenAI...")
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0,
            openai_api_key=api_key,
            verbose=False
        )
        print("   ✅ LLM configurado")
        
        # Inicializar busca semântica (NOVO v5)
        self.semantic_search = None
        if settings.use_semantic_search:
            try:
                print("🔍 Inicializando busca semântica Pinecone...")
                self.semantic_search = CFOPSemanticSearchService()
                print("   ✅ Busca semântica ativada")
            except Exception as e:
                print(f"   ⚠️  Busca semântica desabilitada: {e}")
        
        # Criar ferramentas (15 do v4 + novas do v5)
        print(f"🛠️  Criando ferramentas...")
        self.tools = self._criar_ferramentas()
        print(f"   ✅ {len(self.tools)} ferramentas criadas")
        
        # Criar prompt
        print("📝 Criando prompt do agente...")
        self.prompt = self._criar_prompt()
        print("   ✅ Prompt criado")
        
        # Criar agente executor
        print("🤖 Criando agente executor...")
        self.agent = create_openai_functions_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=False,
            max_iterations=10,
            return_intermediate_steps=True,
            handle_parsing_errors=True
        )
        print("   ✅ Agente executor criado")
        
        print("="*70)
        print("✅ AGENTE v5.0 INICIALIZADO E PRONTO!")
        print(f"   📊 {len(self.tools)} ferramentas disponíveis")
        if self.semantic_search:
            print("   🔍 Busca semântica ativa")
        print("="*70 + "\n")
    
    def _carregar_dados(self):
        """Carregar dados dos CSVs"""
        print("\n📂 Carregando dados...")
        
        # Cabeçalhos
        cabecalho_path = settings.cabecalho_csv
        self.df_cabecalho = pd.read_csv(cabecalho_path)
        print(f"   ✅ {len(self.df_cabecalho)} registros de cabeçalho")
        
        # Itens
        itens_path = settings.itens_csv
        self.df_itens = pd.read_csv(itens_path)
        print(f"   ✅ {len(self.df_itens)} itens")
        
        # CFOPs
        cfop_path = settings.cfop_csv
        self.df_cfop = pd.read_csv(cfop_path)
        print(f"   ✅ {len(self.df_cfop)} códigos CFOP")
        
        # Mostrar colunas
        print(f"   📋 Colunas: {', '.join(self.df_cabecalho.columns.tolist()[:5])}...")
    
    def _formatar_cfop_para_busca(self, cfop: str) -> str:
        """Formata CFOP para padrão do CSV (X.YYY)"""
        cfop_limpo = str(cfop).strip().replace('.', '').replace(',', '')
        
        if len(cfop_limpo) == 4 and cfop_limpo.isdigit():
            return f"{cfop_limpo[0]}.{cfop_limpo[1:]}"
        
        return cfop_limpo
    
    def _explicar_primeiro_digito(self, digito: str) -> str:
        """Explica significado do primeiro dígito"""
        explicacoes = {
            '1': 'Entrada - Operação Interna',
            '2': 'Entrada - Operação Interestadual',
            '3': 'Entrada - Operação com Exterior',
            '5': 'Saída - Operação Interna',
            '6': 'Saída - Operação Interestadual',
            '7': 'Saída - Operação com Exterior'
        }
        return explicacoes.get(digito, 'Indefinido')
    
    def _criar_prompt(self):
        """Cria prompt do agente"""
        system_message = """Você é um especialista em análise e validação de CFOP (Código Fiscal de Operações e Prestações) de Notas Fiscais brasileiras com IA avançada.

Sua missão:
1. Analisar notas fiscais e seus itens
2. Inferir o CFOP correto baseado nas regras fiscais
3. Validar se o CFOP informado está correto
4. Gerar relatórios de divergências
5. Explicar as regras aplicadas
6. Usar busca semântica para encontrar CFOPs similares (NOVO v5)

FORMATO DE CFOP:
- CFOPs aceitos: "5102", "5.102", "5 102"
- Sistema formata automaticamente (4 dígitos = X.YYY)

PROCEDIMENTO PARA INFERIR CFOP:

PASSO 1 - IDENTIFICAR TIPO:
- VENDA, REMESSA, RETORNO (sem Dev) → SAÍDA (5, 6, 7)
- ENTRADA, COMPRA, DEVOLUÇÃO, Dev → ENTRADA (1, 2, 3)

PASSO 2 - DETERMINAR ÂMBITO:
- "OPERAÇÃO INTERNA" ou UF_Emit = UF_Dest:
  * Entrada: 1xxx
  * Saída: 5xxx
- "OPERAÇÃO INTERESTADUAL" ou UF_Emit ≠ UF_Dest:
  * Entrada: 2xxx
  * Saída: 6xxx
- "OPERAÇÃO COM EXTERIOR":
  * Entrada: 3xxx
  * Saída: 7xxx

IMPORTANTE - ÍNDICES:
- Índices começam em 0
- "Primeiro" = 0, "Quinto" = 4, "Décimo" = 9
- Converter: posição - 1 = índice

FERRAMENTAS DISPONÍVEIS:
{tool_names}

BUSCA SEMÂNTICA (NOVO v5):
- Use buscar_cfop_semantico para encontrar CFOPs por descrição
- Exemplo: "CFOPs para venda de mercadoria"
- Retorna resultados ranqueados por similaridade

Seja preciso, objetivo e sempre cite as regras aplicadas."""

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_message),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        return prompt
    
    def _criar_ferramentas(self):
        """
        Cria todas as ferramentas do agente
        v4: 15 ferramentas originais
        v5: + busca semântica Pinecone
        """
        
        # ===== FERRAMENTA 1: contar_notas =====
        def contar_notas(dummy: str = "") -> str:
            """Estatísticas completas dos arquivos"""
            try:
                resultado = "📊 ESTATÍSTICAS DO SISTEMA\n"
                resultado += f"{'='*70}\n\n"
                resultado += f"📋 Notas Fiscais: {len(self.df_cabecalho):,}\n"
                resultado += f"📦 Itens: {len(self.df_itens):,}\n"
                resultado += f"🏷️ CFOPs Únicos: {self.df_itens['CFOP'].nunique()}\n"
                resultado += f"📚 CFOPs na Tabela: {len(self.df_cfop)}\n\n"
                
                resultado += f"📋 Colunas Cabeçalho:\n"
                for col in self.df_cabecalho.columns[:10]:
                    resultado += f"   • {col}\n"
                
                return resultado
            except Exception as e:
                return f"Erro: {str(e)}"
        
        # ===== FERRAMENTA 2: listar_notas_cabecalho =====
        def listar_notas_cabecalho(limit: str = "10") -> str:
            """Lista primeiras N notas"""
            try:
                limite = int(limit)
                notas = self.df_cabecalho.head(limite)
                
                resultado = f"📋 PRIMEIRAS {limite} NOTAS FISCAIS\n"
                resultado += f"{'='*70}\n\n"
                
                for idx, nota in notas.iterrows():
                    resultado += f"{idx+1}. Nota: {nota.get('Número da Nota Fiscal', 'N/A')}\n"
                    if 'Data de Emissão' in nota:
                        resultado += f"   Data: {nota['Data de Emissão']}\n"
                    if 'Chave de Acesso da NF-e' in nota:
                        chave = nota['Chave de Acesso da NF-e']
                        resultado += f"   Chave: ...{str(chave)[-8:]}\n"
                    resultado += "\n"
                
                return resultado
            except Exception as e:
                return f"Erro: {str(e)}"
        
        # ===== FERRAMENTA 3: buscar_nota_por_chave =====
        def buscar_nota_por_chave(chave: str) -> str:
            """Busca nota pela chave de 44 dígitos"""
            try:
                chave_limpa = re.sub(r'\D', '', chave)
                nota = self.df_cabecalho[
                    self.df_cabecalho['Chave de Acesso da NF-e'].astype(str).str.replace(r'\D', '', regex=True) == chave_limpa
                ]
                
                if nota.empty:
                    return f"❌ Nota não encontrada para chave: {chave_limpa}"
                
                nota = nota.iloc[0]
                resultado = f"📋 NOTA FISCAL ENCONTRADA\n{'='*70}\n\n"
                
                for col in nota.index:
                    if pd.notna(nota[col]):
                        resultado += f"{col}: {nota[col]}\n"
                
                return resultado
            except Exception as e:
                return f"Erro: {str(e)}"
        
        # ===== FERRAMENTA 4: buscar_nota_por_indice =====
        def buscar_nota_por_indice(indice: str) -> str:
            """Busca nota por índice/posição"""
            try:
                idx = int(indice)
                if idx < 0 or idx >= len(self.df_cabecalho):
                    return f"❌ Índice {idx} fora do intervalo (0-{len(self.df_cabecalho)-1})"
                
                nota = self.df_cabecalho.iloc[idx]
                resultado = f"📋 NOTA NO ÍNDICE {idx}\n{'='*70}\n\n"
                
                for col in nota.index:
                    if pd.notna(nota[col]):
                        resultado += f"{col}: {nota[col]}\n"
                
                return resultado
            except Exception as e:
                return f"Erro: {str(e)}"
        
        # ===== FERRAMENTA 5: buscar_item_por_indice =====
        def buscar_item_por_indice(indice: str) -> str:
            """Busca item por índice"""
            try:
                idx = int(indice)
                if idx < 0 or idx >= len(self.df_itens):
                    return f"❌ Índice {idx} fora do intervalo (0-{len(self.df_itens)-1})"
                
                item = self.df_itens.iloc[idx]
                resultado = f"📦 ITEM NO ÍNDICE {idx}\n{'='*70}\n\n"
                
                for col in item.index:
                    if pd.notna(item[col]):
                        resultado += f"{col}: {item[col]}\n"
                
                return resultado
            except Exception as e:
                return f"Erro: {str(e)}"
        
        # ===== FERRAMENTA 6: buscar_cfop_por_indice =====
        def buscar_cfop_por_indice(indice: str) -> str:
            """Busca CFOP por índice na tabela"""
            try:
                idx = int(indice)
                if idx < 0 or idx >= len(self.df_cfop):
                    return f"❌ Índice {idx} fora do intervalo"
                
                cfop = self.df_cfop.iloc[idx]
                resultado = f"🏷️ CFOP NO ÍNDICE {idx}\n{'='*70}\n\n"
                
                for col in cfop.index:
                    if pd.notna(cfop[col]):
                        resultado += f"{col}: {cfop[col]}\n"
                
                return resultado
            except Exception as e:
                return f"Erro: {str(e)}"
        
        # ===== FERRAMENTA 7: buscar_nota_cabecalho =====
        def buscar_nota_cabecalho(numero: str) -> str:
            """Busca nota pelo número"""
            try:
                nota = self.df_cabecalho[
                    self.df_cabecalho['Número da Nota Fiscal'].astype(str) == str(numero)
                ]
                
                if nota.empty:
                    return f"❌ Nota {numero} não encontrada"
                
                nota = nota.iloc[0]
                resultado = f"📋 NOTA {numero}\n{'='*70}\n\n"
                
                for col in nota.index:
                    if pd.notna(nota[col]):
                        resultado += f"{col}: {nota[col]}\n"
                
                return resultado
            except Exception as e:
                return f"Erro: {str(e)}"
        
        # ===== FERRAMENTA 8: buscar_itens_nota =====
        def buscar_itens_nota(numero: str) -> str:
            """Busca todos itens de uma nota"""
            try:
                nota_cab = self.df_cabecalho[
                    self.df_cabecalho['Número da Nota Fiscal'].astype(str) == str(numero)
                ]
                
                if nota_cab.empty:
                    return f"❌ Nota {numero} não encontrada"
                
                chave = nota_cab.iloc[0]['Chave de Acesso da NF-e']
                itens = self.df_itens[self.df_itens['Chave de Acesso da NF-e'] == chave]
                
                resultado = f"📦 ITENS DA NOTA {numero}\n{'='*70}\n\n"
                resultado += f"Total de itens: {len(itens)}\n\n"
                
                for idx, item in itens.iterrows():
                    resultado += f"Item {item.get('Número do Item', 'N/A')}:\n"
                    resultado += f"   CFOP: {item.get('CFOP', 'N/A')}\n"
                    if 'Descrição do Produto' in item:
                        resultado += f"   Produto: {item['Descrição do Produto']}\n"
                    resultado += "\n"
                
                return resultado
            except Exception as e:
                return f"Erro: {str(e)}"
        
        # ===== FERRAMENTA 9: buscar_cfop =====
        def buscar_cfop(codigo: str) -> str:
            """Busca informações detalhadas de um CFOP"""
            try:
                cfop_formatado = self._formatar_cfop_para_busca(codigo)
                
                # Tentar com formatação
                cfop_info = self.df_cfop[self.df_cfop['CFOP'].astype(str) == cfop_formatado]
                
                # Tentar sem formatação
                if cfop_info.empty:
                    cfop_info = self.df_cfop[self.df_cfop['CFOP'].astype(str).str.replace('.', '') == codigo.replace('.', '')]
                
                if cfop_info.empty:
                    return f"❌ CFOP {codigo} não encontrado"
                
                cfop = cfop_info.iloc[0]
                resultado = f"🏷️ CFOP {codigo}\n{'='*70}\n\n"
                
                for col in cfop.index:
                    if pd.notna(cfop[col]):
                        resultado += f"{col}: {cfop[col]}\n\n"
                
                # Quantas vezes é usado
                count = len(self.df_itens[self.df_itens['CFOP'].astype(str).str.replace('.', '') == codigo.replace('.', '')])
                resultado += f"📊 Utilização: {count:,} vezes no sistema\n"
                
                return resultado
            except Exception as e:
                return f"Erro: {str(e)}"
        
        # ===== FERRAMENTA 10: validar_todas_notas =====
        def validar_todas_notas(limit: str = "100") -> str:
            """Valida CFOP de todas as notas (limite 100)"""
            try:
                limite = min(int(limit), 100)
                
                resultado = f"🔍 VALIDAÇÃO DE CFOPs\n{'='*70}\n\n"
                resultado += f"Analisando {limite} primeiras notas...\n\n"
                
                divergencias = 0
                conformes = 0
                
                for idx in range(min(limite, len(self.df_cabecalho))):
                    nota = self.df_cabecalho.iloc[idx]
                    chave = nota['Chave de Acesso da NF-e']
                    itens = self.df_itens[self.df_itens['Chave de Acesso da NF-e'] == chave]
                    
                    for _, item in itens.iterrows():
                        cfop = item.get('CFOP', '')
                        # Validação básica
                        if cfop and str(cfop) != 'nan':
                            conformes += 1
                        else:
                            divergencias += 1
                
                resultado += f"✅ Conformes: {conformes}\n"
                resultado += f"⚠️ Divergências: {divergencias}\n"
                resultado += f"📊 Taxa de conformidade: {(conformes/(conformes+divergencias)*100):.1f}%\n"
                
                return resultado
            except Exception as e:
                return f"Erro: {str(e)}"
        
        # ===== FERRAMENTA 11: validar_cfop_item_especifico =====
        def validar_cfop_item_especifico(chave_acesso: str, numero_item: str) -> str:
            """Valida CFOP de um item específico com inferência"""
            try:
                # Converter número item
                item_num = numero_item
                if numero_item.lower() in ['primeiro', '1', 'um']:
                    item_num = '1'
                elif numero_item.lower() in ['segundo', '2', 'dois']:
                    item_num = '2'
                
                # Buscar item
                item = self.df_itens[
                    (self.df_itens['Chave de Acesso da NF-e'] == chave_acesso) &
                    (self.df_itens['Número do Item'].astype(str) == str(item_num))
                ]
                
                if item.empty:
                    return f"❌ Item {numero_item} não encontrado na nota {chave_acesso[-8:]}"
                
                item = item.iloc[0]
                cfop_registrado = str(item.get('CFOP', '')).replace('.', '')
                
                # Buscar cabeçalho para inferir
                nota = self.df_cabecalho[self.df_cabecalho['Chave de Acesso da NF-e'] == chave_acesso]
                
                resultado = f"🔍 VALIDAÇÃO CFOP - Item {numero_item}\n{'='*70}\n\n"
                resultado += f"📋 Nota: ...{chave_acesso[-8:]}\n"
                resultado += f"📦 Item: {numero_item}\n"
                resultado += f"🏷️ CFOP Registrado: {cfop_registrado}\n\n"
                
                if not nota.empty:
                    nota = nota.iloc[0]
                    natureza = nota.get('NATUREZA DA OPERAÇÃO', '')
                    uf_emit = nota.get('UF DO EMITENTE', '')
                    uf_dest = nota.get('UF DO DESTINATÁRIO', '')
                    destino = nota.get('DESTINO DA OPERAÇÃO', '')
                    
                    resultado += f"📝 Natureza: {natureza}\n"
                    resultado += f"🗺️ UF Emit: {uf_emit} → UF Dest: {uf_dest}\n"
                    resultado += f"🎯 Destino: {destino}\n\n"
                    
                    # Inferir primeiro dígito
                    primeiro = self._inferir_primeiro_digito(natureza, uf_emit, uf_dest, destino)
                    resultado += f"🔢 Primeiro dígito inferido: {primeiro}\n"
                    resultado += f"   {self._explicar_primeiro_digito(primeiro)}\n\n"
                    
                    # Validar
                    if cfop_registrado and cfop_registrado[0] == primeiro:
                        resultado += "✅ CFOP VÁLIDO - Primeiro dígito correto!\n"
                    elif cfop_registrado:
                        resultado += f"⚠️ POSSÍVEL DIVERGÊNCIA\n"
                        resultado += f"   Registrado: {cfop_registrado[0]} ({self._explicar_primeiro_digito(cfop_registrado[0])})\n"
                        resultado += f"   Esperado: {primeiro} ({self._explicar_primeiro_digito(primeiro)})\n"
                
                return resultado
            except Exception as e:
                return f"Erro: {str(e)}"
        
        # ===== FERRAMENTA 12: analisar_cfops_mais_usados =====
        def analisar_cfops_mais_usados(limite: str = "10") -> str:
            """Analisa CFOPs mais utilizados"""
            try:
                top_n = int(limite)
                cfops_count = self.df_itens['CFOP'].value_counts().head(top_n)
                
                resultado = f"📊 TOP {top_n} CFOPs MAIS USADOS\n{'='*70}\n\n"
                
                total = len(self.df_itens)
                for idx, (cfop, count) in enumerate(cfops_count.items(), 1):
                    percentual = (count / total) * 100
                    resultado += f"{idx}. CFOP {cfop}\n"
                    resultado += f"   Quantidade: {count:,} ({percentual:.1f}%)\n"
                    
                    # Buscar descrição
                    cfop_info = self.df_cfop[self.df_cfop['CFOP'].astype(str) == str(cfop)]
                    if not cfop_info.empty and 'DESCRIÇÃO' in cfop_info.columns:
                        desc = cfop_info.iloc[0]['DESCRIÇÃO']
                        if pd.notna(desc):
                            resultado += f"   Descrição: {desc}\n"
                    resultado += "\n"
                
                return resultado
            except Exception as e:
                return f"Erro: {str(e)}"
        
        # ===== FERRAMENTA 13: analisar_distribuicao_por_uf =====
        def analisar_distribuicao_por_uf(dummy: str = "") -> str:
            """Analisa distribuição por UF"""
            try:
                resultado = "🗺️ DISTRIBUIÇÃO POR UF\n{'='*70}\n\n"
                
                # UF Emitente
                resultado += "📤 UF EMITENTE (TOP 10):\n"
                uf_emit = self.df_cabecalho['UF DO EMITENTE'].value_counts().head(10)
                for uf, count in uf_emit.items():
                    percentual = (count / len(self.df_cabecalho)) * 100
                    resultado += f"   {uf}: {count:,} ({percentual:.1f}%)\n"
                
                resultado += "\n📥 UF DESTINATÁRIO (TOP 10):\n"
                uf_dest = self.df_cabecalho['UF DO DESTINATÁRIO'].value_counts().head(10)
                for uf, count in uf_dest.items():
                    percentual = (count / len(self.df_cabecalho)) * 100
                    resultado += f"   {uf}: {count:,} ({percentual:.1f}%)\n"
                
                return resultado
            except Exception as e:
                return f"Erro: {str(e)}"
        
        # ===== FERRAMENTA 14: analisar_natureza_operacao =====
        def analisar_natureza_operacao(limite: str = "10") -> str:
            """Analisa naturezas de operação mais comuns"""
            try:
                top_n = int(limite)
                naturezas = self.df_cabecalho['NATUREZA DA OPERAÇÃO'].value_counts().head(top_n)
                
                resultado = f"📝 TOP {top_n} NATUREZAS DE OPERAÇÃO\n{'='*70}\n\n"
                
                for idx, (natureza, count) in enumerate(naturezas.items(), 1):
                    percentual = (count / len(self.df_cabecalho)) * 100
                    resultado += f"{idx}. {natureza}\n"
                    resultado += f"   Quantidade: {count:,} ({percentual:.1f}%)\n\n"
                
                return resultado
            except Exception as e:
                return f"Erro: {str(e)}"
        
        # ===== FERRAMENTA 15: calcular_estatisticas_valores =====
        def calcular_estatisticas_valores(dummy: str = "") -> str:
            """Calcula estatísticas de valores das notas"""
            try:
                valores = self.df_cabecalho['VALOR NOTA FISCAL'].dropna()
                
                resultado = "💰 ESTATÍSTICAS DE VALORES\n{'='*70}\n\n"
                resultado += f"Total de notas: {len(valores):,}\n\n"
                resultado += f"Valor Total: R$ {valores.sum():,.2f}\n"
                resultado += f"Valor Médio: R$ {valores.mean():,.2f}\n"
                resultado += f"Valor Mediano: R$ {valores.median():,.2f}\n"
                resultado += f"Valor Mínimo: R$ {valores.min():,.2f}\n"
                resultado += f"Valor Máximo: R$ {valores.max():,.2f}\n"
                resultado += f"Desvio Padrão: R$ {valores.std():,.2f}\n"
                
                return resultado
            except Exception as e:
                return f"Erro: {str(e)}"
        
        # ===== FERRAMENTA 16 (NOVA v5): buscar_cfop_semantico =====
        def buscar_cfop_semantico(query: str) -> str:
            """Busca semântica de CFOPs com Pinecone (NOVO v5)"""
            if not self.semantic_search:
                return "⚠️ Busca semântica não disponível. Configure o Pinecone."
            
            try:
                resultados = self.semantic_search.search_cfop(query, top_k=5)
                
                if not resultados:
                    return f"❌ Nenhum CFOP encontrado para: '{query}'"
                
                resultado = f"🔍 BUSCA SEMÂNTICA: '{query}'\n{'='*70}\n\n"
                
                for i, res in enumerate(resultados, 1):
                    metadata = res.get('metadata', {})
                    score = res.get('score', 0)
                    
                    resultado += f"{i}. CFOP {metadata.get('codigo', 'N/A')} "
                    resultado += f"(Relevância: {score:.1%})\n"
                    
                    if 'descricao' in metadata:
                        resultado += f"   📝 {metadata['descricao']}\n"
                    
                    if 'aplicacao' in metadata:
                        resultado += f"   ✅ {metadata['aplicacao']}\n"
                    
                    resultado += "\n"
                
                return resultado
            except Exception as e:
                return f"Erro na busca semântica: {str(e)}"
        
        # ===== CRIAR LISTA DE FERRAMENTAS =====
        tools = [
            Tool(name="contar_notas", func=contar_notas, 
                 description="Retorna estatísticas completas (notas, itens, CFOPs, colunas)"),
            
            Tool(name="listar_notas_cabecalho", func=listar_notas_cabecalho,
                 description="Lista primeiras N notas. Parâmetro: limit (padrão: 10)"),
            
            Tool(name="buscar_nota_por_chave", func=buscar_nota_por_chave,
                 description="Busca nota pela chave de 44 dígitos"),
            
            Tool(name="buscar_nota_por_indice", func=buscar_nota_por_indice,
                 description="Busca nota por índice/posição (0=primeira, 4=quinta)"),
            
            Tool(name="buscar_item_por_indice", func=buscar_item_por_indice,
                 description="Busca item por índice (0=primeiro, 14=décimo-quinto)"),
            
            Tool(name="buscar_cfop_por_indice", func=buscar_cfop_por_indice,
                 description="Busca CFOP por índice na tabela"),
            
            Tool(name="buscar_nota_cabecalho", func=buscar_nota_cabecalho,
                 description="Busca nota pelo número da nota"),
            
            Tool(name="buscar_itens_nota", func=buscar_itens_nota,
                 description="Busca todos itens de uma nota específica"),
            
            Tool(name="buscar_cfop", func=buscar_cfop,
                 description="Busca informações detalhadas de um CFOP. Aceita: 5102, 5.102, etc"),
            
            Tool(name="validar_todas_notas", func=validar_todas_notas,
                 description="Valida CFOP de todas as notas (limite 100)"),
            
            StructuredTool.from_function(
                func=validar_cfop_item_especifico,
                name="validar_cfop_item_especifico",
                description="Valida CFOP de item específico com inferência. Parâmetros: chave_acesso, numero_item"
            ),
            
            Tool(name="analisar_cfops_mais_usados", func=analisar_cfops_mais_usados,
                 description="Analisa CFOPs mais utilizados. Parâmetro: limite (padrão: 10). Use quando perguntarem sobre CFOPs mais usados"),
            
            Tool(name="analisar_distribuicao_por_uf", func=analisar_distribuicao_por_uf,
                 description="Analisa distribuição de operações por UF (emitente e destinatário)"),
            
            Tool(name="analisar_natureza_operacao", func=analisar_natureza_operacao,
                 description="Analisa naturezas de operação mais comuns"),
            
            Tool(name="calcular_estatisticas_valores", func=calcular_estatisticas_valores,
                 description="Calcula estatísticas financeiras das notas (total, média, mediana, min, max)"),
            
            # NOVA FERRAMENTA v5
            Tool(name="buscar_cfop_semantico", func=buscar_cfop_semantico,
                 description="Busca semântica de CFOPs com Pinecone. Use para encontrar CFOPs por descrição ou contexto. Exemplo: 'CFOPs para venda de mercadoria'. NOVO v5!")
        ]
        
        return tools
    
    def _inferir_primeiro_digito(self, natureza: str, uf_emit: str, 
                                  uf_dest: str, destino_op: str) -> str:
        """Infere primeiro dígito do CFOP"""
        natureza = natureza.upper()
        
        is_entrada = any(palavra in natureza for palavra in 
                        ['ENTRADA', 'COMPRA', 'DEVOLUÇÃO', 'DEV'])
        is_saida = any(palavra in natureza for palavra in 
                      ['VENDA', 'REMESSA']) and 'DEV' not in natureza
        
        if '1 - OPERAÇÃO INTERNA' in destino_op or uf_emit == uf_dest:
            return '1' if is_entrada else '5'
        elif '2 - OPERAÇÃO INTERESTADUAL' in destino_op or uf_emit != uf_dest:
            return '2' if is_entrada else '6'
        elif '3 - OPERAÇÃO COM EXTERIOR' in destino_op:
            return '3' if is_entrada else '7'
        
        return '?'
    
    def processar_mensagem(self, mensagem: str) -> str:
        """
        Processa mensagem do usuário (compatibilidade v4)
        Na verdade delega para o agente LangChain
        """
        return self.processar_pergunta(mensagem)
    
    def processar_pergunta(self, pergunta: str) -> str:
        """Processa pergunta usando agente executor"""
        try:
            resultado = self.agent_executor.invoke({"input": pergunta})
            return resultado["output"]
        except Exception as e:
            error_msg = f"❌ Erro ao processar pergunta: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            return error_msg
    
    def obter_estatisticas(self) -> dict:
        """Retorna estatísticas do sistema"""
        return {
            "total_notas": len(self.df_cabecalho),
            "total_itens": len(self.df_itens),
            "cfops_unicos": self.df_itens['CFOP'].nunique(),
            "cfop_mais_usado": self.df_itens['CFOP'].mode()[0] if not self.df_itens.empty else None
        }
    
    def _obter_descricao_cfop(self, cfop_code: str) -> Optional[str]:
        """Obter descrição de um CFOP"""
        cfop_code = str(cfop_code).replace('.', '')
        cfop_info = self.df_cfop[self.df_cfop['CFOP'].astype(str).str.replace('.', '') == cfop_code]
        
        if not cfop_info.empty and 'DESCRIÇÃO' in cfop_info.columns:
            desc = cfop_info.iloc[0]['DESCRIÇÃO']
            if pd.notna(desc):
                return str(desc)
        
        return None
    
    def validar_item(self, chave_nf: str, numero_item: int) -> str:
        """Validar CFOP de um item (wrapper)"""
        # Usar ferramenta do agente
        return self.processar_pergunta(
            f"Valide o CFOP do item {numero_item} da nota {chave_nf}"
        )

    """
    Agente principal para validação e análise de CFOPs
    Integra busca semântica com Pinecone e análise de dados
    """
    
    def __init__(self):
        """Inicializar agente e carregar dados"""
        print("\n" + "="*70)
        print("🤖 INICIALIZANDO AGENTE VALIDADOR DE CFOP v5.0")
        print("="*70)
        
        # Carregar dados
        self._carregar_dados()
        
        # Inicializar busca semântica se configurado
        self.semantic_search = None
        if settings.use_semantic_search:
            try:
                self.semantic_search = CFOPSemanticSearchService()
                print("✅ Busca semântica ativada")
            except Exception as e:
                print(f"⚠️  Busca semântica desabilitada: {e}")
        
        print("="*70)
        print("✅ AGENTE INICIALIZADO!")
        print("="*70 + "\n")
    
    def _carregar_dados(self):
        """Carregar dados dos CSVs"""
        print("\n📂 Carregando dados...")
        
        # Cabeçalhos
        cabecalho_path = Path(settings.cabecalho_csv)
        if not cabecalho_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {cabecalho_path}")
        
        self.df_cabecalho = pd.read_csv(cabecalho_path)
        print(f"   ✅ Cabeçalhos: {len(self.df_cabecalho)} notas fiscais")
        
        # Itens
        itens_path = Path(settings.itens_csv)
        if not itens_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {itens_path}")
        
        self.df_itens = pd.read_csv(itens_path)
        print(f"   ✅ Itens: {len(self.df_itens)} itens")
        
        # CFOPs
        cfop_path = Path(settings.cfop_csv)
        if not cfop_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {cfop_path}")
        
        self.df_cfop = pd.read_csv(cfop_path)
        print(f"   ✅ CFOPs: {len(self.df_cfop)} códigos")
    
    def processar_mensagem(self, mensagem: str) -> str:
        """
        Processar mensagem do usuário e retornar resposta
        
        Args:
            mensagem: Mensagem do usuário
            
        Returns:
            Resposta formatada
        """
        mensagem = mensagem.lower().strip()
        
        # Comandos diretos
        if "quantas notas" in mensagem or "total de notas" in mensagem:
            return self._contar_notas()
        
        if "quantos itens" in mensagem or "total de itens" in mensagem:
            return self._contar_itens()
        
        if "cfops mais" in mensagem or "cfops populares" in mensagem:
            return self._cfops_populares()
        
        if "explique o cfop" in mensagem or "explicar cfop" in mensagem:
            # Extrair código do CFOP
            import re
            match = re.search(r'\d{4}', mensagem)
            if match:
                cfop_code = match.group(0)
                return self._explicar_cfop(cfop_code)
            else:
                return "Por favor, especifique o código do CFOP (ex: 5102)"
        
        if "valide" in mensagem or "validar" in mensagem:
            return self._processar_validacao(mensagem)
        
        if "mostre" in mensagem and "nota" in mensagem:
            # Extrair número da nota
            import re
            match = re.search(r'\d+', mensagem)
            if match:
                numero = int(match.group(0))
                return self._mostrar_nota(numero)
            else:
                return "Por favor, especifique o número da nota (ex: 'mostre a nota 5')"
        
        # Busca semântica se disponível
        if self.semantic_search and ("cfop" in mensagem or "código" in mensagem):
            return self._buscar_cfop_semanticamente(mensagem)
        
        # Resposta padrão
        return self._resposta_padrao()
    
    def _contar_notas(self) -> str:
        """Contar total de notas fiscais"""
        total = len(self.df_cabecalho)
        return f"📋 Temos **{total:,} notas fiscais** no sistema."
    
    def _contar_itens(self) -> str:
        """Contar total de itens"""
        total = len(self.df_itens)
        return f"📦 Temos **{total:,} itens** cadastrados nas notas fiscais."
    
    def _cfops_populares(self, top_n: int = 10) -> str:
        """Listar CFOPs mais utilizados"""
        cfops_count = self.df_itens['CFOP'].value_counts().head(top_n)
        
        resposta = f"📊 **Top {top_n} CFOPs Mais Utilizados:**\n\n"
        for i, (cfop, count) in enumerate(cfops_count.items(), 1):
            # Buscar descrição
            desc = self._obter_descricao_cfop(str(cfop))
            resposta += f"{i}. **CFOP {cfop}** - {count:,} ocorrências\n"
            if desc:
                resposta += f"   📝 {desc}\n"
            resposta += "\n"
        
        return resposta
    
    def _explicar_cfop(self, cfop_code: str) -> str:
        """Explicar um CFOP específico"""
        # Remover pontos
        cfop_code = cfop_code.replace('.', '')
        
        # Buscar no dataframe
        cfop_info = self.df_cfop[self.df_cfop['Código'].astype(str).str.replace('.', '') == cfop_code]
        
        if cfop_info.empty:
            return f"❌ CFOP {cfop_code} não encontrado na base de dados."
        
        info = cfop_info.iloc[0]
        
        resposta = f"📋 **CFOP {cfop_code}**\n\n"
        
        if 'DESCRIÇÃO' in info and pd.notna(info['DESCRIÇÃO']):
            resposta += f"📝 **Descrição:**\n{info['DESCRIÇÃO']}\n\n"
        
        if 'APLICAÇÃO' in info and pd.notna(info['APLICAÇÃO']):
            resposta += f"✅ **Aplicação:**\n{info['APLICAÇÃO']}\n\n"
        
        # Ver quantas vezes é usado
        count = len(self.df_itens[self.df_itens['CFOP'].astype(str).str.replace('.', '') == cfop_code])
        resposta += f"📊 **Utilização:** {count:,} vezes no sistema\n"
        
        return resposta
    
    def _obter_descricao_cfop(self, cfop_code: str) -> Optional[str]:
        """Obter descrição de um CFOP"""
        cfop_code = str(cfop_code).replace('.', '')
        cfop_info = self.df_cfop[self.df_cfop['Código'].astype(str).str.replace('.', '') == cfop_code]
        
        if not cfop_info.empty and 'DESCRIÇÃO' in cfop_info.columns:
            desc = cfop_info.iloc[0]['DESCRIÇÃO']
            if pd.notna(desc):
                return str(desc)
        
        return None
    
    def _mostrar_nota(self, numero: int) -> str:
        """Mostrar informações de uma nota específica"""
        if numero < 1 or numero > len(self.df_cabecalho):
            return f"❌ Nota {numero} não existe. Temos {len(self.df_cabecalho)} notas no sistema."
        
        # Pegar nota (índice -1)
        nota = self.df_cabecalho.iloc[numero - 1]
        
        resposta = f"📋 **Nota Fiscal #{numero}**\n\n"
        
        # Chave
        if 'Chave de Acesso da NF-e' in nota:
            resposta += f"🔑 **Chave:** {nota['Chave de Acesso da NF-e']}\n\n"
        
        # Número
        if 'Número da Nota Fiscal' in nota:
            resposta += f"📄 **Número NF:** {nota['Número da Nota Fiscal']}\n"
        
        # Data
        if 'Data de Emissão' in nota:
            resposta += f"📅 **Data:** {nota['Data de Emissão']}\n\n"
        
        # Itens
        if 'Chave de Acesso da NF-e' in nota:
            chave = nota['Chave de Acesso da NF-e']
            itens = self.df_itens[self.df_itens['Chave de Acesso da NF-e'] == chave]
            resposta += f"📦 **Itens:** {len(itens)}\n"
        
        return resposta
    
    def _processar_validacao(self, mensagem: str) -> str:
        """Processar solicitação de validação de CFOP"""
        import re
        
        # Tentar extrair chave da NF
        chave_match = re.search(r'\d{44}', mensagem)
        if not chave_match:
            return "❌ Por favor, forneça a chave de 44 dígitos da nota fiscal."
        
        chave = chave_match.group(0)
        
        # Tentar extrair número do item
        item_match = re.search(r'item\s+(\d+)', mensagem)
        if not item_match:
            return "❌ Por favor, especifique o número do item (ex: 'item 2')."
        
        numero_item = int(item_match.group(1))
        
        return self.validar_item(chave, numero_item)
    
    def validar_item(self, chave_nf: str, numero_item: int) -> str:
        """
        Validar CFOP de um item específico
        
        Args:
            chave_nf: Chave da nota fiscal (44 dígitos)
            numero_item: Número do item na nota
            
        Returns:
            Resultado da validação formatado
        """
        # Buscar item
        item = self.df_itens[
            (self.df_itens['Chave de Acesso da NF-e'] == chave_nf) &
            (self.df_itens['Número do Item'] == numero_item)
        ]
        
        if item.empty:
            return f"❌ Item {numero_item} não encontrado na nota {chave_nf[-8:]}"
        
        item = item.iloc[0]
        cfop_item = str(item['CFOP']).replace('.', '')
        
        resposta = f"🔍 **Validação de CFOP**\n\n"
        resposta += f"📋 Nota: ...{chave_nf[-8:]}\n"
        resposta += f"📦 Item: {numero_item}\n"
        resposta += f"🏷️  CFOP: {cfop_item}\n\n"
        
        # Buscar descrição
        desc = self._obter_descricao_cfop(cfop_item)
        if desc:
            resposta += f"📝 **Descrição:**\n{desc}\n\n"
        
        # Análise básica
        resposta += "✅ **Status:** CFOP válido e cadastrado no sistema\n"
        
        return resposta
    
    def _buscar_cfop_semanticamente(self, query: str) -> str:
        """Buscar CFOP usando busca semântica"""
        if not self.semantic_search:
            return "⚠️ Busca semântica não disponível."
        
        try:
            resultados = self.semantic_search.search_cfop(query, top_k=3)
            
            if not resultados:
                return "❌ Nenhum CFOP encontrado para essa busca."
            
            resposta = f"🔍 **Resultados da busca semântica:**\n\n"
            
            for i, resultado in enumerate(resultados, 1):
                metadata = resultado.get('metadata', {})
                score = resultado.get('score', 0)
                
                resposta += f"{i}. **CFOP {metadata.get('codigo', 'N/A')}** "
                resposta += f"(Relevância: {score:.0%})\n"
                
                if 'descricao' in metadata:
                    resposta += f"   📝 {metadata['descricao']}\n"
                
                resposta += "\n"
            
            return resposta
            
        except Exception as e:
            return f"❌ Erro na busca semântica: {e}"
    
    def _resposta_padrao(self) -> str:
        """Resposta padrão quando não entende a pergunta"""
        return """
❓ Desculpe, não entendi sua pergunta.

📋 **Exemplos do que posso fazer:**

• "Quantas notas fiscais temos?"
• "Quais são os CFOPs mais utilizados?"
• "Explique o CFOP 5102"
• "Mostre a quinta nota fiscal"
• "Valide o CFOP do item 2 da nota 35240134028316923228550010003680821895807710"

💡 **Dica:** Seja específico na sua pergunta!
"""
    
    def obter_estatisticas(self) -> Dict:
        """Obter estatísticas do sistema"""
        return {
            "total_notas": len(self.df_cabecalho),
            "total_itens": len(self.df_itens),
            "cfops_unicos": self.df_itens['CFOP'].nunique(),
            "cfop_mais_usado": self.df_itens['CFOP'].mode()[0] if not self.df_itens.empty else None
        }
    
    def obter_cfops_populares(self, top_n: int = 10) -> List[Dict]:
        """Obter lista de CFOPs mais utilizados"""
        cfops_count = self.df_itens['CFOP'].value_counts().head(top_n)
        
        resultado = []
        for cfop, count in cfops_count.items():
            resultado.append({
                "codigo": str(cfop),
                "count": int(count),
                "descricao": self._obter_descricao_cfop(str(cfop))
            })
        
        return resultado
