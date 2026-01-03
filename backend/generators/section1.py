"""
Section1Generator - Gerador para Seção 1: Contexto da Ocorrência

Extrai texto baseado nas 13 perguntas da seção 1 (incluindo follow-ups).
Seção 1 nunca tem skip logic (sempre gera).
"""

import re
from datetime import datetime
from typing import Dict

from .base import BaseSectionGenerator


class Section1Generator(BaseSectionGenerator):
    """Gerador para Seção 1: Contexto da Ocorrência"""

    def _enrich_datetime(self, datetime_str: str) -> str:
        """
        Enriquece data/hora para formato narrativo.

        Converte:
        - "22/03/2025 21:11" → "sexta-feira, 22 de março de 2025, às 21h11min"
        - "2025-03-22 21:11:00" → "sexta-feira, 22 de março de 2025, às 21h11min"

        Args:
            datetime_str: String com data/hora (vários formatos aceitos)

        Returns:
            String formatada ou original se não for possível parsear
        """
        if not datetime_str or datetime_str == "Não informado":
            return datetime_str

        # Remover possíveis sufixos de timezone
        datetime_str = re.sub(r'\s*[+-]\d{2}:\d{2}$', '', datetime_str.strip())

        # Tentar vários formatos
        formats = [
            "%d/%m/%Y %H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%d/%m/%Y",
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(datetime_str, fmt)

                # Mapear dia da semana
                weekdays = {
                    0: "segunda-feira",
                    1: "terça-feira",
                    2: "quarta-feira",
                    3: "quinta-feira",
                    4: "sexta-feira",
                    5: "sábado",
                    6: "domingo"
                }

                # Mapear mês
                months = {
                    1: "janeiro", 2: "fevereiro", 3: "março",
                    4: "abril", 5: "maio", 6: "junho",
                    7: "julho", 8: "agosto", 9: "setembro",
                    10: "outubro", 11: "novembro", 12: "dezembro"
                }

                weekday = weekdays[dt.weekday()]
                month = months[dt.month]

                # Se formato inclui hora
                if "%H" in fmt:
                    return f"{weekday}, {dt.day} de {month} de {dt.year}, às {dt.hour}h{dt.minute:02d}min"
                else:
                    return f"{weekday}, {dt.day} de {month} de {dt.year}"

            except ValueError:
                continue

        # Se não conseguiu parsear, retorna original
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
            "1.2": "Composição da guarnição e prefixo da viatura",
            "1.3": "Como foi acionado",
            "1.4": "Informações recebidas no acionamento",
            "1.5": "Houve deslocamento",
            "1.5.1": "Local de partida da guarnição",
            "1.5.2": "Alterações durante o percurso",
            "1.6": "Local exato da ocorrência",
            "1.7": "Histórico do local (ponto de tráfico)",
            "1.8": "Facção criminosa",
            "1.9": "Proximidade de espaço de interesse público",
            "1.9.1": "Nome do estabelecimento",
            "1.9.2": "Distância aproximada"
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
8. ⚠️ NUNCA CITAR LEIS: Não mencione artigos, leis, incisos ou códigos (Ex: Art. 33, Lei 11.343/06, CPP). O policial apenas DESCREVE OS FATOS, a tipificação legal é feita pelo delegado.

⚠️ OBSERVAÇÃO CRÍTICA DO CLAUDIO:
"Não existe patrulhamento de rotina, operação de rotina... É sempre a atividade seguida do objetivo."
Exemplos CORRETOS:
- "Patrulhamento preventivo para combater o tráfico de drogas"
- "Incursão para localizar foragidos"
- "Operação para desarticular ponto de tráfico"
Exemplos ERRADOS:
- "Patrulhamento de rotina" ❌
- "Operação de rotina" ❌

ESTRUTURA ESPERADA (baseada nos modelos do Claudio):
1. Início com contexto temporal: "Cumprindo a ordem de serviço, prevista para [dia da semana], [dia] de [mês] de [ano], por volta das [hora]h[min]min..."
2. Identificar equipe: "a equipe composta pelo [posto + nome]..." (ou "pelos [posto + nomes]" se múltiplos)
3. Se prefixo fornecido: "na viatura [prefixo]..."
4. Descrever acionamento: "foi acionada para...", "recebeu determinação para...", "foi empenhada para..." (SEMPRE com objetivo específico)
5. Informar conteúdo da ordem: O que foi fornecido - use VARIAÇÃO: "A ordem indicava...", "Segundo a denúncia...", "O acionamento reportava..."
6. Deslocamento (se houve): Se resposta 1.5 = SIM, incluir: "A guarnição partiu de [local 1.5.1]..." e se houve alterações [1.5.2], mencionar
7. Detalhar local: Use EXATAMENTE o que foi fornecido - "O local indicado foi..." ou "no endereço..."
8. Histórico do local (se aplicável): "O endereço consta em registros anteriores..." ou "O local possui histórico..." [resposta 1.7]
9. Facção (se aplicável): "A área é dominada pela facção..." [resposta 1.8]
10. Proximidade de interesse público: Se resposta 1.9 = SIM, incluir: "O local da ocorrência situa-se a aproximadamente [1.9.2] do/da [1.9.1]." (NÃO mencione leis ou artigos)

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
