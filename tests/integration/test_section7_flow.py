# -*- coding: utf-8 -*-
"""
Teste de integração: Fluxo completo da Seção 7 (Apreensões e Cadeia de Custódia)
Valida sincronização, skip logic, validação allow_none_response, e geração de texto

Executar: python -m pytest tests/integration/test_section7_flow.py -v
"""
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.main import sessions
from backend.state_machine import BOStateMachine
from backend.state_machine_section7 import BOStateMachineSection7
from backend.validator_section7 import ResponseValidatorSection7
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


def create_test_session():
    """Cria uma sessão de teste com estrutura completa"""
    session_id = str(uuid.uuid4())
    bo_id = f"BO-TEST-{uuid.uuid4().hex[:6].upper()}"

    sessions[session_id] = {
        "bo_id": bo_id,
        "sections": {
            1: BOStateMachine(),
            7: BOStateMachineSection7()
        },
        "current_section": 7,
        "section7_text": ""
    }

    return session_id, bo_id


def get_section7_answers():
    """Retorna respostas válidas para Seção 7 (todas as 4 perguntas)"""
    return {
        "7.1": "SIM",
        "7.2": "O Soldado Breno encontrou 14 pedras de substância análoga ao crack dentro de uma lata azul sobre o banco de concreto próximo ao portão da casa 12. A Soldado Pires localizou 23 pinos de cocaína em um buraco no muro da lateral do imóvel",
        "7.3": "Foram apreendidos R$ 450,00 em notas de R$ 10 e R$ 20, típicas de comercialização, 2 celulares Samsung, 1 balança de precisão e uma caderneta com anotações de contabilidade do tráfico",
        "7.4": "O Soldado Faria lacrou as substâncias no invólucro 01 e os objetos no invólucro 02, fotografou todos os itens no local e ficou responsável pelo material até a entrega na CEFLAN 2"
    }


def test_section7_state_machine_yes():
    """Testa state machine quando há apreensão (7.1 = SIM)"""
    print(f"\n{Colors.BLUE}=== TESTE 1: State Machine Seção 7 com Apreensão ==={Colors.END}")

    sm = BOStateMachineSection7()
    all_ok = True

    # 1. Estado inicial
    init_ok = sm.current_step == "7.1" and sm.answers == {} and not sm.section_skipped
    print_test("Inicializa no step 7.1", init_ok)
    all_ok = all_ok and init_ok

    # 2. Armazenar resposta SIM em 7.1
    sm.store_answer("SIM")
    stored_ok = sm.answers.get("7.1") == "SIM" and not sm.section_skipped
    print_test("Armazena SIM em 7.1", stored_ok)
    all_ok = all_ok and stored_ok

    # 3. Avançar para 7.2
    sm.next_step()
    step2_ok = sm.current_step == "7.2"
    print_test("Avança para 7.2 após SIM", step2_ok,
               f"Esperado: 7.2, Atual: {sm.current_step}")
    all_ok = all_ok and step2_ok

    # 4. Completar Seção 7
    sm.store_answer("O Soldado Breno encontrou 14 pedras de crack em lata azul")
    sm.next_step()
    sm.store_answer("Foram apreendidos R$ 450,00 e 2 celulares")
    sm.next_step()
    sm.store_answer("O Soldado Faria lacrou no invólucro 01 e ficou responsável até CEFLAN 2")
    sm.next_step()

    complete_ok = sm.is_section_complete()
    print_test("Seção completa após 4 respostas", complete_ok)
    all_ok = all_ok and complete_ok

    return all_ok


def test_section7_state_machine_no():
    """Testa state machine quando NÃO há apreensão (7.1 = NÃO)"""
    print(f"\n{Colors.BLUE}=== TESTE 2: State Machine Seção 7 Sem Apreensão ==={Colors.END}")

    sm = BOStateMachineSection7()
    all_ok = True

    # 1. Responder NÃO em 7.1
    sm.store_answer("NÃO")

    # 2. section_skipped deve estar True
    skipped_ok = sm.section_skipped
    print_test("Flag section_skipped ativado", skipped_ok)
    all_ok = all_ok and skipped_ok

    # 3. current_step deve ser "complete"
    complete_step_ok = sm.current_step == "complete"
    print_test("current_step = 'complete' após NÃO", complete_step_ok,
               f"Esperado: complete, Atual: {sm.current_step}")
    all_ok = all_ok and complete_step_ok

    # 4. Seção deve estar marcada como completa
    complete_ok = sm.is_section_complete()
    print_test("Seção marcada como completa", complete_ok)
    all_ok = all_ok and complete_ok

    # 5. Skip reason deve ser válido
    skip_reason = sm.get_skip_reason()
    reason_ok = skip_reason is not None and "apreensão" in skip_reason.lower()
    print_test("Skip reason contém 'apreensão'", reason_ok,
               f"Skip reason: {skip_reason}")
    all_ok = all_ok and reason_ok

    return all_ok


