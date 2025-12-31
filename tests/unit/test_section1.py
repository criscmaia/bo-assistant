# -*- coding: utf-8 -*-
"""
Testes unitários para Seção 1: Contexto da Ocorrência
"""
import sys
import os

# Adicionar backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from state_machine import BOStateMachine
from validator import ResponseValidator

# Acessar atributos de classe
QUESTIONS = BOStateMachine.QUESTIONS
STEPS = BOStateMachine.STEPS


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_test(name, passed, message=""):
    status = f"{Colors.GREEN}[PASS]{Colors.END}" if passed else f"{Colors.RED}[FAIL]{Colors.END}"
    print(f"{status} - {name}")
    if message and not passed:
        print(f"  {Colors.YELLOW}-> {message}{Colors.END}")


class TestSection1StateMachine:
    """Testes para BOStateMachine (Seção 1)"""

    def test_initialization(self):
        """Testa inicialização correta"""
        sm = BOStateMachine()
        assert sm.current_step == "1.1", "Estado inicial deve ser 1.1"
        assert sm.answers == {}, "Respostas devem estar vazias"
        assert sm.step_index == 0, "Índice deve ser 0"

    def test_questions_defined(self):
        """Verifica que todas as 13 perguntas estão definidas (11 principais + 2 condicionais)"""
        assert len(QUESTIONS) == 13, f"Esperado 13 perguntas, encontrado {len(QUESTIONS)}"
        assert "1.1" in QUESTIONS, "Pergunta 1.1 deve existir"
        assert "1.9.2" in QUESTIONS, "Pergunta 1.9.2 deve existir"

    def test_steps_defined(self):
        """Verifica que todos os steps estão definidos"""
        expected_steps = ["1.1", "1.2", "1.3", "1.4", "1.5", "1.5.1", "1.5.2", "1.6", "1.7", "1.8", "1.9", "1.9.1", "1.9.2", "complete"]
        assert STEPS == expected_steps, f"Esperado {expected_steps}, encontrado {STEPS}"

    def test_full_flow(self):
        """Testa fluxo completo da seção (todas as perguntas respondidas com SIM)"""
        sm = BOStateMachine()

        # 1.1 a 1.9.2 (respondendo SIM para 1.5 e 1.9 para testar sub-perguntas)
        steps_to_answer = ["1.1", "1.2", "1.3", "1.4", "1.5", "1.5.1", "1.5.2", "1.6", "1.7", "1.8", "1.9", "1.9.1", "1.9.2"]
        for step in steps_to_answer:
            assert sm.current_step == step, f"Esperado step {step}, encontrado {sm.current_step}"
            # Responder SIM para 1.5 e 1.9 para ativar sub-perguntas
            if step in ["1.5", "1.9"]:
                sm.store_answer("SIM")
            else:
                sm.store_answer(f"Resposta para {step}")
            sm.next_step()

        assert sm.is_section_complete() == True, "Seção deve estar completa"
        assert len(sm.answers) == 13, f"Esperado 13 respostas, encontrado {len(sm.answers)}"

    def test_skip_logic_1_5(self):
        """Testa lógica de pular sub-perguntas 1.5.x quando 1.5 = NÃO"""
        sm = BOStateMachine()

        # Responder perguntas até 1.5
        for step in ["1.1", "1.2", "1.3", "1.4"]:
            sm.store_answer(f"Resposta para {step}")
            sm.next_step()

        # Responder NÃO para 1.5
        assert sm.current_step == "1.5"
        sm.store_answer("NÃO")
        sm.next_step()

        # Deve pular 1.5.1 e 1.5.2, indo direto para 1.6
        assert sm.current_step == "1.6", f"Esperado 1.6, encontrado {sm.current_step}"
        assert "1.5.1" not in sm.answers, "1.5.1 não deve ser respondida"
        assert "1.5.2" not in sm.answers, "1.5.2 não deve ser respondida"

    def test_skip_logic_1_9(self):
        """Testa lógica de pular sub-perguntas 1.9.x quando 1.9 = NÃO"""
        sm = BOStateMachine()

        # Responder todas até 1.8 (porque precisamos estar em 1.9 para testar)
        steps_until_1_8 = ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8"]
        for step in steps_until_1_8:
            # Responder NÃO para 1.5 para pular sub-perguntas
            if step == "1.5":
                sm.store_answer("NÃO")
            else:
                sm.store_answer(f"Resposta para {step}")
            sm.next_step()

        # Agora devemos estar em 1.9
        assert sm.current_step == "1.9", f"Esperado 1.9, encontrado {sm.current_step}"

        # Responder NÃO para 1.9
        sm.store_answer("NÃO")
        sm.next_step()

        # Deve pular 1.9.1 e 1.9.2, indo direto para complete
        assert sm.current_step == "complete", f"Esperado complete, encontrado {sm.current_step}"
        assert "1.9.1" not in sm.answers, "1.9.1 não deve ser respondida"
        assert "1.9.2" not in sm.answers, "1.9.2 não deve ser respondida"

    def test_get_progress(self):
        """Testa cálculo de progresso"""
        sm = BOStateMachine()

        # Sem respostas - deve ser 9 (base)
        progress = sm.get_progress()
        assert progress['total'] == 9, "Total inicial deve ser 9 (perguntas obrigatórias)"
        assert progress['total_base'] == 9, "Total base deve ser sempre 9"
        assert progress['answered'] == 0, "Respondidas deve ser 0"

        # Com 3 respostas (1.1, 1.2, 1.3)
        sm.store_answer("Resposta 1")
        sm.next_step()
        sm.store_answer("Resposta 2")
        sm.next_step()
        sm.store_answer("Resposta 3")

        progress = sm.get_progress()
        assert progress['answered'] == 3, "Respondidas deve ser 3"
        assert progress['total'] == 9, "Total deve continuar 9 até responder condicional"
        assert progress['percentage'] == 33, "Percentual deve ser 33"  # 3/9 * 100 = 33.33...

    def test_get_progress_dynamic_with_conditionals(self):
        """Testa cálculo dinâmico de progresso com perguntas condicionais"""
        sm = BOStateMachine()

        # Responder até 1.4
        for step in ["1.1", "1.2", "1.3", "1.4"]:
            sm.store_answer(f"Resposta {step}")
            sm.next_step()

        progress = sm.get_progress()
        assert progress['answered'] == 4, "Deve ter 4 respostas"
        assert progress['total'] == 9, "Total deve ser 9 (ainda não respondeu condicionais)"

        # Responder SIM em 1.5 - deve aumentar total para 11
        sm.store_answer("SIM")
        sm.next_step()

        progress = sm.get_progress()
        assert progress['answered'] == 5, "Deve ter 5 respostas"
        assert progress['total'] == 11, "Total deve mudar para 11 após SIM em 1.5"

        # Responder 1.5.1 e 1.5.2
        sm.store_answer("Resposta 1.5.1")
        sm.next_step()
        sm.store_answer("Resposta 1.5.2")
        sm.next_step()

        progress = sm.get_progress()
        assert progress['answered'] == 7, "Deve ter 7 respostas"
        assert progress['total'] == 11, "Total deve continuar 11"

        # Pular para 1.9 respondendo 1.6, 1.7, 1.8
        for step in ["1.6", "1.7", "1.8"]:
            assert sm.current_step == step
            sm.store_answer(f"Resposta {step}")
            sm.next_step()

        # Responder SIM em 1.9 - deve aumentar total para 13
        assert sm.current_step == "1.9"
        sm.store_answer("SIM")
        sm.next_step()

        progress = sm.get_progress()
        assert progress['answered'] == 11, "Deve ter 11 respostas"
        assert progress['total'] == 13, "Total deve mudar para 13 após SIM em 1.9"
        assert progress['percentage'] == 84, "Percentual deve ser 84"  # 11/13 * 100 = 84.61...


