# -*- coding: utf-8 -*-
"""
Validador de respostas para Seção 3: Campana (Vigilância Velada)
REFATORADO - Usa Strategy Pattern (v0.13.1)

Reduzido de 211 → ~30 linhas (85% menos código)

Author: Cristiano Maia + Claude (Anthropic)
Date: 02/01/2026
"""
from typing import Tuple, Dict, Any
from backend.validators import get_validator, validate_answer


class ResponseValidatorSection3:
    """
    Validador de respostas para Seção 3 (Campana).

    REFATORADO (v0.13.1): Usa ValidationFactory centralizado.
    Elimina duplicação de código (~180 linhas) mantendo compatibilidade total.
    """

    @classmethod
    def validate(cls, question_id: str, answer: str, context: Dict[str, Any] = None) -> Tuple[bool, str]:
        """
        Valida resposta usando ValidationFactory.

        Método de classe para compatibilidade com main.py.

        Args:
            question_id: ID da pergunta (ex: "3.1", "3.2", etc.)
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
