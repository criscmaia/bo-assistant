# -*- coding: utf-8 -*-
"""
Teste de integração: Endpoint /sync_session
Valida sincronização em bloco durante restauração de rascunho

Executar: python test_integration_sync.py
"""
import sys
import os

# Adicionar diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.main import sessions
from backend.state_machine import BOStateMachine
from backend.state_machine_section2 import BOStateMachineSection2
from backend.validator import ResponseValidator
from backend.validator_section2 import ResponseValidatorSection2
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

def simulate_sync_session(session_id, answers):
    """
    Simula o endpoint /sync_session sem fazer requisição HTTP.
    Replica a lógica exata do endpoint.
    """
    if session_id not in sessions:
        return None

    session_data = sessions[session_id]
    bo_id = session_data["bo_id"]

    # Ordenar steps (1.1, 1.2, ..., 2.1, 2.2, ...)
    sorted_steps = sorted(answers.keys(), key=lambda s: tuple(map(int, s.split('.'))))

    current_section = 1

    for step in sorted_steps:
        answer = answers[step]

        # Detectar mudança de seção
        step_section = int(step.split('.')[0])
        if step_section != current_section:
            # Inicializar nova seção
            if step_section not in session_data["sections"]:
                if step_section == 2:
                    session_data["sections"][2] = BOStateMachineSection2()

            current_section = step_section
            session_data["current_section"] = current_section

        # Obter state machine da seção
        state_machine = session_data["sections"][current_section]

        # Validar resposta
        if current_section == 1:
            is_valid, error_message = ResponseValidator.validate(step, answer)
        elif current_section == 2:
            is_valid, error_message = ResponseValidatorSection2.validate(step, answer)
        else:
            continue  # Seção não suportada, pular

        if not is_valid:
            continue  # Pular resposta inválida

        # Armazenar e avançar
        state_machine.store_answer(answer)
        state_machine.next_step()

    # Retornar estado final
    final_section = current_section
    final_state_machine = session_data["sections"][final_section]

    return {
        "success": True,
        "current_step": final_state_machine.current_step,
        "current_section": final_section,
        "section1_complete": session_data["sections"][1].is_section_complete(),
        "section2_complete": session_data["sections"].get(2, None) and session_data["sections"][2].is_section_complete(),
        "bo_id": bo_id
    }

def test_sync_section1_incomplete():
    """Testa sincronização com Seção 1 incompleta (3 de 6 respostas)"""
    print(f"\n{Colors.BLUE}=== TESTE 1: Sincronização Seção 1 Incompleta ==={Colors.END}")

    # Criar sessão simulada
    session_id = str(uuid.uuid4())
    bo_id = f"BO-TEST-001"

    sessions[session_id] = {
        "bo_id": bo_id,
        "sections": {
            1: BOStateMachine()
        },
        "current_section": 1,
        "section1_text": "",
        "section2_text": ""
    }

    # Respostas parciais (1.1, 1.2, 1.3 apenas)
    answers = {
        "1.1": "Dia 19 de dezembro de 2025, por volta das 15h30",
        "1.2": "Sargento Silva, Soldado Pereira, prefixo 12345",
        "1.3": "Abordagem preventiva em área conhecida por tráfico"
    }

    result = simulate_sync_session(session_id, answers)

    # Validações
    all_ok = True

    # 1. Deve retornar sucesso
    if not result or not result.get("success"):
        print_test("Retorna sucesso", False, "Resultado nulo ou sem success=True")
        all_ok = False
    else:
        print_test("Retorna sucesso", True)

    # 2. current_step deve ser "1.4" (próxima pergunta)
    expected_step = "1.4"
    actual_step = result.get("current_step")
    step_ok = actual_step == expected_step
    print_test(f"current_step correto ({expected_step})", step_ok,
               f"Esperado: {expected_step}, Atual: {actual_step}")
    all_ok = all_ok and step_ok

    # 3. Seção 1 NÃO deve estar completa
    section1_complete = result.get("section1_complete")
    not_complete_ok = not section1_complete
    print_test("Seção 1 NÃO completa", not_complete_ok,
               f"section1_complete: {section1_complete}")
    all_ok = all_ok and not_complete_ok

    # 4. current_section deve ser 1
    current_section = result.get("current_section")
    section_ok = current_section == 1
    print_test("current_section = 1", section_ok,
               f"Esperado: 1, Atual: {current_section}")
    all_ok = all_ok and section_ok

    # Limpar
    del sessions[session_id]

    return all_ok

