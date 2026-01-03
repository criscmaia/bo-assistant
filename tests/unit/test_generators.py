"""
Testes unitários para backend/generators/

Valida:
- Inicialização dos geradores
- Skip logic (seções 2-4)
- Construção de prompts
- Tratamento de erros
"""
import pytest
from unittest.mock import Mock, MagicMock
import sys
import os

# Adicionar backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.generators import (
    BaseSectionGenerator,
    Section1Generator,
    Section2Generator,
    Section3Generator,
    Section4Generator
)


class TestBaseSectionGenerator:
    """Testes para classe base"""

    def test_abstract_class_cannot_be_instantiated(self):
        """BaseSectionGenerator é abstrata e não pode ser instanciada"""
        with pytest.raises(TypeError):
            BaseSectionGenerator(None, None)

    def test_provider_validation(self):
        """Testa validação de provider inválido"""

        # Criar subclasse concreta para testar
        class ConcreteGenerator(BaseSectionGenerator):
            def _build_prompt(self, section_data):
                return "test prompt"

        generator = ConcreteGenerator(None, None)

        with pytest.raises(ValueError, match="Provider 'invalid' não suportado"):
            generator.generate({"test": "data"}, provider="invalid")


class TestSection1Generator:
    """Testes para gerador da seção 1"""

    def test_initialization(self):
        """Testa inicialização do gerador"""
        mock_gemini = Mock()
        mock_groq = Mock()

        generator = Section1Generator(mock_gemini, mock_groq)

        assert generator.gemini_model == mock_gemini
        assert generator.groq_client == mock_groq

    def test_no_skip_logic(self):
        """Seção 1 nunca tem skip"""
        generator = Section1Generator(None, None)

        # Testar várias respostas - nenhuma deve causar skip
        test_cases = [
            {},
            {"1.1": "NÃO"},
            {"1.1": "SIM"},
            {"1.1": "22/03/2025 21:11"},
        ]

        for data in test_cases:
            assert generator._should_skip(data) == False

    def test_datetime_enrichment(self):
        """Testa enriquecimento de data/hora"""
        generator = Section1Generator(None, None)

        # Data no formato DD/MM/YYYY HH:MM (22/03/2025 é sábado)
        result = generator._enrich_datetime("22/03/2025 21:11")

        assert "sábado" in result.lower()
        assert "22 de março de 2025" in result.lower()
        assert "21h11min" in result.lower()

    def test_datetime_enrichment_handles_invalid_date(self):
        """Testa tratamento de data inválida"""
        generator = Section1Generator(None, None)

        # Data inválida deve retornar original
        invalid_date = "data inválida"
        result = generator._enrich_datetime(invalid_date)

        assert result == invalid_date

    def test_build_prompt_includes_all_questions(self):
        """Testa que prompt inclui todas as perguntas da seção 1"""
        generator = Section1Generator(None, None)

        section_data = {
            "1.1": "22/03/2025 21:11",
            "1.2": "Sgt Silva, Cb Almeida",
            "1.3": "COPOM",
            "1.6": "Rua das Flores, 123"
        }

        prompt = generator._build_prompt(section_data)

        # Verificar elementos chave no prompt (22/03/2025 é sábado)
        assert "sábado, 22 de março de 2025" in prompt
        assert "Sgt Silva, Cb Almeida" in prompt
        assert "COPOM" in prompt
        assert "Rua das Flores, 123" in prompt
        assert "SEÇÃO 1" in prompt
        assert "CONTEXTO DA OCORRÊNCIA" in prompt


