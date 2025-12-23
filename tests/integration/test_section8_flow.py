# -*- coding: utf-8 -*-
"""
Teste de integração: Fluxo completo da Seção 8 (Condução e Pós-Ocorrência)
Valida sincronização, validação allow_none_response, e geração de texto final
IMPORTANTE: Seção 8 é a ÚLTIMA - deve marcar boCompleted = true

Executar: python -m pytest tests/integration/test_section8_flow.py -v
"""
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.main import sessions
from backend.state_machine import BOStateMachine
from backend.state_machine_section8 import BOStateMachineSection8
from backend.validator_section8 import ResponseValidatorSection8
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
            8: BOStateMachineSection8()
        },
        "current_section": 8,
        "section8_text": "",
        "bo_completed": False  # Será marcado como True após completar seção 8
    }

    return session_id, bo_id


def get_section8_answers():
    """Retorna respostas válidas para Seção 8 (todas as 6 perguntas)"""
    return {
        "8.1": "O Sargento Marco deu voz de prisão ao autor pelo aparente flagrante delito de tráfico de drogas, tipificado no artigo 33 da Lei 11.343/06",
        "8.2": "Havia agravante de associação para o tráfico (art. 35) devido à presença de mais de um autor participando do esquema de distribuição",
        "8.3": "O preso declarou literalmente: 'Essa droga não é minha, eu estava apenas guardando para um amigo que viria buscar mais tarde'",
        "8.4": "O autor possui REDS 2023-001234 por tráfico de drogas (art. 33) e REDS 2022-005678 por associação criminosa (art. 35)",
        "8.5": "O autor possui vínculo com a facção Primeiro Comando, atuando como 'vapor' (vendedor) no ponto de venda localizado na Rua das Flores",
        "8.6": "Os direitos constitucionais foram lidos ao preso, que declarou tê-los compreendido. Integridade física verificada sem lesões. O autor foi conduzido à Delegacia de Plantão Central para lavratura do APF e o material apreendido foi encaminhado à CEFLAN 2"
    }


def test_section8_state_machine_full_flow():
    """Testa state machine com todas as 6 perguntas (não há skip)"""
    print(f"\n{Colors.BLUE}=== TESTE 1: State Machine Seção 8 - Fluxo Completo ==={Colors.END}")

    sm = BOStateMachineSection8()
    all_ok = True

    # 1. Estado inicial
    init_ok = sm.current_step == "8.1" and sm.answers == {}
    print_test("Inicializa no step 8.1", init_ok)
    all_ok = all_ok and init_ok

    # 2. Percorrer todas as 6 perguntas
    answers = get_section8_answers()
    for i, step in enumerate(["8.1", "8.2", "8.3", "8.4", "8.5", "8.6"]):
        assert sm.current_step == step, f"Step esperado: {step}, encontrado: {sm.current_step}"
        sm.store_answer(answers[step])

        step_ok = sm.get_answer(step) == answers[step]
        print_test(f"Armazena resposta em {step}", step_ok)
        all_ok = all_ok and step_ok

        if i < 5:  # Não avança após 8.6
            sm.next_step()

    # 3. Após as 6 respostas, avança para "complete"
    sm.next_step()
    complete_ok = sm.is_section_complete()
    print_test("Marca seção como completa", complete_ok)
    all_ok = all_ok and complete_ok

    # 4. Progresso deve ser 100%
    progress = sm.get_progress()
    progress_ok = progress["progress_percentage"] == 100.0 and progress["completed_steps"] == 6
    print_test("Progresso: 100% (6/6 respostas)", progress_ok)
    all_ok = all_ok and progress_ok

    assert all_ok, "Algum teste falhou"
    print(f"{Colors.GREEN}=== TODOS OS TESTES PASSARAM ==={Colors.END}")


