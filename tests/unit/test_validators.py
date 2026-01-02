# -*- coding: utf-8 -*-
"""
Testes Unitários para Validators - Strategy Pattern
BO Inteligente v0.13.1

Author: Cristiano Maia + Claude (Anthropic)
Date: 02/01/2026
"""
import pytest
from backend.validators.base import ValidationResult, ValidationStrategy, CompositeValidator, ConditionalValidator
from backend.validators.strategies import (
    RequiredFieldValidator,
    MinLengthValidator,
    MaxLengthValidator,
    YesNoValidator,
    KeywordsValidator,
    RegexValidator,
    NumericRangeValidator,
    DateTimeValidator,
    VehiclePlateValidator,
    InjuryDescriptionValidator,
    HospitalDestinationValidator,
    MilitaryRankValidator
)
from backend.validators.factory import ValidationFactory, get_validator


# ============================================================================
# TESTES - VALIDATORS BÁSICOS
# ============================================================================

class TestRequiredFieldValidator:
    """Testes para RequiredFieldValidator"""

    def test_valid_answer(self):
        validator = RequiredFieldValidator()
        result = validator.validate("Texto válido", {})
        assert result.valid is True
        assert result.error is None

    def test_empty_answer(self):
        validator = RequiredFieldValidator()
        result = validator.validate("", {})
        assert result.valid is False
        assert "obrigatório" in result.error.lower()

    def test_whitespace_only(self):
        validator = RequiredFieldValidator()
        result = validator.validate("   ", {})
        assert result.valid is False


class TestMinLengthValidator:
    """Testes para MinLengthValidator"""

    def test_valid_length(self):
        validator = MinLengthValidator(10)
        result = validator.validate("Este texto tem mais de 10 caracteres", {})
        assert result.valid is True

    def test_invalid_length(self):
        validator = MinLengthValidator(10)
        result = validator.validate("Curto", {})
        assert result.valid is False
        assert "mínimo 10" in result.error

    def test_exact_length(self):
        validator = MinLengthValidator(5)
        result = validator.validate("exato", {})
        assert result.valid is True


class TestYesNoValidator:
    """Testes para YesNoValidator"""

    @pytest.mark.parametrize("answer", ["SIM", "sim", "S", "s", "YES", "POSITIVO"])
    def test_valid_yes_variants(self, answer):
        validator = YesNoValidator()
        result = validator.validate(answer, {})
        assert result.valid is True

    @pytest.mark.parametrize("answer", ["NÃO", "não", "NAO", "N", "n", "NO", "NEGATIVO"])
    def test_valid_no_variants(self, answer):
        validator = YesNoValidator()
        result = validator.validate(answer, {})
        assert result.valid is True

    def test_invalid_answer(self):
        validator = YesNoValidator()
        result = validator.validate("Talvez", {})
        assert result.valid is False
        assert "SIM ou NÃO" in result.error


class TestKeywordsValidator:
    """Testes para KeywordsValidator"""

    def test_contains_keyword(self):
        validator = KeywordsValidator(["data", "hora", "horário"])
        result = validator.validate("A data da ocorrência foi 10/01/2026", {})
        assert result.valid is True

    def test_missing_keywords(self):
        validator = KeywordsValidator(["data", "hora"])
        result = validator.validate("Aconteceu ontem", {})
        assert result.valid is False

    def test_case_insensitive(self):
        validator = KeywordsValidator(["DATA"], case_sensitive=False)
        result = validator.validate("a data foi ontem", {})
        assert result.valid is True


class TestRegexValidator:
    """Testes para RegexValidator"""

    def test_date_format(self):
        validator = RegexValidator(r'\d{2}/\d{2}/\d{4}', "Formato: DD/MM/AAAA")
        result = validator.validate("10/01/2026", {})
        assert result.valid is True

    def test_invalid_format(self):
        validator = RegexValidator(r'\d{2}/\d{2}/\d{4}')
        result = validator.validate("2026-01-10", {})
        assert result.valid is False


# ============================================================================
# TESTES - COMPOSITE E CONDITIONAL VALIDATORS
# ============================================================================