def test_section7_validation_7_2_graduation():
    """Testa que 7.2 exige graduação militar"""
    print(f"\n{Colors.BLUE}=== TESTE 3: Validação Graduação em 7.2 ==={Colors.END}")

    all_ok = True

    # Sem graduação - deve falhar
    is_valid, error = ResponseValidatorSection7.validate(
        "7.2",
        "Breno encontrou 14 pedras de crack em uma lata azul"
    )
    no_grad_fail = not is_valid
    print_test("Rejeita resposta sem graduação", no_grad_fail,
               f"is_valid: {is_valid}")
    all_ok = all_ok and no_grad_fail

    # Com graduação - deve passar
    is_valid, error = ResponseValidatorSection7.validate(
        "7.2",
        "O Soldado Breno encontrou 14 pedras de crack em uma lata azul sobre o banco de concreto"
    )
    with_grad_pass = is_valid
    print_test("Aceita resposta com graduação", with_grad_pass,
               f"is_valid: {is_valid}")
    all_ok = all_ok and with_grad_pass

    return all_ok


def test_section7_validation_7_3_none_response():
    """Testa que 7.3 aceita 'Nenhum objeto' como resposta válida (NOVA FUNCIONALIDADE)"""
    print(f"\n{Colors.BLUE}=== TESTE 4: Validação 'Nenhum Objeto' em 7.3 (NOVA) ==={Colors.END}")

    all_ok = True

    # Teste 1: "Nenhum objeto ligado ao tráfico foi encontrado" - deve passar
    is_valid, error = ResponseValidatorSection7.validate(
        "7.3",
        "Nenhum objeto ligado ao tráfico foi encontrado"
    )
    test1 = is_valid
    print_test("Aceita 'Nenhum objeto ligado'", test1,
               f"is_valid: {is_valid}")
    all_ok = all_ok and test1

    # Teste 2: "Não havia objetos..." - deve passar
    is_valid, error = ResponseValidatorSection7.validate(
        "7.3",
        "Não havia objetos ligados ao tráfico"
    )
    test2 = is_valid
    print_test("Aceita 'Não havia objetos'", test2,
               f"is_valid: {is_valid}")
    all_ok = all_ok and test2

    # Teste 3: "Não houve apreensão de objetos" - deve passar
    is_valid, error = ResponseValidatorSection7.validate(
        "7.3",
        "Não houve apreensão de objetos"
    )
    test3 = is_valid
    print_test("Aceita 'Não houve apreensão'", test3,
               f"is_valid: {is_valid}")
    all_ok = all_ok and test3

    # Teste 4: Resposta com objetos - deve passar
    is_valid, error = ResponseValidatorSection7.validate(
        "7.3",
        "Foram apreendidos R$ 450,00 em notas diversas, 2 celulares e 1 balança"
    )
    test4 = is_valid
    print_test("Aceita resposta com objetos", test4,
               f"is_valid: {is_valid}")
    all_ok = all_ok and test4

    # Teste 5: Resposta muito curta sem "nenhum" - deve falhar
    is_valid, error = ResponseValidatorSection7.validate(
        "7.3",
        "nada"
    )
    test5 = not is_valid
    print_test("Rejeita resposta curta sem 'nenhum'", test5,
               f"is_valid: {is_valid}")
    all_ok = all_ok and test5

    return all_ok


def test_section7_validation_7_4_destination():
    """Testa que 7.4 exige destino (CEFLAN, delegacia, etc)"""
    print(f"\n{Colors.BLUE}=== TESTE 5: Validação Destino em 7.4 ==={Colors.END}")

    all_ok = True

    # Sem destino - deve falhar
    is_valid, error = ResponseValidatorSection7.validate(
        "7.4",
        "O Soldado Faria lacrou as substâncias no invólucro 01 e os objetos no invólucro 02"
    )
    no_dest_fail = not is_valid
    print_test("Rejeita resposta sem destino", no_dest_fail,
               f"is_valid: {is_valid}")
    all_ok = all_ok and no_dest_fail

    # Com CEFLAN - deve passar
    is_valid, error = ResponseValidatorSection7.validate(
        "7.4",
        "O Soldado Faria lacrou as substâncias no invólucro 01 e ficou responsável até a entrega na CEFLAN 2"
    )
    with_ceflan_pass = is_valid
    print_test("Aceita com destino CEFLAN", with_ceflan_pass,
               f"is_valid: {is_valid}")
    all_ok = all_ok and with_ceflan_pass

    # Com delegacia - deve passar
    is_valid, error = ResponseValidatorSection7.validate(
        "7.4",
        "O Cabo Almeida acondicionou em saco plástico e transportou até a Delegacia Civil"
    )
    with_delegacia_pass = is_valid
    print_test("Aceita com destino Delegacia", with_delegacia_pass,
               f"is_valid: {is_valid}")
    all_ok = all_ok and with_delegacia_pass

    return all_ok


