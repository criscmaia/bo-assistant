# -*- coding: utf-8 -*-
"""
Testes unitários para Seção 6: Reação e Uso da Força
"""
import sys
import os

# Adicionar backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from state_machine_section6 import BOStateMachineSection6, SECTION6_QUESTIONS, SECTION6_STEPS
from validator_section6 import ResponseValidatorSection6


class TestSection6StateMachine:
    """Testes para BOStateMachineSection6"""

    def test_initialization(self):
        """Testa inicialização correta"""
        sm = BOStateMachineSection6()
        assert sm.current_step == "6.1"
        assert sm.answers == {}
        assert sm.section_skipped == False

    def test_questions_defined(self):
        """Verifica que todas as 5 perguntas estão definidas"""
        assert len(SECTION6_QUESTIONS) == 5
        assert "6.1" in SECTION6_QUESTIONS
        assert "6.5" in SECTION6_QUESTIONS

    def test_steps_defined(self):
        """Verifica que todos os steps estão definidos"""
        assert SECTION6_STEPS == ["6.1", "6.2", "6.3", "6.4", "6.5", "complete"]

    def test_skip_section_on_no(self):
        """Testa que responder NÃO em 6.1 pula a seção"""
        sm = BOStateMachineSection6()
        sm.store_answer("NÃO")
        assert sm.section_skipped == True
        assert sm.current_step == "complete"
        assert sm.is_section_complete() == True

    def test_continue_on_yes(self):
        """Testa que responder SIM em 6.1 continua normalmente"""
        sm = BOStateMachineSection6()
        sm.store_answer("SIM")
        sm.next_step()
        assert sm.section_skipped == False
        assert sm.current_step == "6.2"

    def test_full_flow(self):
        """Testa fluxo completo da seção"""
        sm = BOStateMachineSection6()

        # 6.1 - SIM
        sm.store_answer("SIM")
        sm.next_step()

        # 6.2 a 6.5
        for step in ["6.2", "6.3", "6.4", "6.5"]:
            assert sm.current_step == step
            sm.store_answer(f"Resposta para {step}")
            sm.next_step()

        assert sm.is_section_complete() == True
        assert len(sm.answers) == 5


