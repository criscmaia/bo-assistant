# -*- coding: utf-8 -*-
"""
Teste de integração: Fluxo completo da Seção 3 (Campana - Vigilância Velada)
Valida sincronização, skip logic e geração de texto

Executar: python -m pytest tests/integration/test_section3_flow.py -v
"""
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.main import sessions
from backend.state_machine import BOStateMachine
from backend.state_machine_section2 import BOStateMachineSection2
from backend.state_machine_section3 import BOStateMachineSection3
from backend.validator import ResponseValidator
from backend.validator_section2 import ResponseValidatorSection2
from backend.validator_section3 import ResponseValidatorSection3
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
    Simula o endpoint /sync_session para Seções 1, 2 e 3.
    Replica a lógica exata do endpoint.
    """
    if session_id not in sessions:
        return None

    session_data = sessions[session_id]
    bo_id = session_data["bo_id"]

    # Ordenar steps (1.1, 1.2, ..., 2.1, 2.2, ..., 3.1, 3.2, ...)
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
                elif step_section == 3:
                    session_data["sections"][3] = BOStateMachineSection3()

            current_section = step_section
            session_data["current_section"] = current_section

        # Obter state machine da seção
        state_machine = session_data["sections"][current_section]

        # Validar resposta
        if current_section == 1:
            is_valid, error_message = ResponseValidator.validate(step, answer)
        elif current_section == 2:
            is_valid, error_message = ResponseValidatorSection2.validate(step, answer)
        elif current_section == 3:
            is_valid, error_message = ResponseValidatorSection3.validate(step, answer)
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
        "section3_complete": session_data["sections"].get(3, None) and session_data["sections"][3].is_section_complete(),
        "bo_id": bo_id
    }


def create_test_session():
    """Cria uma sessão de teste com estrutura completa"""
    session_id = str(uuid.uuid4())
    bo_id = f"BO-TEST-{uuid.uuid4().hex[:6].upper()}"

    sessions[session_id] = {
        "bo_id": bo_id,
        "sections": {
            1: BOStateMachine()
        },
        "current_section": 1,
        "section1_text": "",
        "section2_text": "",
        "section3_text": ""
    }

    return session_id, bo_id


def get_section1_answers():
    """Retorna respostas válidas para Seção 1 (6 perguntas)"""
    return {
        "1.1": "Dia 21 de dezembro de 2025, por volta das 15h30",
        "1.2": "Sargento Silva, Soldado Pereira, prefixo 12345",
        "1.3": "Abordagem preventiva em área conhecida por tráfico",
        "1.4": "Ordem de serviço número 123/2025 do Comando de Área",
        "1.5": "Rua das Flores, altura do número 456, Bairro Centro",
        "1.6": "Local dominado pela facção TCP, histórico de apreensões"
    }


def get_section2_answers():
    """Retorna respostas válidas para Seção 2 (8 perguntas)"""
    return {
        "2.1": "SIM",
        "2.2": "VW Gol branco, placa ABC-1D23",
        "2.3": "Rua das Flores, altura do número 123",
        "2.4": "O Sargento Silva viu o veículo em alta velocidade",
        "2.5": "Foi gritado 'Parado, Polícia Militar!' pelo megafone",
        "2.6": "Parou imediatamente após ordem de parada",
        "2.7": "O Cabo Almeida revistou o porta-luvas e encontrou entorpecente",
        "2.8": "NÃO"
    }


def get_section3_answers():
    """Retorna respostas válidas para Seção 3 (8 perguntas)"""
    return {
        "3.1": "SIM",
        "3.2": "Esquina da Rua das Flores com Avenida Brasil, atrás do muro da casa 145, a aproximadamente 30 metros do bar do João",
        "3.3": "O Sargento Silva tinha visão desobstruída da porta do bar. O Cabo Almeida observava a lateral do estabelecimento pela janela da viatura.",
        "3.4": "Denúncia anônima recebida via COPOM informando comercialização de drogas no local há pelo menos 3 meses",
        "3.5": "15 minutos de vigilância contínua atrás do muro da casa 145",
        "3.6": "Foi observado um homem de camiseta vermelha retirando pequenos invólucros de uma mochila preta e entregando a dois indivíduos que chegaram de motocicleta. Após receberem os invólucros, os indivíduos entregaram dinheiro ao homem de vermelho.",
        "3.7": "Sim, foi abordado um usuário que estava saindo do local. Ele portava 2 porções de substância análoga à cocaína e relatou ter comprado do 'cara de vermelho' por R$ 50,00.",
        "3.8": "Sim, ao perceber a movimentação policial, o homem de vermelho correu para o beco ao lado do bar, tentando fugir em direção à Rua Sete."
    }


def test_sync_section3_incomplete():
    """Testa sincronização com Seção 3 incompleta (Seção 1+2 completas + 3 perguntas da Seção 3)"""
    print(f"\n{Colors.BLUE}=== TESTE 1: Sincronização Seção 3 Incompleta ==={Colors.END}")

    session_id, bo_id = create_test_session()

    # Respostas: Seção 1 completa + Seção 2 completa + Seção 3 parcial (3.1-3.4)
    answers = {
        **get_section1_answers(),
        **get_section2_answers(),
        "3.1": "SIM",
        "3.2": "Esquina da Rua das Flores com Avenida Brasil, atrás do muro da casa 145, a aproximadamente 30 metros do bar",
        "3.3": "O Sargento Silva tinha visão desobstruída da porta do bar. O Cabo Almeida observava a lateral.",
        "3.4": "Denúncia anônima recebida via COPOM informando comercialização de drogas no local"
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

    # 2. current_step deve ser "3.5" (próxima pergunta)
    expected_step = "3.5"
    actual_step = result.get("current_step")
    step_ok = actual_step == expected_step
    print_test(f"current_step correto ({expected_step})", step_ok,
               f"Esperado: {expected_step}, Atual: {actual_step}")
    all_ok = all_ok and step_ok

    # 3. Seções 1 e 2 devem estar completas
    s1_complete = result.get("section1_complete")
    s2_complete = result.get("section2_complete")
    s1_s2_ok = s1_complete and s2_complete
    print_test("Seções 1 e 2 completas", s1_s2_ok,
               f"S1: {s1_complete}, S2: {s2_complete}")
    all_ok = all_ok and s1_s2_ok

    # 4. Seção 3 NÃO deve estar completa
    s3_complete = result.get("section3_complete")
    s3_ok = not s3_complete
    print_test("Seção 3 NÃO completa", s3_ok,
               f"section3_complete: {s3_complete}")
    all_ok = all_ok and s3_ok

    # 5. current_section deve ser 3
    current_section = result.get("current_section")
    section_ok = current_section == 3
    print_test("current_section = 3", section_ok,
               f"Esperado: 3, Atual: {current_section}")
    all_ok = all_ok and section_ok

    # Limpar
    del sessions[session_id]

    return all_ok


def test_sync_all_three_sections_complete():
    """Testa sincronização com todas as 3 seções completas (22 respostas)"""
    print(f"\n{Colors.BLUE}=== TESTE 2: Sincronização Completa (Seções 1+2+3) ==={Colors.END}")

    session_id, bo_id = create_test_session()

    # Todas as respostas
    answers = {
        **get_section1_answers(),
        **get_section2_answers(),
        **get_section3_answers()
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

    # 3. Todas as seções devem estar completas
    s1_complete = result.get("section1_complete")
    s2_complete = result.get("section2_complete")
    s3_complete = result.get("section3_complete")

    all_complete = s1_complete and s2_complete and s3_complete
    print_test("Todas as 3 seções completas", all_complete,
               f"S1: {s1_complete}, S2: {s2_complete}, S3: {s3_complete}")
    all_ok = all_ok and all_complete

    # 4. current_section deve ser 3
    current_section = result.get("current_section")
    section_ok = current_section == 3
    print_test("current_section = 3", section_ok,
               f"Esperado: 3, Atual: {current_section}")
    all_ok = all_ok and section_ok

    # 5. Verificar total de respostas
    sm3 = sessions[session_id]["sections"][3]
    total_answers = len(sm3.get_all_answers())
    answers_ok = total_answers == 8
    print_test(f"Seção 3 com 8 respostas", answers_ok,
               f"Total: {total_answers}")
    all_ok = all_ok and answers_ok

    # Limpar
    del sessions[session_id]

    return all_ok


def test_sync_section3_skipped():
    """Testa sincronização quando Seção 3 é pulada (resposta NÃO em 3.1)"""
    print(f"\n{Colors.BLUE}=== TESTE 3: Sincronização Seção 3 Pulada ==={Colors.END}")

    session_id, bo_id = create_test_session()

    # Seções 1 e 2 completas + 3.1 = "NÃO" (pula Seção 3)
    answers = {
        **get_section1_answers(),
        **get_section2_answers(),
        "3.1": "NÃO"
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

    # 3. Seção 3 deve estar marcada como completa (porque foi pulada)
    s3_complete = result.get("section3_complete")
    s3_ok = s3_complete
    print_test("Seção 3 marcada como completa (pulada)", s3_ok,
               f"section3_complete: {s3_complete}")
    all_ok = all_ok and s3_ok

    # 4. Verificar se state machine tem flag de seção pulada
    state_machine = sessions[session_id]["sections"][3]
    was_skipped = state_machine.was_section_skipped()
    skipped_ok = was_skipped
    print_test("Flag section_skipped ativado", skipped_ok,
               f"was_section_skipped(): {was_skipped}")
    all_ok = all_ok and skipped_ok

    # 5. Verificar skip_reason
    skip_reason = state_machine.get_skip_reason()
    reason_ok = skip_reason is not None and "campana" in skip_reason.lower()
    print_test("Skip reason correto", reason_ok,
               f"get_skip_reason(): {skip_reason}")
    all_ok = all_ok and reason_ok

    # Limpar
    del sessions[session_id]

    return all_ok


def test_section3_validation_graduation():
    """Testa que pergunta 3.3 exige graduação militar"""
    print(f"\n{Colors.BLUE}=== TESTE 4: Validação Graduação Militar (3.3) ==={Colors.END}")

    all_ok = True

    # Sem graduação - deve falhar
    is_valid, error = ResponseValidatorSection3.validate("3.3", "João viu a porta do bar claramente")
    no_grad_fail = not is_valid
    print_test("Rejeita resposta sem graduação", no_grad_fail,
               f"is_valid: {is_valid}, error: {error[:50] if error else ''}")
    all_ok = all_ok and no_grad_fail

    # Com graduação - deve passar
    is_valid, error = ResponseValidatorSection3.validate(
        "3.3",
        "O Sargento Silva tinha visão desobstruída da porta do bar"
    )
    with_grad_pass = is_valid
    print_test("Aceita resposta com graduação (Sargento)", with_grad_pass,
               f"is_valid: {is_valid}")
    all_ok = all_ok and with_grad_pass

    # Outras graduações
    for grad in ["Cabo", "Soldado", "Tenente", "Capitão"]:
        is_valid, _ = ResponseValidatorSection3.validate(
            "3.3",
            f"O {grad} Almeida observava a lateral do estabelecimento"
        )
        grad_ok = is_valid
        print_test(f"Aceita graduação {grad}", grad_ok)
        all_ok = all_ok and grad_ok

    return all_ok


def test_section3_validation_concrete_acts():
    """Testa que pergunta 3.6 exige atos concretos (mínimo 40 caracteres)"""
    print(f"\n{Colors.BLUE}=== TESTE 5: Validação Atos Concretos (3.6) ==={Colors.END}")

    all_ok = True

    # Muito curto - deve falhar
    is_valid, error = ResponseValidatorSection3.validate("3.6", "Viu tráfico")
    short_fail = not is_valid
    print_test("Rejeita resposta muito curta", short_fail,
               f"is_valid: {is_valid}")
    all_ok = all_ok and short_fail

    # Detalhado - deve passar
    is_valid, error = ResponseValidatorSection3.validate(
        "3.6",
        "O homem tirou pequenos invólucros da mochila preta e entregou para dois rapazes de moto"
    )
    detailed_pass = is_valid
    print_test("Aceita descrição detalhada (>40 chars)", detailed_pass,
               f"is_valid: {is_valid}")
    all_ok = all_ok and detailed_pass

    return all_ok


def test_section3_optional_questions():
    """Testa que perguntas 3.7 e 3.8 aceitam 'NÃO' como resposta válida"""
    print(f"\n{Colors.BLUE}=== TESTE 6: Perguntas Opcionais (3.7 e 3.8) ==={Colors.END}")

    all_ok = True

    # 3.7 - aceita NÃO
    is_valid, _ = ResponseValidatorSection3.validate("3.7", "NÃO")
    q37_no = is_valid
    print_test("3.7 aceita 'NÃO'", q37_no)
    all_ok = all_ok and q37_no

    # 3.7 - aceita resposta detalhada
    is_valid, _ = ResponseValidatorSection3.validate(
        "3.7",
        "Sim, foi abordado um usuário que portava 2 porções de cocaína"
    )
    q37_yes = is_valid
    print_test("3.7 aceita resposta detalhada", q37_yes)
    all_ok = all_ok and q37_yes

    # 3.8 - aceita NÃO
    is_valid, _ = ResponseValidatorSection3.validate("3.8", "NÃO")
    q38_no = is_valid
    print_test("3.8 aceita 'NÃO'", q38_no)
    all_ok = all_ok and q38_no

    # 3.8 - aceita resposta detalhada
    is_valid, _ = ResponseValidatorSection3.validate(
        "3.8",
        "Sim, ao perceber a movimentação policial, correu para o beco"
    )
    q38_yes = is_valid
    print_test("3.8 aceita resposta detalhada", q38_yes)
    all_ok = all_ok and q38_yes

    return all_ok


def main():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}  TESTES DE INTEGRAÇÃO - SEÇÃO 3 (CAMPANA){Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

    tests = [
        ("Sincronização Seção 3 Incompleta", test_sync_section3_incomplete),
        ("Sincronização Completa (3 Seções)", test_sync_all_three_sections_complete),
        ("Sincronização Seção 3 Pulada", test_sync_section3_skipped),
        ("Validação Graduação Militar (3.3)", test_section3_validation_graduation),
        ("Validação Atos Concretos (3.6)", test_section3_validation_concrete_acts),
        ("Perguntas Opcionais (3.7/3.8)", test_section3_optional_questions),
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
        print(f"{Colors.GREEN}Seção 3 está funcionando corretamente.{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}*** {total - passed} teste(s) falharam ***{Colors.END}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
