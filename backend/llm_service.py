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
        if section_data.get("2.0", "").strip().upper() in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
            return ""  # Não gerar texto

        # Extrair respostas
        veiculo_desc = section_data.get("2.1", "Não informado")
        local_visto = section_data.get("2.2", "Não informado")
        policial_viu = section_data.get("2.3", "Não informado")
        ordem_parada = section_data.get("2.4", "Não informado")
        reacao_veiculo = section_data.get("2.5", "Não informado")
        abordagem_busca = section_data.get("2.6", "Não informado")
        irregularidades = section_data.get("2.7", "Não informado")

        # Construir prompt baseado no material do Claudio
        prompt = f"""Você é um redator especializado em Boletins de Ocorrência policiais da Polícia Militar de Minas Gerais. Sua tarefa é gerar o trecho da SEÇÃO 2 (Abordagem a Veículo) do BO de tráfico de drogas.

REGRAS OBRIGATÓRIAS (Claudio Moreira - autor de "Polícia na Prática"):

1. NUNCA invente informações não fornecidas pelo usuário
2. Use APENAS os dados das respostas fornecidas abaixo
3. Escreva em terceira pessoa, tempo passado
4. Use linguagem técnica, objetiva e norma culta
5. Descreva PASSO A PASSO: visualização → comportamento → ordem de parada → reação → busca
6. Siga jurisprudência do STF HC 261029 (fundada suspeita requer descrição concreta)
7. Gere texto em parágrafo único, fluido, SEM quebras de linha
8. NÃO use juridiquês, gerúndio ou termos vagos como "atitude suspeita"

DADOS FORNECIDOS PELO USUÁRIO:

- Marca/modelo/cor/placa: {veiculo_desc}
- Local onde foi visto: {local_visto}
- Policial que viu e o que observou: {policial_viu}
- Ordem de parada: {ordem_parada}
- Reação do veículo: {reacao_veiculo}
- Abordagem e busca: {abordagem_busca}
- Irregularidades: {irregularidades}

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

1. Contexto inicial: onde e quando o veículo foi visualizado
2. Descrição do veículo: marca, modelo, cor, placa
3. Comportamento observado: o que chamou atenção (CONCRETO, não vago)
4. Identificação: qual policial viu primeiro
5. Ordem de parada: como foi dada
6. Reação: veículo parou ou fugiu? Se fugiu, descrever trajeto e distância
7. Fundada suspeita: conectar comportamento observado com decisão de buscar
8. Busca: quem fez, onde procurou, o que encontrou
9. Irregularidades (se houver): veículo furtado/roubado/clonado

IMPORTANTE:

- Se alguma resposta estiver como "Não informado", simplesmente OMITA aquela informação (não invente)
- Descreva SEMPRE: motivo da atenção → conduta observada → decisão pela busca
- Use conectivos para fluidez: "ao notar", "diante de", "sendo que", "durante", "onde"
- Mantenha coerência temporal: visualização → ordem → reação → abordagem
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
        # Se não havia veículo, retorna vazio
        if section_data.get("2.0", "").strip().upper() in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
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
6. Conecte observações à fundada suspeita conforme STF 2025
7. Gere texto em 2-3 parágrafos fluidos
8. NÃO use juridiquês, gerúndio ou termos vagos como "atitude suspeita"

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
