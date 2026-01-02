# -*- coding: utf-8 -*-
"""
Validador de respostas para Seção 8: Condução e Pós-Ocorrência
REFATORADO - Usa Strategy Pattern (v0.13.1)

Reduzido de 292 → ~30 linhas (90% menos código)

Author: Cristiano Maia + Claude (Anthropic)
Date: 02/01/2026
"""
from typing import Tuple, Dict, Any
from backend.validators import get_validator, validate_answer


class ResponseValidatorSection8:
    """
    Validador de respostas para Seção 8 (Condução e Pós-Ocorrência).

    REFATORADO (v0.13.1): Usa ValidationFactory centralizado.
    Elimina duplicação de código (~260 linhas) mantendo compatibilidade total.
    """

    def validate_answer(self, question_id: str, answer: str, context: Dict[str, Any] = None) -> Tuple[bool, str]:
        """
        Valida resposta usando ValidationFactory.

        Args:
            question_id: ID da pergunta (ex: "8.1", "8.2", etc.)
            answer: Resposta fornecida pelo usuário
            context: Contexto com respostas anteriores (opcional)

        Returns:
            Tuple[bool, str]: (válido, mensagem de erro ou "OK")
        """
        context = context or {}
        result = validate_answer(question_id, answer, context)

        if result["valid"]:
            return (True, "OK")
        else:
            return (False, result.get("error", "Resposta inválida"))
