# -*- coding: utf-8 -*-
"""
Testes automatizados para validar mudanças v0.6.4
- Renumeração de IDs (2.0-2.7 → 2.1-2.8)
- Endpoint /sync_session
- Lógica de seção pulada

Executar: python test_backend_changes.py
"""
import sys
import os

# Adicionar diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.state_machine_section2 import BOStateMachineSection2, SECTION2_QUESTIONS, SECTION2_STEPS
from backend.validator_section2 import ResponseValidatorSection2, VALIDATION_RULES_SECTION2

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

def test_section2_ids_renumbered():
    """Testa se IDs foram renumerados corretamente"""
    print(f"\n{Colors.BLUE}=== TESTE 1: Renumeração de IDs ==={Colors.END}")

    # Verifica se 2.0 NÃO existe mais
    has_old_id = "2.0" in SECTION2_QUESTIONS
    print_test("ID '2.0' removido", not has_old_id,
               f"Encontrado '2.0' em SECTION2_QUESTIONS" if has_old_id else "")

    # Verifica se 2.1 a 2.8 existem
    expected_ids = ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8"]
    missing_ids = [id for id in expected_ids if id not in SECTION2_QUESTIONS]
    print_test("IDs 2.1-2.8 presentes", len(missing_ids) == 0,
               f"IDs faltando: {missing_ids}" if missing_ids else "")

    # Verifica ordem dos steps
    expected_steps = ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "complete"]
    steps_correct = SECTION2_STEPS == expected_steps
    print_test("SECTION2_STEPS correto", steps_correct,
               f"Esperado: {expected_steps}, Atual: {SECTION2_STEPS}")

    return not has_old_id and len(missing_ids) == 0 and steps_correct

def test_validator_ids_renumbered():
    """Testa se validador foi atualizado"""
    print(f"\n{Colors.BLUE}=== TESTE 2: Validador Renumerado ==={Colors.END}")

    # Verifica se 2.0 NÃO existe mais
    has_old_id = "2.0" in VALIDATION_RULES_SECTION2
    print_test("ID '2.0' removido do validador", not has_old_id)

    # Verifica se 2.1 a 2.8 existem
    expected_ids = ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8"]
    missing_ids = [id for id in expected_ids if id not in VALIDATION_RULES_SECTION2]
    print_test("IDs 2.1-2.8 no validador", len(missing_ids) == 0,
               f"IDs faltando: {missing_ids}" if missing_ids else "")

    # Verifica se 2.1 é a pergunta condicional
    is_conditional = "valid_responses" in VALIDATION_RULES_SECTION2.get("2.1", {})
    print_test("2.1 é pergunta condicional (SIM/NÃO)", is_conditional)

    return not has_old_id and len(missing_ids) == 0 and is_conditional

def test_state_machine_initialization():
    """Testa inicialização da state machine"""
    print(f"\n{Colors.BLUE}=== TESTE 3: State Machine ==={Colors.END}")

    sm = BOStateMachineSection2()

    # Verifica se inicia em 2.1
    starts_at_21 = sm.current_step == "2.1"
    print_test("Inicia em 2.1", starts_at_21,
               f"Atual: {sm.current_step}")

    # Verifica se get_current_question() retorna "Havia veículo?"
    first_q = sm.get_current_question()
    correct_question = first_q == "Havia veículo?"
    print_test("Primeira pergunta correta", correct_question,
               f"Esperado: 'Havia veículo?', Atual: '{first_q}'")

    return starts_at_21 and correct_question

def test_section_skip_logic():
    """Testa lógica de pular seção"""
    print(f"\n{Colors.BLUE}=== TESTE 4: Lógica de Seção Pulada ==={Colors.END}")

    sm = BOStateMachineSection2()

    # Responder "NÃO" na 2.1
    sm.store_answer("NÃO")

    # Verificar se seção foi marcada como pulada
    is_skipped = sm.was_section_skipped()
    print_test("Seção marcada como pulada", is_skipped)

    # Verificar se avançou para "complete"
    sm.next_step()
    is_complete = sm.is_section_complete()
    print_test("Seção completa após 'NÃO'", is_complete,
               f"current_step: {sm.current_step}")

    # Verificar se get_skip_reason() retorna texto
    skip_reason = sm.get_skip_reason()
    has_reason = skip_reason is not None and len(skip_reason) > 0
    print_test("Texto explicativo disponível", has_reason,
               f"Texto: '{skip_reason}'")

    return is_skipped and is_complete and has_reason

