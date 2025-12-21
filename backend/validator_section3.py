# -*- coding: utf-8 -*-
"""
Validador de respostas para Seção 3: Campana (Vigilância Velada)

Implementa regras de validação específicas para perguntas sobre campana,
incluindo validação de presença de graduação militar e descrição de atos concretos.

Author: Cristiano Maia + Claude (Anthropic)
Date: 19/12/2025
"""
from typing import Tuple


# Regras de validação para cada pergunta da Seção 3
VALIDATION_RULES_SECTION3 = {
    "3.1": {
        "valid_responses": ["SIM", "NÃO", "NAO", "S", "N", "NENHUM", "NEGATIVO"],
        "examples": ["SIM", "NÃO"],
        "error_message": "Responda com SIM ou NÃO. A equipe realizou campana antes da abordagem?"
    },
    "3.2": {
        "min_length": 30,
        "examples": [
            "Esquina da Rua das Flores com Av. Brasil, atrás do muro da casa 145, a 30 metros do bar",
            "Dentro da viatura estacionada no nº 233 da Rua Sete, a um quarteirão do ponto",
            "Beco da Rua Principal, atrás de uma caçamba de lixo, a 20 metros do alvo"
        ],
        "error_message": "Descreva o local exato da campana, ponto de observação e distância aproximada até o suspeito."
    },
    "3.3": {
        "min_length": 30,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Sargento Silva tinha visão desobstruída da porta do bar. O Cabo Almeida observava a lateral.",
            "O Soldado Faria conseguia ver a entrada do beco de sua posição atrás do muro."
        ],
        "error_message": "Informe qual policial (graduação + nome) tinha visão direta e o que cada um conseguia ver."
    },
    "3.4": {
        "min_length": 20,
        "examples": [
            "Denúncia anônima específica recebida via COPOM",
            "Informações da inteligência policial sobre o ponto",
            "Histórico de ocorrências no local e usuários abordados antes indicando o ponto"
        ],
        "error_message": "Descreva o que motivou a campana (denúncia, inteligência, histórico, usuários, moradores)."
    },
    "3.5": {
        "min_length": 10,
        "examples": [
            "10 minutos de vigilância contínua",
            "20 minutos alternados entre observação e deslocamento",
            "Aproximadamente 15 minutos de campana contínua"
        ],
        "error_message": "Informe a duração da campana e se foi contínua ou alternada."
    },
    "3.6": {
        "min_length": 40,
        "examples": [
            "O homem tirou pequenos invólucros da mochila preta e entregou para dois rapazes que chegaram de moto",
            "A mulher recebia dinheiro e retirava algo do bolso esquerdo, entregando aos compradores",
            "O suspeito pegava porções de um pote azul escondido atrás do poste e entregava aos usuários"
        ],
        "error_message": "Descreva atos CONCRETOS observados (trocas, entregas, esconderijos). NÃO use generalizações como 'atitude suspeita'."
    },
    "3.7": {
        "min_length": 3,
        "examples": [
            "NÃO",
            "Sim, foram abordados 2 usuários que saíam do local. Portavam 3 porções de cocaína e relataram ter comprado do 'cara de vermelho' por R$ 50",
            "Sim, 1 usuário foi abordado pelo Cabo Silva. Tinha 1 porção de maconha e disse ter comprado no bar"
        ],
        "error_message": "Houve abordagem de usuários? Se sim, informe quantos, o que tinham, o que relataram. Se não, escreva NÃO."
    },
    "3.8": {
        "min_length": 3,
        "examples": [
            "NÃO",
            "Sim, ao perceber a movimentação policial, correu para o beco ao lado da casa 40",
            "Sim, tentou fugir pulando o muro dos fundos do bar, sendo alcançado pelo Soldado Faria"
        ],
        "error_message": "Houve fuga ao notar a equipe? Se sim, descreva como. Se não, escreva NÃO."
    }
}


class ResponseValidatorSection3:
    """
    Validador de respostas para Seção 3 (Campana - Vigilância Velada).

    Aplica regras específicas para cada pergunta, incluindo:
    - Validação de resposta condicional (3.1)
    - Validação de presença de graduação militar (3.3)
    - Validações de comprimento mínimo para atos concretos
    - Aceitação de "NÃO" para perguntas opcionais
    """

    @staticmethod
    def validate(step: str, answer: str) -> Tuple[bool, str]:
        """
        Valida uma resposta para uma pergunta específica da Seção 3.

        Args:
            step: ID da pergunta (ex: "3.1", "3.2", etc.)
            answer: Resposta fornecida pelo usuário

        Returns:
            Tupla (is_valid, error_message)
            - is_valid: True se válida, False caso contrário
            - error_message: Mensagem de erro (vazia se válida)
        """
        # Verifica se step existe
        if step not in VALIDATION_RULES_SECTION3:
            return False, f"Pergunta {step} não encontrada"

        # Remove espaços extras
        answer = answer.strip()

        # Verifica se resposta está vazia
        if not answer:
            return False, "Por favor, forneça uma resposta."

        rules = VALIDATION_RULES_SECTION3[step]

        # Validação especial para pergunta 3.1 (condicional)
        if step == "3.1":
            return ResponseValidatorSection3._validate_yes_no(answer, rules)

        # Validação de comprimento mínimo
        if "min_length" in rules:
            if len(answer) < rules["min_length"]:
                return False, rules["error_message"]

        # Validação de palavras-chave obrigatórias (ex: graduação militar)
        if "required_keywords" in rules:
            has_keyword = ResponseValidatorSection3._check_required_keywords(
                answer, rules["required_keywords"]
            )
            if not has_keyword:
                return False, rules["error_message"]

        # Validações específicas por pergunta
        if step in ["3.7", "3.8"]:
            # Perguntas 3.7 e 3.8 aceitam "NÃO" como resposta válida curta
            if answer.upper() in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO", "NENHUMA"]:
                return True, ""

        # Se passou todas as validações
        return True, ""

    @staticmethod
    def _validate_yes_no(answer: str, rules: dict) -> Tuple[bool, str]:
        """Valida resposta SIM/NÃO para pergunta 3.1"""
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
            step: ID da pergunta (ex: "3.3")

        Returns:
            Lista de exemplos ou lista vazia se step não existe
        """
        if step not in VALIDATION_RULES_SECTION3:
            return []

        return VALIDATION_RULES_SECTION3[step].get("examples", [])

    @staticmethod
    def get_error_message(step: str) -> str:
        """Retorna mensagem de erro padrão para uma pergunta"""
        if step not in VALIDATION_RULES_SECTION3:
            return "Pergunta não encontrada"

        return VALIDATION_RULES_SECTION3[step].get("error_message", "Resposta inválida")
