# backend/services/estatisticas_service.py
"""
Serviço de estatísticas e análises
"""
from collections import Counter, defaultdict
from typing import List, Dict, Any
import random
from datetime import datetime

class EstatisticasService:
    """Serviço para cálculo de estatísticas"""
    
    def __init__(self, agente):
        self.agente = agente
    
    def obter_resumo(self, sample_size: int = 200) -> Dict[str, Any]:
        """Calcula resumo geral das estatísticas"""
        total_notas = len(self.agente.df_cabecalho)
        total_itens = len(self.agente.df_itens)
        
        # Validar amostra
        divergencias = self._validar_amostra(sample_size)
        
        taxa_conformidade = (
            (sample_size - len(divergencias)) / sample_size * 100
            if sample_size > 0 else 0
        )
        
        divergencias_criticas = len([
            d for d in divergencias if d.get('tipo') == 'critico'
        ])
        
        return {
            "total_notas": total_notas,
            "total_itens": total_itens,
            "taxa_conformidade": round(taxa_conformidade, 1),
            "divergencias_criticas": divergencias_criticas,
            "divergencias_total": len(divergencias),
            "ultima_analise": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
    
    def obter_distribuicao_cfop(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Retorna distribuição dos CFOPs mais utilizados"""
        # Contar CFOPs
        cfops = self.agente.df_itens['CFOP'].astype(str).str.replace(
            '.', ''
        ).str.replace(',', '').str.replace(' ', '')
        
        contador = Counter(cfops)
        total_itens = len(self.agente.df_itens)
        
        # Top N CFOPs
        top_cfops = []
        for cfop, count in contador.most_common(top_n):
            # Formatar CFOP
            if len(cfop) == 4 and cfop.isdigit():
                cfop_formatado = f"{cfop[0]}.{cfop[1:]}"
            else:
                cfop_formatado = cfop
            
            top_cfops.append({
                "cfop": cfop_formatado,
                "quantidade": count,
                "percentual": round((count / total_itens * 100), 2)
            })
        
        return top_cfops
    
    def obter_divergencias_por_tipo(self, sample_size: int = 200) -> List[Dict[str, Any]]:
        """Retorna divergências agrupadas por tipo"""
        divergencias = {
            "primeiro_digito": 0,
            "ultimos_digitos": 0,
            "conformes": 0
        }
        
        sample_size = min(sample_size, len(self.agente.df_itens))
        
        for _, item in self.agente.df_itens.head(sample_size).iterrows():
            numero_nota = str(item.get('NÚMERO', ''))
            cfop_item = str(item.get('CFOP', ''))
            
            cabecalho = self.agente.df_cabecalho[
                self.agente.df_cabecalho['NÚMERO'].astype(str) == numero_nota
            ]
            
            if not cabecalho.empty:
                primeiro_digito_esperado = self._inferir_primeiro_digito_nota(
                    cabecalho.iloc[0]
                )
                
                cfop_limpo = cfop_item.replace('.', '').replace(',', '').replace(' ', '')
                primeiro_digito_atual = cfop_limpo[0] if cfop_limpo else "?"
                
                if primeiro_digito_esperado != primeiro_digito_atual:
                    divergencias["primeiro_digito"] += 1
                else:
                    divergencias["conformes"] += 1
        
        return [
            {
                "tipo": "Primeiro Dígito Incorreto",
                "quantidade": divergencias["primeiro_digito"],
                "cor": "#ef4444"
            },
            {
                "tipo": "Últimos Dígitos Incorretos",
                "quantidade": divergencias["ultimos_digitos"],
                "cor": "#f59e0b"
            },
            {
                "tipo": "Conformes",
                "quantidade": divergencias["conformes"],
                "cor": "#10b981"
            }
        ]
    
    def obter_operacoes_por_uf(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Retorna distribuição de operações por UF"""
        uf_destino = self.agente.df_cabecalho['UF DESTINATÁRIO'].value_counts().head(top_n)
        
        return [
            {"uf": str(uf), "quantidade": int(count)}
            for uf, count in uf_destino.items()
        ]
    
    def obter_tendencia_mensal(self) -> List[Dict[str, Any]]:
        """Retorna tendência de notas ao longo do tempo (simulado)"""
        meses = ["Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro"]
        
        random.seed(42)  # Resultados consistentes
        
        return [
            {
                "mes": mes,
                "notas": random.randint(80, 150),
                "divergencias": random.randint(5, 25)
            }
            for mes in meses
        ]
    
    def obter_top_divergencias(self, sample_size: int = 200, top_n: int = 10) -> List[Dict[str, Any]]:
        """Retorna top N notas com mais problemas"""
        divergencias_por_nota = defaultdict(list)
        
        sample_size = min(sample_size, len(self.agente.df_itens))
        
        for _, item in self.agente.df_itens.head(sample_size).iterrows():
            numero_nota = str(item.get('NÚMERO', ''))
            cfop_item = str(item.get('CFOP', ''))
            
            cabecalho = self.agente.df_cabecalho[
                self.agente.df_cabecalho['NÚMERO'].astype(str) == numero_nota
            ]
            
            if not cabecalho.empty:
                primeiro_digito_esperado = self._inferir_primeiro_digito_nota(
                    cabecalho.iloc[0]
                )
                
                cfop_limpo = cfop_item.replace('.', '').replace(',', '').replace(' ', '')
                primeiro_digito_atual = cfop_limpo[0] if cfop_limpo else "?"
                
                if primeiro_digito_esperado != primeiro_digito_atual:
                    divergencias_por_nota[numero_nota].append({
                        'cfop': cfop_item,
                        'esperado': f"{primeiro_digito_esperado}xxx"
                    })
        
        # Top N notas com mais divergências
        top_notas = sorted(
            [(nota, len(divs)) for nota, divs in divergencias_por_nota.items()],
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        resultado = []
        for nota, qtd_divergencias in top_notas:
            cabecalho = self.agente.df_cabecalho[
                self.agente.df_cabecalho['NÚMERO'].astype(str) == nota
            ]
            
            if not cabecalho.empty:
                resultado.append({
                    "nota": nota,
                    "divergencias": qtd_divergencias,
                    "natureza": str(cabecalho.iloc[0].get('NATUREZA DA OPERAÇÃO', 'N/A'))[:50],
                    "valor": float(cabecalho.iloc[0].get('VALOR TOTAL DA NF', 0))
                })
        
        return resultado
    
    # ========================================================================
    # MÉTODOS AUXILIARES PRIVADOS
    # ========================================================================
    
    def _validar_amostra(self, sample_size: int) -> List[Dict[str, Any]]:
        """Valida uma amostra de itens"""
        divergencias = []
        sample_size = min(sample_size, len(self.agente.df_itens))
        
        for _, item in self.agente.df_itens.head(sample_size).iterrows():
            numero_nota = str(item.get('NÚMERO', ''))
            cfop_item = str(item.get('CFOP', ''))
            
            cabecalho = self.agente.df_cabecalho[
                self.agente.df_cabecalho['NÚMERO'].astype(str) == numero_nota
            ]
            
            if not cabecalho.empty:
                primeiro_digito_esperado = self._inferir_primeiro_digito_nota(
                    cabecalho.iloc[0]
                )
                
                cfop_limpo = cfop_item.replace('.', '').replace(',', '').replace(' ', '')
                primeiro_digito_atual = cfop_limpo[0] if cfop_limpo else "?"
                
                if primeiro_digito_esperado != primeiro_digito_atual:
                    divergencias.append({
                        'nota': numero_nota,
                        'tipo': 'critico'
                    })
        
        return divergencias
    
    def _inferir_primeiro_digito_nota(self, nota_row) -> str:
        """Infere o primeiro dígito do CFOP para uma nota"""
        natureza = str(nota_row.get('NATUREZA DA OPERAÇÃO', '')).upper()
        uf_emit = str(nota_row.get('UF EMITENTE', '')).strip()
        uf_dest = str(nota_row.get('UF DESTINATÁRIO', '')).strip()
        destino_op = str(nota_row.get('DESTINO DA OPERAÇÃO', '')).strip()
        
        return self.agente._inferir_primeiro_digito(
            natureza, uf_emit, uf_dest, destino_op
        )