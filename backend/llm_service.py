import os
from typing import Dict
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime
import re
import locale

# Carregar variáveis do .env
load_dotenv()

class LLMService:
    """
    Serviço para integração com diferentes LLMs.
    Por enquanto: Gemini apenas.
    Depois: adicionar Claude, OpenAI.
    """
    
    def __init__(self):
        # Carregar API keys do ambiente
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Configurar Gemini
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            # Usar gemini-2.5-flash (rápido, barato, boa quota)
            self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.gemini_model = None
    
    def _enrich_datetime(self, datetime_str: str) -> str:
        """
        Enriquece string de data/hora com ano e dia da semana se necessário.
        
        Exemplos:
        - "22/03 as 21:11" → "sexta-feira, 22 de março de 2025, às 21h11min"
        - "22/03/2025, 21h11" → "sexta-feira, 22 de março de 2025, às 21h11min"
        - "15 de março de 2024, 14h30" → mantém como está (já completo)
        """
        try:
            # Extrair data
            date_match = re.search(r'(\d{1,2})/(\d{1,2})(?:/(\d{4}))?', datetime_str)
            
            if date_match:
                day = int(date_match.group(1))
                month = int(date_match.group(2))
                year = int(date_match.group(3)) if date_match.group(3) else datetime.now().year
                
                # Criar objeto datetime
                date_obj = datetime(year, month, day)
                
                # Dias da semana em português
                weekdays = ['segunda-feira', 'terça-feira', 'quarta-feira', 
                           'quinta-feira', 'sexta-feira', 'sábado', 'domingo']
                weekday = weekdays[date_obj.weekday()]
                
                # Meses em português
                months = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
                         'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
                month_name = months[month - 1]
                
                # Extrair hora
                time_match = re.search(r'(\d{1,2})[h:](\d{0,2})', datetime_str)
                if time_match:
                    hour = time_match.group(1)
                    minute = time_match.group(2) if time_match.group(2) else "00"
                    time_str = f"às {hour}h{minute}min"
                else:
                    time_str = ""
                
                # Formato final: "sexta-feira, 22 de março de 2025, às 21h11min"
                return f"{weekday}, {day} de {month_name} de {year}, {time_str}".strip(", ")
            
            # Se não conseguir parsear, retornar original
            return datetime_str
            
        except Exception as e:
            # Em caso de erro, retornar original
            print(f"[DEBUG] Erro ao enriquecer data: {e}")
            return datetime_str
    
    def _build_prompt(self, section_data: Dict[str, str]) -> str:
        """
        Constrói o prompt usando os modelos do Claudio como referência.
        
        Baseado nos documentos:
        - 1 Início do BO.docx (6 modelos diferentes)
        - PACOTÃO 1 e 2 (exemplos certo vs errado)
        - REGRAS GERAIS.docx
        """
        
        # Enriquecer data/hora se necessário
        datetime_raw = section_data.get("1.1", "Não informado")
        datetime_enriched = self._enrich_datetime(datetime_raw)
        
        # Montar dados das respostas
        questions_map = {
            "1.1": "Dia, data e hora do acionamento",
            "1.2": "Composição da guarnição e prefixo",
            "1.3": "Natureza do empenho",
            "1.4": "Ordem de serviço / COPOM / DDU",
            "1.5": "Local exato da ocorrência",
            "1.6": "Histórico do local / facção"
        }
        
        answers_text = f"{questions_map['1.1']}: {datetime_enriched}\n"
        
        for key, question in questions_map.items():
            if key == "1.1":
                continue  # Já adicionamos acima com data enriquecida
            answer = section_data.get(key, "Não informado")
            answers_text += f"{question}: {answer}\n"
        
        prompt = f"""Você é um assistente especializado em redigir Boletins de Ocorrência policiais de tráfico de drogas, seguindo o manual do Claudio Moreira.

Sua tarefa é gerar o texto da SEÇÃO 1 - CONTEXTO DA OCORRÊNCIA com base nas informações coletadas.

INFORMAÇÕES COLETADAS:
{answers_text}

⚠️ REGRA CRÍTICA - NUNCA INVENTAR INFORMAÇÕES:
- Use APENAS as informações fornecidas acima
- Se algo não foi informado, NÃO invente (número de OS, horário, endereço completo, etc)
- Se falta informação, use formulações genéricas: "a equipe foi acionada", "no local indicado"
- PROIBIDO inventar: números, nomes, horários, endereços, facções, prefixos

REGRAS DE REDAÇÃO (nunca violar):
1. Narração em 3ª pessoa, voz ativa, ordem direta
2. Frases curtas, estilo jornalístico, dois espaços entre frases
3. Norma culta - ZERO juridiquês, ZERO gerúndio, ZERO "linguagem policial"
4. PROIBIDO termos vazios: "em atitude suspeita", "resistiu ativamente", "movimentação típica"
5. Substituições obrigatórias: "veio a óbito"→"foi a óbito"; "caiu ao solo"→"caiu no chão"
6. Individualizar locais: use o endereço FORNECIDO, não invente números ou nomes
7. Evitar repetições: use pronomes ou sinônimos ("a guarnição", "os militares", "a equipe")

ESTRUTURA ESPERADA (baseada nos modelos do Claudio):
1. Início com contexto temporal: "Cumprindo a ordem de serviço, prevista para [dia da semana], [dia] de [mês] de [ano], por volta das [hora]h[min]min..."
2. Identificar equipe: "a equipe composta pelo [posto + nome]..." (ou "pelos [posto + nomes]" se múltiplos)
3. Se prefixo fornecido: "na viatura [prefixo]..."
4. Descrever acionamento: "foi acionada para...", "recebeu determinação para...", "foi empenhada para..."
5. Informar conteúdo da ordem: O que foi fornecido - use VARIAÇÃO: "A ordem indicava...", "Segundo a denúncia...", "O acionamento reportava..."
6. Detalhar local: Use EXATAMENTE o que foi fornecido - "O local indicado foi..." ou "no endereço..."
7. Histórico (se aplicável): "O endereço consta em registros anteriores..." ou "O local possui histórico..."

EXEMPLOS DE QUALIDADE (do manual do Claudio):

✅ CERTO (informações completas):
"Cumprindo a ordem de serviço nº 123/2024, prevista para sexta-feira, 15 de março de 2024, por volta das 14h30min, a equipe composta pelo Sgt João Silva e Cb Pedro Santos, na viatura prefixo 1234, foi acionada para atender ocorrência de tráfico de drogas.  A ordem de serviço indicava denúncia anônima via COPOM reportando comercialização de entorpecentes na Rua das Flores, número 123, bairro Centro, próximo ao Bar do João.  O endereço consta em registros e relatórios anteriores como ponto de tráfico e reincidência de denúncias.  Segundo as denúncias e boletins anteriores, trata-se de área sob influência da facção denominada XYZ."

✅ TAMBÉM CERTO (informações parciais - SEM INVENTAR):
"No dia 22 de março de 2025, a guarnição foi acionada via COPOM para atender denúncia anônima de tráfico de drogas.  O local indicado foi a Rua das Acácias, bairro Floresta.  O endereço possui histórico de operações anteriores relacionadas ao tráfico."

❌ ERRADO (inventou informações):
"No dia 22/03, às 14h30min..." (inventou horário)
"...ordem de serviço nº 123/2024..." (inventou número de OS)
"...número 456..." (inventou número do endereço)

FORMATO DE SAÍDA:
- Parágrafo corrido, SEM bullet points
- Dois espaços entre frases
- Completude: incluir elementos FORNECIDOS, sem inventar

GERE AGORA o texto da Seção 1 usando SOMENTE as informações fornecidas:"""

        return prompt
    
    async def generate_section_text(
        self, 
        section_data: Dict[str, str],
        provider: str = "gemini"
    ) -> str:
        """
        Gera o texto da seção usando o LLM escolhido.
        """
        
        if provider == "gemini":
            return self._generate_with_gemini(section_data)
        elif provider == "claude":
            # TODO: implementar depois
            raise NotImplementedError("Claude ainda não implementado")
        elif provider == "openai":
            # TODO: implementar depois
            raise NotImplementedError("OpenAI ainda não implementado")
        else:
            raise ValueError(f"Provider {provider} não suportado")
    
    def _generate_with_gemini(self, section_data: Dict[str, str]) -> str:
        """
        Gera texto usando Gemini.
        """
        if not self.gemini_model:
            raise ValueError("Gemini API key não configurada. Configure GEMINI_API_KEY no .env")
        
        try:
            prompt = self._build_prompt(section_data)
            
            # Gerar texto
            response = self.gemini_model.generate_content(prompt)
            
            # Extrair texto
            generated_text = response.text.strip()
            
            return generated_text
            
        except Exception as e:
            raise Exception(f"Erro ao gerar texto com Gemini: {str(e)}")
    
    def validate_api_keys(self) -> Dict[str, bool]:
        """
        Verifica quais API keys estão configuradas.
        Útil para health check.
        """
        return {
            "gemini": self.gemini_api_key is not None,
            "claude": False,  # TODO
            "openai": False   # TODO
        }
