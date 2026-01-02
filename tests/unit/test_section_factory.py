# -*- coding: utf-8 -*-
"""
Testes Unitários: section_factory.py

Valida o padrão Factory para criação de seções.

Executar: python -m pytest tests/unit/test_section_factory.py -v
"""
import sys
import os
import pytest

# Adicionar diretório raiz ao path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, root_dir)

from backend.section_factory import (
    create_section_handler,
    get_section_metadata,
    Section1Handler,
    Section2Handler,
    Section6Handler,
    Section8Handler,
    SECTION_HANDLERS
)


class TestFactoryCreation:
    """Testes de criação via Factory"""

    def test_create_all_sections(self):
        """Deve criar handlers para todas as 8 seções"""
        for section_num in range(1, 9):
            handler = create_section_handler("session-123", "BO-001", section_num)
            assert handler is not None
            assert handler.section_number == section_num

    def test_invalid_section_raises_error(self):
        """Deve levantar ValueError para seção inválida"""
        with pytest.raises(ValueError, match="Seção 0 inválida"):
            create_section_handler("session-123", "BO-001", 0)

        with pytest.raises(ValueError, match="Seção 9 inválida"):
            create_section_handler("session-123", "BO-001", 9)

    def test_handler_attributes(self):
        """Deve inicializar atributos corretamente"""
        handler = create_section_handler("sess-456", "BO-002", 3)
        assert handler.session_id == "sess-456"
        assert handler.bo_id == "BO-002"
        assert handler.section_number == 3


class TestAutoAnswerBehavior:
    """Testes do comportamento de auto-resposta"""

    def test_section1_no_auto_answer(self):
        """Seção 1 não deve ter auto-resposta"""
        handler = Section1Handler("sess", "bo", 1)
        assert handler.has_auto_answer() is False
        assert handler.get_auto_answer_step() is None

    def test_section2_has_auto_answer(self):
        """Seção 2 deve ter auto-resposta em 2.1"""
        handler = Section2Handler("sess", "bo", 2)
        assert handler.has_auto_answer() is True
        assert handler.get_auto_answer_step() == "2.1"

    def test_section6_no_auto_answer(self):
        """Seção 6 NÃO deve ter auto-resposta (bug corrigido v0.13.1)"""
        handler = Section6Handler("sess", "bo", 6)
        assert handler.has_auto_answer() is False
        assert handler.get_auto_answer_step() is None

    def test_section8_no_auto_answer(self):
        """Seção 8 não deve ter auto-resposta"""
        handler = Section8Handler("sess", "bo", 8)
        assert handler.has_auto_answer() is False
        assert handler.get_auto_answer_step() is None


class TestStateMachineCreation:
    """Testes de criação de state machines"""

    def test_each_section_creates_correct_state_machine(self):
        """Cada seção deve criar a state machine correta"""
        from backend.state_machine import BOStateMachine
        from backend.state_machine_section2 import BOStateMachineSection2
        from backend.state_machine_section8 import BOStateMachineSection8

        # Seção 1 → BOStateMachine
        handler1 = create_section_handler("s", "b", 1)
        sm1 = handler1.create_state_machine()
        assert isinstance(sm1, BOStateMachine)

        # Seção 2 → BOStateMachineSection2
        handler2 = create_section_handler("s", "b", 2)
        sm2 = handler2.create_state_machine()
        assert isinstance(sm2, BOStateMachineSection2)

        # Seção 8 → BOStateMachineSection8
        handler8 = create_section_handler("s", "b", 8)
        sm8 = handler8.create_state_machine()
        assert isinstance(sm8, BOStateMachineSection8)


class TestMetadata:
    """Testes da função get_section_metadata"""

    def test_metadata_for_all_sections(self):
        """Deve retornar metadados para todas as seções"""
        for section_num in range(1, 9):
            metadata = get_section_metadata(section_num)
            assert "name" in metadata
            assert "has_skip" in metadata
            assert "questions" in metadata
            assert "handler_class" in metadata

    def test_metadata_section1(self):
        """Metadados da Seção 1"""
        metadata = get_section_metadata(1)
        assert metadata["name"] == "Contexto da Ocorrência"
        assert metadata["has_skip"] is False
        assert metadata["questions"] == 11
        assert metadata["handler_class"] == "Section1Handler"

    def test_metadata_section6(self):
        """Metadados da Seção 6 (sem skip após correção)"""
        metadata = get_section_metadata(6)
        assert metadata["name"] == "Uso de Força"
        assert metadata["has_skip"] is False  # Bug corrigido
        assert metadata["questions"] == 6

    def test_metadata_invalid_section(self):
        """Deve levantar erro para seção inválida"""
        with pytest.raises(ValueError, match="Seção 99 não existe"):
            get_section_metadata(99)


class TestSectionHandlerRegistry:
    """Testes do registro SECTION_HANDLERS"""

    def test_all_sections_registered(self):
        """Todas as 8 seções devem estar registradas"""
        assert len(SECTION_HANDLERS) == 8
        for i in range(1, 9):
            assert i in SECTION_HANDLERS

    def test_handler_classes_are_unique(self):
        """Cada seção deve ter sua própria classe handler"""
        handler_classes = list(SECTION_HANDLERS.values())
        assert len(handler_classes) == len(set(handler_classes))


class TestStartMethod:
    """Testes do método start() que inicializa seções"""

    def test_start_creates_state_machine(self):
        """Método start deve criar state machine se não existir"""
        session_data = {"sections": {}, "current_section": None}
        handler = create_section_handler("sess", "bo", 3)

        # State machine não existe ainda
        assert 3 not in session_data["sections"]

        response = handler.start(session_data)

        # Agora deve existir
        assert 3 in session_data["sections"]
        assert session_data["current_section"] == 3

    def test_start_returns_correct_format(self):
        """Método start deve retornar dicionário no formato correto"""
        session_data = {"sections": {}, "current_section": None}
        handler = create_section_handler("sess-789", "BO-003", 5)

        response = handler.start(session_data)

        # Verificar estrutura da resposta
        assert "session_id" in response
        assert "bo_id" in response
        assert "section" in response
        assert "question" in response
        assert "current_step" in response

        # Verificar valores
        assert response["session_id"] == "sess-789"
        assert response["bo_id"] == "BO-003"
        assert response["section"] == 5

    def test_start_reuses_existing_state_machine(self):
        """Método start deve reusar state machine existente"""
        from backend.state_machine_section8 import BOStateMachineSection8

        # Criar state machine previamente (Seção 8 não tem auto-resposta)
        existing_sm = BOStateMachineSection8()
        existing_sm.store_answer("test_answer")

        session_data = {
            "sections": {8: existing_sm},
            "current_section": None
        }

        handler = create_section_handler("sess", "bo", 8)
        handler.start(session_data)

        # Deve ser a mesma instância
        assert session_data["sections"][8] is existing_sm
        # Resposta deve estar preservada (Seção 8 não sobrescreve)
        assert "test_answer" in existing_sm.answers.values()


# Executar testes
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