def test_section_continue_logic():
    """Testa fluxo normal (responder SIM)"""
    print(f"\n{Colors.BLUE}=== TESTE 5: Fluxo Normal (SIM) ==={Colors.END}")

    sm = BOStateMachineSection2()

    # Responder "SIM" na 2.1
    sm.store_answer("SIM")
    sm.next_step()

    # Verificar se avançou para 2.2
    at_22 = sm.current_step == "2.2"
    print_test("Avançou para 2.2", at_22,
               f"current_step: {sm.current_step}")

    # Verificar que seção NÃO foi pulada
    not_skipped = not sm.was_section_skipped()
    print_test("Seção NÃO pulada", not_skipped)

    # Testar próxima pergunta
    next_q = sm.get_current_question()
    correct_q = "Marca/modelo/cor/placa." in next_q
    print_test("Pergunta 2.2 correta", correct_q,
               f"Pergunta: '{next_q}'")

    return at_22 and not_skipped and correct_q

def test_validator_2_1():
    """Testa validação da pergunta 2.1"""
    print(f"\n{Colors.BLUE}=== TESTE 6: Validação 2.1 ==={Colors.END}")

    # Testar respostas válidas
    valid_responses = ["SIM", "NÃO", "NAO", "S", "N"]
    all_valid = True
    for resp in valid_responses:
        is_valid, _ = ResponseValidatorSection2.validate("2.1", resp)
        if not is_valid:
            all_valid = False
            print_test(f"Validar '{resp}'", False, f"Deveria ser válido")

    print_test("Respostas válidas (SIM/NÃO/S/N)", all_valid)

    # Testar resposta inválida
    is_invalid, error_msg = ResponseValidatorSection2.validate("2.1", "talvez")
    print_test("Rejeita resposta inválida", not is_invalid,
               f"'talvez' deveria ser rejeitado")

    return all_valid and not is_invalid

def test_validator_2_8():
    """Testa validação da pergunta 2.8 (última)"""
    print(f"\n{Colors.BLUE}=== TESTE 7: Validação 2.8 ==={Colors.END}")

    # 2.8 deve aceitar "NÃO" como resposta curta
    is_valid_short, _ = ResponseValidatorSection2.validate("2.8", "NÃO")
    print_test("2.8 aceita 'NÃO' curto", is_valid_short)

    # 2.8 deve aceitar resposta longa
    long_answer = "Veículo furtado, consta no REDS número 12345/2024"
    is_valid_long, _ = ResponseValidatorSection2.validate("2.8", long_answer)
    print_test("2.8 aceita resposta longa", is_valid_long)

    return is_valid_short and is_valid_long

def test_full_flow_with_vehicle():
    """Testa fluxo completo com veículo"""
    print(f"\n{Colors.BLUE}=== TESTE 8: Fluxo Completo (COM veículo) ==={Colors.END}")

    sm = BOStateMachineSection2()

    test_answers = {
        "2.1": "SIM",
        "2.2": "VW Gol branco, placa ABC-1D23",
        "2.3": "Rua das Flores, altura do nº 123",
        "2.4": "O Sargento Lucas viu o veículo em alta velocidade",
        "2.5": "Foi gritado 'Parado, Polícia Militar!' pelo megafone",
        "2.6": "Parou imediatamente",
        "2.7": "O Cabo Nogueira revistou o porta-luvas e encontrou entorpecente",
        "2.8": "NÃO"
    }

    all_valid = True
    for step in ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8"]:
        # Validar
        is_valid, error = ResponseValidatorSection2.validate(step, test_answers[step])
        if not is_valid:
            print_test(f"Validar {step}", False, f"Erro: {error}")
            all_valid = False
            continue

        # Armazenar e avançar
        sm.store_answer(test_answers[step])
        sm.next_step()

    print_test("Todas as 8 respostas válidas", all_valid)

    # Verificar se chegou ao fim
    is_complete = sm.is_section_complete()
    print_test("Seção completa após 8 respostas", is_complete)

    # Verificar que NÃO foi pulada
    not_skipped = not sm.was_section_skipped()
    print_test("Seção NÃO foi pulada", not_skipped)

    return all_valid and is_complete and not_skipped

def main():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}  TESTES AUTOMATIZADOS - BACKEND v0.6.4{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

    tests = [
        ("Renumeração de IDs", test_section2_ids_renumbered),
        ("Validador Renumerado", test_validator_ids_renumbered),
        ("State Machine Init", test_state_machine_initialization),
        ("Lógica Seção Pulada", test_section_skip_logic),
        ("Fluxo Normal (SIM)", test_section_continue_logic),
        ("Validação 2.1", test_validator_2_1),
        ("Validação 2.8", test_validator_2_8),
        ("Fluxo Completo", test_full_flow_with_vehicle),
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
        print(f"{Colors.GREEN}Backend esta pronto para o frontend.{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}*** {total - passed} teste(s) falharam ***{Colors.END}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
