# -*- coding: utf-8 -*-
"""
Validador de respostas para Seção 2: Abordagem a Veículo

Implementa regras de validação específicas para perguntas sobre veículos,
incluindo validação de placas no formato Mercosul.

Author: Cristiano Maia + Claude (Anthropic)
Date: 19/12/2025
"""
import re
from typing import Tuple


# Regras de validação para cada pergunta da Seção 2
VALIDATION_RULES_SECTION2 = {
    "2.0": {
        "valid_responses": ["SIM", "NÃO", "NAO", "S", "N", "NENHUM", "NEGATIVO"],
        "examples": ["SIM", "NÃO"],
        "error_message": "Responda com SIM ou NÃO. Havia veículo envolvido na ocorrência?"
    },
    "2.1": {
        "min_length": 15,
        "custom_check": "vehicle_plate",
        "examples": [
            "VW Gol branco, placa ABC-1D23",
            "Fiat Palio preto, placa DXY9876",
            "Chevrolet Onix prata, ABC1A23"
        ],
        "error_message": "Informe marca, modelo, cor e placa do veículo. Ex: 'VW Gol branco, placa ABC-1D23'"
    },
    "2.2": {
        "min_length": 20,
        "examples": [
            "Rua das Flores, altura do nº 123, Bairro Centro",
            "Esquina da Av. Brasil com Rua Rio",
            "Rodovia BR-381, km 450"
        ],
        "error_message": "Onde o veículo foi visto? Informe o local com detalhes (rua, número, referências)."
    },
    "2.3": {
        "min_length": 30,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Sargento Lucas viu o veículo em alta velocidade mudando bruscamente de direção",
            "O Soldado Marcos percebeu o condutor olhando nervosamente para o retrovisor",
            "O Cabo Almeida visualizou o veículo tentando fugir ao notar a viatura"
        ],
        "error_message": "Informe qual policial viu (graduação + nome) E o que exatamente observou. Ex: 'O Sargento Lucas viu...'"
    },
    "2.4": {
        "min_length": 20,
        "examples": [
            "Foi gritado 'Parado, Polícia Militar!' pelo megafone",
            "O Sargento acionou a sirene e sinalizou com a mão para o veículo encostar",
            "Foi usado o alto-falante da viatura ordenando a parada imediata"
        ],
        "error_message": "Descreva como foi dada a ordem de parada (megafone, sirene, sinal, etc.)."
    },
    "2.5": {
        "min_length": 15,
        "examples": [
            "Parou imediatamente",
            "Fugiu pela Rua Sete, percorreu aproximadamente 200 metros e parou",
            "Acelerou tentando fugir, foi perseguido por 500m até encostar"
        ],
        "error_message": "O veículo parou ou houve perseguição? Descreva o que aconteceu."
    },
    "2.6": {
        "min_length": 30,
        "examples": [
            "O Cabo Nogueira revistou o porta-luvas e encontrou dois tabletes de substância análoga à cocaína",
            "Foi realizada busca no banco traseiro, porta-malas e painel, sendo localizado material entorpecente",
            "O Soldado Faria vistoriou o veículo encontrando porções de maconha sob o banco do motorista"
        ],
        "error_message": "Descreva a abordagem e a busca no veículo (quem fez, onde procurou, o que encontrou)."
    },
    "2.7": {
        "min_length": 3,
        "examples": [
            "NÃO",
            "Veículo furtado, consta no REDS número 12345/2024",
            "Placa clonada, identificado através de chassi divergente",
            "Veículo com registro de roubo em Contagem/MG"
        ],
        "error_message": "Havia irregularidades no veículo (furto, roubo, clonagem, REDS)? Se não, responda 'NÃO'."
    }
}