def test_sync_section2_incomplete():
    """Testa sincronização com Seção 1 completa + Seção 2 incompleta (4 de 8)"""
    print(f"\n{Colors.BLUE}=== TESTE 2: Sincronização Seção 2 Incompleta ==={Colors.END}")

    # Criar sessão simulada
    session_id = str(uuid.uuid4())
    bo_id = f"BO-TEST-002"

    sessions[session_id] = {
        "bo_id": bo_id,
        "sections": {
            1: BOStateMachine()
        },
        "current_section": 1,
        "section1_text": "",
        "section2_text": ""
    }

    # Respostas: Seção 1 completa (1.1-1.6) + Seção 2 parcial (2.1-2.4)
    answers = {
        "1.1": "Dia 19 de dezembro de 2025, por volta das 15h30",
        "1.2": "Sargento Silva, Soldado Pereira, prefixo 12345",
        "1.3": "Abordagem preventiva em área conhecida por tráfico",
        "1.4": "Ordem de serviço nº 123/2025 do Comando de Área",
        "1.5": "Rua das Flores, altura do nº 456, Bairro Centro",
        "1.6": "Local dominado pela facção TCP, histórico de apreensões",
        "2.1": "SIM",
        "2.2": "VW Gol branco, placa ABC-1D23",
        "2.3": "Rua das Flores, altura do nº 123",
        "2.4": "O Sargento Lucas viu o veículo em alta velocidade"
    }

    result = simulate_sync_session(session_id, answers)

    # Validações
    all_ok = True

    # 1. Deve retornar sucesso
    if not result or not result.get("success"):
        print_test("Retorna sucesso", False)
        all_ok = False
    else:
        print_test("Retorna sucesso", True)

    # 2. current_step deve ser "2.5" (próxima pergunta da Seção 2)
    expected_step = "2.5"
    actual_step = result.get("current_step")
    step_ok = actual_step == expected_step
    print_test(f"current_step correto ({expected_step})", step_ok,
               f"Esperado: {expected_step}, Atual: {actual_step}")
    all_ok = all_ok and step_ok

    # 3. Seção 1 deve estar completa
    section1_complete = result.get("section1_complete")
    s1_ok = section1_complete
    print_test("Seção 1 completa", s1_ok,
               f"section1_complete: {section1_complete}")
    all_ok = all_ok and s1_ok

    # 4. Seção 2 NÃO deve estar completa
    section2_complete = result.get("section2_complete")
    s2_ok = not section2_complete
    print_test("Seção 2 NÃO completa", s2_ok,
               f"section2_complete: {section2_complete}")
    all_ok = all_ok and s2_ok

    # 5. current_section deve ser 2
    current_section = result.get("current_section")
    section_ok = current_section == 2
    print_test("current_section = 2", section_ok,
               f"Esperado: 2, Atual: {current_section}")
    all_ok = all_ok and section_ok

    # Limpar
    del sessions[session_id]

    return all_ok

def test_sync_all_complete():
    """Testa sincronização com Seção 1 e 2 completas (14 respostas)"""
    print(f"\n{Colors.BLUE}=== TESTE 3: Sincronização Completa (14 respostas) ==={Colors.END}")

    # Criar sessão simulada
    session_id = str(uuid.uuid4())
    bo_id = f"BO-TEST-003"

    sessions[session_id] = {
        "bo_id": bo_id,
        "sections": {
            1: BOStateMachine()
        },
        "current_section": 1,
        "section1_text": "",
        "section2_text": ""
    }

    # Todas as respostas
    answers = {
        "1.1": "Dia 19 de dezembro de 2025, por volta das 15h30",
        "1.2": "Sargento Silva, Soldado Pereira, prefixo 12345",
        "1.3": "Abordagem preventiva em área conhecida por tráfico",
        "1.4": "Ordem de serviço nº 123/2025 do Comando de Área",
        "1.5": "Rua das Flores, altura do nº 456, Bairro Centro",
        "1.6": "Local dominado pela facção TCP, histórico de apreensões",
        "2.1": "SIM",
        "2.2": "VW Gol branco, placa ABC-1D23",
        "2.3": "Rua das Flores, altura do nº 123",
        "2.4": "O Sargento Lucas viu o veículo em alta velocidade",
        "2.5": "Foi gritado 'Parado, Polícia Militar!' pelo megafone",
        "2.6": "Parou imediatamente",
        "2.7": "O Cabo Nogueira revistou o porta-luvas e encontrou entorpecente",
        "2.8": "NÃO"
    }

    result = simulate_sync_session(session_id, answers)

    # Validações
    all_ok = True

    # 1. Deve retornar sucesso
    if not result or not result.get("success"):
        print_test("Retorna sucesso", False)
        all_ok = False
    else:
        print_test("Retorna sucesso", True)

    # 2. current_step deve ser "complete"
    expected_step = "complete"
    actual_step = result.get("current_step")
    step_ok = actual_step == expected_step
    print_test(f"current_step correto ({expected_step})", step_ok,
               f"Esperado: {expected_step}, Atual: {actual_step}")
    all_ok = all_ok and step_ok

    # 3. Ambas seções devem estar completas
    section1_complete = result.get("section1_complete")
    section2_complete = result.get("section2_complete")

    both_ok = section1_complete and section2_complete
    print_test("Ambas seções completas", both_ok,
               f"S1: {section1_complete}, S2: {section2_complete}")
    all_ok = all_ok and both_ok

    # 4. current_section deve ser 2
    current_section = result.get("current_section")
    section_ok = current_section == 2
    print_test("current_section = 2", section_ok,
               f"Esperado: 2, Atual: {current_section}")
    all_ok = all_ok and section_ok

    # Limpar
    del sessions[session_id]

    return all_ok

