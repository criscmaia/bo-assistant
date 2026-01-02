# -*- coding: utf-8 -*-
"""
Validador de respostas para Seção 4: Entrada em Domicílio

Implementa regras de validação específicas para perguntas sobre entrada em domicílio,
incluindo validação de justa causa, presença de graduação militar e descrição de ações.

Author: Cristiano Maia + Claude (Anthropic)
Date: 21/12/2025
"""
from typing import Tuple


# Regras de validação para cada pergunta da Seção 4
VALIDATION_RULES_SECTION4 = {
    "4.1": {
        "valid_responses": ["SIM", "NÃO", "NAO", "S", "N", "NENHUM", "NEGATIVO"],
        "examples": ["SIM", "NÃO"],
        "error_message": "Responda com SIM ou NÃO. Houve entrada em domicílio durante a ocorrência?"
    },
    "4.2": {
        "min_length": 40,
        "examples": [
            "Vimos o suspeito arremessando uma sacola branca para dentro da casa enquanto corria em direção ao imóvel",
            "Ouvimos sons de descarga no banheiro, compatíveis com eliminação de drogas. A porta estava aberta.",
            "Sentimos forte odor de maconha vindo da janela aberta do imóvel nº 44"
        ],
        "error_message": "Descreva o que foi visto/ouvido/sentido ANTES da entrada. A justa causa deve ser concreta e sensorial (visualização, audição, olfato)."
    },
    "4.3": {
        "min_length": 30,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Sargento Silva viu o suspeito arremessando a sacola para dentro do imóvel nº 120",
            "O Cabo Rodrigues ouviu duas descargas vindas do banheiro, compatíveis com eliminação de drogas"
        ],
        "error_message": "Informe a GRADUAÇÃO + nome do policial e o que ele viu/ouviu exatamente. Exemplo: 'O Sargento Silva viu...'"
    },
    "4.4": {
        "min_length": 30,
        "examples": [
            "Perseguição contínua: a equipe iniciou acompanhamento na rua e manteve contato visual ininterrupto até o interior da residência",
            "Autorização do morador: o proprietário franqueou a entrada voluntariamente após identificação da equipe",
            "Flagrante visual: de fora, através da janela que dava para a rua, visualizamos as drogas sobre a mesa",
            "Droga à vista: pela porta aberta, visualizamos porções de cocaína sobre a mesa da cozinha"
        ],
        "error_message": "Descreva como ocorreu o ingresso: autorização, perseguição contínua, droga à vista ou outro fundamento concreto."
    },
    "4.5": {
        "min_length": 50,
        "examples": [
            "O Sargento Alves entrou primeiro pela porta principal que estava aberta. O Cabo Silva ficou na contenção do portão. O Soldado Pires entrou em seguida pela cozinha e localizou a sacola embaixo da pia."
        ],
        "error_message": "Descreva ação por ação: quem entrou primeiro, por onde entrou, quem ficou na contenção/fora, o que cada um visualizou ou fez."
    }
}


class ResponseValidatorSection4:
    """
    Validador de respostas para Seção 4 (Entrada em Domicílio).

    Aplica regras específicas para cada pergunta, incluindo:
    - Validação de resposta condicional (4.1)
    - Validação de justa causa concreta (4.2)
    - Validação de presença de graduação militar (4.3)
    - Validações de comprimento mínimo para descrição de ações
    """

    @staticmethod
    def validate(step: str, answer: str) -> Tuple[bool, str]:
        """
        Valida uma resposta para uma pergunta específica da Seção 4.

        Args:
            step: ID da pergunta (ex: "4.1", "4.2", etc.)
            answer: Resposta fornecida pelo usuário

        Returns:
            Tupla (is_valid, error_message)
            - is_valid: True se válida, False caso contrário
            - error_message: Mensagem de erro (vazia se válida)
        """
        # Verifica se step existe
        if step not in VALIDATION_RULES_SECTION4:
            return False, f"Pergunta {step} não encontrada"

        # Remove espaços extras
        answer = answer.strip()

        # Verifica se resposta está vazia
        if not answer:
            return False, "Por favor, forneça uma resposta."

        rules = VALIDATION_RULES_SECTION4[step]

        # Validação especial para pergunta 4.1 (condicional)
        if step == "4.1":
            return ResponseValidatorSection4._validate_yes_no(answer, rules)

        # Validação de comprimento mínimo
        if "min_length" in rules:
            if len(answer) < rules["min_length"]:
                return False, rules["error_message"]

        # Validação de palavras-chave obrigatórias (ex: graduação militar)
        if "required_keywords" in rules:
            has_keyword = ResponseValidatorSection4._check_required_keywords(
                answer, rules["required_keywords"]
            )
            if not has_keyword:
                return False, rules["error_message"]

        # Se passou todas as validações
        return True, ""

    @staticmethod
    def _validate_yes_no(answer: str, rules: dict) -> Tuple[bool, str]:
        """Valida resposta SIM/NÃO para pergunta 4.1"""
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
    def get_validation_examples(step: str) -> list:
        """
        Retorna exemplos de respostas válidas para uma pergunta.

        Args:
            step: ID da pergunta (ex: "4.3")

        Returns:
            Lista de exemplos ou lista vazia se step não existe
        """
        if step not in VALIDATION_RULES_SECTION4:
            return []

        return VALIDATION_RULES_SECTION4[step].get("examples", [])

    @staticmethod
    def get_error_message(step: str) -> str:
        """Retorna mensagem de erro padrão para uma pergunta"""
        if step not in VALIDATION_RULES_SECTION4:
            return "Pergunta não encontrada"

        return VALIDATION_RULES_SECTION4[step].get("error_message", "Resposta inválida")