class TestSection1Validator:
    """Testes para ResponseValidator (Seção 1)"""

    def test_validate_1_5_yes_no(self):
        """Testa que 1.5 aceita apenas SIM ou NÃO"""
        is_valid, error = ResponseValidator.validate("1.5", "SIM")
        assert is_valid == True, "1.5 deve aceitar SIM"

        is_valid, error = ResponseValidator.validate("1.5", "NÃO")
        assert is_valid == True, "1.5 deve aceitar NÃO"

        is_valid, error = ResponseValidator.validate("1.5", "Houve deslocamento")
        assert is_valid == False, "1.5 deve rejeitar resposta que não seja SIM/NÃO"

    def test_validate_1_9_yes_no(self):
        """Testa que 1.9 aceita apenas SIM ou NÃO"""
        is_valid, error = ResponseValidator.validate("1.9", "SIM")
        assert is_valid == True, "1.9 deve aceitar SIM"

        is_valid, error = ResponseValidator.validate("1.9", "NÃO")
        assert is_valid == True, "1.9 deve aceitar NÃO"

        is_valid, error = ResponseValidator.validate("1.9", "Próximo de escola")
        assert is_valid == False, "1.9 deve rejeitar resposta que não seja SIM/NÃO"

    def test_validate_1_7_accepts_no(self):
        """Testa que 1.7 aceita NÃO como resposta válida"""
        is_valid, error = ResponseValidator.validate("1.7", "Não há histórico")
        assert is_valid == True, "1.7 deve aceitar respostas negativas"

    def test_validate_1_8_accepts_no(self):
        """Testa que 1.8 aceita NÃO como resposta válida"""
        is_valid, error = ResponseValidator.validate("1.8", "Não há facção")
        assert is_valid == True, "1.8 deve aceitar respostas negativas"

    def test_validate_datetime(self):
        """Testa validação de data/hora para 1.1"""
        # Resposta válida
        is_valid, error = ResponseValidator.validate("1.1", "22/03/2025, às 19h03")
        assert is_valid == True, "Deve aceitar data/hora válida"

        # Resposta sem data
        is_valid, error = ResponseValidator.validate("1.1", "às 19h03")
        assert is_valid == False, "Deve rejeitar sem data"

    def test_validate_1_2_requires_prefix(self):
        """Testa que 1.2 requer prefixo ou viatura"""
        # Sem prefixo - deve falhar
        is_valid, error = ResponseValidator.validate("1.2", "Sgt João Silva e Cb Pedro Santos")
        assert is_valid == False, "1.2 deve exigir prefixo ou viatura"

        # Com prefixo - deve passar
        is_valid, error = ResponseValidator.validate("1.2", "Sgt João Silva e Cb Pedro Santos, prefixo 1234")
        assert is_valid == True, "1.2 deve aceitar com prefixo"

    def test_validate_1_6_requires_address(self):
        """Testa que 1.6 requer endereço completo (mudou de 1.5 para 1.6)"""
        # Endereço incompleto - deve falhar
        is_valid, error = ResponseValidator.validate("1.6", "Rua das Flores")
        assert is_valid == False, "1.6 deve exigir endereço completo"

        # Endereço completo - deve passar
        is_valid, error = ResponseValidator.validate("1.6", "Rua das Flores, número 123, bairro Centro")
        assert is_valid == True, "1.6 deve aceitar endereço completo"


