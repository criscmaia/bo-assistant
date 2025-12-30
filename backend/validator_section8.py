# -*- coding: utf-8 -*-
"""
Validador de respostas para Seção 8: Condução e Pós-Ocorrência

Implementa regras de validação específicas para perguntas sobre condução e pós-ocorrência:
- Validação de graduação militar obrigatória (8.1, 8.10)
- Validação de resposta negativa aceita (8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9) - allow_none_response
- Validação de transporte obrigatório (8.2)
- Validação de destino obrigatório (8.11)
- Validação de comprimento mínimo

Fundamento jurídico:
- Lei 11.343/06 (Lei de Drogas) - Arts. 33, 35, 40
- Lei 13.869/19 (Lei de Abuso de Autoridade)
- CPP Arts. 282-284 (Prisão em flagrante e garantias)

Author: Cristiano Maia + Claude (Anthropic)
Date: 30/12/2025
"""
from typing import Tuple


# Regras de validação para cada pergunta da Seção 8
VALIDATION_RULES_SECTION8 = {
    "8.1": {
        "min_length": 30,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Sargento Silva deu voz de prisão pelo crime de tráfico de drogas (art. 33 da Lei 11.343/06)",
            "O Cabo Almeida deu voz de prisão por tráfico (art. 33) e associação (art. 35)"
        ],
        "error_message": "Informe QUEM deu voz de prisão (graduação + nome) e POR QUAL CRIME (artigo). Mínimo 30 caracteres."
    },
    "8.2": {
        "min_length": 20,
        "required_keywords_any": ["viatura", "prefixo", "veículo", "conduzido", "transportado"],
        "examples": [
            "O preso foi conduzido na viatura prefixo 1234, no banco traseiro, algemado",
            "Transportado na viatura da guarnição até a Delegacia de Plantão"
        ],
        "error_message": "Informe como o preso foi transportado (viatura, prefixo, posição). Mínimo 20 caracteres."
    },
    "8.3": {
        "min_length": 10,
        "allow_none_response": True,
        "none_patterns": ["não declarou", "permaneceu em silêncio", "silêncio", "nada declarou", "recusou"],
        "examples": [
            "O preso declarou: 'Essa droga não é minha, estava só guardando'",
            "Permaneceu em silêncio, exercendo seu direito constitucional",
            "Não declarou nada"
        ],
        "error_message": "Transcreva literalmente o que o preso declarou ou informe 'Permaneceu em silêncio'."
    },
    "8.4": {
        "min_length": 10,
        "allow_none_response": True,
        "none_patterns": ["não identificada", "não apurada", "desconhecida", "não informada"],
        "examples": [
            "Vapor - responsável pela venda direta aos usuários",
            "Gerente do ponto de tráfico",
            "Olheiro - vigiava a chegada da polícia",
            "Função não identificada durante a ocorrência"
        ],
        "error_message": "Informe a função no tráfico (vapor, gerente, olheiro, etc.) ou 'Não identificada'."
    },
    "8.5": {
        "min_length": 5,
        "allow_none_response": True,
        "none_patterns": ["sem passagens", "nada consta", "sem registros", "não possui", "negativo"],
        "examples": [
            "Possui REDS 2024-001234 por tráfico e REDS 2023-005678 por associação",
            "Sem passagens anteriores no sistema REDS",
            "Nada consta"
        ],
        "error_message": "Informe os REDS anteriores ou 'Sem passagens anteriores'."
    },
    "8.6": {
        "min_length": 5,
        "allow_none_response": True,
        "none_patterns": ["não há", "sem indícios", "não identificado", "negativo", "não foram identificados"],
        "examples": [
            "Sim, portava cordão de ouro, relógio de luxo e R$ 5.000 em espécie",
            "Tatuagem com símbolo da facção no antebraço direito",
            "Não há indícios aparentes"
        ],
        "error_message": "Descreva indícios de dedicação ao crime (ostentação, tatuagens) ou 'Não há indícios'."
    },
    "8.7": {
        "min_length": 5,
        "allow_none_response": True,
        "none_patterns": ["não", "sem papel", "não identificado", "negativo", "não possui", "ocasional"],
        "examples": [
            "Sim, identificado como gerente regional da facção na zona norte",
            "É conhecido como 'disciplina' da boca de fumo, atuação contínua",
            "Atuação ocasional, sem papel de liderança identificado"
        ],
        "error_message": "Informe papel na facção (ocasional ou contínua) ou 'Não identificado'."
    },
    "8.8": {
        "min_length": 5,
        "allow_none_response": True,
        "none_patterns": ["não houve", "não tentou", "negativo", "não"],
        "examples": [
            "Sim, tentou jogar sacola com drogas pela janela ao ver a viatura",
            "Tentou engolir porções de cocaína durante a abordagem",
            "Ameaçou testemunha: 'Se falar de mim, vou voltar aqui'",
            "Não houve tentativa de destruição ou intimidação"
        ],
        "error_message": "Descreva tentativa de destruir/ocultar provas ou intimidar, ou 'Não houve'."
    },
    "8.9": {
        "min_length": 5,
        "allow_none_response": True,
        "none_patterns": ["não havia", "não", "negativo", "nenhum menor"],
        "examples": [
            "Sim, menor de 16 anos atuava como olheiro",
            "Havia criança de 12 anos no imóvel, encaminhada ao Conselho Tutelar",
            "Não havia menor envolvido"
        ],
        "error_message": "Informe se havia menor, idade e participação, ou 'Não havia menor'."
    },
    "8.10": {
        "min_length": 20,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Sargento Silva informou as garantias constitucionais ao preso",
            "O Cabo Almeida leu os direitos do preso, que declarou ter compreendido"
        ],
        "error_message": "Informe QUEM (graduação + nome) informou as garantias constitucionais."
    },
    "8.11": {
        "min_length": 30,
        "required_keywords_any": ["delegacia", "ceflan", "dp", "dipc", "central", "plantão"],
        "examples": [
            "Presos conduzidos à Delegacia de Plantão Central. Drogas encaminhadas à CEFLAN 2",
            "Autor apresentado na DIPC. Material apreendido lacrado e entregue na CEFLAN",
            "Conduzido à DP de Contagem. Drogas e dinheiro entregues na delegacia"
        ],
        "error_message": "Informe destino dos PRESOS (delegacia) e dos MATERIAIS (CEFLAN). Mínimo 30 caracteres."
    }
}