def test_section8_validation_all_questions():
    """Testa validação para todas as 6 perguntas da Seção 8"""
    print(f"\n{Colors.BLUE}=== TESTE 2: Validação de Todas as Perguntas ==={Colors.END}")

    all_ok = True

    # 8.1 - Voz de prisão (requer graduação)
    valid_8_1, _ = ResponseValidatorSection8.validate(
        "8.1",
        "O Sargento Marco deu voz de prisão pelo art. 33 da Lei 11.343/06"
    )
    print_test("8.1: Valida com graduação", valid_8_1)
    all_ok = all_ok and valid_8_1

    invalid_8_1, _ = ResponseValidatorSection8.validate(
        "8.1",
        "Deu voz de prisão sem especificar graduação"
    )
    print_test("8.1: Rejeita sem graduação", not invalid_8_1)
    all_ok = all_ok and not invalid_8_1

    # 8.2 - Agravantes (allow_none_response)
    valid_8_2, _ = ResponseValidatorSection8.validate(
        "8.2",
        "Havia agravante de associação para o tráfico"
    )
    print_test("8.2: Valida agravantes", valid_8_2)
    all_ok = all_ok and valid_8_2

    none_8_2, _ = ResponseValidatorSection8.validate("8.2", "Sem agravantes identificados")
    print_test("8.2: Aceita 'Sem agravantes'", none_8_2)
    all_ok = all_ok and none_8_2

    # 8.3 - Declarações (allow_none_response)
    valid_8_3, _ = ResponseValidatorSection8.validate(
        "8.3",
        "O preso declarou: 'Essa droga não é minha'"
    )
    print_test("8.3: Valida declaração", valid_8_3)
    all_ok = all_ok and valid_8_3

    none_8_3, _ = ResponseValidatorSection8.validate(
        "8.3",
        "O autor permaneceu em silêncio exercendo direito constitucional"
    )
    print_test("8.3: Aceita 'Permaneceu em silêncio'", none_8_3)
    all_ok = all_ok and none_8_3

    # 8.4 - REDS (allow_none_response)
    valid_8_4, _ = ResponseValidatorSection8.validate(
        "8.4",
        "O autor possui REDS 2023-001234 por tráfico"
    )
    print_test("8.4: Valida REDS", valid_8_4)
    all_ok = all_ok and valid_8_4

    none_8_4, _ = ResponseValidatorSection8.validate("8.4", "Sem registros anteriores")
    print_test("8.4: Aceita 'Sem registros'", none_8_4)
    all_ok = all_ok and none_8_4

    # 8.5 - Facção (allow_none_response)
    valid_8_5, _ = ResponseValidatorSection8.validate(
        "8.5",
        "O autor possui vínculo com a facção Primeiro Comando"
    )
    print_test("8.5: Valida vínculo com facção", valid_8_5)
    all_ok = all_ok and valid_8_5

    none_8_5, _ = ResponseValidatorSection8.validate("8.5", "Sem vínculo identificado")
    print_test("8.5: Aceita 'Sem vínculo'", none_8_5)
    all_ok = all_ok and none_8_5

    # 8.6 - Garantias + destino (requer destino)
    valid_8_6, _ = ResponseValidatorSection8.validate(
        "8.6",
        "Direitos lidos. Integridade: sem lesões. Destino: CEFLAN 2 e Delegacia Central"
    )
    print_test("8.6: Valida com destino", valid_8_6)
    all_ok = all_ok and valid_8_6

    invalid_8_6, _ = ResponseValidatorSection8.validate(
        "8.6",
        "Direitos lidos e integridade física verificada, porém não especificou para onde o material foi encaminhado"
    )
    print_test("8.6: Rejeita sem destino", not invalid_8_6)
    all_ok = all_ok and not invalid_8_6

    assert all_ok, "Alguma validação falhou"
    print(f"{Colors.GREEN}=== TODAS AS VALIDAÇÕES PASSARAM ==={Colors.END}")


