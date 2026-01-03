"""
Section3Generator - Gerador para Seção 3: Campana (Vigilância Velada)

Extrai texto baseado nas 8 perguntas da seção 3.
Seção 3 tem skip logic: se 3.1 = "NÃO" (não houve campana), retorna string vazia.
"""

from typing import Dict

from .base import BaseSectionGenerator


class Section3Generator(BaseSectionGenerator):
    """Gerador para Seção 3: Campana (Vigilância Velada)"""

    def _should_skip(self, section_data: Dict[str, str]) -> bool:
        """
        Skip se não houve campana (pergunta 3.1 = NÃO)

        Args:
            section_data: Dicionário com respostas da seção

        Returns:
            True se deve pular a seção, False caso contrário
        """
        answer = section_data.get("3.1", "").strip().upper()
        return answer in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]

    def _build_prompt(self, section_data: Dict[str, str]) -> str:
        """
        Constrói prompt para Seção 3 (Campana - Vigilância Velada).

        Fonte:
        - materiais-claudio/_secao_-_campana.txt
        - materiais-claudio/_regras_gerais_-_gpt_trafico.txt (linhas 42-52)
        """

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
