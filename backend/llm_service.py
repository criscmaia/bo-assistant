import os
from typing import Dict
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
import re
import locale

# Importar geradores do novo package
from backend.generators import (
    Section1Generator,
    Section2Generator,
    Section3Generator,
    Section4Generator,
)

# Carregar variáveis do .env
load_dotenv()

class LLMService:
    """
    Serviço para integração com diferentes LLMs.
    Suportados: Gemini, Groq.
    Planejados: Claude, OpenAI.
    """

    def __init__(self):
        # Carregar API keys do ambiente
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")

        # Configurar Gemini
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            # Usar gemini-2.5-flash (20 req/dia no free tier)
            # NOTA: Se atingir limite diário, aguardar reset às 00:00 UTC ou upgrade para tier pago
            self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.gemini_model = None

        # Configurar Groq
        if self.groq_api_key:
            # Usar llama-3.3-70b-versatile (14.400 req/dia no free tier)
            self.groq_client = Groq(api_key=self.groq_api_key)
        else:
            self.groq_client = None

        # Inicializar geradores (Template Method Pattern)
        self._generators = {
            1: Section1Generator(self.gemini_model, self.groq_client),
            2: Section2Generator(self.gemini_model, self.groq_client),
            3: Section3Generator(self.gemini_model, self.groq_client),
            4: Section4Generator(self.gemini_model, self.groq_client),
        }

    # ==================== MÉTODO UNIFICADO (NOVO) ====================

    def generate_section_text(self, section: int, section_data: Dict[str, str], provider: str = "groq") -> str:
        """
        Método unificado para gerar texto de qualquer seção.

        Este método substitui os 8 métodos generate_sectionX_text() duplicados
        usando o Template Method Pattern.

        Args:
            section: Número da seção (1-8)
            section_data: Dicionário com respostas da seção (ex: {"1.1": "...", "1.2": "..."})
            provider: "gemini" ou "groq" (padrão: "groq")

        Returns:
            Texto gerado pela LLM ou string vazia se seção pulada

        Raises:
            ValueError: Se seção não suportada ou provider inválido

        Exemplo:
            >>> text = llm_service.generate_section_text(1, {"1.1": "22/03/2025 21:11", ...}, "groq")
        """
        generator = self._generators.get(section)
        if not generator:
            raise ValueError(f"Seção {section} não suportada. Seções disponíveis: {list(self._generators.keys())}")

        return generator.generate(section_data, provider)

    # ==================== MÉTODOS LEGADOS (serão removidos após validação) ====================

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
    
    # ⚠️ NOTA: Métodos _build_prompt, generate_section1_text, _generate_with_gemini e _generate_with_groq
    # foram removidos e substituídos por backend/generators/section1.py (Template Method Pattern)
    # Use: llm_service.generate_section_text(section=1, section_data, provider)

    def validate_api_keys(self) -> Dict[str, bool]:
        """
        Verifica quais API keys estão configuradas.
        Útil para health check.
        """
        return {
            "gemini": self.gemini_api_key is not None,
            "groq": self.groq_api_key is not None,
            "claude": False,  # TODO
            "openai": False   # TODO
        }

    # ========== SEÇÃO 2: ABORDAGEM A VEÍCULO ==========

    # ⚠️ NOTA: Métodos _build_prompt_sectionN, generate_sectionN_text, _generate_sectionN_with_*
    # das seções 2, 3 e 4 foram removidos e substituídos por backend/generators/sectionN.py
    # Use: llm_service.generate_section_text(section=N, section_data, provider)

    # ========================================================================
    # SEÇÃO 5: FUNDADA SUSPEITA
    # ========================================================================

    def generate_section5_text(self, section_data: Dict[str, str], provider: str = "groq") -> str:
        """
        Gera texto narrativo da Seção 5 (Fundada Suspeita).

        Args:
            section_data: Dicionário com respostas {step: answer}
            provider: "gemini", "groq", "claude" ou "openai"

        Returns:
            Texto gerado ou string vazia se seção foi pulada
        """
        # Se não houve abordagem por fundada suspeita, retorna vazio
        if section_data.get("5.1", "").strip().upper() in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
            return ""

        # Gerar com provider selecionado
        if provider == "gemini":
            return self._generate_section5_with_gemini(section_data)
        elif provider == "groq":
            return self._generate_section5_with_groq(section_data)
        elif provider == "claude":
            raise NotImplementedError("Claude ainda não implementado para Seção 5")
        elif provider == "openai":
            raise NotImplementedError("OpenAI ainda não implementado para Seção 5")
        else:
            raise ValueError(f"Provider {provider} não suportado")

    def _generate_section5_with_gemini(self, section_data: Dict[str, str]) -> str:
        """
        Gera texto da Seção 5 usando Gemini.
        """
        if not self.gemini_model:
            raise ValueError("Gemini API key não configurada. Configure GEMINI_API_KEY no .env")

        try:
            prompt = self._build_prompt_section5(section_data)

            # Se prompt vazio (seção pulada), retornar vazio
            if not prompt:
                return ""

            # Gerar texto
            response = self.gemini_model.generate_content(prompt)

            # Extrair texto
            generated_text = response.text.strip()

            return generated_text

        except Exception as e:
            error_msg = str(e)

            # Tratar erro de quota excedida
            if "429" in error_msg or "quota" in error_msg.lower() or "ResourceExhausted" in error_msg:
                raise Exception("Quota diária do Gemini excedida. Tente novamente mais tarde ou use outro modelo.")

            raise Exception(f"Erro ao gerar texto da Seção 5 com Gemini: {error_msg}")

    def _generate_section5_with_groq(self, section_data: Dict[str, str]) -> str:
        """
        Gera texto da Seção 5 (Fundada Suspeita) usando Groq.
        """
        if not self.groq_client:
            raise ValueError("Groq API key não configurada. Configure GROQ_API_KEY no .env")

        try:
            prompt = self._build_prompt_section5(section_data)

            # Se prompt vazio (seção pulada), retornar vazio
            if not prompt:
                return ""

            # Gerar texto
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente especializado em redigir Boletins de Ocorrência policiais no padrão da PMMG."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )

            generated_text = response.choices[0].message.content.strip()
            return generated_text

        except Exception as e:
            error_msg = str(e)

            # Tratar erro de rate limit
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                raise Exception("Limite de requisições do Groq atingido. Aguarde alguns segundos.")

            raise Exception(f"Erro ao gerar texto da Seção 5 com Groq: {error_msg}")

    def _build_prompt_section5(self, section_data: Dict[str, str]) -> str:
        """
        Constrói prompt para Seção 5 (Fundada Suspeita).

        Fonte:
        - materiais-claudio/_01_fundada_suspeita.txt
        - materiais-claudio/_regras_gerais_-_gpt_trafico.txt
        """

        # Verifica se seção foi pulada (não houve abordagem por fundada suspeita)
        if section_data.get("5.1", "").strip().upper() in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
            return ""  # Não gerar texto

        # Extrair respostas
        o_que_viu = section_data.get("5.2", "Não informado")
        quem_viu = section_data.get("5.3", "Não informado")
        caracteristicas = section_data.get("5.4", "Não informado")

        # Construir prompt baseado no material do Claudio
        prompt = f"""Você é um redator especializado em Boletins de Ocorrência policiais da Polícia Militar de Minas Gerais. Sua tarefa é gerar o trecho da SEÇÃO 5 (Fundada Suspeita) do BO de tráfico de drogas.

REGRAS OBRIGATÓRIAS (Claudio Moreira - autor de "Polícia na Prática"):

1. NUNCA invente informações não fornecidas pelo usuário
2. Use APENAS os dados das respostas fornecidas abaixo
3. Escreva em terceira pessoa, tempo passado
4. Use linguagem técnica, objetiva e norma culta
5. Descreva FATOS CONCRETOS observados (não impressões subjetivas)
6. Gere texto em 2-3 parágrafos fluidos
7. NÃO use juridiquês, gerúndio ou termos vagos como "em atitude suspeita"
8. ⚠️ NUNCA CITAR LEIS: Não mencione artigos, leis, incisos, códigos ou jurisprudência (Ex: Art. 33, Lei 11.343/06, CPP, STF, HC). O policial apenas DESCREVE OS FATOS, a tipificação legal é feita pelo delegado.

CONTEXTO TÉCNICO (para sua compreensão, NÃO incluir no texto gerado):

A busca pessoal exige INDÍCIOS CONCRETOS E OBJETIVOS, não sendo suficiente:
- Nervosismo isolado (sem contexto)
- Mera presença em local de criminalidade
- "Atitude suspeita" (termo vago e inadmissível)

BASES LEGÍTIMAS PARA BUSCA PESSOAL (pelo menos uma):

1. CONDUTA VISÍVEL E ANORMAL:
   - Correr ou fugir ao avistar a viatura
   - Desfazer-se de objetos (jogar sacola, arremessar algo)
   - Vigiar terceiros de forma sistemática
   - Simular transações comerciais (entrega rápida + dinheiro)

2. INFORMAÇÃO PRÉVIA CONFIÁVEL:
   - Denúncia anônima corroborada por observação direta
   - BOs anteriores do local (registros de tráfico)
   - Relatórios de inteligência
   - Registros de monitoramento

3. CONTEXTO SENSÍVEL RECONHECIDO:
   - Ponto de tráfico comprovado (por registros ou investigações)
   - Área com ocorrências recentes documentadas

REQUISITOS DA ABORDAGEM:

1. Sequência lógica dos fatos observados (o que vimos → comportamento anormal → abordagem)
2. Individualização das percepções ("O Sgt. Silva viu X", "O Cb. Almeida observou Y")
3. Conexão entre comportamento e suspeita de crime específico

DADOS FORNECIDOS PELO USUÁRIO:

- O que a equipe viu ao chegar: {o_que_viu}
- Quem viu, de onde viu e o que exatamente observou: {quem_viu}
- Características e ações dos abordados: {caracteristicas}

ESTRUTURA NARRATIVA (seguir esta ordem):

1. Contexto de chegada: o que a equipe visualizou ao chegar no local
2. Observação específica: qual policial viu e o que exatamente observou
3. Comportamento suspeito: reação dos abordados ao perceberem a viatura
4. Identificação: características físicas, roupas e identificação completa (nome + vulgo)

EXEMPLOS CORRETOS:

✅ Exemplo 1 - Flagrante visual + reação suspeita:
"Durante patrulhamento pela Rua das Palmeiras, região com registros anteriores de tráfico de drogas, a equipe visualizou um homem de camisa vermelha e bermuda jeans retirando pequenos invólucros de um buraco no muro e entregando-os a motociclistas que paravam rapidamente. O Sargento João, de dentro da viatura estacionada a aproximadamente 20 metros do local, observou o suspeito realizando pelo menos três entregas e recebendo dinheiro em troca. Ao perceber a aproximação da viatura, o indivíduo demonstrou nervosismo acentuado, guardou parte do material no bolso e tentou fugir em direção ao beco lateral. Foi realizada abordagem ao suspeito, posteriormente identificado como JOÃO DA SILVA SANTOS, vulgo 'Vermelho', CPF 123.456.789-00, residente na Rua das Palmeiras, nº 45."

✅ Exemplo 2 - Local conhecido + comportamento anormal:
"No local indicado pela denúncia, conhecido por registros de tráfico conforme BOs 2024-123 e 2024-456, a equipe observou um indivíduo de camiseta azul realizando contato rápido com motoristas que paravam por cerca de 10 segundos. O Cabo Almeida, posicionado na esquina oposta, viu o suspeito entregar pequenos pacotes e receber valores em espécie. Ao avistar a viatura, o indivíduo jogou uma pochete no chão e correu em direção ao Bar Central. Após cerco tático, foi abordado o indivíduo CARLOS SANTOS OLIVEIRA, alcunha 'Marreco', altura aproximada de 1,80m, trajando camiseta azul e bermuda preta."

✅ Exemplo 3 - Vigilância + transação ilícita:
"Na Rua Central, altura do número 200, durante operação de combate ao tráfico, o Soldado Pires visualizou um homem de boné preto realizando vigilância constante, olhando repetidamente para os dois lados da rua. Momentos depois, dois indivíduos se aproximaram, receberam algo das mãos do homem de boné e entregaram dinheiro. A troca durou menos de cinco segundos. Ao perceber a presença policial, o suspeito tentou esconder objetos na cintura e se desfez de uma sacola plástica. Foi abordado MARCOS VIEIRA DA COSTA, vulgo 'Marquinhos', morador da Rua Central, nº 220, trajando boné preto, camiseta branca e calça jeans."

❌ ERROS A EVITAR (causam NULIDADE):

• "Em atitude suspeita" (termo vago demais - INADMISSÍVEL)
• "Demonstrou nervosismo" (sem descrever COMO demonstrou)
• "Área conhecida pelo tráfico" (sem base objetiva - BOs, registros)
• "Foi abordado por fundadas suspeitas" (conclusão jurídica, não é fato)
• "Indivíduo suspeito" (sem descrever O QUE gerou suspeita)
• Não individualizar as características físicas de cada abordado

IMPORTANTE:

- A observação ANTES da abordagem é crucial (o que vimos que motivou a abordagem)
- Sempre descrever COMPORTAMENTOS CONCRETOS (correu, jogou, vigiava, entregava)
- Cada abordado deve ter descrição individualizada (roupa + porte + gestos + nome completo + vulgo)
- Se alguma resposta estiver como "Não informado", OMITA aquela informação
- Dois espaços entre frases
- Manter coerência temporal: observação → comportamento → abordagem → identificação

GERE AGORA O TEXTO DA SEÇÃO 5, seguindo RIGOROSAMENTE as regras acima:"""

        return prompt

    # ========================================================================
    # SEÇÃO 6: REAÇÃO E USO DA FORÇA
    # ========================================================================

    def generate_section6_text(self, section_data: Dict[str, str], provider: str = "groq") -> str:
        """
        Gera texto narrativo da Seção 6 (Reação e Uso da Força).

        Args:
            section_data: Dicionário com respostas {step: answer}
            provider: "gemini", "groq", "claude" ou "openai"

        Returns:
            Texto gerado ou string vazia se seção foi pulada
        """
        # Se não houve resistência, retorna vazio
        if section_data.get("6.1", "").strip().upper() in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
            return ""

        # Gerar com provider selecionado
        if provider == "gemini":
            return self._generate_section6_with_gemini(section_data)
        elif provider == "groq":
            return self._generate_section6_with_groq(section_data)
        elif provider == "claude":
            raise NotImplementedError("Claude ainda não implementado para Seção 6")
        elif provider == "openai":
            raise NotImplementedError("OpenAI ainda não implementado para Seção 6")
        else:
            raise ValueError(f"Provider {provider} não suportado")

    def _generate_section6_with_gemini(self, section_data: Dict[str, str]) -> str:
        """
        Gera texto da Seção 6 usando Gemini.
        """
        if not self.gemini_model:
            raise ValueError("Gemini API key não configurada. Configure GEMINI_API_KEY no .env")

        try:
            prompt = self._build_prompt_section6(section_data)

            # Se prompt vazio (seção pulada), retornar vazio
            if not prompt:
                return ""

            # Gerar texto
            response = self.gemini_model.generate_content(prompt)

            # Extrair texto
            generated_text = response.text.strip()

            return generated_text

        except Exception as e:
            error_msg = str(e)

            # Tratar erro de quota excedida
            if "429" in error_msg or "quota" in error_msg.lower() or "ResourceExhausted" in error_msg:
                raise Exception("Quota diária do Gemini excedida. Tente novamente mais tarde ou use outro modelo.")

            raise Exception(f"Erro ao gerar texto da Seção 6 com Gemini: {error_msg}")

    def _generate_section6_with_groq(self, section_data: Dict[str, str]) -> str:
        """
        Gera texto da Seção 6 (Reação e Uso da Força) usando Groq.
        """
        if not self.groq_client:
            raise ValueError("Groq API key não configurada. Configure GROQ_API_KEY no .env")

        try:
            prompt = self._build_prompt_section6(section_data)

            # Se prompt vazio (seção pulada), retornar vazio
            if not prompt:
                return ""

            # Gerar texto
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente especializado em redigir Boletins de Ocorrência policiais no padrão da PMMG."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )

            generated_text = response.choices[0].message.content.strip()
            return generated_text

        except Exception as e:
            error_msg = str(e)

            # Tratar erro de rate limit
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                raise Exception("Limite de requisições do Groq atingido. Aguarde alguns segundos.")

            raise Exception(f"Erro ao gerar texto da Seção 6 com Groq: {error_msg}")

    def _build_prompt_section6(self, section_data: Dict[str, str]) -> str:
        """
        Constrói prompt para Seção 6 (Reação e Uso da Força).

        Fonte:
        - materiais-claudio/_02_uso_da_forca_e_algemas.txt
        - materiais-claudio/_08_atendimento_medico_e_integridade_fisica_do_autor.txt
        - Súmula Vinculante 11 (STF) + Decreto 8.858/2016
        """

        # Verifica se seção foi pulada (não houve resistência)
        if section_data.get("6.1", "").strip().upper() in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
            return ""  # Não gerar texto

        # Extrair respostas
        descricao_resistencia = section_data.get("6.2", "Não informado")
        tecnica_aplicada = section_data.get("6.3", "Não informado")
        justificativa_algemas = section_data.get("6.4", "Não informado")
        ferimentos = section_data.get("6.5", "Não informado")

        # Construir prompt baseado no material do Claudio
        prompt = f"""Você é um redator especializado em Boletins de Ocorrência policiais da Polícia Militar de Minas Gerais. Sua tarefa é gerar o trecho da SEÇÃO 6 (Reação e Uso da Força) do BO de tráfico de drogas.

REGRAS OBRIGATÓRIAS (Claudio Moreira - autor de "Polícia na Prática"):

1. NUNCA invente informações não fornecidas pelo usuário
2. Use APENAS os dados das respostas fornecidas abaixo
3. Escreva em terceira pessoa, tempo passado
4. Use linguagem técnica, objetiva e norma culta
5. Descreva AÇÕES CONCRETAS (não impressões subjetivas)
6. Gere texto em 4 parágrafos fluidos e objetivos
7. PROIBIDO usar expressões genéricas como "resistiu ativamente", "uso moderado da força", "ficou agressivo"
8. ⚠️ NUNCA CITAR LEIS: Não mencione artigos, leis, incisos, códigos, súmulas ou jurisprudência (Ex: Art. 33, Lei 11.343/06, Súmula Vinculante 11, STF, Decreto). O policial apenas DESCREVE OS FATOS, a tipificação legal é feita pelo delegado.

CONTEXTO TÉCNICO (para sua compreensão, NÃO incluir no texto gerado):

O uso de algemas só é lícito em caso de resistência, fundado receio de fuga ou perigo à integridade física própria ou alheia. A força e as algemas são REAÇÕES, nunca decisões prévias. Deve-se narrar comportamentos CONCRETOS que geraram a necessidade, sem clichês ou termos vagos.

ESTRUTURA NARRATIVA OBRIGATÓRIA (4 PARÁGRAFOS):

PARÁGRAFO 1 - RESISTÊNCIA:
- O que o autor fez? (empurrou, correu, desferiu soco, etc.)
- Contra quem? (nome e graduação do policial)
- Em que contexto? (durante abordagem, ao ser revistado, etc.)

PARÁGRAFO 2 - TÉCNICA E RESULTADO:
- Quem aplicou? (graduação + nome)
- Qual técnica? (chave de braço, cotovelada, taser, etc.)
- Qual resultado? (imobilizou, neutralizou, conteve)

PARÁGRAFO 3 - ALGEMAS:
- Por que foi necessário? (risco de fuga, agressividade, etc.)
- Quem algemou?

PARÁGRAFO 4 - INTEGRIDADE FÍSICA:
- Houve lesão? (sim/não)
- Se sim: qual lesão, como ocorreu, onde foi atendido, nº da ficha
- Se não: mencionar que a guarnição verificou integridade

ERROS A EVITAR (NULIDADE CERTA):
❌ "Foi necessário uso moderado da força" (genérico)
❌ "O autor resistiu" (sem descrever como)
❌ "Foi algemado por segurança" (sem fato concreto)
❌ "Houve resistência ativa" (linguagem policial vaga)
❌ "O autor ficou agressivo" (subjetivo)
❌ "Nada a relatar" sobre integridade (omissão legal)

REGRA DE OURO: "Narrar AÇÕES, não IMPRESSÕES"

---

INFORMAÇÕES FORNECIDAS PELO USUÁRIO:

Descrição da resistência (o que o autor FEZ):
{descricao_resistencia}

Técnica aplicada (quem, qual técnica, resultado):
{tecnica_aplicada}

Justificativa das algemas (fato objetivo):
{justificativa_algemas}

Ferimentos e integridade física:
{ferimentos}

---

IMPORTANTE:

- A força e as algemas são REAÇÕES a comportamentos concretos (nunca decisões arbitrárias)
- Sempre descrever AÇÕES ESPECÍFICAS (correu, empurrou, desferiu soco, tentou fugir)
- Cada policial mencionado deve ter graduação + nome
- A integridade física é OBRIGATÓRIA (com ou sem ferimentos, deve-se relatar)
- Se houver ferimentos, SEMPRE mencionar: lesão + causa + hospital/UPA + nº da ficha
- Se alguma resposta estiver como "Não informado", OMITA aquela informação
- Dois espaços entre frases
- Manter coerência temporal: resistência → contenção → algemas → verificação de integridade

GERE AGORA O TEXTO DA SEÇÃO 6, seguindo RIGOROSAMENTE as regras acima:"""

        return prompt

    # ========================================================================
    # SEÇÃO 7: APREENSÕES E CADEIA DE CUSTÓDIA
    # ========================================================================

    def generate_section7_text(self, section_data: Dict[str, str], provider: str = "groq") -> str:
        """
        Gera texto narrativo da Seção 7 (Apreensões e Cadeia de Custódia).

        Args:
            section_data: Dicionário com respostas {step: answer}
            provider: "gemini", "groq", "claude" ou "openai"

        Returns:
            Texto gerado ou string vazia se seção foi pulada
        """
        # Se não houve apreensão, retorna vazio
        if section_data.get("7.1", "").strip().upper() in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
            return ""

        # Gerar com provider selecionado
        if provider == "gemini":
            return self._generate_section7_with_gemini(section_data)
        elif provider == "groq":
            return self._generate_section7_with_groq(section_data)
        elif provider == "claude":
            raise NotImplementedError("Claude ainda não implementado para Seção 7")
        elif provider == "openai":
            raise NotImplementedError("OpenAI ainda não implementado para Seção 7")
        else:
            raise ValueError(f"Provider {provider} não suportado")

    def _generate_section7_with_gemini(self, section_data: Dict[str, str]) -> str:
        """
        Gera texto da Seção 7 usando Gemini.
        """
        if not self.gemini_model:
            raise ValueError("Gemini API key não configurada. Configure GEMINI_API_KEY no .env")

        try:
            prompt = self._build_prompt_section7(section_data)

            # Se prompt vazio (seção pulada), retornar vazio
            if not prompt:
                return ""

            # Gerar texto
            response = self.gemini_model.generate_content(prompt)

            # Extrair texto
            generated_text = response.text.strip()

            return generated_text

        except Exception as e:
            error_msg = str(e)

            # Tratar erro de quota excedida
            if "429" in error_msg or "quota" in error_msg.lower() or "ResourceExhausted" in error_msg:
                raise Exception("Quota diária do Gemini excedida. Tente novamente mais tarde ou use outro modelo.")

            raise Exception(f"Erro ao gerar texto da Seção 7 com Gemini: {error_msg}")

    def _generate_section7_with_groq(self, section_data: Dict[str, str]) -> str:
        """
        Gera texto da Seção 7 (Apreensões e Cadeia de Custódia) usando Groq.
        """
        if not self.groq_client:
            raise ValueError("Groq API key não configurada. Configure GROQ_API_KEY no .env")

        try:
            prompt = self._build_prompt_section7(section_data)

            # Se prompt vazio (seção pulada), retornar vazio
            if not prompt:
                return ""

            # Gerar texto
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente especializado em redigir Boletins de Ocorrência policiais no padrão da PMMG."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )

            generated_text = response.choices[0].message.content.strip()
            return generated_text

        except Exception as e:
            error_msg = str(e)

            # Tratar erro de rate limit
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                raise Exception("Limite de requisições do Groq atingido. Aguarde alguns segundos.")

            raise Exception(f"Erro ao gerar texto da Seção 7 com Groq: {error_msg}")

    def _build_prompt_section7(self, section_data: Dict[str, str]) -> str:
        """
        Constrói prompt para Seção 7 (Apreensões e Cadeia de Custódia).

        Fonte:
        - materiais-claudio/_pacotao_2.txt (Seção E)
        - materiais-claudio/_regras_gerais_-_gpt_trafico.txt (linhas 77-83)
        - Lei 11.343/06 (Lei de Drogas) + CPP Arts. 240§2 e 244
        """

        # Verifica se seção foi pulada (não houve apreensão)
        if section_data.get("7.1", "").strip().upper() in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
            return ""  # Não gerar texto

        # Extrair respostas
        substancias = section_data.get("7.2", "Não informado")
        objetos = section_data.get("7.3", "Não informado")
        acondicionamento = section_data.get("7.4", "Não informado")

        # Construir prompt baseado no material do Claudio
        prompt = f"""Você é um redator especializado em Boletins de Ocorrência policiais da Polícia Militar de Minas Gerais. Sua tarefa é gerar o trecho da SEÇÃO 7 (Apreensões e Cadeia de Custódia) do BO de tráfico de drogas.

REGRAS OBRIGATÓRIAS (Claudio Moreira - autor de "Polícia na Prática"):

1. NUNCA invente informações não fornecidas pelo usuário
2. Use APENAS os dados das respostas fornecidas abaixo
3. Escreva em terceira pessoa, tempo passado
4. Use linguagem técnica, objetiva e norma culta
5. A CADEIA DE CUSTÓDIA é CRÍTICA: quem encontrou + onde + como acondicionou + para onde levou
6. Gere texto em 2-3 parágrafos fluidos
7. NÃO use juridiquês ou termos genéricos como "foi apreendido material ilícito"
8. ⚠️ NUNCA CITAR LEIS: Não mencione artigos, leis, incisos, códigos ou jurisprudência (Ex: Art. 33, Lei 11.343/06, CPP). O policial apenas DESCREVE OS FATOS, a tipificação legal é feita pelo delegado.

CONTEXTO TÉCNICO (para sua compreensão, NÃO incluir no texto gerado):

A cadeia de custódia assegura a integridade de drogas apreendidas desde a apreensão até o depósito, documentando QUEM a detinha, QUANDO, ONDE e COMO.

PRINCÍPIOS DA CADEIA DE CUSTÓDIA (obrigatórios):
1. Identificar QUEM encontrou o material (graduação + nome)
2. Descrever ONDE encontrou (local preciso - não genérico)
3. Informar COMO acondicionou (invólucro, saco plástico, número)
4. Registrar PARA ONDE levou (CEFLAN, delegacia, central)

ESTRUTURA NARRATIVA (2-3 PARÁGRAFOS):

PARÁGRAFO 1 - SUBSTÂNCIAS ENTORPECENTES:
- Tipo de droga (crack, cocaína, maconha)
- Quantidade exata (pedras, pinos, gramas, tabletes)
- Embalagem (invólucros plásticos, lata, sacola, mochila)
- Local PRECISO onde foi encontrado (caixa azul em cima da geladeira, buraco no muro)
- QUEM encontrou (graduação + nome completo do policial)

Exemplo CORRETO:
"O Soldado Breno encontrou 14 pedras de substância análoga ao crack dentro de uma lata azul sobre o banco de concreto próximo ao portão da casa 12. A Soldado Pires localizou 23 pinos de cocaína em um buraco no muro da lateral do imóvel."

PARÁGRAFO 2 - OBJETOS LIGADOS AO TRÁFICO (se houver):
- Dinheiro (valores fracionados típicos de venda - R$ 10, R$ 20)
- Celulares (quantidade e marca)
- Balança de precisão
- Armas, cadernos de contabilidade, embalagens vazias

Exemplo CORRETO:
"Foram apreendidos R$ 450,00 em notas de R$ 10 e R$ 20, típicas de comercialização, 2 celulares Samsung, 1 balança de precisão e uma caderneta com anotações de contabilidade do tráfico."

Se a resposta indicar "Nenhum objeto" ou similar, usar:
"Não foram apreendidos objetos ligados ao tráfico além das substâncias entorpecentes."

PARÁGRAFO 3 - ACONDICIONAMENTO E GUARDA:
- Como foi lacrado (invólucro 01, 02, saco plástico, etc.)
- Quem ficou responsável (graduação + nome)
- Destino do material (CEFLAN, delegacia civil, central)
- Fotografias realizadas (mencionar se foram feitas)

Exemplo CORRETO:
"O Soldado Faria lacrou as substâncias no invólucro 01 e os objetos no invólucro 02, fotografou todos os itens no local e ficou responsável pelo material até a entrega na CEFLAN 2."

---

ERROS A EVITAR (NULIDADE CERTA):

❌ "Apreensão feita conforme protocolo" (genérico demais)
❌ "Várias drogas foram apreendidas" (sem quantificar exatamente)
❌ "Material entregue" (sem dizer QUEM entregou e PARA ONDE)
❌ "Drogas localizadas" (sem dizer ONDE exatamente e por QUEM)
❌ "Material acondicionado adequadamente" (sem descrever COMO)
❌ "Encaminhado à delegacia" (sem identificar quem ficou responsável)

REGRA DE OURO: Quantidade exata + Local preciso + Nome do policial + Destino

---

DADOS FORNECIDOS PELO USUÁRIO:

Substâncias apreendidas (tipo, quantidade, embalagem, local, quem encontrou):
{substancias}

Objetos ligados ao tráfico (dinheiro, celulares, balança, etc.):
{objetos}

Acondicionamento e guarda (como lacrou, responsável, destino):
{acondicionamento}

---

IMPORTANTE:

- A cadeia de custódia é A PROVA MAIS IMPORTANTE em processo de tráfico
- Sem individualizar QUEM encontrou, o processo pode ser ANULADO
- Se objetos = "Nenhum" ou similar, mencionar brevemente e seguir para acondicionamento
- Se alguma resposta estiver como "Não informado", OMITA aquela informação
- Dois espaços entre frases
- Manter coerência: substâncias → objetos (se houver) → acondicionamento

GERE AGORA O TEXTO DA SEÇÃO 7, seguindo RIGOROSAMENTE as regras acima:"""

        return prompt

    # ========================================================================
    # SEÇÃO 8: Condução e Pós-Ocorrência (ÚLTIMA SEÇÃO - MARCA BO COMPLETO)
    # ========================================================================

    def generate_section8_text(self, section_data: Dict[str, str], provider: str = "groq") -> str:
        """
        Gera texto narrativo da Seção 8 (Condução e Pós-Ocorrência) - ÚLTIMA SEÇÃO.

        Args:
            section_data: Dicionário com respostas {step: answer}
            provider: "gemini", "groq", "claude" ou "openai"

        Returns:
            Texto gerado (todas as 11 perguntas são obrigatórias)
        """
        # Seção 8 NÃO tem skip logic - todas as 11 perguntas são obrigatórias

        # Gerar com provider selecionado
        if provider == "gemini":
            return self._generate_section8_with_gemini(section_data)
        elif provider == "groq":
            return self._generate_section8_with_groq(section_data)
        elif provider == "claude":
            raise NotImplementedError("Claude ainda não implementado para Seção 8")
        elif provider == "openai":
            raise NotImplementedError("OpenAI ainda não implementado para Seção 8")
        else:
            raise ValueError(f"Provider {provider} não suportado")

    def _generate_section8_with_gemini(self, section_data: Dict[str, str]) -> str:
        """
        Gera texto da Seção 8 usando Gemini.
        """
        if not self.gemini_model:
            raise ValueError("Gemini API key não configurada. Configure GEMINI_API_KEY no .env")

        try:
            prompt = self._build_prompt_section8(section_data)

            # Gerar texto
            response = self.gemini_model.generate_content(prompt)

            # Extrair texto
            generated_text = response.text.strip()

            return generated_text

        except Exception as e:
            error_msg = str(e)

            # Tratar erro de quota excedida
            if "429" in error_msg or "quota" in error_msg.lower() or "ResourceExhausted" in error_msg:
                raise Exception("Quota diária do Gemini excedida. Tente novamente mais tarde ou use outro modelo.")

            raise Exception(f"Erro ao gerar texto da Seção 8 com Gemini: {error_msg}")

    def _generate_section8_with_groq(self, section_data: Dict[str, str]) -> str:
        """
        Gera texto da Seção 8 (Condução e Pós-Ocorrência) usando Groq.
        """
        if not self.groq_client:
            raise ValueError("Groq API key não configurada. Configure GROQ_API_KEY no .env")

        try:
            prompt = self._build_prompt_section8(section_data)

            # Gerar texto
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente especializado em redigir Boletins de Ocorrência policiais no padrão da PMMG."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )

            generated_text = response.choices[0].message.content.strip()
            return generated_text

        except Exception as e:
            error_msg = str(e)

            # Tratar erro de rate limit
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                raise Exception("Limite de requisições do Groq atingido. Aguarde alguns segundos.")

            raise Exception(f"Erro ao gerar texto da Seção 8 com Groq: {error_msg}")

    def _build_prompt_section8(self, section_data: Dict[str, str]) -> str:
        """
        Constrói prompt para Seção 8 (Condução e Pós-Ocorrência) - ÚLTIMA SEÇÃO.

        Fonte:
        - materiais-claudio/_pacotao_2.txt (Seção F)
        - materiais-claudio/_regras_gerais_-_gpt_trafico.txt (linhas 85-94)
        - Lei 11.343/06 (Lei de Drogas)
        - Lei 13.869/19 (Lei de Abuso de Autoridade)
        - CPP Arts. 282-284 (Prisão em flagrante)
        """

        # Extrair respostas (TODAS as 11 perguntas são obrigatórias - Section 8 não tem skip)
        voz_prisao = section_data.get("8.1", "Não informado")
        transporte = section_data.get("8.2", "Não informado")
        declaracoes = section_data.get("8.3", "Não declarou")
        funcao_trafico = section_data.get("8.4", "Não identificada")
        passagens = section_data.get("8.5", "Sem passagens")
        dedicacao_crime = section_data.get("8.6", "Sem indícios")
        papel_faccao = section_data.get("8.7", "Não identificado")
        destruicao_provas = section_data.get("8.8", "Não houve")
        menor_envolvido = section_data.get("8.9", "Não havia")
        garantias = section_data.get("8.10", "Não informado")
        destino = section_data.get("8.11", "Não informado")

        # Construir prompt baseado no material do Claudio
        prompt = f"""Você é um redator especializado em Boletins de Ocorrência policiais da Polícia Militar de Minas Gerais. Sua tarefa é gerar o trecho da SEÇÃO 8 (Condução e Pós-Ocorrência) do BO de tráfico de drogas.

**IMPORTANTE:** Esta é a ÚLTIMA seção do BO. O texto deve consolidar a narrativa final da ocorrência com base nas 11 perguntas respondidas.

REGRAS OBRIGATÓRIAS (Claudio Moreira - autor de "Polícia na Prática"):

1. NUNCA invente informações não fornecidas pelo usuário
2. Use APENAS os dados das respostas fornecidas abaixo
3. Escreva em terceira pessoa, tempo passado
4. Use linguagem técnica, objetiva e norma culta
5. Gere texto em 3-4 parágrafos fluidos
6. NÃO use juridiquês ou termos genéricos
7. ⚠️ NUNCA CITAR LEIS: Não mencione artigos, leis, incisos, códigos ou jurisprudência (Ex: Art. 33, Lei 11.343/06, CPP, Lei 13.869/19). O policial apenas DESCREVE OS FATOS, a tipificação legal é feita pelo delegado.

CONTEXTO TÉCNICO (para sua compreensão, NÃO incluir no texto gerado):

A prisão em flagrante deve ser documentada com voz de prisão, leitura de direitos constitucionais, verificação de integridade física e condução adequada.

ESTRUTURA NARRATIVA (3-4 PARÁGRAFOS):

PARÁGRAFO 1 - VOZ DE PRISÃO E TRANSPORTE:
- QUEM deu voz de prisão (graduação + nome)
- Por QUAL CRIME (descrever o fato, NÃO citar artigo de lei)
- Como foi transportado (viatura, prefixo, posição)

PARÁGRAFO 2 - DECLARAÇÕES E PERFIL DO PRESO:
- Declaração do preso (literal) OU "permaneceu em silêncio"
- Função no tráfico (vapor, gerente, olheiro) se identificada
- Passagens anteriores (REDS) se houver
- Sinais de dedicação ao crime (ostentação, tatuagens) se houver

PARÁGRAFO 3 - ORGANIZAÇÃO CRIMINOSA E PROVAS:
- Papel na facção (ocasional ou contínua) se identificado
- Tentativas de destruir/ocultar provas ou intimidar se houver
- Envolvimento de menor se houver

PARÁGRAFO 4 - GARANTIAS E DESTINO:
- QUEM informou garantias constitucionais (graduação + nome)
- Destino dos PRESOS (delegacia específica)
- Destino dos MATERIAIS (CEFLAN)

---

DADOS FORNECIDOS PELO USUÁRIO (11 PERGUNTAS):

1. Voz de prisão (quem deu e por qual crime):
{voz_prisao}

2. Transporte (onde e como):
{transporte}

3. Declarações do preso:
{declaracoes}

4. Função no tráfico:
{funcao_trafico}

5. Passagens anteriores (REDS):
{passagens}

6. Sinais de dedicação ao crime:
{dedicacao_crime}

7. Papel na facção:
{papel_faccao}

8. Destruição/ocultação de provas:
{destruicao_provas}

9. Menor envolvido:
{menor_envolvido}

10. Quem informou garantias:
{garantias}

11. Destino (presos e materiais):
{destino}

---

IMPORTANTE:

- Esta é a ÚLTIMA seção - finalize a narrativa de forma completa
- Se alguma resposta indicar "Não", "Sem", "Nenhum", mencione brevemente quando relevante
- Se alguma resposta estiver como "Não informado", OMITA aquela informação
- Dois espaços entre frases
- Integre naturalmente as informações das 11 perguntas no texto

GERE AGORA O TEXTO DA SEÇÃO 8, seguindo RIGOROSAMENTE as regras acima:"""

        return prompt
