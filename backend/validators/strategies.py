# -*- coding: utf-8 -*-
"""
Validation Strategies - Concrete Implementations
BO Inteligente v0.13.1

Implementações concretas de validadores reutilizáveis.

Author: Cristiano Maia + Claude (Anthropic)
Date: 02/01/2026
"""
import re
from typing import Dict, Any, List, Optional
from backend.validators.base import ValidationStrategy, ValidationResult


# ============================================================================
# VALIDATORS BÁSICOS
# ============================================================================

class RequiredFieldValidator(ValidationStrategy):
    """
    Valida que o campo não está vazio.

    Exemplo:
        validator = RequiredFieldValidator()
        result = validator.validate("", {})  # valid=False
        result = validator.validate("Texto", {})  # valid=True
    """

    def __init__(self, error_message: str = "Campo obrigatório"):
        self.error_message = error_message

    def validate(self, answer: str, context: Dict[str, Any]) -> ValidationResult:
        if not answer or not answer.strip():
            return ValidationResult(valid=False, error=self.error_message)
        return ValidationResult(valid=True)


class MinLengthValidator(ValidationStrategy):
    """
    Valida comprimento mínimo da resposta.

    Exemplo:
        validator = MinLengthValidator(10)
        result = validator.validate("Curto", {})  # valid=False
        result = validator.validate("Resposta suficientemente longa", {})  # valid=True
    """

    def __init__(self, min_length: int, error_message: Optional[str] = None):
        self.min_length = min_length
        self.error_message = error_message or f"Resposta muito curta (mínimo {min_length} caracteres)"

    def validate(self, answer: str, context: Dict[str, Any]) -> ValidationResult:
        if len(answer.strip()) < self.min_length:
            return ValidationResult(valid=False, error=self.error_message)
        return ValidationResult(valid=True)


class MaxLengthValidator(ValidationStrategy):
    """
    Valida comprimento máximo da resposta.

    Exemplo:
        validator = MaxLengthValidator(100)
        result = validator.validate("x" * 150, {})  # valid=False
    """

    def __init__(self, max_length: int, error_message: Optional[str] = None):
        self.max_length = max_length
        self.error_message = error_message or f"Resposta muito longa (máximo {max_length} caracteres)"

    def validate(self, answer: str, context: Dict[str, Any]) -> ValidationResult:
        if len(answer.strip()) > self.max_length:
            return ValidationResult(valid=False, error=self.error_message)
        return ValidationResult(valid=True)


class YesNoValidator(ValidationStrategy):
    """
    Valida respostas de sim/não.

    Aceita variantes: SIM/NÃO, S/N, YES/NO, POSITIVO/NEGATIVO

    Exemplo:
        validator = YesNoValidator()
        result = validator.validate("SIM", {})  # valid=True
        result = validator.validate("Talvez", {})  # valid=False
    """

    VALID_ANSWERS = [
        "SIM", "S", "YES", "Y", "POSITIVO", "AFIRMATIVO",
        "NÃO", "NAO", "N", "NO", "NEGATIVO"
    ]

    def __init__(self, error_message: str = "Responda SIM ou NÃO"):
        self.error_message = error_message

    def validate(self, answer: str, context: Dict[str, Any]) -> ValidationResult:
        answer_upper = answer.strip().upper()
        if answer_upper not in self.VALID_ANSWERS:
            return ValidationResult(valid=False, error=self.error_message)
        return ValidationResult(valid=True)


class KeywordsValidator(ValidationStrategy):
    """
    Valida que a resposta contém pelo menos uma das keywords esperadas.

    Útil para verificar se o usuário mencionou informações críticas.

    Exemplo:
        validator = KeywordsValidator(["data", "hora", "horário"])
        result = validator.validate("Aconteceu no dia 10/01/2026", {})  # valid=True (contém "dia")
    """

    def __init__(
        self,
        keywords: List[str],
        case_sensitive: bool = False,
        error_message: Optional[str] = None
    ):
        self.keywords = keywords
        self.case_sensitive = case_sensitive
        self.error_message = error_message or f"Resposta deve conter ao menos uma das informações: {', '.join(keywords)}"

    def validate(self, answer: str, context: Dict[str, Any]) -> ValidationResult:
        answer_check = answer if self.case_sensitive else answer.lower()

        for keyword in self.keywords:
            keyword_check = keyword if self.case_sensitive else keyword.lower()
            if keyword_check in answer_check:
                return ValidationResult(valid=True)

        return ValidationResult(valid=False, error=self.error_message)