class TestCompositeValidator:
    """Testes para CompositeValidator"""

    def test_all_pass(self):
        validator = CompositeValidator(
            RequiredFieldValidator(),
            MinLengthValidator(10)
        )
        result = validator.validate("Texto longo o suficiente", {})
        assert result.valid is True

    def test_first_fails(self):
        validator = CompositeValidator(
            RequiredFieldValidator(),
            MinLengthValidator(10)
        )
        result = validator.validate("", {})
        assert result.valid is False
        assert "obrigatório" in result.error.lower()

    def test_second_fails(self):
        validator = CompositeValidator(
            RequiredFieldValidator(),
            MinLengthValidator(10)
        )
        result = validator.validate("Curto", {})
        assert result.valid is False
        assert "mínimo" in result.error.lower()

    def test_empty_composite_raises_error(self):
        with pytest.raises(ValueError):
            CompositeValidator()


class TestConditionalValidator:
    """Testes para ConditionalValidator"""

    def test_condition_true_validates(self):
        validator = ConditionalValidator(
            condition=lambda ctx: ctx.get("previous") == "SIM",
            validator=MinLengthValidator(10)
        )
        result = validator.validate("Texto longo", {"previous": "SIM"})
        assert result.valid is True

    def test_condition_false_skips(self):
        validator = ConditionalValidator(
            condition=lambda ctx: ctx.get("previous") == "SIM",
            validator=MinLengthValidator(10)
        )
        result = validator.validate("X", {"previous": "NÃO"})
        assert result.valid is True  # Skipped, so passes

    def test_condition_true_fails_validation(self):
        validator = ConditionalValidator(
            condition=lambda ctx: ctx.get("previous") == "SIM",
            validator=MinLengthValidator(10)
        )
        result = validator.validate("Curto", {"previous": "SIM"})
        assert result.valid is False


# ============================================================================
# TESTES - VALIDATORS DE DOMÍNIO
# ============================================================================

class TestDateTimeValidator:
    """Testes para DateTimeValidator"""

    def test_date_only(self):
        validator = DateTimeValidator(require_time=False)
        result = validator.validate("10/01/2026", {})
        assert result.valid is True

    def test_date_with_time(self):
        validator = DateTimeValidator(require_time=True)
        result = validator.validate("10/01/2026 às 14:30", {})
        assert result.valid is True

    def test_missing_required_time(self):
        validator = DateTimeValidator(require_time=True)
        result = validator.validate("10/01/2026", {})
        assert result.valid is False
        assert "hora" in result.error.lower()

    def test_invalid_date(self):
        validator = DateTimeValidator()
        result = validator.validate("ontem", {})
        assert result.valid is False


class TestVehiclePlateValidator:
    """Testes para VehiclePlateValidator"""

    @pytest.mark.parametrize("plate", ["ABC1234", "abc1234", "ABC-1234"])
    def test_old_format(self, plate):
        validator = VehiclePlateValidator()
        result = validator.validate(plate, {})
        assert result.valid is True

    @pytest.mark.parametrize("plate", ["ABC1D23", "abc1d23", "ABC-1D23"])
    def test_mercosul_format(self, plate):
        validator = VehiclePlateValidator()
        result = validator.validate(plate, {})
        assert result.valid is True

    def test_invalid_format(self):
        validator = VehiclePlateValidator()
        result = validator.validate("12345", {})
        assert result.valid is False


class TestInjuryDescriptionValidator:
    """Testes para InjuryDescriptionValidator"""

    def test_valid_description(self):
        validator = InjuryDescriptionValidator()
        result = validator.validate("Corte profundo no braço esquerdo", {})
        assert result.valid is True

    def test_missing_injury_type(self):
        validator = InjuryDescriptionValidator()
        result = validator.validate("No braço esquerdo", {})
        assert result.valid is False
        assert "tipo de lesão" in result.error.lower()

    def test_missing_body_part(self):
        validator = InjuryDescriptionValidator()
        result = validator.validate("Corte profundo", {})
        assert result.valid is False
        assert "localização" in result.error.lower()


