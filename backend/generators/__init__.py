"""
Generators Package - Template Method Pattern para geração de texto do BO

Este package implementa o padrão Template Method para consolidar a lógica
duplicada de geração de texto em 8 métodos diferentes do llm_service.py.

Estrutura:
- base.py: Classe abstrata BaseSectionGenerator com template method
- section1.py a section8.py: Implementações específicas de cada seção

Uso:
    from generators import Section1Generator, Section2Generator

    generator = Section1Generator(gemini_model, groq_client)
    text = generator.generate(section_data, provider="groq")
"""

from .base import BaseSectionGenerator
from .section1 import Section1Generator
from .section2 import Section2Generator
from .section3 import Section3Generator
from .section4 import Section4Generator

__all__ = [
    'BaseSectionGenerator',
    'Section1Generator',
    'Section2Generator',
    'Section3Generator',
    'Section4Generator',
]
