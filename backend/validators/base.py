# -*- coding: utf-8 -*-
"""
Base Validator Classes - Strategy Pattern
BO Inteligente v0.13.1

Define a interface base para validadores usando Strategy Pattern.
Cada validador é uma estratégia que pode ser composta e reutilizada.

Author: Cristiano Maia + Claude (Anthropic)
Date: 02/01/2026
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """
    Resultado de uma validação.

    Attributes:
        valid: Se a validação passou
        error: Mensagem de erro (None se valid=True)
        field: Campo que foi validado (opcional)
        value: Valor que foi validado (opcional, para debug)
    """
    valid: bool
    error: Optional[str] = None
    field: Optional[str] = None
    value: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário (compatibilidade com código legado)"""
        result = {"valid": self.valid}
        if self.error:
            result["error"] = self.error
        if self.field:
            result["field"] = self.field
        return result


class ValidationStrategy(ABC):
    """
    Strategy Pattern para validação de respostas.

    Classe abstrata que define a interface comum para todos os validadores.
    Cada validador implementa uma lógica específica de validação.

    Exemplo:
        class RequiredFieldValidator(ValidationStrategy):
            def validate(self, answer: str, context: dict) -> ValidationResult:
                if not answer or not answer.strip():
                    return ValidationResult(valid=False, error="Campo obrigatório")
                return ValidationResult(valid=True)
    """

    @abstractmethod
    def validate(self, answer: str, context: Dict[str, Any]) -> ValidationResult:
        """
        Valida uma resposta baseado em critérios específicos.

        Args:
            answer: Resposta fornecida pelo usuário
            context: Contexto adicional (respostas anteriores, configurações, etc.)

        Returns:
            ValidationResult com o resultado da validação
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class CompositeValidator(ValidationStrategy):
    """
    Combina múltiplos validators usando lógica AND.

    Todos os validators devem passar para que a validação seja bem-sucedida.
    Para quando encontra o primeiro erro (fail-fast).

    Exemplo:
        validator = CompositeValidator(
            RequiredFieldValidator(),
            MinLengthValidator(10),
            KeywordsValidator(["data", "hora"])
        )
    """

    def __init__(self, *validators: ValidationStrategy):
        """
        Args:
            *validators: Lista de validators a serem aplicados em ordem
        """
        if not validators:
            raise ValueError("CompositeValidator precisa de pelo menos um validator")
        self.validators: List[ValidationStrategy] = list(validators)

    def validate(self, answer: str, context: Dict[str, Any]) -> ValidationResult:
        """
        Executa todos os validators em sequência.
        Para no primeiro erro encontrado.

        Args:
            answer: Resposta a validar
            context: Contexto da validação

        Returns:
            ValidationResult do primeiro validator que falhar, ou sucesso se todos passarem
        """
        for validator in self.validators:
            result = validator.validate(answer, context)
            if not result.valid:
                return result  # Fail-fast

        return ValidationResult(valid=True)

    def __repr__(self) -> str:
        validators_str = ", ".join(repr(v) for v in self.validators)
        return f"CompositeValidator({validators_str})"


class ConditionalValidator(ValidationStrategy):
    """
    Aplica um validator apenas se uma condição for atendida.

    Útil para validações que dependem de respostas anteriores.

    Exemplo:
        # Só valida placa se resposta 2.1 for "SIM"
        validator = ConditionalValidator(
            condition=lambda ctx: ctx.get("2.1", "").upper() == "SIM",
            validator=VehiclePlateValidator(),
            skip_message="Validação pulada (não se aplica)"
        )
    """

    def __init__(
        self,
        condition: callable,
        validator: ValidationStrategy,
        skip_message: Optional[str] = None
    ):
        """
        Args:
            condition: Função que recebe context e retorna bool
            validator: Validator a aplicar se condição for True
            skip_message: Mensagem opcional quando validação é pulada
        """
        self.condition = condition
        self.validator = validator
        self.skip_message = skip_message

    def validate(self, answer: str, context: Dict[str, Any]) -> ValidationResult:
        """
        Executa validator apenas se condição for atendida.

        Args:
            answer: Resposta a validar
            context: Contexto da validação

        Returns:
            ValidationResult do validator interno, ou sucesso se condição não for atendida
        """
        if self.condition(context):
            return self.validator.validate(answer, context)
        else:
            # Condição não atendida - validação passa automaticamente
            return ValidationResult(valid=True)

    def __repr__(self) -> str:
        return f"ConditionalValidator(validator={repr(self.validator)})"
