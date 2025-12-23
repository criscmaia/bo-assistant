# -*- coding: utf-8 -*-
"""
Testes unitários para Seção 8: Condução e Pós-Ocorrência
"""
import sys
import os

# Adicionar backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from state_machine_section8 import BOStateMachineSection8, SECTION8_QUESTIONS, SECTION8_STEPS
from validator_section8 import ResponseValidatorSection8


class TestSection8StateMachine:
    """Testes para BOStateMachineSection8"""

    def test_initialization(self):
        """Testa inicialização correta"""
        sm = BOStateMachineSection8()
        assert sm.current_step == "8.1"
        assert sm.answers == {}
        assert sm.step_index == 0

    def test_questions_defined(self):
        """Verifica que todas as 6 perguntas estão definidas"""
        assert len(SECTION8_QUESTIONS) == 6
        assert "8.1" in SECTION8_QUESTIONS
        assert "8.6" in SECTION8_QUESTIONS

    def test_steps_defined(self):
        """Verifica que todos os steps estão definidos"""
        assert SECTION8_STEPS == ["8.1", "8.2", "8.3", "8.4", "8.5", "8.6", "complete"]

    def test_store_answer(self):
        """Testa armazenamento de resposta"""
        sm = BOStateMachineSection8()
        sm.store_answer("O Sargento Marco deu voz de prisão")
        assert sm.answers["8.1"] == "O Sargento Marco deu voz de prisão"

    def test_next_step(self):
        """Testa avançamento entre steps"""
        sm = BOStateMachineSection8()
        for i, step in enumerate(SECTION8_STEPS[:-1]):  # Excluir "complete"
            assert sm.current_step == step
            sm.next_step()
        assert sm.current_step == "complete"

    def test_full_flow(self):
        """Testa fluxo completo da seção"""
        sm = BOStateMachineSection8()

        # Todas as 6 perguntas devem ser respondidas
        answers = {
            "8.1": "O Sargento Marco deu voz de prisão pelo art. 33 da Lei 11.343/06",
            "8.2": "Havia agravante de associação para o tráfico",
            "8.3": "O preso declarou: 'Essa droga não é minha'",
            "8.4": "O autor possui REDS 2023-001234 por tráfico",
            "8.5": "O autor possui vínculo com a facção Primeiro Comando",
            "8.6": "Os direitos foram lidos. Integridade: sem lesões. Destino: CEFLAN 2"
        }

        for step in ["8.1", "8.2", "8.3", "8.4", "8.5", "8.6"]:
            assert sm.current_step == step
            sm.store_answer(answers[step])
            sm.next_step()

        assert sm.is_section_complete() == True
        assert len(sm.answers) == 6

    def test_get_current_question(self):
        """Testa obtenção da pergunta atual"""
        sm = BOStateMachineSection8()
        assert sm.get_current_question() == SECTION8_QUESTIONS["8.1"]
        sm.next_step()
        assert sm.get_current_question() == SECTION8_QUESTIONS["8.2"]

    def test_get_answer(self):
        """Testa recuperação de resposta específica"""
        sm = BOStateMachineSection8()
        sm.store_answer("O Sargento Marco deu voz de prisão")
        sm.next_step()

        # Deve recuperar resposta anterior
        assert sm.get_answer("8.1") == "O Sargento Marco deu voz de prisão"

    def test_update_answer(self):
        """Testa atualização de resposta anterior"""
        sm = BOStateMachineSection8()
        sm.store_answer("Resposta inicial")

        updated = sm.update_answer("8.1", "Resposta atualizada")
        assert updated == True
        assert sm.get_answer("8.1") == "Resposta atualizada"

    def test_update_answer_invalid_step(self):
        """Testa que não é possível atualizar step inexistente"""
        sm = BOStateMachineSection8()
        updated = sm.update_answer("8.9", "Resposta")
        assert updated == False

    def test_get_progress(self):
        """Testa cálculo de progresso"""
        sm = BOStateMachineSection8()

        # Início: 0 respostas
        progress = sm.get_progress()
        assert progress["completed_steps"] == 0
        assert progress["total_steps"] == 6
        assert progress["progress_percentage"] == 0.0

        # Após 3 respostas
        sm.store_answer("Resposta 1")
        sm.next_step()
        sm.store_answer("Resposta 2")
        sm.next_step()
        sm.store_answer("Resposta 3")

        progress = sm.get_progress()
        assert progress["completed_steps"] == 3
        assert progress["total_steps"] == 6
        assert progress["progress_percentage"] == 50.0

    def test_reset(self):
        """Testa reset da state machine"""
        sm = BOStateMachineSection8()
        sm.store_answer("Resposta")
        sm.next_step()

        # Resetar
        sm.reset()
        assert sm.current_step == "8.1"
        assert sm.answers == {}
        assert sm.step_index == 0

    def test_get_formatted_answers(self):
        """Testa formatação de respostas para debug"""
        sm = BOStateMachineSection8()
        sm.store_answer("O Sargento Marco deu voz de prisão")
        sm.next_step()
        sm.store_answer("Havia agravantes")

        formatted = sm.get_formatted_answers()
        assert "8.1" in formatted
        assert "8.2" in formatted
        assert "O Sargento Marco" in formatted