class TestSection6Validator:
    """Testes para ResponseValidatorSection6"""

    def test_validate_6_1_yes(self):
        """Testa validação de SIM para 6.1"""
        is_valid, error = ResponseValidatorSection6.validate("6.1", "SIM")
        assert is_valid == True
        assert error == ""

    def test_validate_6_1_no(self):
        """Testa validação de NÃO para 6.1"""
        is_valid, error = ResponseValidatorSection6.validate("6.1", "NÃO")
        assert is_valid == True

    def test_validate_6_1_invalid(self):
        """Testa resposta inválida para 6.1"""
        is_valid, error = ResponseValidatorSection6.validate("6.1", "TALVEZ")
        assert is_valid == False

    def test_validate_6_2_forbidden_phrase_resistiu_ativamente(self):
        """Testa que 6.2 rejeita 'resistiu ativamente'"""
        is_valid, error = ResponseValidatorSection6.validate(
            "6.2",
            "O autor resistiu ativamente e tentou fugir"
        )
        assert is_valid == False
        assert "resistiu ativamente" in error

    def test_validate_6_2_forbidden_phrase_uso_moderado(self):
        """Testa que 6.2 rejeita 'uso moderado da força'"""
        is_valid, error = ResponseValidatorSection6.validate(
            "6.2",
            "Foi necessário uso moderado da força para contenção"
        )
        assert is_valid == False
        assert "uso moderado" in error

    def test_validate_6_2_forbidden_phrase_resistiu_sozinho(self):
        """Testa que 6.2 rejeita 'resistiu' sem contexto"""
        is_valid, error = ResponseValidatorSection6.validate(
            "6.2",
            "O autor resistiu"
        )
        assert is_valid == False

    def test_validate_6_2_valid_concrete_action(self):
        """Testa que 6.2 aceita descrição de ação concreta"""
        is_valid, error = ResponseValidatorSection6.validate(
            "6.2",
            "O autor empurrou o Cabo Rezende e tentou correr em direção ao beco lateral"
        )
        assert is_valid == True

    def test_validate_6_3_requires_graduation(self):
        """Testa que 6.3 requer graduação militar"""
        # Sem graduação - deve falhar
        is_valid, error = ResponseValidatorSection6.validate(
            "6.3",
            "João aplicou chave de braço no suspeito imobilizando no chão"
        )
        assert is_valid == False

        # Com graduação - deve passar
        is_valid, error = ResponseValidatorSection6.validate(
            "6.3",
            "O Cabo Marcelo aplicou chave de braço no suspeito, imobilizando-o no chão sem lesões"
        )
        assert is_valid == True

    def test_validate_6_4_requires_justification(self):
        """Testa que 6.4 requer justificativa com fato objetivo"""
        # Muito vago - deve falhar
        is_valid, error = ResponseValidatorSection6.validate(
            "6.4",
            "Aplicamos algemas por segurança"
        )
        assert is_valid == False

        # Com justificativa objetiva - deve passar
        is_valid, error = ResponseValidatorSection6.validate(
            "6.4",
            "Diante do risco de nova tentativa de fuga, o autor foi algemado"
        )
        assert is_valid == True

    def test_validate_6_5_no_injuries(self):
        """Testa que 6.5 aceita resposta sem ferimentos"""
        is_valid, error = ResponseValidatorSection6.validate(
            "6.5",
            "Não houve ferimentos. A guarnição verificou a integridade física e não encontrou lesões."
        )
        assert is_valid == True

    def test_validate_6_5_with_injury_requires_hospital(self):
        """Testa que 6.5 exige hospital quando menciona lesão"""
        # Com lesão mas sem hospital - deve falhar
        is_valid, error = ResponseValidatorSection6.validate(
            "6.5",
            "O autor apresentou escoriação no joelho esquerdo"
        )
        assert is_valid == False

        # Com lesão E hospital com ficha - deve passar
        is_valid, error = ResponseValidatorSection6.validate(
            "6.5",
            "O autor apresentou escoriação no joelho esquerdo. Foi atendido no Hospital João XXIII (ficha nº 2025-12345)"
        )
        assert is_valid == True


if __name__ == "__main__":
    print("Executando testes da Seção 6...")

    # State Machine
    t = TestSection6StateMachine()
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
    v = TestSection6Validator()
    v.test_validate_6_1_yes()
    print("[OK] test_validate_6_1_yes")
    v.test_validate_6_1_no()
    print("[OK] test_validate_6_1_no")
    v.test_validate_6_1_invalid()
    print("[OK] test_validate_6_1_invalid")
    v.test_validate_6_2_forbidden_phrase_resistiu_ativamente()
    print("[OK] test_validate_6_2_forbidden_phrase_resistiu_ativamente")
    v.test_validate_6_2_forbidden_phrase_uso_moderado()
    print("[OK] test_validate_6_2_forbidden_phrase_uso_moderado")
    v.test_validate_6_2_forbidden_phrase_resistiu_sozinho()
    print("[OK] test_validate_6_2_forbidden_phrase_resistiu_sozinho")
    v.test_validate_6_2_valid_concrete_action()
    print("[OK] test_validate_6_2_valid_concrete_action")
    v.test_validate_6_3_requires_graduation()
    print("[OK] test_validate_6_3_requires_graduation")
    v.test_validate_6_4_requires_justification()
    print("[OK] test_validate_6_4_requires_justification")
    v.test_validate_6_5_no_injuries()
    print("[OK] test_validate_6_5_no_injuries")
    v.test_validate_6_5_with_injury_requires_hospital()
    print("[OK] test_validate_6_5_with_injury_requires_hospital")

    print("\nTodos os testes passaram!")
