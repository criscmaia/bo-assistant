# -*- coding: utf-8 -*-
"""
Validador de respostas para Seção 5: Fundada Suspeita
REFATORADO - Usa Strategy Pattern (v0.13.1)

Reduzido de 143 → ~30 linhas (79% menos código)

Author: Cristiano Maia + Claude (Anthropic)
Date: 02/01/2026
"""
from typing import Tuple, Dict, Any
from backend.validators import get_validator, validate_answer


class ResponseValidatorSection5:
    """
    Validador de respostas para Seção 5 (Fundada Suspeita).

    REFATORADO (v0.13.1): Usa ValidationFactory centralizado.
    Elimina duplicação de código (~110 linhas) mantendo compatibilidade total.
    """

    @classmethod
    def validate(cls, question_id: str, answer: str, context: Dict[str, Any] = None) -> Tuple[bool, str]:
        """
        Valida resposta usando ValidationFactory.

        Método de classe para compatibilidade com main.py.

        Args:
            question_id: ID da pergunta (ex: "5.1", "5.2", etc.)
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

    def validate_answer(self, question_id: str, answer: str, context: Dict[str, Any] = None) -> Tuple[bool, str]:
        """Alias para validate() para compatibilidade."""
        return self.__class__.validate(question_id, answer, context)
