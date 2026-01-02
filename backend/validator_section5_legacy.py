# -*- coding: utf-8 -*-
"""
Validador de respostas para Seção 5: Fundada Suspeita

Implementa regras de validação específicas para perguntas sobre fundada suspeita,
incluindo validação de descrição de comportamentos observados, presença de graduação militar
e descrição individualizada dos abordados.

Author: Cristiano Maia + Claude (Anthropic)
Date: 22/12/2025
"""
from typing import Tuple


# Regras de validação para cada pergunta da Seção 5
VALIDATION_RULES_SECTION5 = {
    "5.1": {
        "min_length": 40,
        "examples": [
            "Durante patrulhamento pela Rua das Palmeiras, região com registros anteriores de tráfico de drogas, visualizamos um homem de camisa vermelha e bermuda jeans retirando pequenos invólucros de um buraco no muro",
            "No local indicado pela denúncia, conhecido por registros de tráfico, observamos indivíduo realizando contato rápido com motoristas que paravam e entregando pequenos pacotes",
            "Ao chegar na Rua Central, visualizamos comportamento suspeito: indivíduo entregando objetos a terceiros que chegavam de veículo, recebendo valores em troca"
        ],
        "error_message": "Descreva o que a equipe viu ao chegar no local. Mínimo 40 caracteres com detalhes concretos (local, contexto, comportamento observado)."
    },
    "5.2": {
        "min_length": 30,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Sargento João, de dentro da viatura estacionada a 20 metros, visualizou o suspeito retirando invólucros do buraco no muro",
            "O Cabo Almeida, posicionado na esquina oposta, viu o indivíduo entregar pacotes e receber dinheiro",
            "O Soldado Pires, de pé próximo ao poste de energia, observou todo o procedimento de entrega"
        ],
        "error_message": "Informe a GRADUAÇÃO + nome do policial, de onde viu e o que exatamente viu. Exemplo: 'O Sargento João viu...'"
    },
    "5.3": {
        "min_length": 50,
        "examples": [
            "Homem de camisa vermelha e bermuda jeans, porte atlético, gestos nervosos ao perceber a viatura, posteriormente identificado como JOÃO DA SILVA, vulgo 'Vermelho'. Ao ser abordado, tentou esconder objeto no bolso da bermuda.",
            "Indivíduo trajando camiseta azul e bermuda preta, cabelos pretos, aproximadamente 1,80m de altura. Apresentava comportamento evasivo, procurando olhar repetidamente para trás. Identificado como CARLOS SANTOS OLIVEIRA, alcunha 'Marreco'."
        ],
        "error_message": "Descreva INDIVIDUALMENTE cada abordado: roupa, porte físico, gestos/comportamento, e identificação completa (nome completo + vulgo). Mínimo 50 caracteres."
    }
}


class ResponseValidatorSection5:
    """
    Validador de respostas para Seção 5 (Fundada Suspeita).

    Aplica regras específicas para cada pergunta, incluindo:
    - Validação de resposta condicional (5.1)
    - Validação de descrição de comportamentos observados (5.2)
    - Validação de presença de graduação militar (5.3)
    - Validações de comprimento mínimo para descrição individualizada
    """

    @staticmethod
    def validate(step: str, answer: str) -> Tuple[bool, str]:
        """
        Valida uma resposta para uma pergunta específica da Seção 5.

        Args:
            step: ID da pergunta (ex: "5.1", "5.2", etc.)
            answer: Resposta fornecida pelo usuário

        Returns:
            Tupla (is_valid, error_message)
            - is_valid: True se válida, False caso contrário
            - error_message: Mensagem de erro (vazia se válida)
        """
        # Verifica se step existe
        if step not in VALIDATION_RULES_SECTION5:
            return False, f"Pergunta {step} não encontrada"

        # Remove espaços extras
        answer = answer.strip()

        # Verifica se resposta está vazia
        if not answer:
            return False, "Por favor, forneça uma resposta."

        rules = VALIDATION_RULES_SECTION5[step]

        # Validação de comprimento mínimo
        if "min_length" in rules:
            if len(answer) < rules["min_length"]:
                return False, rules["error_message"]

        # Validação de palavras-chave obrigatórias (ex: graduação militar)
        if "required_keywords" in rules:
            has_keyword = ResponseValidatorSection5._check_required_keywords(
                answer, rules["required_keywords"]
            )
            if not has_keyword:
                return False, rules["error_message"]

        # Se passou todas as validações
        return True, ""

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
            step: ID da pergunta (ex: "5.3")

        Returns:
            Lista de exemplos ou lista vazia se step não existe
        """
        if step not in VALIDATION_RULES_SECTION5:
            return []

        return VALIDATION_RULES_SECTION5[step].get("examples", [])

    @staticmethod
    def get_error_message(step: str) -> str:
        """Retorna mensagem de erro padrão para uma pergunta"""
        if step not in VALIDATION_RULES_SECTION5:
            return "Pergunta não encontrada"

        return VALIDATION_RULES_SECTION5[step].get("error_message", "Resposta inválida")