class TestSection2Generator:
    """Testes para gerador da seção 2"""

    def test_skip_logic_when_no_vehicle(self):
        """Testa skip quando não havia veículo"""
        generator = Section2Generator(None, None)

        test_cases = [
            {"2.1": "NÃO"},
            {"2.1": "NAO"},
            {"2.1": "N"},
            {"2.1": "NENHUM"},
            {"2.1": "NEGATIVO"},
            {"2.1": "  nÃo  "},  # Com espaços e case diferente
        ]

        for data in test_cases:
            assert generator._should_skip(data) == True

    def test_no_skip_when_vehicle_present(self):
        """Testa que não skip quando havia veículo"""
        generator = Section2Generator(None, None)

        test_cases = [
            {"2.1": "SIM"},
            {"2.1": "sim"},
            {"2.1": "S"},
            {"2.1": "AFIRMATIVO"},
            {"2.1": "Sim, um Gol branco"},
        ]

        for data in test_cases:
            assert generator._should_skip(data) == False

    def test_generate_returns_empty_when_skip(self):
        """Testa que generate() retorna vazio quando skip"""
        generator = Section2Generator(None, None)

        result = generator.generate({"2.1": "NÃO"}, provider="groq")

        assert result == ""

    def test_build_prompt_includes_vehicle_data(self):
        """Testa que prompt inclui dados do veículo"""
        generator = Section2Generator(None, None)

        section_data = {
            "2.1": "SIM",
            "2.2": "Rua X",
            "2.3": "VW Gol branco ABC-1234"
        }

        prompt = generator._build_prompt(section_data)

        assert "SEÇÃO 2" in prompt
        assert "VEÍCULO" in prompt.upper() or "Abordagem" in prompt
        assert "Rua X" in prompt
        assert "VW Gol branco ABC-1234" in prompt


class TestSection3Generator:
    """Testes para gerador da seção 3"""

    def test_skip_logic_when_no_surveillance(self):
        """Testa skip quando não houve campana"""
        generator = Section3Generator(None, None)

        test_cases = [
            {"3.1": "NÃO"},
            {"3.1": "NAO"},
            {"3.1": "N"},
        ]

        for data in test_cases:
            assert generator._should_skip(data) == True

    def test_no_skip_when_surveillance_occurred(self):
        """Testa que não skip quando houve campana"""
        generator = Section3Generator(None, None)

        assert generator._should_skip({"3.1": "SIM"}) == False

    def test_build_prompt_includes_surveillance_data(self):
        """Testa que prompt inclui dados da campana"""
        generator = Section3Generator(None, None)

        section_data = {
            "3.1": "SIM",
            "3.2": "Esquina da Rua A com Rua B",
            "3.5": "15 minutos"
        }

        prompt = generator._build_prompt(section_data)

        assert "SEÇÃO 3" in prompt
        assert "CAMPANA" in prompt.upper() or "Vigilância" in prompt
        assert "Esquina da Rua A com Rua B" in prompt
        assert "15 minutos" in prompt


class TestSection4Generator:
    """Testes para gerador da seção 4"""

    def test_skip_logic_when_no_home_entry(self):
        """Testa skip quando não houve entrada em domicílio"""
        generator = Section4Generator(None, None)

        test_cases = [
            {"4.1": "NÃO"},
            {"4.1": "NAO"},
            {"4.1": "NEGATIVO"},
        ]

        for data in test_cases:
            assert generator._should_skip(data) == True

    def test_no_skip_when_home_entry_occurred(self):
        """Testa que não skip quando houve entrada"""
        generator = Section4Generator(None, None)

        assert generator._should_skip({"4.1": "SIM"}) == False

    def test_build_prompt_includes_entry_data(self):
        """Testa que prompt inclui dados da entrada"""
        generator = Section4Generator(None, None)

        section_data = {
            "4.1": "SIM",
            "4.2": "Visualização de embalagem pela janela",
            "4.4": "Porta estava aberta"
        }

        prompt = generator._build_prompt(section_data)

        assert "SEÇÃO 4" in prompt
        assert "Entrada em Domicílio" in prompt or "DOMICÍLIO" in prompt.upper()
        assert "Visualização de embalagem pela janela" in prompt
        assert "Porta estava aberta" in prompt


class TestIntegration:
    """Testes de integração entre geradores"""

    def test_all_generators_implement_base_interface(self):
        """Testa que todos os geradores implementam interface base"""
        generators = [
            Section1Generator,
            Section2Generator,
            Section3Generator,
            Section4Generator,
        ]

        for GeneratorClass in generators:
            # Verificar que é subclasse de BaseSectionGenerator
            assert issubclass(GeneratorClass, BaseSectionGenerator)

            # Verificar que implementa _build_prompt
            generator = GeneratorClass(None, None)
            assert hasattr(generator, '_build_prompt')
            assert callable(generator._build_prompt)

    def test_all_generators_have_generate_method(self):
        """Testa que todos os geradores têm método generate()"""
        generators = [
            Section1Generator(None, None),
            Section2Generator(None, None),
            Section3Generator(None, None),
            Section4Generator(None, None),
        ]

        for generator in generators:
            assert hasattr(generator, 'generate')
            assert callable(generator.generate)


# Executar testes se rodado diretamente
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
