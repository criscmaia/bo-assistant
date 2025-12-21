# -*- coding: utf-8 -*-
"""
Testes unitários para Seção 3: Campana (Vigilância Velada)
"""
import sys
import os

# Adicionar backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from state_machine_section3 import BOStateMachineSection3, SECTION3_QUESTIONS, SECTION3_STEPS
from validator_section3 import ResponseValidatorSection3


class TestSection3StateMachine:
    """Testes para BOStateMachineSection3"""

    def test_initialization(self):
        """Testa inicialização correta"""
        sm = BOStateMachineSection3()
        assert sm.current_step == "3.1"
        assert sm.answers == {}
        assert sm.section_skipped == False

    def test_questions_defined(self):
        """Verifica que todas as 8 perguntas estão definidas"""
        assert len(SECTION3_QUESTIONS) == 8
        assert "3.1" in SECTION3_QUESTIONS
        assert "3.8" in SECTION3_QUESTIONS

    def test_steps_defined(self):
        """Verifica que todos os steps estão definidos"""
        assert SECTION3_STEPS == ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "complete"]

    def test_skip_section_on_no(self):
        """Testa que responder NÃO em 3.1 pula a seção"""
        sm = BOStateMachineSection3()
        sm.store_answer("NÃO")
        assert sm.section_skipped == True
        assert sm.current_step == "complete"
        assert sm.is_section_complete() == True

    def test_continue_on_yes(self):
        """Testa que responder SIM em 3.1 continua normalmente"""
        sm = BOStateMachineSection3()
        sm.store_answer("SIM")
        sm.next_step()
        assert sm.section_skipped == False
        assert sm.current_step == "3.2"

    def test_full_flow(self):
        """Testa fluxo completo da seção"""
        sm = BOStateMachineSection3()

        # 3.1 - SIM
        sm.store_answer("SIM")
        sm.next_step()

        # 3.2 a 3.8
        for step in ["3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8"]:
            assert sm.current_step == step
            sm.store_answer(f"Resposta para {step}")
            sm.next_step()

        assert sm.is_section_complete() == True
        assert len(sm.answers) == 8


class TestSection3Validator:
    """Testes para ResponseValidatorSection3"""

    def test_validate_3_1_yes(self):
        """Testa validação de SIM para 3.1"""
        is_valid, error = ResponseValidatorSection3.validate("3.1", "SIM")
        assert is_valid == True
        assert error == ""

    def test_validate_3_1_no(self):
        """Testa validação de NÃO para 3.1"""
        is_valid, error = ResponseValidatorSection3.validate("3.1", "NÃO")
        assert is_valid == True

    def test_validate_3_1_invalid(self):
        """Testa resposta inválida para 3.1"""
        is_valid, error = ResponseValidatorSection3.validate("3.1", "TALVEZ")
        assert is_valid == False

    def test_validate_3_3_requires_graduation(self):
        """Testa que 3.3 requer graduação militar"""
        # Sem graduação - deve falhar
        is_valid, error = ResponseValidatorSection3.validate("3.3", "João viu a porta do bar claramente")
        assert is_valid == False

        # Com graduação - deve passar
        is_valid, error = ResponseValidatorSection3.validate("3.3", "O Sargento João viu a porta do bar claramente")
        assert is_valid == True

    def test_validate_3_6_min_length(self):
        """Testa comprimento mínimo para 3.6 (atos concretos)"""
        # Muito curto - deve falhar
        is_valid, error = ResponseValidatorSection3.validate("3.6", "Viu tráfico")
        assert is_valid == False

        # Detalhado - deve passar
        is_valid, error = ResponseValidatorSection3.validate("3.6", "O homem tirou pequenos invólucros da mochila preta e entregou para dois rapazes de moto")
        assert is_valid == True

    def test_validate_3_7_accepts_no(self):
        """Testa que 3.7 aceita NÃO como resposta válida"""
        is_valid, error = ResponseValidatorSection3.validate("3.7", "NÃO")
        assert is_valid == True

    def test_validate_3_8_accepts_no(self):
        """Testa que 3.8 aceita NÃO como resposta válida"""
        is_valid, error = ResponseValidatorSection3.validate("3.8", "NÃO")
        assert is_valid == True


if __name__ == "__main__":
    print("Executando testes da Seção 3...")

    # State Machine
    t = TestSection3StateMachine()
    t.test_initialization()
    print("✓ test_initialization")
    t.test_questions_defined()
    print("✓ test_questions_defined")
    t.test_steps_defined()
    print("✓ test_steps_defined")
    t.test_skip_section_on_no()
    print("✓ test_skip_section_on_no")
    t.test_continue_on_yes()
    print("✓ test_continue_on_yes")
    t.test_full_flow()
    print("✓ test_full_flow")

    # Validator
    v = TestSection3Validator()
    v.test_validate_3_1_yes()
    print("✓ test_validate_3_1_yes")
    v.test_validate_3_1_no()
    print("✓ test_validate_3_1_no")
    v.test_validate_3_1_invalid()
    print("✓ test_validate_3_1_invalid")
    v.test_validate_3_3_requires_graduation()
    print("✓ test_validate_3_3_requires_graduation")
    v.test_validate_3_6_min_length()
    print("✓ test_validate_3_6_min_length")
    v.test_validate_3_7_accepts_no()
    print("✓ test_validate_3_7_accepts_no")
    v.test_validate_3_8_accepts_no()
    print("✓ test_validate_3_8_accepts_no")

    print("\n✅ Todos os testes passaram!")