class TestHospitalDestinationValidator:
    """Testes para HospitalDestinationValidator"""

    @pytest.mark.parametrize("answer", [
        "Hospital Municipal de Contagem",
        "UPA Centro",
        "Pronto Socorro",
        "Não foi conduzido",
        "Recusou atendimento"
    ])
    def test_valid_destinations(self, answer):
        validator = HospitalDestinationValidator()
        result = validator.validate(answer, {})
        assert result.valid is True

    def test_invalid_destination(self):
        validator = HospitalDestinationValidator()
        result = validator.validate("Foi embora", {})
        assert result.valid is False


class TestMilitaryRankValidator:
    """Testes para MilitaryRankValidator"""

    @pytest.mark.parametrize("answer", [
        "O Sargento Silva viu o suspeito arremessando a sacola",
        "O Cabo Rodrigues ouviu duas descargas",
        "O Soldado Faria visualizou o suspeito",
        "Sgt Alves tinha visão desobstruída",
        "O Tenente Costa coordenou a operação"
    ])
    def test_valid_with_rank(self, answer):
        validator = MilitaryRankValidator()
        result = validator.validate(answer, {})
        assert result.valid is True

    @pytest.mark.parametrize("answer", [
        "Silva viu o suspeito",
        "O policial observou",
        "Vimos o indivíduo"
    ])
    def test_missing_rank(self, answer):
        validator = MilitaryRankValidator()
        result = validator.validate(answer, {})
        assert result.valid is False
        assert "GRADUAÇÃO" in result.error


# ============================================================================
# TESTES - VALIDATION FACTORY
# ============================================================================

class TestValidationFactory:
    """Testes para ValidationFactory"""

    def test_get_validator_section1(self):
        factory = ValidationFactory()
        validator = factory.get_validator("1.1")
        assert validator is not None
        assert isinstance(validator, ValidationStrategy)

    def test_validate_answer_valid(self):
        factory = ValidationFactory()
        result = factory.validate_answer("1.1", "10/01/2026 às 14:30", {})
        assert result["valid"] is True

    def test_validate_answer_invalid(self):
        factory = ValidationFactory()
        result = factory.validate_answer("1.1", "", {})
        assert result["valid"] is False
        assert "error" in result

    def test_conditional_validation_section2(self):
        factory = ValidationFactory()

        # 2.1 = NÃO -> 2.2 deve passar (skip)
        result = factory.validate_answer("2.2", "", {"2.1": "NÃO"})
        assert result["valid"] is True

        # 2.1 = SIM -> 2.2 deve falhar se vazio
        result = factory.validate_answer("2.2", "", {"2.1": "SIM"})
        assert result["valid"] is False

    def test_fallback_validator(self):
        factory = ValidationFactory()
        validator = factory.get_validator("999.999")  # Não existe
        assert isinstance(validator, RequiredFieldValidator)

    def test_global_get_validator(self):
        validator = get_validator("1.1")
        assert validator is not None
        assert isinstance(validator, ValidationStrategy)


# ============================================================================
# TESTES - INTEGRAÇÃO COM CONTEXTO
# ============================================================================

class TestValidationWithContext:
    """Testes de validação com contexto completo"""

    def test_section1_flow(self):
        factory = ValidationFactory()
        context = {}

        # 1.1: Data/hora
        result = factory.validate_answer("1.1", "10/01/2026 às 14:30", context)
        assert result["valid"] is True
        context["1.1"] = "10/01/2026 às 14:30"

        # 1.5: Deslocamento = SIM
        result = factory.validate_answer("1.5", "SIM", context)
        assert result["valid"] is True
        context["1.5"] = "SIM"

        # 1.5.1: Local de partida (deve validar pois 1.5=SIM)
        result = factory.validate_answer("1.5.1", "Base da PM", context)
        assert result["valid"] is True

    def test_section2_skip(self):
        factory = ValidationFactory()
        context = {"2.1": "NÃO"}

        # 2.2 deve passar (skip) porque 2.1=NÃO
        result = factory.validate_answer("2.2", "", context)
        assert result["valid"] is True

        # 2.3 também deve passar (skip)
        result = factory.validate_answer("2.3", "", context)
        assert result["valid"] is True