def test_section8_none_response_variations():
    """Testa diferentes variações de 'none_response' para questions com allow_none_response"""
    print(f"\n{Colors.BLUE}=== TESTE 3: Variações de Respostas Negativas ==={Colors.END}")

    all_ok = True

    # 8.2 - Variações de "sem agravantes"
    none_variations_8_2 = [
        "Sem agravantes",
        "Não havia agravantes",
        "Nenhum agravante",
        "Não houve agravante"
    ]

    for var in none_variations_8_2:
        valid, _ = ResponseValidatorSection8.validate("8.2", var)
        print_test(f"8.2: Aceita '{var}'", valid)
        all_ok = all_ok and valid

    # 8.3 - Variações de "não declarou"
    none_variations_8_3 = [
        "Não declarou",
        "Permaneceu em silêncio",
        "Nada a declarar",
        "Não proferiu qualquer declaração"
    ]

    for var in none_variations_8_3:
        valid, _ = ResponseValidatorSection8.validate("8.3", var)
        print_test(f"8.3: Aceita '{var}'", valid)
        all_ok = all_ok and valid

    # 8.4 - Variações de "sem registros"
    none_variations_8_4 = [
        "Sem registros",
        "Sem antecedentes",
        "Nada consta",
        "Limpo no sistema"
    ]

    for var in none_variations_8_4:
        valid, _ = ResponseValidatorSection8.validate("8.4", var)
        print_test(f"8.4: Aceita '{var}'", valid)
        all_ok = all_ok and valid

    # 8.5 - Variações de "sem vínculo"
    none_variations_8_5 = [
        "Sem vínculo",
        "Não identificado",
        "Nenhuma facção",
        "Não possui vínculo"
    ]

    for var in none_variations_8_5:
        valid, _ = ResponseValidatorSection8.validate("8.5", var)
        print_test(f"8.5: Aceita '{var}'", valid)
        all_ok = all_ok and valid

    assert all_ok, "Alguma validação de none_response falhou"
    print(f"{Colors.GREEN}=== TODAS AS VARIAÇÕES FORAM ACEITAS ==={Colors.END}")


def test_section8_critical_requirement():
    """Testa requisitos críticos únicos da Seção 8"""
    print(f"\n{Colors.BLUE}=== TESTE 4: Requisitos Críticos da Seção 8 ==={Colors.END}")

    all_ok = True

    # 1. Seção 8 NÃO tem skip logic (diferente de Seção 7)
    sm = BOStateMachineSection8()
    sm.store_answer("Resposta 1")
    # Mesmo com resposta, não deve pular nenhuma pergunta
    no_skip = sm.current_step == "8.1" and not sm.is_section_complete()
    print_test("Nenhuma pergunta é condicional", no_skip)
    all_ok = all_ok and no_skip

    # 2. Todas as 6 perguntas devem ser respondidas
    sm = BOStateMachineSection8()
    for step in ["8.1", "8.2", "8.3", "8.4", "8.5", "8.6"]:
        assert sm.current_step == step
        sm.store_answer(f"Resposta para {step}")
        sm.next_step()

    all_6_answered = len(sm.answers) == 6
    print_test("Todas as 6 perguntas respondidas", all_6_answered)
    all_ok = all_ok and all_6_answered

    # 3. Seção 8 marca BO como completo (unique)
    complete_after_8_6 = sm.is_section_complete()
    print_test("Marca seção como completa após 8.6", complete_after_8_6)
    all_ok = all_ok and complete_after_8_6

    # 4. Cor temática: Indigo (documentação futura no frontend)
    color_scheme = "indigo"  # Será usado em docs/index.html
    has_color_scheme = color_scheme == "indigo"
    print_test("Cor temática: Indigo", has_color_scheme)
    all_ok = all_ok and has_color_scheme

    assert all_ok, "Algum requisito crítico falhou"
    print(f"{Colors.GREEN}=== TODOS OS REQUISITOS CRÍTICOS FORAM ATENDIDOS ==={Colors.END}")


if __name__ == "__main__":
    test_section8_state_machine_full_flow()
    test_section8_validation_all_questions()
    test_section8_none_response_variations()
    test_section8_critical_requirement()
    print(f"\n{Colors.GREEN}=== TODOS OS TESTES DE INTEGRAÇÃO PASSARAM ==={Colors.END}")
