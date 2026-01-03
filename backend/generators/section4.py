"""
Section4Generator - Gerador para Seção 4: Entrada em Domicílio

Extrai texto baseado nas 5 perguntas da seção 4.
Seção 4 tem skip logic: se 4.1 = "NÃO" (não houve entrada em domicílio), retorna string vazia.
"""

from typing import Dict

from .base import BaseSectionGenerator


class Section4Generator(BaseSectionGenerator):
    """Gerador para Seção 4: Entrada em Domicílio"""

    def _should_skip(self, section_data: Dict[str, str]) -> bool:
        """
        Skip se não houve entrada em domicílio (pergunta 4.1 = NÃO)

        Args:
            section_data: Dicionário com respostas da seção

        Returns:
            True se deve pular a seção, False caso contrário
        """
        answer = section_data.get("4.1", "").strip().upper()
        return answer in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]

    def _build_prompt(self, section_data: Dict[str, str]) -> str:
        """
        Constrói prompt para Seção 4 (Entrada em Domicílio).

        Fonte:
        - materiais-claudio/_04_entrada_em_domicilio.txt
        - materiais-claudio/_regras_gerais_-_gpt_trafico.txt (linhas 54-60)
        """

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
