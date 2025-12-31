import os
from typing import Dict
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
import re
import locale

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
        elif provider == "groq":
            return self._generate_with_groq(section_data)
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
            error_msg = str(e)

            # Tratar erro de quota excedida
            if "429" in error_msg or "quota" in error_msg.lower() or "ResourceExhausted" in error_msg:
                raise Exception("Quota diária do Gemini excedida. Tente novamente mais tarde ou use outro modelo.")

            raise Exception(f"Erro ao gerar texto com Gemini: {error_msg}")

    def _generate_with_groq(self, section_data: Dict[str, str]) -> str:
        """
        Gera texto da Seção 1 usando Groq (Llama 3.3 70B).
        14.400 req/dia no free tier vs 20 do Gemini.
        """
        if not self.groq_client:
            raise ValueError("Groq API key não configurada. Configure GROQ_API_KEY no .env")

        try:
            prompt = self._build_prompt(section_data)

            # Groq usa formato OpenAI chat completions
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Melhor modelo do Groq
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
                temperature=0.3,  # Baixa criatividade (importante para BOs)
                max_tokens=2000
            )

            generated_text = response.choices[0].message.content.strip()
            return generated_text

        except Exception as e:
            error_msg = str(e)

            # Tratar erro de rate limit do Groq
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                raise Exception("Limite de requisições do Groq atingido. Aguarde alguns segundos.")

            raise Exception(f"Erro ao gerar texto com Groq: {error_msg}")

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

    def _build_prompt_section2(self, section_data: Dict[str, str]) -> str:
        """
        Constrói prompt para Seção 2 baseado no material do Claudio.

        Fonte:
        - materiais-claudio/_03_busca_veicular.txt
        - materiais-claudio/_regras_gerais_-_gpt_trafico.txt (linhas 29-40)
        - materiais-claudio/_pacotao_1.txt (linhas 24-26)
        """

        # Verifica se seção foi pulada (não havia veículo)
        if section_data.get("2.1", "").strip().upper() in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
            return ""  # Não gerar texto

        # Extrair respostas (agora são 13 perguntas)
        local_contexto = section_data.get("2.2", "Não informado")
        veiculo_desc = section_data.get("2.3", "Não informado")
        policial_viu = section_data.get("2.4", "Não informado")
        reacao_motorista = section_data.get("2.5", "Não informado")
        ordem_parada = section_data.get("2.6", "Não informado")
        parou_ou_perseguicao = section_data.get("2.7", "Não informado")
        motivo_parada = section_data.get("2.8", "Não informado")
        abordagem_ocupantes = section_data.get("2.9", "Não informado")
        busca_veiculo = section_data.get("2.10", "Não informado")
        busca_pessoal = section_data.get("2.11", "Não informado")
        material_encontrado = section_data.get("2.12", "Não informado")
        irregularidades = section_data.get("2.13", "Não informado")

        # Construir prompt baseado no material do Claudio
        prompt = f"""Você é um redator especializado em Boletins de Ocorrência policiais da Polícia Militar de Minas Gerais. Sua tarefa é gerar o trecho da SEÇÃO 2 (Abordagem a Veículo) do BO de tráfico de drogas.

REGRAS OBRIGATÓRIAS (Claudio Moreira - autor de "Polícia na Prática"):

1. NUNCA invente informações não fornecidas pelo usuário
2. Use APENAS os dados das respostas fornecidas abaixo
3. Escreva em terceira pessoa, tempo passado
4. Use linguagem técnica, objetiva e norma culta
5. Descreva PASSO A PASSO: visualização → comportamento → ordem de parada → reação → busca
6. Gere texto em parágrafo único, fluido, SEM quebras de linha
7. NÃO use juridiquês, gerúndio ou termos vagos como "atitude suspeita"
8. ⚠️ NUNCA CITAR LEIS: Não mencione artigos, leis, incisos ou códigos (Ex: Art. 33, Lei 11.343/06, CPP, STF). O policial apenas DESCREVE OS FATOS, a tipificação legal é feita pelo delegado.

DADOS FORNECIDOS PELO USUÁRIO:

- Local e contexto onde foi visto: {local_contexto}
- Marca/modelo/cor/placa: {veiculo_desc}
- Policial que viu primeiro e o que observou: {policial_viu}
- Reação do motorista/ocupantes: {reacao_motorista}
- Ordem de parada: {ordem_parada}
- Parou imediatamente ou houve perseguição: {parou_ou_perseguicao}
- Motivo da parada (se houve perseguição): {motivo_parada}
- Abordagem dos ocupantes: {abordagem_ocupantes}
- Busca no veículo (quem e onde): {busca_veiculo}
- Busca pessoal nos ocupantes: {busca_pessoal}
- Material encontrado (o que, com quem, onde): {material_encontrado}
- Irregularidades veiculares: {irregularidades}

EXEMPLOS CORRETOS (do material do Claudio):

✅ Exemplo 1 – Conduta atípica observada:
"Durante patrulhamento pelo Bairro Pinhalzinho, a equipe visualizou um veículo VW/Fox prata, placa DWL9I93, transitando em alta velocidade e mudando repentinamente o sentido de direção ao notar a aproximação da viatura. O Sargento Lucas determinou a perseguição, sendo o carro alcançado na Rodovia IMG-880, onde foi procedida a abordagem. O condutor apresentava visível nervosismo e mantinha o olhar fixo no banco traseiro. Diante da fundada suspeita de transporte de ilícitos, foi realizada busca no interior do veículo, sendo localizados cinco tabletes de substância análoga à cocaína no porta-malas, além de duas buchas de maconha no bolso traseiro da calça do motorista."

✅ Exemplo 2 – Denúncia corroborada + comportamento evasivo:
"Durante operação de combate ao tráfico, a guarnição recebeu via COPOM denúncia informando que um veículo Fiat Palio, cor preta, placa ABC-1234, estaria sendo utilizado para transporte de drogas entre os bairros Esperança e São João. Ao transitar pela Rua das Acácias, o Cabo Almeida visualizou o veículo denunciado. O condutor, ao perceber a viatura, reduziu a velocidade, olhou diversas vezes para o retrovisor e tentou entrar em um beco lateral. Foi dada ordem de parada, prontamente atendida. Durante a vistoria, foi localizado um invólucro contendo substância análoga à maconha sob o banco do passageiro, além de valores fracionados no console central."

✅ Exemplo 3 – Apoio da inteligência:
"Em patrulhamento com o objetivo de combater o tráfico de drogas, após levantamento do setor de inteligência da PM indicando o uso de um Chevrolet Onix branco, placa RST-8899, no transporte de drogas, a equipe visualizou o veículo estacionado em frente à Rua das Oliveiras, local apontado como ponto de entrega. Durante a observação, o condutor recebeu rapidamente um pacote de um motociclista e o colocou no porta-malas. Diante da fundada suspeita de crime de tráfico, o Sargento Marcos determinou a abordagem, sendo o pacote arrecadado e constatado tratar-se de substância análoga à cocaína embalada para comércio."

❌ ERROS A EVITAR (do material do Claudio):

• "O veículo foi abordado por suspeita" (genérico, sem fatos concretos)
• "Condutor nervoso" (sem descrever COMO estava nervoso - tremores? olhar fixo? tentou esconder algo?)
• "Local conhecido por tráfico" (sem base factual - qual informação prévia? qual relatório?)
• "Foi feita revista no veículo" (sem dizer O MOTIVO da busca - qual fundada suspeita?)

ESTRUTURA NARRATIVA (seguir esta ordem):

1. Contexto inicial: onde, em que situação o veículo foi visualizado
2. Descrição do veículo: marca, modelo, cor, placa
3. Comportamento observado: o que chamou atenção (CONCRETO, não vago)
4. Identificação: qual policial viu primeiro, de onde viu
5. Reação do motorista/ocupantes: manobra brusca, fuga, descarte de objeto (ou ausência de reação)
6. Ordem de parada: como foi dada (sirene, megafone, sinal), quem deu
7. Resposta à ordem: veículo parou ou houve perseguição?
8. Motivo da parada (se houve perseguição): desistiu, cercado, bateu, capotou
9. Abordagem dos ocupantes: quem abordou, quantos ocupantes, posicionamento
10. Busca veicular: quem vistoriou o veículo e quais partes (porta-luvas, bancos, porta-malas, etc)
11. Busca pessoal: quem realizou busca pessoal em cada ocupante
12. Material encontrado: o que foi localizado, com quem estava, em qual parte do veículo/corpo
13. Irregularidades (se houver): veículo furtado/roubado/clonado com REDS

IMPORTANTE - SEPARAÇÃO DE BUSCA PESSOAL E BUSCA VEICULAR:

- A busca PESSOAL (nos ocupantes) e a busca NO VEÍCULO são atos DIFERENTES
- Cada busca deve ter SEU RESPONSÁVEL identificado (graduação + nome)
- Isso é CRÍTICO para a CADEIA DE CUSTÓDIA: quem encontrou o quê e onde
- Se alguma resposta estiver como "Não informado", simplesmente OMITA aquela informação (não invente)
- Descreva SEMPRE: motivo da atenção → reação do motorista → ordem de parada → resposta (parou/perseguição) → abordagem → busca veicular → busca pessoal → o que foi encontrado
- Use conectivos para fluidez: "ao notar", "diante de", "sendo que", "durante", "onde"
- Mantenha coerência temporal: visualização → reação → ordem → parou/perseguição → abordagem → busca veicular → busca pessoal → material encontrado
- A busca VEICULAR agora vem ANTES da busca PESSOAL na narrativa
- Se houver irregularidade no veículo (REDS, furto, etc.), mencionar ao final

Gere APENAS o texto da Seção 2 agora (um único parágrafo contínuo):"""

        return prompt

    def generate_section2_text(self, section_data: Dict[str, str], provider: str = "gemini") -> str:
        """
        Gera texto narrativo da Seção 2 (Abordagem a Veículo).

        Args:
            section_data: Dicionário com respostas {step: answer}
            provider: "gemini", "claude" ou "openai"

        Returns:
            Texto gerado ou string vazia se seção foi pulada
        """
        # Se não havia veículo, retorna vazio (pergunta 2.1)
        if section_data.get("2.1", "").strip().upper() in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
            return ""

        # Gerar com provider selecionado
        if provider == "gemini":
            return self._generate_section2_with_gemini(section_data)
        elif provider == "groq":
            return self._generate_section2_with_groq(section_data)
        elif provider == "claude":
            raise NotImplementedError("Claude ainda não implementado para Seção 2")
        elif provider == "openai":
            raise NotImplementedError("OpenAI ainda não implementado para Seção 2")
        else:
            raise ValueError(f"Provider {provider} não suportado")

    def _generate_section2_with_gemini(self, section_data: Dict[str, str]) -> str:
        """
        Gera texto da Seção 2 usando Gemini.
        """
        if not self.gemini_model:
            raise ValueError("Gemini API key não configurada. Configure GEMINI_API_KEY no .env")

        try:
            prompt = self._build_prompt_section2(section_data)

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

            raise Exception(f"Erro ao gerar texto da Seção 2 com Gemini: {error_msg}")

    def _generate_section2_with_groq(self, section_data: Dict[str, str]) -> str:
        """
        Gera texto da Seção 2 (Abordagem a Veículo) usando Groq.
        """
        if not self.groq_client:
            raise ValueError("Groq API key não configurada. Configure GROQ_API_KEY no .env")

        try:
            prompt = self._build_prompt_section2(section_data)

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

            raise Exception(f"Erro ao gerar texto da Seção 2 com Groq: {error_msg}")

    # ==================== SEÇÃO 3: CAMPANA ====================

    def _build_prompt_section3(self, section_data: Dict[str, str]) -> str:
        """
        Constrói prompt para Seção 3 (Campana - Vigilância Velada).

        Fonte:
        - materiais-claudio/_secao_-_campana.txt
        - materiais-claudio/_regras_gerais_-_gpt_trafico.txt (linhas 42-52)
        """

        # Verifica se seção foi pulada (não houve campana)
        if section_data.get("3.1", "").strip().upper() in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
            return ""  # Não gerar texto

        # Extrair respostas
        local_campana = section_data.get("3.2", "Não informado")
        policial_visao = section_data.get("3.3", "Não informado")
        motivacao = section_data.get("3.4", "Não informado")
        duracao = section_data.get("3.5", "Não informado")
        observacoes = section_data.get("3.6", "Não informado")
        usuarios = section_data.get("3.7", "Não informado")
        fuga = section_data.get("3.8", "Não informado")

        # Construir prompt baseado no material do Claudio
        prompt = f"""Você é um redator especializado em Boletins de Ocorrência policiais da Polícia Militar de Minas Gerais. Sua tarefa é gerar o trecho da SEÇÃO 3 (Campana - Vigilância Velada) do BO de tráfico de drogas.

REGRAS OBRIGATÓRIAS (Claudio Moreira - autor de "Polícia na Prática"):

1. NUNCA invente informações não fornecidas pelo usuário
2. Use APENAS os dados das respostas fornecidas abaixo
3. Escreva em terceira pessoa, tempo passado
4. Use linguagem técnica, objetiva e norma culta
5. Descreva ATOS CONCRETOS observados, NÃO impressões subjetivas
6. Gere texto em 2-3 parágrafos fluidos
7. NÃO use juridiquês, gerúndio ou termos vagos como "atitude suspeita"
8. ⚠️ NUNCA CITAR LEIS: Não mencione artigos, leis, incisos ou códigos (Ex: Art. 33, Lei 11.343/06, CPP, STF). O policial apenas DESCREVE OS FATOS, a tipificação legal é feita pelo delegado.

DADOS FORNECIDOS PELO USUÁRIO:

- Local da campana: {local_campana}
- Policial com visão direta: {policial_visao}
- Motivação para campana: {motivacao}
- Duração: {duracao}
- O que foi observado (atos concretos): {observacoes}
- Abordagem de usuários: {usuarios}
- Tentativa de fuga: {fuga}

ESTRUTURA NARRATIVA (seguir esta ordem):

1. Motivação: por que foi realizada a campana (denúncia, inteligência, histórico)
2. Local e posicionamento: onde a equipe se posicionou, quem tinha visão
3. Duração: quanto tempo durou (contínua ou alternada)
4. Observações concretas: descrever ATOS específicos (não generalizações)
   - Exemplo correto: "tirou invólucros da mochila e entregou a dois rapazes de moto"
   - Exemplo errado: "estava em atitude suspeita"
5. Usuários (se houver): quantos, o que tinham, o que disseram
6. Fuga (se houver): como tentou fugir ao perceber a equipe
7. Fundada suspeita: conectar observações com decisão de abordar

EXEMPLOS CORRETOS:

✅ Exemplo 1:
"Motivados por denúncia anônima recebida via COPOM informando comercialização de drogas na esquina da Rua das Flores com Avenida Brasil, a guarnição posicionou-se atrás do muro da casa nº 145, a aproximadamente 30 metros do local denunciado. O Sargento Silva tinha visão desobstruída da porta do bar do João, enquanto o Cabo Almeida observava a lateral do estabelecimento. Durante 15 minutos de vigilância contínua, foi observado um homem de camiseta vermelha retirando pequenos invólucros de uma mochila preta e entregando a dois indivíduos que chegaram de motocicleta. Após receberem os invólucros, os indivíduos entregaram dinheiro ao homem de vermelho. Durante a campana, foi abordado um usuário que saía do local. Ele portava 2 porções de substância análoga à cocaína e relatou ter comprado do 'cara de vermelho' por R$ 50,00. Ao perceber a movimentação policial, o homem de vermelho correu para o beco ao lado do bar, tentando fugir em direção à Rua Sete. Diante das observações concretas e do relato do usuário, caracterizou-se fundada suspeita para a abordagem."

✅ Exemplo 2:
"Com base em informações da inteligência policial sobre comercialização de drogas no Beco da Rua Principal, a equipe realizou campana posicionada dentro da viatura estacionada no nº 233 da Rua Sete, a um quarteirão do ponto. Durante 20 minutos de vigilância alternada, o Soldado Faria conseguia ver a entrada do beco de sua posição. Foi observada uma mulher que recebia dinheiro de diversas pessoas e retirava algo do bolso esquerdo, entregando aos compradores. As trocas eram rápidas e ocorriam em sequência. Diante do comportamento compatível com comercialização de entorpecentes, a equipe decidiu realizar a abordagem."

❌ ERROS A EVITAR:

• "Local conhecido por tráfico" (sem informação prévia específica)
• "Comportamento suspeito" (vago - descrever O QUE exatamente fez)
• "Vários usuários" (quantificar - 2? 5? 10?)
• "Comercializando drogas" (descrever OS ATOS - entregou invólucros? recebeu dinheiro?)

IMPORTANTE:

- Se alguma resposta estiver como "Não informado", OMITA aquela informação (não invente)
- Se resposta for "NÃO" para usuários ou fuga, não mencione no texto
- Sempre conectar observações concretas → fundada suspeita
- Dois espaços entre frases
- Manter coerência temporal e espacial

Gere APENAS o texto da Seção 3 agora (2-3 parágrafos fluidos):"""

        return prompt

    def generate_section3_text(self, section_data: Dict[str, str], provider: str = "gemini") -> str:
        """
        Gera texto narrativo da Seção 3 (Campana - Vigilância Velada).

        Args:
            section_data: Dicionário com respostas {step: answer}
            provider: "gemini", "groq", "claude" ou "openai"

        Returns:
            Texto gerado ou string vazia se seção foi pulada
        """
        # Se não houve campana, retorna vazio
        if section_data.get("3.1", "").strip().upper() in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
            return ""

        # Gerar com provider selecionado
        if provider == "gemini":
            return self._generate_section3_with_gemini(section_data)
        elif provider == "groq":
            return self._generate_section3_with_groq(section_data)
        elif provider == "claude":
            raise NotImplementedError("Claude ainda não implementado para Seção 3")
        elif provider == "openai":
            raise NotImplementedError("OpenAI ainda não implementado para Seção 3")
        else:
            raise ValueError(f"Provider {provider} não suportado")

    def _generate_section3_with_gemini(self, section_data: Dict[str, str]) -> str:
        """
        Gera texto da Seção 3 usando Gemini.
        """
        if not self.gemini_model:
            raise ValueError("Gemini API key não configurada. Configure GEMINI_API_KEY no .env")

        try:
            prompt = self._build_prompt_section3(section_data)

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

            raise Exception(f"Erro ao gerar texto da Seção 3 com Gemini: {error_msg}")

    def _generate_section3_with_groq(self, section_data: Dict[str, str]) -> str:
        """
        Gera texto da Seção 3 (Campana - Vigilância Velada) usando Groq.
        """
        if not self.groq_client:
            raise ValueError("Groq API key não configurada. Configure GROQ_API_KEY no .env")

        try:
            prompt = self._build_prompt_section3(section_data)

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

            raise Exception(f"Erro ao gerar texto da Seção 3 com Groq: {error_msg}")

    # ============================================================================
    # SEÇÃO 4: ENTRADA EM DOMICÍLIO
    # ============================================================================

    def _build_prompt_section4(self, section_data: Dict[str, str]) -> str:
        """
        Constrói prompt para Seção 4 (Entrada em Domicílio).

        Fonte:
        - materiais-claudio/_04_entrada_em_domicilio.txt
        - materiais-claudio/_regras_gerais_-_gpt_trafico.txt (linhas 54-60)
        """

        # Verifica se seção foi pulada (não houve entrada em domicílio)
        if section_data.get("4.1", "").strip().upper() in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
            return ""  # Não gerar texto

        # Extrair respostas
        justa_causa = section_data.get("4.2", "Não informado")
        policial_presenciou = section_data.get("4.3", "Não informado")
        tipo_ingresso = section_data.get("4.4", "Não informado")
        acoes_policiais = section_data.get("4.5", "Não informado")

        # Construir prompt baseado no material do Claudio
        prompt = f"""Você é um redator especializado em Boletins de Ocorrência policiais da Polícia Militar de Minas Gerais. Sua tarefa é gerar o trecho da SEÇÃO 4 (Entrada em Domicílio) do BO de tráfico de drogas.

REGRAS OBRIGATÓRIAS (Claudio Moreira - autor de "Polícia na Prática"):

1. NUNCA invente informações não fornecidas pelo usuário
2. Use APENAS os dados das respostas fornecidas abaixo
3. Escreva em terceira pessoa, tempo passado
4. Use linguagem técnica, objetiva e norma culta
5. A JUSTA CAUSA deve vir ANTES da entrada no texto narrativo
6. Descreva FATOS CONCRETOS observados (não impressões subjetivas)
7. Gere texto em 2-3 parágrafos fluidos
8. NÃO use juridiquês, gerúndio ou termos vagos
9. ⚠️ NUNCA CITAR LEIS: Não mencione artigos, leis, incisos, códigos ou jurisprudência (Ex: Art. 33, Lei 11.343/06, CPP, STF). O policial apenas DESCREVE OS FATOS, a tipificação legal é feita pelo delegado.

CONTEXTO TÉCNICO (para sua compreensão, NÃO incluir no texto gerado):

O ingresso em domicílio sem mandado judicial só é legítimo quando houver FUNDADAS RAZÕES, devidamente justificadas, de que ocorre flagrante delito no interior do imóvel. A justa causa deve existir ANTES da entrada. Não basta alegar que "encontrou drogas depois".

ELEMENTOS CONCRETOS EXIGIDOS (pelo menos um):
- Visualização de ilícito em andamento (pela janela, porta)
- Perseguição contínua sem perda de contato visual
- Flagrante auditivo (sons de embalagem, descargas)
- Odor intenso característico
- Autorização expressa do morador

DADOS FORNECIDOS PELO USUÁRIO:

- O que foi visto/ouvido/sentido ANTES do ingresso: {justa_causa}
- Qual policial presenciou e o que viu: {policial_presenciou}
- Como ocorreu o ingresso: {tipo_ingresso}
- Ação de cada policial: {acoes_policiais}

ESTRUTURA NARRATIVA (seguir esta ordem):

1. Justa causa ANTERIOR: descrever O QUE foi visto/ouvido/sentido ANTES de entrar
2. Quem presenciou: qual policial viu e o que exatamente observou
3. Tipo de ingresso: perseguição contínua, autorização ou flagrante visual/auditivo
4. Ações dos policiais: quem entrou primeiro, por onde, quem ficou na contenção, o que encontraram

EXEMPLOS CORRETOS:

✅ Exemplo 1 - Perseguição contínua:
"Durante patrulhamento na Rua São Miguel, a equipe visualizou um indivíduo entregando pequenos invólucros a terceiros e recebendo dinheiro. Ao perceber a presença policial, o suspeito correu, adentrando o imóvel nº 120. O Sargento Silva manteve contato visual ininterrupto com o alvo desde a rua até o interior da residência. A guarnição iniciou perseguição imediata, acompanhando-o até a cozinha, onde o autor tentou esconder uma sacola embaixo da pia. O Sargento Silva entrou primeiro pela porta principal que estava aberta. O Cabo Almeida ficou na contenção do portão. No interior da sacola, foram localizadas diversas porções de substância análoga à cocaína."

✅ Exemplo 2 - Flagrante visual/auditivo:
"Durante incursão pelo Beco das Palmeiras, os militares perceberam forte odor característico de maconha vindo do interior do imóvel nº 88. O Sargento Almeida, ao olhar pela janela que dava para o beco, visualizou um homem embalando invólucros sobre a mesa da sala. Diante do flagrante delito observado antes da entrada, o Sargento Almeida determinou o ingresso imediato. O Sargento Almeida entrou primeiro pela porta lateral. O Soldado Pires permaneceu na contenção externa. Foram arrecadadas diversas porções de maconha, balança de precisão e dinheiro fracionado sobre a mesa."

✅ Exemplo 3 - Autorização do morador:
"No local, o suspeito franqueou voluntariamente a entrada dos militares após identificação da equipe, autorizando expressamente a vistoria no interior da residência. Na presença do morador, o Cabo Silva localizou uma mochila contendo tabletes de substância análoga à maconha sobre o guarda-roupa do quarto."

❌ ERROS A EVITAR (causam NULIDADE):

• "Entramos por ser local conhecido por tráfico" (sem justa causa anterior)
• "O suspeito correu pra dentro" (sem ver ilícito antes da entrada)
• "Havia denúncia de drogas" (denúncia não é justa causa sem constatação direta)
• "Entramos e encontramos drogas" (justa causa posterior não vale)
• "Comportamento nervoso" (sem fato concreto anterior)

IMPORTANTE:

- A justa causa (4.2) É O PONTO CENTRAL - deve ser CLARA e ANTERIOR à entrada
- Sempre explicitar: viu O QUÊ, ouviu O QUÊ, sentiu O QUÊ (odor de quê)
- Se alguma resposta estiver como "Não informado", OMITA aquela informação
- Dois espaços entre frases
- Manter coerência temporal: antes de entrar → ingresso → o que foi encontrado

Gere APENAS o texto da Seção 4 agora (2-3 parágrafos fluidos):"""

        return prompt

    def generate_section4_text(self, section_data: Dict[str, str], provider: str = "gemini") -> str:
        """
        Gera texto narrativo da Seção 4 (Entrada em Domicílio).

        Args:
            section_data: Dicionário com respostas {step: answer}
            provider: "gemini", "groq", "claude" ou "openai"

        Returns:
            Texto gerado ou string vazia se seção foi pulada
        """
        # Se não houve entrada em domicílio, retorna vazio
        if section_data.get("4.1", "").strip().upper() in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
            return ""

        # Gerar com provider selecionado
        if provider == "gemini":
            return self._generate_section4_with_gemini(section_data)
        elif provider == "groq":
            return self._generate_section4_with_groq(section_data)
        elif provider == "claude":
            raise NotImplementedError("Claude ainda não implementado para Seção 4")
        elif provider == "openai":
            raise NotImplementedError("OpenAI ainda não implementado para Seção 4")
        else:
            raise ValueError(f"Provider {provider} não suportado")

    def _generate_section4_with_gemini(self, section_data: Dict[str, str]) -> str:
        """
        Gera texto da Seção 4 usando Gemini.
        """
        if not self.gemini_model:
            raise ValueError("Gemini API key não configurada. Configure GEMINI_API_KEY no .env")

        try:
            prompt = self._build_prompt_section4(section_data)

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

            raise Exception(f"Erro ao gerar texto da Seção 4 com Gemini: {error_msg}")

    def _generate_section4_with_groq(self, section_data: Dict[str, str]) -> str:
        """
        Gera texto da Seção 4 (Entrada em Domicílio) usando Groq.
        """
        if not self.groq_client:
            raise ValueError("Groq API key não configurada. Configure GROQ_API_KEY no .env")

        try:
            prompt = self._build_prompt_section4(section_data)

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

            raise Exception(f"Erro ao gerar texto da Seção 4 com Groq: {error_msg}")

    # ========================================================================
    # SEÇÃO 5: FUNDADA SUSPEITA
    # ========================================================================

    def generate_section5_text(self, section_data: Dict[str, str], provider: str = "gemini") -> str:
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

    def generate_section6_text(self, section_data: Dict[str, str], provider: str = "gemini") -> str:
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

    def generate_section7_text(self, section_data: Dict[str, str], provider: str = "gemini") -> str:
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

    def generate_section8_text(self, section_data: Dict[str, str], provider: str = "gemini") -> str:
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
