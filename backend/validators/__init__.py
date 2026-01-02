# -*- coding: utf-8 -*-
"""
Validators Package - Strategy Pattern Implementation
BO Inteligente v0.13.1

Author: Cristiano Maia + Claude (Anthropic)
Date: 02/01/2026
"""
from backend.validators.base import ValidationStrategy, ValidationResult, CompositeValidator, ConditionalValidator
from backend.validators.strategies import (
    RequiredFieldValidator,
    MinLengthValidator,
    YesNoValidator,
    KeywordsValidator
)
from backend.validators.factory import get_validator, validate_answer, ValidationFactory

__all__ = [
    'ValidationStrategy',
    'ValidationResult',
    'CompositeValidator',
    'ConditionalValidator',
    'RequiredFieldValidator',
    'MinLengthValidator',
    'YesNoValidator',
    'KeywordsValidator',
    'get_validator',
    'validate_answer',
    'ValidationFactory'
]