class RegexValidator(ValidationStrategy):
    """
    Valida resposta usando expressão regular.

    Exemplo:
        # Validar formato DD/MM/AAAA
        validator = RegexValidator(
            pattern=r'\d{2}/\d{2}/\d{4}',
            error_message="Formato esperado: DD/MM/AAAA"
        )
    """

    def __init__(self, pattern: str, error_message: str = "Formato inválido"):
        self.pattern = re.compile(pattern)
        self.error_message = error_message

    def validate(self, answer: str, context: Dict[str, Any]) -> ValidationResult:
        if not self.pattern.search(answer):
            return ValidationResult(valid=False, error=self.error_message)
        return ValidationResult(valid=True)


class NumericRangeValidator(ValidationStrategy):
    """
    Valida que resposta contém número dentro de um range.

    Exemplo:
        validator = NumericRangeValidator(min_value=1, max_value=100)
        result = validator.validate("50", {})  # valid=True
        result = validator.validate("150", {})  # valid=False
    """

    def __init__(
        self,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        error_message: Optional[str] = None
    ):
        self.min_value = min_value
        self.max_value = max_value

        if error_message:
            self.error_message = error_message
        elif min_value is not None and max_value is not None:
            self.error_message = f"Valor deve estar entre {min_value} e {max_value}"
        elif min_value is not None:
            self.error_message = f"Valor deve ser maior ou igual a {min_value}"
        elif max_value is not None:
            self.error_message = f"Valor deve ser menor ou igual a {max_value}"
        else:
            self.error_message = "Valor numérico inválido"

    def validate(self, answer: str, context: Dict[str, Any]) -> ValidationResult:
        try:
            # Extrair primeiro número da resposta
            numbers = re.findall(r'-?\d+\.?\d*', answer)
            if not numbers:
                return ValidationResult(valid=False, error="Nenhum valor numérico encontrado")

            value = float(numbers[0])

            if self.min_value is not None and value < self.min_value:
                return ValidationResult(valid=False, error=self.error_message)

            if self.max_value is not None and value > self.max_value:
                return ValidationResult(valid=False, error=self.error_message)

            return ValidationResult(valid=True)

        except (ValueError, IndexError):
            return ValidationResult(valid=False, error="Valor numérico inválido")


# ============================================================================
# VALIDATORS DE DOMÍNIO (BO-ESPECÍFICOS)
# ============================================================================

class DateTimeValidator(ValidationStrategy):
    """
    Valida data e hora no formato brasileiro.
    Restaurado v0.13.2: Validação completa de hora/minuto inválidos.

    Aceita formatos flexíveis:
    - "10/01/2026 às 14:30"
    - "10/01/2026, 14h30min"
    - "10/01, 14h30" (ano opcional)
    - "14h30, dia 10/01" (ordem flexível)
    - "15 de janeiro de 2026, 14h30" (nome do mês)

    Rejeita:
    - Hora inválida (26h)
    - Minuto inválido (61min)

    Exemplo:
        validator = DateTimeValidator(require_time=True)
        result = validator.validate("10/01/2026 às 14:30", {})  # valid=True
        result = validator.validate("03/01, 17h41", {})  # valid=True
        result = validator.validate("03/01/2026, 26h41", {})  # valid=False (hora > 23)
    """

    # Data flexível: DD/MM ou DD/MM/AAAA
    DATE_PATTERN = r'\d{1,2}/\d{1,2}'
    # Nomes de meses em português
    MONTH_NAMES = [
        'janeiro', 'fevereiro', 'março', 'marco', 'abril', 'maio',
        'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
    ]

    def __init__(
        self,
        require_time: bool = False,
        error_message: Optional[str] = None
    ):
        self.require_time = require_time
        self.error_message = error_message or "Faltou a data. Ex: 03/01/2026, 17h30"

    def validate(self, answer: str, context: Dict[str, Any]) -> ValidationResult:
        # Data: DD/MM ou nome do mês
        has_date = bool(re.search(self.DATE_PATTERN, answer)) or \
                   any(mes in answer.lower() for mes in self.MONTH_NAMES)

        if not has_date:
            return ValidationResult(valid=False, error=self.error_message)

        # Hora: extrair valores para validar
        time_match = re.search(r'(\d{1,2})[h:](\d{0,2})', answer)

        if self.require_time and not time_match:
            return ValidationResult(valid=False, error="Faltou o horário. Ex: 17h30 ou 17:30")

        # Validar hora (0-23) e minuto (0-59)
        if time_match:
            hour = int(time_match.group(1))
            minute_str = time_match.group(2)
            minute = int(minute_str) if minute_str else 0

            if hour > 23:
                return ValidationResult(
                    valid=False,
                    error=f"Hora inválida ({hour}h). Use formato 24h (0-23). Ex: 21h03"
                )
            if minute > 59:
                return ValidationResult(
                    valid=False,
                    error=f"Minuto inválido ({minute}min). Use 0-59. Ex: 21h03"
                )

        return ValidationResult(valid=True)