class ResponseValidatorSection8:
    """
    Validador de respostas para Seção 8 (Condução e Pós-Ocorrência).

    Características:
    - Nenhuma pergunta é condicional (todas as 11 perguntas devem ser respondidas)
    - 7 perguntas usam allow_none_response (8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9)
    - 2 perguntas exigem graduação militar (8.1, 8.10)
    - Pergunta 8.2 requer detalhes de transporte (viatura, prefixo)
    - Pergunta 8.11 requer destino (CEFLAN, delegacia, etc.)

    Fundamento jurídico: Lei 11.343/06, Lei 13.869/19, CPP Arts. 282-284
    """

    @staticmethod
    def validate(step: str, answer: str) -> Tuple[bool, str]:
        """
        Valida uma resposta para uma pergunta específica da Seção 8.

        Args:
            step: ID da pergunta (ex: "8.1", "8.2", etc.)
            answer: Resposta fornecida pelo usuário

        Returns:
            Tupla (is_valid, error_message)
            - is_valid: True se válida, False caso contrário
            - error_message: Mensagem de erro (vazia se válida)
        """
        # Verifica se step existe
        if step not in VALIDATION_RULES_SECTION8:
            return False, f"Pergunta {step} não encontrada"

        # Remove espaços extras
        answer = answer.strip()

        # Verifica se resposta está vazia
        if not answer:
            return False, "Por favor, forneça uma resposta."

        rules = VALIDATION_RULES_SECTION8[step]

        # Validação de resposta negativa aceita (8.2, 8.3, 8.4, 8.5)
        if rules.get("allow_none_response"):
            # Se resposta indica "nenhum", "não declarou", etc., aceitar sem exigir min_length
            if ResponseValidatorSection8._check_none_response(answer, rules.get("none_patterns", [])):
                return True, ""

        # Validação de comprimento mínimo
        if "min_length" in rules:
            if len(answer) < rules["min_length"]:
                return False, rules["error_message"]

        # Validação de palavras-chave obrigatórias (ex: graduação militar)
        if "required_keywords" in rules:
            has_keyword = ResponseValidatorSection8._check_required_keywords(
                answer, rules["required_keywords"]
            )
            if not has_keyword:
                return False, rules["error_message"]

        # Validação de palavras-chave "qualquer uma de" (para destino em 8.6)
        if "required_keywords_any" in rules:
            has_any_keyword = ResponseValidatorSection8._check_required_keywords_any(
                answer, rules["required_keywords_any"]
            )
            if not has_any_keyword:
                return False, rules["error_message"]

        # Se passou todas as validações
        return True, ""

    @staticmethod
    def _check_none_response(answer: str, none_patterns: list) -> bool:
        """
        Verifica se a resposta indica ausência de registros/vínculos/declarações.

        Args:
            answer: Resposta do usuário
            none_patterns: Lista de padrões que indicam "nenhum/não havia/não declarou"

        Returns:
            True se a resposta indica negação, False caso contrário
        """
        answer_lower = answer.lower()

        for pattern in none_patterns:
            if pattern.lower() in answer_lower:
                return True

        return False

    @staticmethod
    def _check_required_keywords(answer: str, keywords: list) -> bool:
        """
        Verifica se a resposta contém pelo menos uma das palavras-chave.

        Args:
            answer: Resposta do usuário
            keywords: Lista de palavras-chave (case-insensitive)

        Returns:
            True se contém ao menos uma keyword, False caso contrário
        """
        answer_lower = answer.lower()

        for keyword in keywords:
            if keyword.lower() in answer_lower:
                return True

        return False

    @staticmethod
    def _check_required_keywords_any(answer: str, keywords: list) -> bool:
        """
        Verifica se a resposta contém pelo menos uma das palavras-chave.
        (Alias para _check_required_keywords, usado para destinos)

        Args:
            answer: Resposta do usuário
            keywords: Lista de palavras-chave (case-insensitive)

        Returns:
            True se contém ao menos uma keyword, False caso contrário
        """
        return ResponseValidatorSection8._check_required_keywords(answer, keywords)

    @staticmethod
    def get_validation_examples(step: str) -> list:
        """
        Retorna exemplos de respostas válidas para uma pergunta.

        Args:
            step: ID da pergunta (ex: "8.2")

        Returns:
            Lista de exemplos ou lista vazia se step não existe
        """
        if step not in VALIDATION_RULES_SECTION8:
            return []

        return VALIDATION_RULES_SECTION8[step].get("examples", [])

    @staticmethod
    def get_error_message(step: str) -> str:
        """Retorna mensagem de erro padrão para uma pergunta"""
        if step not in VALIDATION_RULES_SECTION8:
            return "Pergunta não encontrada"

        return VALIDATION_RULES_SECTION8[step].get("error_message", "Resposta inválida")
