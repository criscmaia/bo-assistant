# -*- coding: utf-8 -*-
"""
Testes unitários para Seção 7: Apreensões e Cadeia de Custódia
"""
import sys
import os

# Adicionar backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from state_machine_section7 import BOStateMachineSection7, SECTION7_QUESTIONS, SECTION7_STEPS
from validator_section7 import ResponseValidatorSection7


class TestSection7StateMachine:
    """Testes para BOStateMachineSection7"""

    def test_initialization(self):
        """Testa inicialização correta"""
        sm = BOStateMachineSection7()
        assert sm.current_step == "7.1"
        assert sm.answers == {}
        assert sm.section_skipped == False

    def test_questions_defined(self):
        """Verifica que todas as 4 perguntas estão definidas"""
        assert len(SECTION7_QUESTIONS) == 4
        assert "7.1" in SECTION7_QUESTIONS
        assert "7.4" in SECTION7_QUESTIONS

    def test_steps_defined(self):
        """Verifica que todos os steps estão definidos"""
        assert SECTION7_STEPS == ["7.1", "7.2", "7.3", "7.4", "complete"]

    def test_skip_section_on_no(self):
        """Testa que responder NÃO em 7.1 pula a seção"""
        sm = BOStateMachineSection7()
        sm.store_answer("NÃO")
        assert sm.section_skipped == True
        assert sm.current_step == "complete"
        assert sm.is_section_complete() == True

    def test_continue_on_yes(self):
        """Testa que responder SIM em 7.1 continua normalmente"""
        sm = BOStateMachineSection7()
        sm.store_answer("SIM")
        sm.next_step()
        assert sm.section_skipped == False
        assert sm.current_step == "7.2"

    def test_full_flow(self):
        """Testa fluxo completo da seção"""
        sm = BOStateMachineSection7()

        # 7.1 - SIM
        sm.store_answer("SIM")
        sm.next_step()

        # 7.2 a 7.4
        for step in ["7.2", "7.3", "7.4"]:
            assert sm.current_step == step
            sm.store_answer(f"Resposta para {step}")
            sm.next_step()

        assert sm.is_section_complete() == True
        assert len(sm.answers) == 4

    def test_get_skip_reason(self):
        """Testa mensagem de skip quando não houve apreensão"""
        sm = BOStateMachineSection7()
        sm.store_answer("NÃO")
        reason = sm.get_skip_reason()
        assert reason is not None
        assert "não houve apreensão" in reason.lower()


class TestSection7Validator:
    """Testes para ResponseValidatorSection7"""

    def test_validate_7_1_yes(self):
        """Testa validação de SIM para 7.1"""
        is_valid, error = ResponseValidatorSection7.validate("7.1", "SIM")
        assert is_valid == True
        assert error == ""

    def test_validate_7_1_no(self):
        """Testa validação de NÃO para 7.1"""
        is_valid, error = ResponseValidatorSection7.validate("7.1", "NÃO")
        assert is_valid == True

    def test_validate_7_1_invalid(self):
        """Testa resposta inválida para 7.1"""
        is_valid, error = ResponseValidatorSection7.validate("7.1", "TALVEZ")
        assert is_valid == False

    def test_validate_7_2_requires_graduation(self):
        """Testa que 7.2 requer graduação militar"""
        # Sem graduação - deve falhar
        is_valid, error = ResponseValidatorSection7.validate(
            "7.2",
            "Breno encontrou 14 pedras de crack em uma lata azul"
        )
        assert is_valid == False

        # Com graduação - deve passar
        is_valid, error = ResponseValidatorSection7.validate(
            "7.2",
            "O Soldado Breno encontrou 14 pedras de crack dentro de uma lata azul sobre o banco de concreto"
        )
        assert is_valid == True

    def test_validate_7_2_requires_min_length(self):
        """Testa que 7.2 requer mínimo de 50 caracteres"""
        is_valid, error = ResponseValidatorSection7.validate(
            "7.2",
            "Soldado encontrou drogas"  # Muito curto
        )
        assert is_valid == False

    def test_validate_7_3_with_objects(self):
        """Testa que 7.3 aceita lista de objetos"""
        is_valid, error = ResponseValidatorSection7.validate(
            "7.3",
            "Foram apreendidos R$ 450,00 em notas diversas, 2 celulares e 1 balança de precisão"
        )
        assert is_valid == True

    def test_validate_7_3_none_response_accepted(self):
        """Testa que 7.3 ACEITA 'Nenhum objeto' como resposta válida (NOVA FUNCIONALIDADE)"""
        # Resposta curta "Nenhum objeto" deve ser aceita
        is_valid, error = ResponseValidatorSection7.validate(
            "7.3",
            "Nenhum objeto ligado ao tráfico foi encontrado"
        )
        assert is_valid == True
        assert error == ""

    def test_validate_7_3_none_response_variations(self):
        """Testa variações de 'nenhum' em 7.3"""
        valid_responses = [
            "Nenhum objeto foi apreendido",
            "Não havia objetos ligados ao tráfico",
            "Não houve apreensão de objetos",
            "Não foram encontrados objetos"
        ]

        for response in valid_responses:
            is_valid, error = ResponseValidatorSection7.validate("7.3", response)
            assert is_valid == True, f"Resposta '{response}' deveria ser válida"

    def test_validate_7_3_short_response_invalid(self):
        """Testa que resposta curta sem 'nenhum' é inválida em 7.3"""
        is_valid, error = ResponseValidatorSection7.validate("7.3", "nada")  # Muito curto e sem "nenhum"
        assert is_valid == False

    def test_validate_7_4_requires_graduation(self):
        """Testa que 7.4 requer graduação militar"""
        # Sem graduação - deve falhar
        is_valid, error = ResponseValidatorSection7.validate(
            "7.4",
            "Material foi lacrado e entregue na delegacia"
        )
        assert is_valid == False

        # Com graduação E destino - deve passar
        is_valid, error = ResponseValidatorSection7.validate(
            "7.4",
            "O Soldado Faria lacrou as substâncias no invólucro 01, fotografou e ficou responsável até a entrega na CEFLAN 2"
        )
        assert is_valid == True

    def test_validate_7_4_requires_destination(self):
        """Testa que 7.4 requer destino (CEFLAN, delegacia, etc)"""
        # Com graduação mas SEM destino - deve falhar
        is_valid, error = ResponseValidatorSection7.validate(
            "7.4",
            "O Cabo Almeida lacrou o material e ficou responsável conforme protocolo"
        )
        assert is_valid == False

        # Com graduação E destino específico - deve passar
        is_valid, error = ResponseValidatorSection7.validate(
            "7.4",
            "O Cabo Almeida acondicionou em saco plástico, fotografou e transportou até a Delegacia Civil de Contagem"
        )
        assert is_valid == True

    def test_validate_7_4_requires_min_length(self):
        """Testa que 7.4 requer mínimo de 40 caracteres"""
        is_valid, error = ResponseValidatorSection7.validate(
            "7.4",
            "Soldado lacrou tudo"  # Muito curto
        )
        assert is_valid == False


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