if __name__ == "__main__":
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Executando testes da Seção 1 - Contexto da Ocorrência{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

    # State Machine
    print(f"{Colors.YELLOW}--- Testes do BOStateMachine ---{Colors.END}")
    t = TestSection1StateMachine()

    try:
        t.test_initialization()
        print_test("test_initialization", True)
    except AssertionError as e:
        print_test("test_initialization", False, str(e))

    try:
        t.test_questions_defined()
        print_test("test_questions_defined", True)
    except AssertionError as e:
        print_test("test_questions_defined", False, str(e))

    try:
        t.test_steps_defined()
        print_test("test_steps_defined", True)
    except AssertionError as e:
        print_test("test_steps_defined", False, str(e))

    try:
        t.test_full_flow()
        print_test("test_full_flow", True)
    except AssertionError as e:
        print_test("test_full_flow", False, str(e))

    try:
        t.test_get_progress()
        print_test("test_get_progress", True)
    except AssertionError as e:
        print_test("test_get_progress", False, str(e))

    try:
        t.test_get_progress_dynamic_with_conditionals()
        print_test("test_get_progress_dynamic_with_conditionals", True)
    except AssertionError as e:
        print_test("test_get_progress_dynamic_with_conditionals", False, str(e))

    try:
        t.test_skip_logic_1_5()
        print_test("test_skip_logic_1_5", True)
    except AssertionError as e:
        print_test("test_skip_logic_1_5", False, str(e))

    try:
        t.test_skip_logic_1_9()
        print_test("test_skip_logic_1_9", True)
    except AssertionError as e:
        print_test("test_skip_logic_1_9", False, str(e))

    # Validator
    print(f"\n{Colors.YELLOW}--- Testes do ResponseValidator ---{Colors.END}")
    v = TestSection1Validator()

    try:
        v.test_validate_1_5_yes_no()
        print_test("test_validate_1_5_yes_no", True)
    except AssertionError as e:
        print_test("test_validate_1_5_yes_no", False, str(e))

    try:
        v.test_validate_1_9_yes_no()
        print_test("test_validate_1_9_yes_no", True)
    except AssertionError as e:
        print_test("test_validate_1_9_yes_no", False, str(e))

    try:
        v.test_validate_1_7_accepts_no()
        print_test("test_validate_1_7_accepts_no", True)
    except AssertionError as e:
        print_test("test_validate_1_7_accepts_no", False, str(e))

    try:
        v.test_validate_1_8_accepts_no()
        print_test("test_validate_1_8_accepts_no", True)
    except AssertionError as e:
        print_test("test_validate_1_8_accepts_no", False, str(e))

    try:
        v.test_validate_datetime()
        print_test("test_validate_datetime", True)
    except AssertionError as e:
        print_test("test_validate_datetime", False, str(e))

    try:
        v.test_validate_1_2_requires_prefix()
        print_test("test_validate_1_2_requires_prefix", True)
    except AssertionError as e:
        print_test("test_validate_1_2_requires_prefix", False, str(e))

    try:
        v.test_validate_1_6_requires_address()
        print_test("test_validate_1_6_requires_address", True)
    except AssertionError as e:
        print_test("test_validate_1_6_requires_address", False, str(e))

    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}Todos os testes da Secao 1 concluidos!{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