class ResponseValidatorSection2:
    """
    Validador de respostas para Seção 2 (Abordagem a Veículo).

    Aplica regras específicas para cada pergunta, incluindo:
    - Validação de resposta condicional (2.0)
    - Validação de placa Mercosul (2.1)
    - Validação de presença de graduação militar (2.3)
    - Validações de comprimento mínimo
    """

    @staticmethod
    def validate(step: str, answer: str) -> Tuple[bool, str]:
        """
        Valida uma resposta para uma pergunta específica da Seção 2.

        Args:
            step: ID da pergunta (ex: "2.1", "2.2", etc.)
            answer: Resposta fornecida pelo usuário

        Returns:
            Tupla (is_valid, error_message)
            - is_valid: True se válida, False caso contrário
            - error_message: Mensagem de erro (vazia se válida)
        """
        # Verifica se step existe
        if step not in VALIDATION_RULES_SECTION2:
            return False, f"Pergunta {step} não encontrada"

        # Remove espaços extras
        answer = answer.strip()

        # Verifica se resposta está vazia
        if not answer:
            return False, "Por favor, forneça uma resposta."

        rules = VALIDATION_RULES_SECTION2[step]

        # Validação especial para pergunta 2.0 (condicional)
        if step == "2.0":
            return ResponseValidatorSection2._validate_yes_no(answer, rules)

        # Validação de comprimento mínimo
        if "min_length" in rules:
            if len(answer) < rules["min_length"]:
                return False, rules["error_message"]

        # Validação custom de placa para pergunta 2.1
        if "custom_check" in rules and rules["custom_check"] == "vehicle_plate":
            plate_valid, plate_error = ResponseValidatorSection2._validate_vehicle_plate(answer)
            if not plate_valid:
                return False, f"{rules['error_message']}\n{plate_error}"

        # Validação de palavras-chave obrigatórias (ex: graduação militar)
        if "required_keywords" in rules:
            has_keyword = ResponseValidatorSection2._check_required_keywords(
                answer, rules["required_keywords"]
            )
            if not has_keyword:
                return False, rules["error_message"]

        # Validações específicas por pergunta
        if step == "2.7":
            # Pergunta 2.7 aceita "NÃO" como resposta válida curta
            if answer.upper() in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO", "NENHUMA"]:
                return True, ""

        # Se passou todas as validações
        return True, ""

    @staticmethod
    def _validate_yes_no(answer: str, rules: dict) -> Tuple[bool, str]:
        """Valida resposta SIM/NÃO para pergunta 2.0"""
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
    def _validate_vehicle_plate(answer: str) -> Tuple[bool, str]:
        """
        Valida presença de placa no formato Mercosul.

        Formatos aceitos:
        - ABC1D23
        - ABC-1D23
        - ABC 1D23

        Args:
            answer: Resposta completa (ex: "VW Gol branco, placa ABC-1D23")

        Returns:
            Tupla (is_valid, error_message)
        """
        # Padrão Mercosul: 3 letras + 1 número + 1 letra + 2 números
        # Com ou sem hífen/espaço
        plate_pattern = r'[A-Z]{3}[-\s]?[0-9][A-Z][0-9]{2}'

        # Busca padrão na resposta (case-insensitive)
        if re.search(plate_pattern, answer.upper()):
            return True, ""

        # Se não encontrou, retorna erro específico
        return False, "⚠️ Placa não encontrada ou em formato inválido. Use formato Mercosul: ABC-1D23 ou ABC1D23"

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
            step: ID da pergunta (ex: "2.3")

        Returns:
            Lista de exemplos ou lista vazia se step não existe
        """
        if step not in VALIDATION_RULES_SECTION2:
            return []

        return VALIDATION_RULES_SECTION2[step].get("examples", [])

    @staticmethod
    def get_error_message(step: str) -> str:
        """Retorna mensagem de erro padrão para uma pergunta"""
        if step not in VALIDATION_RULES_SECTION2:
            return "Pergunta não encontrada"

        return VALIDATION_RULES_SECTION2[step].get("error_message", "Resposta inválida")
