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
        """Verifica que todas as 7 perguntas estão definidas"""
        assert len(QUESTIONS) == 7, f"Esperado 7 perguntas, encontrado {len(QUESTIONS)}"
        assert "1.1" in QUESTIONS, "Pergunta 1.1 deve existir"
        assert "1.7" in QUESTIONS, "Pergunta 1.7 deve existir"

    def test_steps_defined(self):
        """Verifica que todos os steps estão definidos"""
        expected_steps = ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "complete"]
        assert STEPS == expected_steps, f"Esperado {expected_steps}, encontrado {STEPS}"

    def test_full_flow(self):
        """Testa fluxo completo da seção"""
        sm = BOStateMachine()

        # 1.1 a 1.7
        for step in ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7"]:
            assert sm.current_step == step, f"Esperado step {step}, encontrado {sm.current_step}"
            sm.store_answer(f"Resposta para {step}")
            sm.next_step()

        assert sm.is_section_complete() == True, "Seção deve estar completa"
        assert len(sm.answers) == 7, f"Esperado 7 respostas, encontrado {len(sm.answers)}"

    def test_get_progress(self):
        """Testa cálculo de progresso"""
        sm = BOStateMachine()

        # Sem respostas
        progress = sm.get_progress()
        assert progress['total'] == 7, "Total deve ser 7"
        assert progress['answered'] == 0, "Respondidas deve ser 0"

        # Com 3 respostas
        sm.store_answer("Resposta 1")
        sm.next_step()
        sm.store_answer("Resposta 2")
        sm.next_step()
        sm.store_answer("Resposta 3")

        progress = sm.get_progress()
        assert progress['answered'] == 3, "Respondidas deve ser 3"
        assert progress['percentage'] == 42, "Percentual deve ser 42"  # 3/7 * 100 = 42.857...


class TestSection1Validator:
    """Testes para ResponseValidator (Seção 1)"""

    def test_validate_1_7_accepts_no(self):
        """Testa que 1.7 aceita NÃO como resposta válida"""
        is_valid, error = ResponseValidator.validate("1.7", "NÃO")
        assert is_valid == True, "1.7 deve aceitar NÃO"
        assert error is None, "Não deve haver mensagem de erro"

    def test_validate_1_7_accepts_detailed_response(self):
        """Testa que 1.7 aceita resposta com estabelecimento"""
        is_valid, error = ResponseValidator.validate("1.7", "Sim, a 50 metros da Escola Estadual João XXIII")
        assert is_valid == True, "1.7 deve aceitar resposta com detalhes"

    def test_validate_1_7_rejects_too_short(self):
        """Testa que 1.7 rejeita resposta muito curta"""
        is_valid, error = ResponseValidator.validate("1.7", "Si")
        assert is_valid == False, "1.7 deve rejeitar resposta muito curta"
        assert error is not None, "Deve haver mensagem de erro"

    def test_validate_1_6_accepts_no(self):
        """Testa que 1.6 aceita NÃO como resposta válida"""
        is_valid, error = ResponseValidator.validate("1.6", "NÃO")
        assert is_valid == True, "1.6 deve aceitar NÃO"

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

    def test_validate_1_5_requires_address(self):
        """Testa que 1.5 requer endereço completo"""
        # Endereço incompleto - deve falhar
        is_valid, error = ResponseValidator.validate("1.5", "Rua das Flores")
        assert is_valid == False, "1.5 deve exigir endereço completo"

        # Endereço completo - deve passar
        is_valid, error = ResponseValidator.validate("1.5", "Rua das Flores, número 123, bairro Centro")
        assert is_valid == True, "1.5 deve aceitar endereço completo"


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

    # Validator
    print(f"\n{Colors.YELLOW}--- Testes do ResponseValidator ---{Colors.END}")
    v = TestSection1Validator()

    try:
        v.test_validate_1_7_accepts_no()
        print_test("test_validate_1_7_accepts_no", True)
    except AssertionError as e:
        print_test("test_validate_1_7_accepts_no", False, str(e))

    try:
        v.test_validate_1_7_accepts_detailed_response()
        print_test("test_validate_1_7_accepts_detailed_response", True)
    except AssertionError as e:
        print_test("test_validate_1_7_accepts_detailed_response", False, str(e))

    try:
        v.test_validate_1_7_rejects_too_short()
        print_test("test_validate_1_7_rejects_too_short", True)
    except AssertionError as e:
        print_test("test_validate_1_7_rejects_too_short", False, str(e))

    try:
        v.test_validate_1_6_accepts_no()
        print_test("test_validate_1_6_accepts_no", True)
    except AssertionError as e:
        print_test("test_validate_1_6_accepts_no", False, str(e))

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
        v.test_validate_1_5_requires_address()
        print_test("test_validate_1_5_requires_address", True)
    except AssertionError as e:
        print_test("test_validate_1_5_requires_address", False, str(e))

    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}Todos os testes da Secao 1 concluidos!{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