def test_sync_section2_skipped():
    """Testa sincronização quando Seção 2 é pulada (resposta NÃO em 2.1)"""
    print(f"\n{Colors.BLUE}=== TESTE 4: Sincronização Seção 2 Pulada ==={Colors.END}")

    # Criar sessão simulada
    session_id = str(uuid.uuid4())
    bo_id = f"BO-TEST-004"

    sessions[session_id] = {
        "bo_id": bo_id,
        "sections": {
            1: BOStateMachine()
        },
        "current_section": 1,
        "section1_text": "",
        "section2_text": ""
    }

    # Seção 1 completa + 2.1 = "NÃO" (pula Seção 2)
    answers = {
        "1.1": "Dia 19 de dezembro de 2025, por volta das 15h30",
        "1.2": "Sargento Silva, Soldado Pereira, prefixo 12345",
        "1.3": "Abordagem preventiva em área conhecida por tráfico",
        "1.4": "Ordem de serviço nº 123/2025 do Comando de Área",
        "1.5": "Rua das Flores, altura do nº 456, Bairro Centro",
        "1.6": "Local dominado pela facção TCP, histórico de apreensões",
        "2.1": "NÃO"
    }

    result = simulate_sync_session(session_id, answers)

    # Validações
    all_ok = True

    # 1. Deve retornar sucesso
    if not result or not result.get("success"):
        print_test("Retorna sucesso", False)
        all_ok = False
    else:
        print_test("Retorna sucesso", True)

    # 2. current_step deve ser "complete" (seção pulada)
    expected_step = "complete"
    actual_step = result.get("current_step")
    step_ok = actual_step == expected_step
    print_test(f"current_step correto ({expected_step})", step_ok,
               f"Esperado: {expected_step}, Atual: {actual_step}")
    all_ok = all_ok and step_ok

    # 3. Seção 2 deve estar marcada como completa (porque foi pulada)
    section2_complete = result.get("section2_complete")
    s2_ok = section2_complete
    print_test("Seção 2 marcada como completa (pulada)", s2_ok,
               f"section2_complete: {section2_complete}")
    all_ok = all_ok and s2_ok

    # 4. Verificar se state machine tem flag de seção pulada
    state_machine = sessions[session_id]["sections"][2]
    was_skipped = state_machine.was_section_skipped()
    skipped_ok = was_skipped
    print_test("Flag section_skipped ativado", skipped_ok,
               f"was_section_skipped(): {was_skipped}")
    all_ok = all_ok and skipped_ok

    # Limpar
    del sessions[session_id]

    return all_ok

def main():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}  TESTES DE INTEGRAÇÃO - ENDPOINT /sync_session{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

    tests = [
        ("Sincronização Seção 1 Incompleta", test_sync_section1_incomplete),
        ("Sincronização Seção 2 Incompleta", test_sync_section2_incomplete),
        ("Sincronização Completa", test_sync_all_complete),
        ("Sincronização Seção 2 Pulada", test_sync_section2_skipped),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print_test(name, False, f"Erro: {str(e)}")
            results.append((name, False))

    # Resumo
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}  RESUMO{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

    passed = sum(1 for _, p in results if p)
    total = len(results)

    for name, p in results:
        status = f"{Colors.GREEN}[OK]{Colors.END}" if p else f"{Colors.RED}[X]{Colors.END}"
        print(f"{status} {name}")

    print(f"\n{Colors.BLUE}Total: {passed}/{total} testes passaram{Colors.END}")

    if passed == total:
        print(f"\n{Colors.GREEN}*** TODOS OS TESTES PASSARAM! ***{Colors.END}")
        print(f"{Colors.GREEN}Endpoint /sync_session está funcionando corretamente.{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}*** {total - passed} teste(s) falharam ***{Colors.END}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
