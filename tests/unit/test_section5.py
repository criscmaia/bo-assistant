# -*- coding: utf-8 -*-
"""
Testes unitários para Seção 5: Fundada Suspeita
"""
import sys
import os

# Adicionar backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from state_machine_section5 import BOStateMachineSection5, SECTION5_QUESTIONS, SECTION5_STEPS
from validator_section5 import ResponseValidatorSection5


class TestSection5StateMachine:
    """Testes para BOStateMachineSection5"""

    def test_initialization(self):
        """Testa inicialização correta"""
        sm = BOStateMachineSection5()
        assert sm.current_step == "5.1"
        assert sm.answers == {}
        assert sm.section_skipped == False

    def test_questions_defined(self):
        """Verifica que todas as 3 perguntas estão definidas"""
        assert len(SECTION5_QUESTIONS) == 3
        assert "5.1" in SECTION5_QUESTIONS
        assert "5.3" in SECTION5_QUESTIONS

    def test_steps_defined(self):
        """Verifica que todos os steps estão definidos"""
        assert SECTION5_STEPS == ["5.1", "5.2", "5.3", "complete"]

    def test_full_flow(self):
        """Testa fluxo completo da seção (não há mais pergunta condicional)"""
        sm = BOStateMachineSection5()

        # 5.1 a 5.3 - todas obrigatórias
        for step in ["5.1", "5.2", "5.3"]:
            assert sm.current_step == step
            sm.store_answer(f"Resposta para {step}")
            sm.next_step()

        assert sm.is_section_complete() == True
        assert len(sm.answers) == 3


class TestSection5Validator:
    """Testes para ResponseValidatorSection5"""

    def test_validate_5_1_min_length(self):
        """Testa comprimento mínimo para 5.1 (o que viu)"""
        # Muito curto - deve falhar
        is_valid, error = ResponseValidatorSection5.validate("5.1", "Viu algo")
        assert is_valid == False

        # Detalhado - deve passar
        is_valid, error = ResponseValidatorSection5.validate("5.1", "Durante patrulhamento pela Rua das Palmeiras, região com registros anteriores de tráfico, visualizamos um homem de camisa vermelha retirando invólucros de um buraco no muro")
        assert is_valid == True

    def test_validate_5_2_requires_graduation(self):
        """Testa que 5.2 requer graduação militar"""
        # Sem graduação - deve falhar
        is_valid, error = ResponseValidatorSection5.validate("5.2", "João viu o suspeito retirando invólucros do buraco")
        assert is_valid == False

        # Com graduação (Sargento) - deve passar
        is_valid, error = ResponseValidatorSection5.validate("5.2", "O Sargento João viu o suspeito retirando invólucros do buraco no muro")
        assert is_valid == True

        # Com graduação abreviada (Sgt) - deve passar
        is_valid, error = ResponseValidatorSection5.validate("5.2", "O Sgt. Silva viu de perto o procedimento ilícito")
        assert is_valid == True

        # Com outra graduação (Cabo) - deve passar
        is_valid, error = ResponseValidatorSection5.validate("5.2", "O Cabo Almeida, posicionado na esquina, viu o indivíduo entregar pacotes")
        assert is_valid == True

    def test_validate_5_3_min_length(self):
        """Testa comprimento mínimo para 5.3 (características individualizadas)"""
        # Muito curto - deve falhar
        is_valid, error = ResponseValidatorSection5.validate("5.3", "Homem de camisa vermelha")
        assert is_valid == False

        # Detalhado com nome e vulgo - deve passar
        is_valid, error = ResponseValidatorSection5.validate("5.3", "Homem de camisa vermelha e bermuda jeans, porte atlético, gestos nervosos, posteriormente identificado como JOÃO DA SILVA, vulgo 'Vermelho'")
        assert is_valid == True


if __name__ == "__main__":
    print("Executando testes da Seção 5...")

    # State Machine
    t = TestSection5StateMachine()
    t.test_initialization()
    print("[OK] test_initialization")
    t.test_questions_defined()
    print("[OK] test_questions_defined")
    t.test_steps_defined()
    print("[OK] test_steps_defined")
    t.test_full_flow()
    print("[OK] test_full_flow")

    # Validator
    v = TestSection5Validator()
    v.test_validate_5_1_min_length()
    print("[OK] test_validate_5_1_min_length")
    v.test_validate_5_2_requires_graduation()
    print("[OK] test_validate_5_2_requires_graduation")
    v.test_validate_5_3_min_length()
    print("[OK] test_validate_5_3_min_length")

    print("\nTodos os testes passaram!")
