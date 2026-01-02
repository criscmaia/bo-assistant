# -*- coding: utf-8 -*-
"""
Teste de integração: Endpoint /chat
Valida validação, armazenamento e resposta de mensagens

Executar: python test_chat_endpoint.py
"""
import sys
import os

# Adicionar diretório raiz do projeto ao path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, root_dir)

from backend.main import sessions
from backend.state_machine import BOStateMachine
from backend.validator import ResponseValidator
import uuid

# Cores para output
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

def setup_test_session():
    """Cria sessão de teste com Seção 1 iniciada"""
    session_id = str(uuid.uuid4())
    bo_id = f"BO-{session_id[:8]}"

    sessions[session_id] = {
        "bo_id": bo_id,
        "sections": {1: BOStateMachine()},
        "current_section": 1,
        "completed_sections": [],
        "responses": {}
    }

    return session_id, bo_id

def test_chat_valid_response():
    """Testa resposta válida para pergunta 1.1"""
    session_id, bo_id = setup_test_session()
    session = sessions[session_id]
    state_machine = session["sections"][1]

    # Resposta válida para 1.1 (data/hora)
    answer = "22/03/2025, 14h30min, quinta-feira"

    # Validar resposta
    validator = ResponseValidator()
    is_valid, error_msg = validator.validate("1.1", answer)

    print_test(
        "Chat: Aceita resposta válida para 1.1",
        is_valid and error_msg is None,
        error_msg
    )

    # Armazenar resposta
    state_machine.store_answer(answer)
    session["responses"]["1.1"] = answer

    # Verificar armazenamento
    stored = state_machine.answers.get("1.1")  # Primeiro step é "1.1"
    print_test(
        "Chat: Resposta armazenada corretamente",
        stored == answer,
        f"Esperava '{answer}', obteve '{stored}'"
    )

def test_chat_invalid_response():
    """Testa rejeição de resposta inválida"""
    session_id, bo_id = setup_test_session()

    # Resposta inválida para 1.1 (muito curta)
    answer = "hoje"

    validator = ResponseValidator()
    is_valid, error_msg = validator.validate("1.1", answer)

    print_test(
        "Chat: Rejeita resposta inválida para 1.1",
        not is_valid and error_msg is not None,
        f"Deveria ser inválido. Erro: {error_msg}"
    )

def test_chat_message_flow():
    """Testa fluxo completo de mensagem: validação → armazenamento → próxima pergunta"""
    session_id, bo_id = setup_test_session()
    session = sessions[session_id]
    state_machine = session["sections"][1]

    # Simular primeiro chat
    validator = ResponseValidator()

    # Q1.1
    answer1 = "22/03/2025, 14h30min, quinta-feira"
    is_valid, _ = validator.validate("1.1", answer1)
    print_test("Chat: 1.1 aceita resposta válida", is_valid)

    state_machine.store_answer(answer1)
    state_machine.next_step()

    # Q1.2
    answer2 = "Sargento João Silva, Cabo Pedro Almeida, Soldado Carlos Faria, prefixo 1234"
    is_valid, _ = validator.validate("1.2", answer2)
    print_test("Chat: 1.2 aceita resposta válida", is_valid)

    state_machine.store_answer(answer2)
    state_machine.next_step()

    # Verificar progresso
    current_question = state_machine.get_current_question()
    expected_id = "1.3"
    print_test(
        "Chat: Avança para próxima pergunta (1.3)",
        expected_id in current_question,
        f"Pergunta atual: {current_question[:50]}..."
    )

def test_chat_follow_up_trigger():
    """Testa ativação de follow-up via chat"""
    session_id, bo_id = setup_test_session()
    session = sessions[session_id]
    state_machine = session["sections"][1]

    validator = ResponseValidator()

    # Avançar até 1.5 (pergunta condicional)
    for i in range(4):
        answer = f"resposta_{i}" if i > 0 else "22/03/2025, 14h30min, quinta-feira"
        state_machine.store_answer(answer)
        state_machine.next_step()

    # Responder 1.5 com SIM (ativa follow-ups)
    state_machine.store_answer("SIM")

    # Verificar se a resposta foi armazenada
    answer_1_5 = state_machine.answers.get("1.5")
    print_test(
        "Chat: Resposta 1.5=SIM armazenada",
        answer_1_5 and answer_1_5.upper() == "SIM",
        f"Resposta armazenada: {answer_1_5}"
    )

def test_chat_multiple_consecutive():
    """Testa múltiplas mensagens consecutivas sem perder contexto"""
    session_id, bo_id = setup_test_session()
    session = sessions[session_id]
    state_machine = session["sections"][1]

    validator = ResponseValidator()
    responses = [
        ("1.1", "22/03/2025, 14h30min, quinta-feira", True),
        ("1.2", "Sgt João, Cb Pedro, Sd Carlos, prefixo 1234", True),
        ("1.3", "Via 190", True),
        ("1.4", "Ordem de serviço determinava patrulhamento no Bairro Santa Rita. COPOM informou denúncia", True),
        ("1.5", "SIM", True),
    ]

    for step_id, answer, should_be_valid in responses:
        is_valid, error = validator.validate(step_id, answer)
        state_machine.store_answer(answer)
        state_machine.next_step()

        print_test(
            f"Chat: {step_id} processado corretamente",
            is_valid == should_be_valid,
            f"Validação: {is_valid}, Esperado: {should_be_valid}. Erro: {error}"
        )

def test_chat_error_recovery():
    """Testa recuperação após erro de validação"""
    session_id, bo_id = setup_test_session()
    session = sessions[session_id]
    state_machine = session["sections"][1]

    validator = ResponseValidator()

    # Tentar resposta inválida
    invalid_answer = "hoje"
    is_valid, error = validator.validate("1.1", invalid_answer)
    print_test(
        "Chat: Rejeita resposta inválida",
        not is_valid,
        "Resposta inválida foi aceita"
    )

    # State machine NÃO deve avançar se resposta é inválida
    state_machine_backup = state_machine.current_step
    # (Não armazenar resposta inválida)

    # Tentar resposta válida
    valid_answer = "22/03/2025, 14h30min, quinta-feira"
    is_valid, error = validator.validate("1.1", valid_answer)
    print_test(
        "Chat: Aceita resposta válida após erro",
        is_valid,
        error
    )

    state_machine.store_answer(valid_answer)
    state_machine.next_step()

    print_test(
        "Chat: State machine avançou após resposta válida",
        state_machine.current_step > state_machine_backup,
        f"Step anterior: {state_machine_backup}, Step atual: {state_machine.current_step}"
    )

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    print(f"{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}TESTES - Endpoint /chat (Integração){Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")

    test_chat_valid_response()
    print()

    test_chat_invalid_response()
    print()

    test_chat_message_flow()
    print()

    test_chat_follow_up_trigger()
    print()

    test_chat_multiple_consecutive()
    print()

    test_chat_error_recovery()
    print()

    print(f"{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}Testes concluídos!{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}")