class VehiclePlateValidator(ValidationStrategy):
    """
    Valida placa de veículo (formato Mercosul ou antigo).

    Formatos aceitos:
    - ABC1234 (antigo)
    - ABC1D23 (Mercosul)

    Exemplo:
        validator = VehiclePlateValidator()
        result = validator.validate("ABC1234", {})  # valid=True
        result = validator.validate("ABC1D23", {})  # valid=True
    """

    OLD_PATTERN = r'[A-Z]{3}\d{4}'
    MERCOSUL_PATTERN = r'[A-Z]{3}\d[A-Z]\d{2}'

    def validate(self, answer: str, context: Dict[str, Any]) -> ValidationResult:
        answer_upper = answer.strip().upper()

        # Remover hífens e espaços
        answer_clean = answer_upper.replace("-", "").replace(" ", "")

        old_match = re.search(self.OLD_PATTERN, answer_clean)
        mercosul_match = re.search(self.MERCOSUL_PATTERN, answer_clean)

        if old_match or mercosul_match:
            return ValidationResult(valid=True)

        return ValidationResult(
            valid=False,
            error="Formato de placa inválido (esperado: ABC1234 ou ABC1D23)"
        )


class InjuryDescriptionValidator(ValidationStrategy):
    """
    Valida descrição de lesão corporal (Seção 5).

    Verifica que a descrição menciona:
    - Tipo de lesão (corte, hematoma, escoriação, etc.)
    - Localização anatômica (braço, cabeça, perna, etc.)

    Exemplo:
        validator = InjuryDescriptionValidator()
        result = validator.validate("Corte no braço esquerdo", {})  # valid=True
    """

    INJURY_TYPES = [
        "corte", "hematoma", "escoriação", "fratura", "ferimento",
        "perfuração", "queimadura", "contusão", "arranhão", "lesão"
    ]

    BODY_PARTS = [
        "cabeça", "rosto", "olho", "nariz", "boca", "pescoço",
        "braço", "antebraço", "mão", "dedo", "perna", "coxa",
        "joelho", "pé", "tórax", "abdômen", "costas", "ombro"
    ]

    def validate(self, answer: str, context: Dict[str, Any]) -> ValidationResult:
        answer_lower = answer.lower()

        has_injury_type = any(injury in answer_lower for injury in self.INJURY_TYPES)
        has_body_part = any(part in answer_lower for part in self.BODY_PARTS)

        if not has_injury_type:
            return ValidationResult(
                valid=False,
                error="Descreva o tipo de lesão (corte, hematoma, escoriação, etc.)"
            )

        if not has_body_part:
            return ValidationResult(
                valid=False,
                error="Informe a localização da lesão (braço, cabeça, perna, etc.)"
            )

        return ValidationResult(valid=True)


class HospitalDestinationValidator(ValidationStrategy):
    """
    Valida destino hospitalar da vítima (Seção 5).

    Verifica que a resposta menciona nome do hospital/UPA ou "não foi conduzido".

    Exemplo:
        validator = HospitalDestinationValidator()
        result = validator.validate("Hospital Municipal de Contagem", {})  # valid=True
        result = validator.validate("Não foi conduzido", {})  # valid=True
    """

    VALID_KEYWORDS = [
        "hospital", "upa", "pronto socorro", "pronto-socorro",
        "samu", "ambulância", "não foi conduzido", "recusou atendimento"
    ]

    def validate(self, answer: str, context: Dict[str, Any]) -> ValidationResult:
        answer_lower = answer.lower()

        has_valid_keyword = any(keyword in answer_lower for keyword in self.VALID_KEYWORDS)

        if not has_valid_keyword:
            return ValidationResult(
                valid=False,
                error="Informe o hospital/UPA de destino ou indique que não foi conduzido"
            )

        return ValidationResult(valid=True)


class MilitaryRankValidator(ValidationStrategy):
    """
    Valida presença de graduação militar (Seções 3, 4, 5).

    Verifica que a resposta menciona graduação militar + nome do policial.

    Exemplo:
        validator = MilitaryRankValidator()
        result = validator.validate("O Sargento Silva viu...", {})  # valid=True
        result = validator.validate("Silva viu...", {})  # valid=False
    """

    MILITARY_RANKS = [
        "sargento", "soldado", "cabo", "tenente", "capitão",
        "sgt", "sd", "cb", "ten", "cap", "major", "coronel"
    ]

    def validate(self, answer: str, context: Dict[str, Any]) -> ValidationResult:
        answer_lower = answer.lower()

        has_rank = any(rank in answer_lower for rank in self.MILITARY_RANKS)

        if not has_rank:
            return ValidationResult(
                valid=False,
                error="Informe a GRADUAÇÃO + nome do policial (ex: 'O Sargento Silva...')"
            )

        return ValidationResult(valid=True)