class TestSection8Validator:
    """Testes para ResponseValidatorSection8"""

    def test_validate_8_1_valid(self):
        """Testa validação válida para 8.1 com graduação"""
        valid, error = ResponseValidatorSection8.validate(
            "8.1",
            "O Sargento Marco deu voz de prisão ao autor pelo art. 33 da Lei 11.343/06"
        )
        assert valid == True
        assert error == ""

    def test_validate_8_1_missing_graduation(self):
        """Testa que 8.1 rejeita sem graduação militar"""
        valid, error = ResponseValidatorSection8.validate(
            "8.1",
            "Deu voz de prisão sem especificar a graduação de quem fez"
        )
        assert valid == False
        assert "graduação" in error.lower()

    def test_validate_8_2_with_aggravating(self):
        """Testa validação de agravantes em 8.2"""
        valid, error = ResponseValidatorSection8.validate(
            "8.2",
            "Havia agravante de associação para o tráfico art. 35"
        )
        assert valid == True

    def test_validate_8_2_none_response(self):
        """Testa que 8.2 aceita 'Sem agravantes'"""
        valid, error = ResponseValidatorSection8.validate(
            "8.2",
            "Sem agravantes identificados"
        )
        assert valid == True

    def test_validate_8_3_with_declaration(self):
        """Testa validação de declaração em 8.3"""
        valid, error = ResponseValidatorSection8.validate(
            "8.3",
            "O preso declarou literalmente: 'Essa droga não é minha'"
        )
        assert valid == True

    def test_validate_8_3_none_response(self):
        """Testa que 8.3 aceita 'Não declarou'"""
        valid, error = ResponseValidatorSection8.validate(
            "8.3",
            "O autor permaneceu em silêncio, exercendo seu direito constitucional"
        )
        assert valid == True

    def test_validate_8_4_with_reds(self):
        """Testa validação de REDS em 8.4"""
        valid, error = ResponseValidatorSection8.validate(
            "8.4",
            "O autor possui REDS 2023-001234 por tráfico e REDS 2022-005678"
        )
        assert valid == True

    def test_validate_8_4_none_response(self):
        """Testa que 8.4 aceita 'Sem registros'"""
        valid, error = ResponseValidatorSection8.validate(
            "8.4",
            "Sem registros anteriores no sistema REDS"
        )
        assert valid == True

    def test_validate_8_5_with_faction(self):
        """Testa validação de facção em 8.5"""
        valid, error = ResponseValidatorSection8.validate(
            "8.5",
            "O autor possui vínculo com a facção Primeiro Comando, atuando como vapor"
        )
        assert valid == True

    def test_validate_8_5_none_response(self):
        """Testa que 8.5 aceita 'Sem vínculo'"""
        valid, error = ResponseValidatorSection8.validate(
            "8.5",
            "Sem vínculo com facção criminosa identificado"
        )
        assert valid == True

    def test_validate_8_6_valid(self):
        """Testa validação válida para 8.6 com destino"""
        valid, error = ResponseValidatorSection8.validate(
            "8.6",
            "Os direitos foram lidos. Integridade física: sem lesões. Destino: CEFLAN 2 e Delegacia de Plantão"
        )
        assert valid == True

    def test_validate_8_6_missing_destination(self):
        """Testa que 8.6 rejeita sem destino"""
        valid, error = ResponseValidatorSection8.validate(
            "8.6",
            "Os direitos foram lidos sem especificar o destino"
        )
        assert valid == False
        assert "destino" in error.lower()

    def test_validate_empty_answer(self):
        """Testa rejeição de resposta vazia"""
        valid, error = ResponseValidatorSection8.validate("8.1", "")
        assert valid == False
        assert "resposta" in error.lower()

    def test_validate_invalid_step(self):
        """Testa rejeição de step inválido"""
        valid, error = ResponseValidatorSection8.validate("8.9", "Qualquer resposta")
        assert valid == False
        assert "não encontrada" in error.lower()
