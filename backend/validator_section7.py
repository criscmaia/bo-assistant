# -*- coding: utf-8 -*-
"""
Validador de respostas para Seção 7: Apreensões e Cadeia de Custódia

Implementa regras de validação específicas para perguntas sobre apreensões,
incluindo:
- Validação de resposta condicional (7.1)
- Validação de graduação militar obrigatória (7.2, 7.4)
- Validação de resposta negativa aceita (7.3) - NOVA FUNCIONALIDADE
- Validação de destino obrigatório (7.4)

Fundamento jurídico: Lei 11.343/06 (Lei de Drogas) + CPP Arts. 240§2 e 244

Author: Cristiano Maia + Claude (Anthropic)
Date: 22/12/2025
"""
from typing import Tuple


# Regras de validação para cada pergunta da Seção 7
VALIDATION_RULES_SECTION7 = {
    "7.1": {
        "valid_responses": ["SIM", "NÃO", "NAO", "S", "N", "NENHUM", "NEGATIVO"],
        "examples": ["SIM", "NÃO"],
        "error_message": "Responda com SIM ou NÃO: houve apreensão de drogas?"
    },
    "7.2": {
        "min_length": 50,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Soldado Breno encontrou 14 pedras de substância análoga ao crack dentro de uma lata azul sobre o banco de concreto próximo ao portão da casa 12",
            "A Soldado Pires localizou 23 pinos de cocaína em um buraco no muro"
        ],
        "error_message": "Descreva: tipo, quantidade, embalagem, local e QUEM encontrou (graduação + nome). Mínimo 50 caracteres."
    },
    "7.3": {
        "min_length": 30,
        "allow_none_response": True,
        "none_patterns": ["nenhum", "não havia", "não houve", "não foram"],
        "examples": [
            "Foram apreendidos R$ 450,00 em notas diversas, 2 celulares e 1 balança de precisão",
            "Nenhum objeto ligado ao tráfico foi encontrado além das substâncias entorpecentes"
        ],
        "error_message": "Liste objetos apreendidos (dinheiro, celulares, etc) ou informe 'Nenhum objeto'. Mínimo 30 caracteres."
    },
    "7.4": {
        "min_length": 40,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "required_keywords_any": ["ceflan", "delegacia", "dp", "dipc", "central", "entrega"],
        "examples": [
            "O Soldado Faria lacrou as substâncias no invólucro 01 e os objetos no invólucro 02, fotografou todos os itens no local e ficou responsável pelo material até a entrega na CEFLAN 2",
            "O Cabo Almeida acondicionou em saco plástico, fotografou e transportou até a Delegacia Civil de Contagem"
        ],
        "error_message": "Informe: como lacrou, QUEM ficou responsável (graduação + nome) e DESTINO (CEFLAN, delegacia, etc). Mínimo 40 caracteres."
    }
}


class ResponseValidatorSection7:
    """
    Validador de respostas para Seção 7 (Apreensões e Cadeia de Custódia).

    Aplica regras específicas para cada pergunta, incluindo:
    - Validação de resposta condicional (7.1)
    - Validação de graduação militar obrigatória (7.2, 7.4)
    - Validação de resposta negativa aceita (7.3) - NOVA FUNCIONALIDADE (allow_none_response)
    - Validação de destino obrigatório (7.4)

    Fundamento jurídico: Lei 11.343/06 - Arts. 33, 35, 40
    "A cadeia de custódia assegura a integridade de drogas apreendidas desde a
    apreensão até o depósito, documentando quem a detinha, quando, onde e como."
    """

    @staticmethod
    def validate(step: str, answer: str) -> Tuple[bool, str]:
        """
        Valida uma resposta para uma pergunta específica da Seção 7.

        Args:
            step: ID da pergunta (ex: "7.1", "7.2", etc.)
            answer: Resposta fornecida pelo usuário

        Returns:
            Tupla (is_valid, error_message)
            - is_valid: True se válida, False caso contrário
            - error_message: Mensagem de erro (vazia se válida)
        """
        # Verifica se step existe
        if step not in VALIDATION_RULES_SECTION7:
            return False, f"Pergunta {step} não encontrada"

        # Remove espaços extras
        answer = answer.strip()

        # Verifica se resposta está vazia
        if not answer:
            return False, "Por favor, forneça uma resposta."

        rules = VALIDATION_RULES_SECTION7[step]

        # Validação especial para pergunta 7.1 (condicional)
        if step == "7.1":
            return ResponseValidatorSection7._validate_yes_no(answer, rules)

        # Validação de resposta negativa aceita (7.3) - NOVA FUNCIONALIDADE
        if step == "7.3" and rules.get("allow_none_response"):
            # Se resposta indica "nenhum objeto", aceitar sem exigir min_length
            if ResponseValidatorSection7._check_none_response(answer, rules.get("none_patterns", [])):
                return True, ""

        # Validação de comprimento mínimo
        if "min_length" in rules:
            if len(answer) < rules["min_length"]:
                return False, rules["error_message"]

        # Validação de palavras-chave obrigatórias (ex: graduação militar)
        if "required_keywords" in rules:
            has_keyword = ResponseValidatorSection7._check_required_keywords(
                answer, rules["required_keywords"]
            )
            if not has_keyword:
                return False, rules["error_message"]

        # Validação de palavras-chave "qualquer uma de" (para 7.4 - destino)
        if "required_keywords_any" in rules:
            has_any_keyword = ResponseValidatorSection7._check_required_keywords_any(
                answer, rules["required_keywords_any"]
            )
            if not has_any_keyword:
                return False, rules["error_message"]

        # Se passou todas as validações
        return True, ""

    @staticmethod
    def _validate_yes_no(answer: str, rules: dict) -> Tuple[bool, str]:
        """Valida resposta SIM/NÃO para pergunta 7.1"""
        answer_upper = answer.strip().upper()

        # Remove acentos para comparação
        answer_normalized = answer_upper.replace("Ã", "A")

        valid_responses_normalized = [
            resp.replace("Ã", "A") for resp in rules["valid_responses"]
        ]

        if answer_normalized in valid_responses_normalized:
            return True, ""

        return False, rules["error_message"]

    @staticmethod
    def _check_none_response(answer: str, none_patterns: list) -> bool:
        """
        Verifica se a resposta indica ausência de objetos/itens.

        Args:
            answer: Resposta do usuário
            none_patterns: Lista de padrões que indicam "nenhum/não havia"

        Returns:
            True se a resposta indica "nenhum", False caso contrário
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
        (Alias para _check_required_keywords)

        Args:
            answer: Resposta do usuário
            keywords: Lista de palavras-chave (case-insensitive)

        Returns:
            True se contém ao menos uma keyword, False caso contrário
        """
        return ResponseValidatorSection7._check_required_keywords(answer, keywords)

    @staticmethod
    def get_validation_examples(step: str) -> list:
        """
        Retorna exemplos de respostas válidas para uma pergunta.

        Args:
            step: ID da pergunta (ex: "7.2")

        Returns:
            Lista de exemplos ou lista vazia se step não existe
        """
        if step not in VALIDATION_RULES_SECTION7:
            return []

        return VALIDATION_RULES_SECTION7[step].get("examples", [])

    @staticmethod
    def get_error_message(step: str) -> str:
        """Retorna mensagem de erro padrão para uma pergunta"""
        if step not in VALIDATION_RULES_SECTION7:
            return "Pergunta não encontrada"

        return VALIDATION_RULES_SECTION7[step].get("error_message", "Resposta inválida")