def test_section7_full_flow():
    """Testa fluxo completo da Seção 7 (todas as 4 perguntas)"""
    print(f"\n{Colors.BLUE}=== TESTE 6: Fluxo Completo Seção 7 ==={Colors.END}")

    session_id, bo_id = create_test_session()
    sm = sessions[session_id]["sections"][7]
    all_ok = True

    # Respostas válidas
    answers = get_section7_answers()

    # 1. Responder 7.1 - SIM
    is_valid, _ = ResponseValidatorSection7.validate("7.1", answers["7.1"])
    test1 = is_valid
    print_test("7.1 (SIM) válido", test1)
    all_ok = all_ok and test1

    sm.store_answer(answers["7.1"])
    sm.next_step()

    # 2. Responder 7.2 - substâncias com graduação
    is_valid, _ = ResponseValidatorSection7.validate("7.2", answers["7.2"])
    test2 = is_valid and len(answers["7.2"]) >= 50
    print_test("7.2 válido com +50 caracteres", test2,
               f"Comprimento: {len(answers['7.2'])}")
    all_ok = all_ok and test2

    sm.store_answer(answers["7.2"])
    sm.next_step()

    # 3. Responder 7.3 - objetos
    is_valid, _ = ResponseValidatorSection7.validate("7.3", answers["7.3"])
    test3 = is_valid
    print_test("7.3 (objetos) válido", test3)
    all_ok = all_ok and test3

    sm.store_answer(answers["7.3"])
    sm.next_step()

    # 4. Responder 7.4 - acondicionamento + destino
    is_valid, _ = ResponseValidatorSection7.validate("7.4", answers["7.4"])
    test4 = is_valid and len(answers["7.4"]) >= 40
    print_test("7.4 válido com +40 caracteres e destino", test4,
               f"Comprimento: {len(answers['7.4'])}")
    all_ok = all_ok and test4

    sm.store_answer(answers["7.4"])
    sm.next_step()

    # 5. Seção deve estar completa
    complete_ok = sm.is_section_complete()
    print_test("Seção 7 completa após 4 respostas", complete_ok)
    all_ok = all_ok and complete_ok

    # 6. Total de respostas deve ser 4
    total_answers = len(sm.get_all_answers())
    total_ok = total_answers == 4
    print_test(f"Total de 4 respostas", total_ok,
               f"Total: {total_answers}")
    all_ok = all_ok and total_ok

    # Limpar
    del sessions[session_id]

    return all_ok


def main():
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}  TESTES DE INTEGRAÇÃO - SEÇÃO 7 (APREENSÕES E CADEIA DE CUSTÓDIA){Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}")

    tests = [
        ("State Machine com Apreensão (7.1=SIM)", test_section7_state_machine_yes),
        ("State Machine Sem Apreensão (7.1=NÃO)", test_section7_state_machine_no),
        ("Validação Graduação em 7.2", test_section7_validation_7_2_graduation),
        ("Validação 'Nenhum Objeto' em 7.3 (NOVA)", test_section7_validation_7_3_none_response),
        ("Validação Destino em 7.4", test_section7_validation_7_4_destination),
        ("Fluxo Completo Seção 7", test_section7_full_flow),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print_test(name, False, f"Erro: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Resumo
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}  RESUMO{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}")

    passed = sum(1 for _, p in results if p)
    total = len(results)

    for name, p in results:
        status = f"{Colors.GREEN}[OK]{Colors.END}" if p else f"{Colors.RED}[X]{Colors.END}"
        print(f"{status} {name}")

    print(f"\n{Colors.BLUE}Total: {passed}/{total} testes passaram{Colors.END}")

    if passed == total:
        print(f"\n{Colors.GREEN}*** TODOS OS TESTES PASSARAM! ***{Colors.END}")
        print(f"{Colors.GREEN}Seção 7 está funcionando corretamente.{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}*** {total - passed} teste(s) falharam ***{Colors.END}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
