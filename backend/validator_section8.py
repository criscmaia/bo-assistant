# -*- coding: utf-8 -*-
"""
Validador de respostas para Seção 8: Condução e Pós-Ocorrência

Implementa regras de validação específicas para perguntas sobre condução e pós-ocorrência:
- Validação de graduação militar obrigatória (8.1, 8.6)
- Validação de resposta negativa aceita (8.2, 8.3, 8.4, 8.5) - allow_none_response
- Validação de destino obrigatório (8.6)
- Validação de comprimento mínimo

Fundamento jurídico:
- Lei 11.343/06 (Lei de Drogas) - Arts. 33, 35, 40
- Lei 13.869/19 (Lei de Abuso de Autoridade)
- CPP Arts. 282-284 (Prisão em flagrante e garantias)

Author: Cristiano Maia + Claude (Anthropic)
Date: 23/12/2025
"""
from typing import Tuple


# Regras de validação para cada pergunta da Seção 8
VALIDATION_RULES_SECTION8 = {
    "8.1": {
        "min_length": 50,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Sargento Marco deu voz de prisão ao autor pelo aparente flagrante delito de tráfico de drogas (art. 33 da Lei 11.343/06)",
            "O Soldado Faria deu voz de prisão aos dois autores pelo crime de tráfico de entorpecentes (art. 33)"
        ],
        "error_message": "Informe QUEM deu voz de prisão (graduação + nome) e POR QUAL CRIME. Mínimo 50 caracteres."
    },
    "8.2": {
        "min_length": 20,
        "allow_none_response": True,
        "none_patterns": ["sem agravantes", "não havia", "nenhum agravante", "não houve agravante", "nenhuma circunstância agravante"],
        "examples": [
            "Havia agravante de associação para o tráfico (art. 35) e envolvimento de menor de idade",
            "Sem agravantes identificados"
        ],
        "error_message": "Informe os agravantes (art. 40) ou responda 'Sem agravantes'. Mínimo 20 caracteres."
    },
    "8.3": {
        "allow_none_response": True,
        "none_patterns": ["não declarou", "nada a declarar", "não falou", "silêncio", "permaneceu em silêncio", "não proferiu", "recusou"],
        "examples": [
            "O preso declarou literalmente: 'Essa droga não é minha, eu só estava guardando para um amigo'",
            "O autor permaneceu em silêncio, exercendo seu direito constitucional de não produzir prova contra si mesmo"
        ],
        "error_message": "Transcreva literalmente a declaração ou informe 'Não declarou' / 'Permaneceu em silêncio'."
    },
    "8.4": {
        "allow_none_response": True,
        "none_patterns": ["sem registros", "sem antecedentes", "nada consta", "limpo", "não possui", "nenhum registro"],
        "examples": [
            "O autor possui REDS 2023-001234 por tráfico e REDS 2022-005678 por associação criminosa",
            "Sem registros anteriores no sistema REDS"
        ],
        "error_message": "Cite os REDS anteriores ou informe 'Sem registros anteriores'."
    },
    "8.5": {
        "allow_none_response": True,
        "none_patterns": ["sem vínculo", "não identificado", "nenhuma facção", "não possui vínculo", "nenhum vínculo"],
        "examples": [
            "O autor possui vínculo com a facção Primeiro Comando, atuando como 'vapor' no ponto de venda localizado na Rua das Flores",
            "Sem vínculo com facção criminosa identificado"
        ],
        "error_message": "Detalhe o vínculo com facção ou informe 'Sem vínculo identificado'."
    },
    "8.6": {
        "min_length": 50,
        "required_keywords_any": ["ceflan", "delegacia", "dp", "dipc", "central", "hospital", "upa", "destino"],
        "examples": [
            "Os direitos constitucionais foram lidos ao preso, que declarou tê-los compreendido. Integridade física verificada sem lesões. O autor foi conduzido à Delegacia de Plantão Central e o material apreendido encaminhado à CEFLAN 2",
            "Garantias asseguradas: leitura de direitos e verificação de integridade física (sem lesões). Pessoas conduzidas à DIPC e materiais à CEFLAN"
        ],
        "error_message": "Informe: (1) garantias asseguradas (direitos + integridade) e (2) destino de PESSOAS e MATERIAIS. Mínimo 50 caracteres."
    }
}


class ResponseValidatorSection8:
    """
    Validador de respostas para Seção 8 (Condução e Pós-Ocorrência).

    Características:
    - Nenhuma pergunta é condicional (todas devem ser respondidas)
    - 4 perguntas usam allow_none_response (8.2, 8.3, 8.4, 8.5)
    - 2 perguntas exigem graduação militar (8.1, 8.6 implícita)
    - Pergunta 8.6 requer destino (CEFLAN, delegacia, etc.)

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
