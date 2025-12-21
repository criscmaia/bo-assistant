# -*- coding: utf-8 -*-
"""
Testes unitários para Seção 4: Entrada em Domicílio
"""
import sys
import os

# Adicionar backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from state_machine_section4 import BOStateMachineSection4, SECTION4_QUESTIONS, SECTION4_STEPS
from validator_section4 import ResponseValidatorSection4


class TestSection4StateMachine:
    """Testes para BOStateMachineSection4"""

    def test_initialization(self):
        """Testa inicialização correta"""
        sm = BOStateMachineSection4()
        assert sm.current_step == "4.1"
        assert sm.answers == {}
        assert sm.section_skipped == False

    def test_questions_defined(self):
        """Verifica que todas as 5 perguntas estão definidas"""
        assert len(SECTION4_QUESTIONS) == 5
        assert "4.1" in SECTION4_QUESTIONS
        assert "4.5" in SECTION4_QUESTIONS

    def test_steps_defined(self):
        """Verifica que todos os steps estão definidos"""
        assert SECTION4_STEPS == ["4.1", "4.2", "4.3", "4.4", "4.5", "complete"]

    def test_skip_section_on_no(self):
        """Testa que responder NÃO em 4.1 pula a seção"""
        sm = BOStateMachineSection4()
        sm.store_answer("NÃO")
        assert sm.section_skipped == True
        assert sm.current_step == "complete"
        assert sm.is_section_complete() == True

    def test_continue_on_yes(self):
        """Testa que responder SIM em 4.1 continua normalmente"""
        sm = BOStateMachineSection4()
        sm.store_answer("SIM")
        sm.next_step()
        assert sm.section_skipped == False
        assert sm.current_step == "4.2"

    def test_full_flow(self):
        """Testa fluxo completo da seção"""
        sm = BOStateMachineSection4()

        # 4.1 - SIM
        sm.store_answer("SIM")
        sm.next_step()

        # 4.2 a 4.5
        for step in ["4.2", "4.3", "4.4", "4.5"]:
            assert sm.current_step == step
            sm.store_answer(f"Resposta para {step}")
            sm.next_step()

        assert sm.is_section_complete() == True
        assert len(sm.answers) == 5


class TestSection4Validator:
    """Testes para ResponseValidatorSection4"""

    def test_validate_4_1_yes(self):
        """Testa validação de SIM para 4.1"""
        is_valid, error = ResponseValidatorSection4.validate("4.1", "SIM")
        assert is_valid == True
        assert error == ""

    def test_validate_4_1_no(self):
        """Testa validação de NÃO para 4.1"""
        is_valid, error = ResponseValidatorSection4.validate("4.1", "NÃO")
        assert is_valid == True

    def test_validate_4_1_invalid(self):
        """Testa resposta inválida para 4.1"""
        is_valid, error = ResponseValidatorSection4.validate("4.1", "TALVEZ")
        assert is_valid == False

    def test_validate_4_2_min_length(self):
        """Testa comprimento mínimo para 4.2 (justa causa)"""
        # Muito curto - deve falhar
        is_valid, error = ResponseValidatorSection4.validate("4.2", "Viu algo")
        assert is_valid == False

        # Detalhado - deve passar
        is_valid, error = ResponseValidatorSection4.validate("4.2", "Vimos o suspeito arremessando uma sacola branca para dentro da casa enquanto corria")
        assert is_valid == True

    def test_validate_4_3_requires_graduation(self):
        """Testa que 4.3 requer graduação militar"""
        # Sem graduação - deve falhar
        is_valid, error = ResponseValidatorSection4.validate("4.3", "João viu o suspeito entrando na casa")
        assert is_valid == False

        # Com graduação - deve passar
        is_valid, error = ResponseValidatorSection4.validate("4.3", "O Sargento João viu o suspeito entrando na casa")
        assert is_valid == True

    def test_validate_4_4_min_length(self):
        """Testa comprimento mínimo para 4.4 (tipo de ingresso)"""
        # Muito curto - deve falhar
        is_valid, error = ResponseValidatorSection4.validate("4.4", "Perseguiu")
        assert is_valid == False

        # Detalhado - deve passar
        is_valid, error = ResponseValidatorSection4.validate("4.4", "Perseguição contínua desde a rua até o interior do imóvel")
        assert is_valid == True

    def test_validate_4_5_min_length(self):
        """Testa comprimento mínimo para 4.5 (ações dos policiais)"""
        # Muito curto - deve falhar
        is_valid, error = ResponseValidatorSection4.validate("4.5", "Entraram")
        assert is_valid == False

        # Detalhado - deve passar
        is_valid, error = ResponseValidatorSection4.validate("4.5", "O Sargento Silva entrou primeiro pela porta principal. O Cabo Rodrigues ficou na contenção. O Soldado Pires encontrou a sacola.")
        assert is_valid == True


if __name__ == "__main__":
    print("Executando testes da Seção 4...")

    # State Machine
    t = TestSection4StateMachine()
    t.test_initialization()
    print("[OK] test_initialization")
    t.test_questions_defined()
    print("[OK] test_questions_defined")
    t.test_steps_defined()
    print("[OK] test_steps_defined")
    t.test_skip_section_on_no()
    print("[OK] test_skip_section_on_no")
    t.test_continue_on_yes()
    print("[OK] test_continue_on_yes")
    t.test_full_flow()
    print("[OK] test_full_flow")

    # Validator
    v = TestSection4Validator()
    v.test_validate_4_1_yes()
    print("[OK] test_validate_4_1_yes")
    v.test_validate_4_1_no()
    print("[OK] test_validate_4_1_no")
    v.test_validate_4_1_invalid()
    print("[OK] test_validate_4_1_invalid")
    v.test_validate_4_2_min_length()
    print("[OK] test_validate_4_2_min_length")
    v.test_validate_4_3_requires_graduation()
    print("[OK] test_validate_4_3_requires_graduation")
    v.test_validate_4_4_min_length()
    print("[OK] test_validate_4_4_min_length")
    v.test_validate_4_5_min_length()
    print("[OK] test_validate_4_5_min_length")

    print("\nTodos os testes passaram!")
