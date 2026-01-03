"""
Dispatcher centralizado para validadores de seções

Resolve duplicação de 42 linhas de elif repetidas 3x em main.py:
- /chat endpoint (linhas 343-385)
- /sync endpoint (linhas 873-888)
- /update_answer endpoint (validação implícita)

Uso:
    from validator_dispatcher import get_validator

    validator = get_validator(section_number)
    is_valid, error_message = validator.validate(step, answer)
"""

from typing import Tuple, Type
import sys
import os

# Add project root to sys.path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Backend imports
from backend.validator import ResponseValidator
from backend.validator_section2 import ResponseValidatorSection2
from backend.validator_section3 import ResponseValidatorSection3
from backend.validator_section4 import ResponseValidatorSection4
from backend.validator_section5 import ResponseValidatorSection5
from backend.validator_section6 import ResponseValidatorSection6
from backend.validator_section7 import ResponseValidatorSection7
from backend.validator_section8 import ResponseValidatorSection8


# Mapa de seção -> classe de validador
VALIDATOR_MAP = {
    1: ResponseValidator,
    2: ResponseValidatorSection2,
    3: ResponseValidatorSection3,
    4: ResponseValidatorSection4,
    5: ResponseValidatorSection5,
    6: ResponseValidatorSection6,
    7: ResponseValidatorSection7,
    8: ResponseValidatorSection8,
}


def get_validator(section: int) -> Type:
    """
    Retorna a classe de validador para a seção especificada.

    Args:
        section: Número da seção (1-8)

    Returns:
        Classe de validador correspondente

    Raises:
        ValueError: Se a seção não for suportada

    Example:
        >>> validator = get_validator(1)
        >>> is_valid, error = validator.validate("1.1", "22/03/2025 21:11")
    """
    validator_class = VALIDATOR_MAP.get(section)

    if validator_class is None:
        raise ValueError(
            f"Seção {section} não possui validador. "
            f"Seções suportadas: {list(VALIDATOR_MAP.keys())}"
        )

    return validator_class


def validate_answer(section: int, step: str, answer: str) -> Tuple[bool, str]:
    """
    Valida uma resposta usando o validador apropriado.

    Função de conveniência que combina get_validator() + validate().

    Args:
        section: Número da seção (1-8)
        step: ID da pergunta (ex: "1.1", "2.3")
        answer: Resposta do usuário

    Returns:
        Tupla (is_valid, error_message)
        - is_valid: True se resposta válida
        - error_message: String vazia se válida, mensagem de erro caso contrário

    Example:
        >>> is_valid, error = validate_answer(1, "1.1", "22/03/2025 21:11")
        >>> if not is_valid:
        ...     print(f"Erro: {error}")
    """
    validator = get_validator(section)
    return validator.validate(step, answer)
