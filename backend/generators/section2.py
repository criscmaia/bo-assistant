"""
Section2Generator - Gerador para Seção 2: Abordagem a Veículo

Extrai texto baseado nas 13 perguntas da seção 2.
Seção 2 tem skip logic: se 2.1 = "NÃO" (não havia veículo), retorna string vazia.
"""

from typing import Dict

from .base import BaseSectionGenerator


class Section2Generator(BaseSectionGenerator):
    """Gerador para Seção 2: Abordagem a Veículo"""

    def _should_skip(self, section_data: Dict[str, str]) -> bool:
        """
        Skip se não havia veículo (pergunta 2.1 = NÃO)

        Args:
            section_data: Dicionário com respostas da seção

        Returns:
            True se deve pular a seção, False caso contrário
        """
        answer = section_data.get("2.1", "").strip().upper()
        return answer in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]

    def _build_prompt(self, section_data: Dict[str, str]) -> str:
        """
        Constrói prompt para Seção 2 baseado no material do Claudio.

        Fonte:
        - materiais-claudio/_03_busca_veicular.txt
        - materiais-claudio/_regras_gerais_-_gpt_trafico.txt (linhas 29-40)
        - materiais-claudio/_pacotao_1.txt (linhas 24-26)
        """

        # Extrair respostas (13 perguntas)
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
