# -*- coding: utf-8 -*-
"""
Teste de integração: Fluxo completo da Seção 6 (Reação e Uso da Força)
Valida sincronização, skip logic e geração de texto

Executar: python -m pytest tests/integration/test_section6_flow.py -v
"""
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.main import sessions
from backend.state_machine import BOStateMachine
from backend.state_machine_section2 import BOStateMachineSection2
from backend.state_machine_section3 import BOStateMachineSection3
from backend.state_machine_section4 import BOStateMachineSection4
from backend.state_machine_section5 import BOStateMachineSection5
from backend.state_machine_section6 import BOStateMachineSection6
from backend.validator import ResponseValidator
from backend.validator_section2 import ResponseValidatorSection2
from backend.validator_section3 import ResponseValidatorSection3
from backend.validator_section4 import ResponseValidatorSection4
from backend.validator_section5 import ResponseValidatorSection5
from backend.validator_section6 import ResponseValidatorSection6
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
    Simula o endpoint /sync_session para Seções 1-6.
    Replica a lógica exata do endpoint.
    """
    if session_id not in sessions:
        return None

    session_data = sessions[session_id]
    bo_id = session_data["bo_id"]

    # Ordenar steps (1.1, 1.2, ..., 2.1, 2.2, ..., 6.1, 6.2, ...)
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
                elif step_section == 4:
                    session_data["sections"][4] = BOStateMachineSection4()
                elif step_section == 5:
                    session_data["sections"][5] = BOStateMachineSection5()
                elif step_section == 6:
                    session_data["sections"][6] = BOStateMachineSection6()

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
        elif current_section == 4:
            is_valid, error_message = ResponseValidatorSection4.validate(step, answer)
        elif current_section == 5:
            is_valid, error_message = ResponseValidatorSection5.validate(step, answer)
        elif current_section == 6:
            is_valid, error_message = ResponseValidatorSection6.validate(step, answer)
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
        "section4_complete": session_data["sections"].get(4, None) and session_data["sections"][4].is_section_complete(),
        "section5_complete": session_data["sections"].get(5, None) and session_data["sections"][5].is_section_complete(),
        "section6_complete": session_data["sections"].get(6, None) and session_data["sections"][6].is_section_complete(),
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
        "section3_text": "",
        "section4_text": "",
        "section5_text": "",
        "section6_text": ""
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


def get_section4_answers():
    """Retorna respostas válidas para Seção 4 (5 perguntas)"""
    return {
        "4.1": "SIM",
        "4.2": "Vimos o suspeito arremessando uma sacola branca para dentro da casa enquanto corria em direção ao imóvel nº 120 da Rua das Acácias",
        "4.3": "O Sargento Silva viu o suspeito entrando na casa com a sacola e manteve contato visual ininterrupto com o alvo",
        "4.4": "Perseguição contínua: a equipe iniciou acompanhamento no final da Rua das Acácias e manteve contato visual ininterrupto até o interior da residência",
        "4.5": "O Sargento Silva entrou primeiro pela porta principal que estava aberta. O Cabo Almeida ficou na contenção do portão monitorando saídas. O Soldado Faria entrou em seguida pela cozinha e localizou a sacola branca embaixo da pia contendo invólucros de cocaína."
    }


def get_section5_answers():
    """Retorna respostas válidas para Seção 5 (4 perguntas)"""
    return {
        "5.1": "SIM",
        "5.2": "Durante patrulhamento pela Rua das Palmeiras, região com registros anteriores de tráfico de drogas, visualizamos um homem de camisa vermelha e bermuda jeans retirando pequenos invólucros de um buraco no muro e entregando-os a motociclistas que paravam rapidamente",
        "5.3": "O Sargento João, de dentro da viatura estacionada a aproximadamente 20 metros do local, visualizou o suspeito retirando invólucros do buraco no muro e realizando as entregas por cerca de dois minutos antes de perceber a aproximação policial",
        "5.4": "Homem de camisa vermelha e bermuda jeans azul, porte atlético, aproximadamente 1,75m de altura. Ao perceber a aproximação da viatura, demonstrou nervosismo acentuado e tentou guardar parte do material no bolso. Posteriormente identificado como JOÃO DA SILVA SANTOS, vulgo 'Vermelho'."
    }


def get_section6_answers():
    """Retorna respostas válidas para Seção 6 (5 perguntas)"""
    return {
        "6.1": "SIM",
        "6.2": "Durante a abordagem, o autor empurrou o Cabo Rezende com força no peito e tentou correr em direção ao beco lateral, sendo alcançado após aproximadamente 10 metros",
        "6.3": "O Soldado Pires aplicou chave de braço no suspeito, forçando o cotovelo esquerdo, e o imobilizou no chão. O Cabo Rezende auxiliou na contenção segurando as pernas do autor",
        "6.4": "Diante da tentativa de fuga e da agressão física contra o Cabo Rezende, o autor foi algemado para evitar nova tentativa de evasão e garantir a segurança da guarnição",
        "6.5": "O autor apresentou escoriação no joelho direito e hematoma no braço esquerdo. Foi encaminhado ao Hospital João XXIII (ficha nº 2025-78901), medicado e liberado"
    }


def test_sync_section6_incomplete():
    """Testa sincronização com Seção 6 incompleta (Seções 1-5 completas + 3 perguntas da Seção 6)"""
    print(f"\n{Colors.BLUE}=== TESTE 1: Sincronização Seção 6 Incompleta ==={Colors.END}")

    session_id, bo_id = create_test_session()

    # Respostas: Seções 1-5 completas + Seção 6 parcial (6.1-6.3)
    answers = {
        **get_section1_answers(),
        **get_section2_answers(),
        **get_section3_answers(),
        **get_section4_answers(),
        **get_section5_answers(),
        "6.1": "SIM",
        "6.2": "Durante a abordagem, o autor empurrou o Cabo Rezende com força no peito e tentou correr",
        "6.3": "O Soldado Pires aplicou chave de braço no suspeito e o imobilizou no chão"
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

    # 2. current_step deve ser "6.4" (próxima pergunta)
    expected_step = "6.4"
    actual_step = result.get("current_step")
    step_ok = actual_step == expected_step
    print_test(f"current_step correto ({expected_step})", step_ok,
               f"Esperado: {expected_step}, Atual: {actual_step}")
    all_ok = all_ok and step_ok

    # 3. Seções 1-5 devem estar completas
    s1_complete = result.get("section1_complete")
    s2_complete = result.get("section2_complete")
    s3_complete = result.get("section3_complete")
    s4_complete = result.get("section4_complete")
    s5_complete = result.get("section5_complete")
    s1_to_s5_ok = s1_complete and s2_complete and s3_complete and s4_complete and s5_complete
    print_test("Seções 1-5 completas", s1_to_s5_ok,
               f"S1: {s1_complete}, S2: {s2_complete}, S3: {s3_complete}, S4: {s4_complete}, S5: {s5_complete}")
    all_ok = all_ok and s1_to_s5_ok

    # 4. Seção 6 NÃO deve estar completa
    s6_complete = result.get("section6_complete")
    s6_ok = not s6_complete
    print_test("Seção 6 NÃO completa", s6_ok,
               f"section6_complete: {s6_complete}")
    all_ok = all_ok and s6_ok

    # 5. current_section deve ser 6
    current_section = result.get("current_section")
    section_ok = current_section == 6
    print_test("current_section = 6", section_ok,
               f"Esperado: 6, Atual: {current_section}")
    all_ok = all_ok and section_ok

    # Limpar
    del sessions[session_id]

    return all_ok


def test_sync_all_six_sections_complete():
    """Testa sincronização com todas as 6 seções completas (31 respostas)"""
    print(f"\n{Colors.BLUE}=== TESTE 2: Sincronização Completa (Seções 1-6) ==={Colors.END}")

    session_id, bo_id = create_test_session()

    # Todas as respostas
    answers = {
        **get_section1_answers(),
        **get_section2_answers(),
        **get_section3_answers(),
        **get_section4_answers(),
        **get_section5_answers(),
        **get_section6_answers()
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

    # 3. Todas as 6 seções devem estar completas
    s1_complete = result.get("section1_complete")
    s2_complete = result.get("section2_complete")
    s3_complete = result.get("section3_complete")
    s4_complete = result.get("section4_complete")
    s5_complete = result.get("section5_complete")
    s6_complete = result.get("section6_complete")

    all_complete = s1_complete and s2_complete and s3_complete and s4_complete and s5_complete and s6_complete
    print_test("Todas as 6 seções completas", all_complete,
               f"S1: {s1_complete}, S2: {s2_complete}, S3: {s3_complete}, S4: {s4_complete}, S5: {s5_complete}, S6: {s6_complete}")
    all_ok = all_ok and all_complete

    # 4. current_section deve ser 6
    current_section = result.get("current_section")
    section_ok = current_section == 6
    print_test("current_section = 6", section_ok,
               f"Esperado: 6, Atual: {current_section}")
    all_ok = all_ok and section_ok

    # 5. Verificar total de respostas da Seção 6
    sm6 = sessions[session_id]["sections"][6]
    total_answers = len(sm6.get_all_answers())
    answers_ok = total_answers == 5
    print_test(f"Seção 6 com 5 respostas", answers_ok,
               f"Total: {total_answers}")
    all_ok = all_ok and answers_ok

    # Limpar
    del sessions[session_id]

    return all_ok


def test_sync_section6_skipped():
    """Testa sincronização quando Seção 6 é pulada (resposta NÃO em 6.1)"""
    print(f"\n{Colors.BLUE}=== TESTE 3: Sincronização Seção 6 Pulada ==={Colors.END}")

    session_id, bo_id = create_test_session()

    # Seções 1-5 completas + 6.1 = "NÃO" (pula Seção 6)
    answers = {
        **get_section1_answers(),
        **get_section2_answers(),
        **get_section3_answers(),
        **get_section4_answers(),
        **get_section5_answers(),
        "6.1": "NÃO"
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

    # 3. Seção 6 deve estar marcada como completa (porque foi pulada)
    s6_complete = result.get("section6_complete")
    s6_ok = s6_complete
    print_test("Seção 6 marcada como completa (pulada)", s6_ok,
               f"section6_complete: {s6_complete}")
    all_ok = all_ok and s6_ok

    # 4. Verificar se state machine tem flag de seção pulada
    state_machine = sessions[session_id]["sections"][6]
    was_skipped = state_machine.was_section_skipped()
    skipped_ok = was_skipped
    print_test("Flag section_skipped ativado", skipped_ok,
               f"was_section_skipped(): {was_skipped}")
    all_ok = all_ok and skipped_ok

    # 5. Verificar skip_reason
    skip_reason = state_machine.get_skip_reason()
    reason_ok = skip_reason is not None and ("reação" in skip_reason.lower() or "força" in skip_reason.lower() or "resistência" in skip_reason.lower())
    print_test("Skip reason correto", reason_ok,
               f"get_skip_reason(): {skip_reason}")
    all_ok = all_ok and reason_ok

    # Limpar
    del sessions[session_id]

    return all_ok


def test_section6_validation_graduation():
    """Testa que pergunta 6.3 exige graduação militar"""
    print(f"\n{Colors.BLUE}=== TESTE 4: Validação Graduação Militar (6.3) ==={Colors.END}")

    all_ok = True

    # Sem graduação - deve falhar
    is_valid, error = ResponseValidatorSection6.validate("6.3", "João aplicou chave de braço no suspeito")
    no_grad_fail = not is_valid
    print_test("Rejeita resposta sem graduação", no_grad_fail,
               f"is_valid: {is_valid}, error: {error[:50] if error else ''}")
    all_ok = all_ok and no_grad_fail

    # Com graduação - deve passar
    is_valid, error = ResponseValidatorSection6.validate(
        "6.3",
        "O Soldado Pires aplicou chave de braço no suspeito e o imobilizou"
    )
    with_grad_pass = is_valid
    print_test("Aceita resposta com graduação (Soldado)", with_grad_pass,
               f"is_valid: {is_valid}")
    all_ok = all_ok and with_grad_pass

    # Outras graduações
    for grad in ["Cabo", "Sargento", "Tenente", "Capitão"]:
        is_valid, _ = ResponseValidatorSection6.validate(
            "6.3",
            f"O {grad} Silva aplicou chave de braço no suspeito e o imobilizou"
        )
        grad_ok = is_valid
        print_test(f"Aceita graduação {grad}", grad_ok)
        all_ok = all_ok and grad_ok

    return all_ok


def test_section6_validation_forbidden_phrases():
    """Testa validação de frases proibidas em 6.2"""
    print(f"\n{Colors.BLUE}=== TESTE 5: Validação Frases Proibidas (6.2) ==={Colors.END}")

    all_ok = True

    # Teste 1: "resistiu ativamente" é proibida
    is_valid, error = ResponseValidatorSection6.validate(
        "6.2",
        "O autor resistiu ativamente e tentou fugir"
    )
    test1 = not is_valid and "resistiu ativamente" in error
    print_test("Rejeita 'resistiu ativamente'", test1,
               f"is_valid: {is_valid}, error: {error[:60] if error else ''}")
    all_ok = all_ok and test1

    # Teste 2: "uso moderado da força" é proibida
    is_valid, error = ResponseValidatorSection6.validate(
        "6.2",
        "Foi necessário uso moderado da força para a contenção"
    )
    test2 = not is_valid
    print_test("Rejeita 'uso moderado da força'", test2,
               f"is_valid: {is_valid}")
    all_ok = all_ok and test2

    # Teste 3: "resistiu" sozinho é proibida
    is_valid, error = ResponseValidatorSection6.validate(
        "6.2",
        "O autor resistiu"
    )
    test3 = not is_valid
    print_test("Rejeita 'resistiu' (sozinho)", test3,
               f"is_valid: {is_valid}")
    all_ok = all_ok and test3

    # Teste 4: Ação concreta SEM frases proibidas é aceita
    is_valid, error = ResponseValidatorSection6.validate(
        "6.2",
        "O autor empurrou o Cabo Rezende e tentou correr em direção ao beco"
    )
    test4 = is_valid
    print_test("Aceita ação concreta sem frases proibidas", test4,
               f"is_valid: {is_valid}")
    all_ok = all_ok and test4

    # Teste 5: Descrição detalhada com ações específicas
    is_valid, error = ResponseValidatorSection6.validate(
        "6.2",
        "Durante a abordagem, o autor empurrou o policial com força no peito, derrubando-o, e em seguida tentou correr pela viela lateral"
    )
    test5 = is_valid
    print_test("Aceita descrição detalhada de ações", test5,
               f"is_valid: {is_valid}")
    all_ok = all_ok and test5

    return all_ok


def test_section6_ferimentos_com_hospital():
    """Testa validação condicional: ferimentos exigem hospital em 6.5"""
    print(f"\n{Colors.BLUE}=== TESTE 6: Validação Ferimentos e Hospital (6.5) ==={Colors.END}")

    all_ok = True

    # Teste 1: Sem ferimentos - deve passar
    is_valid, error = ResponseValidatorSection6.validate(
        "6.5",
        "Não houve ferimentos. A guarnição verificou a integridade física e nada foi encontrado."
    )
    test1 = is_valid
    print_test("Aceita resposta sem ferimentos", test1,
               f"is_valid: {is_valid}")
    all_ok = all_ok and test1

    # Teste 2: Com ferimentos mas SEM hospital - deve falhar
    is_valid, error = ResponseValidatorSection6.validate(
        "6.5",
        "O autor apresentou escoriação no joelho esquerdo"
    )
    test2 = not is_valid
    print_test("Rejeita ferimentos SEM hospital", test2,
               f"is_valid: {is_valid}, error: {error[:60] if error else ''}")
    all_ok = all_ok and test2

    # Teste 3: Com ferimentos E hospital com ficha - deve passar
    is_valid, error = ResponseValidatorSection6.validate(
        "6.5",
        "O autor apresentou escoriação no joelho esquerdo. Foi atendido no Hospital João XXIII (ficha nº 2025-12345)"
    )
    test3 = is_valid
    print_test("Aceita ferimentos COM hospital e ficha", test3,
               f"is_valid: {is_valid}")
    all_ok = all_ok and test3

    # Teste 4: Com múltiplas lesões E hospital
    is_valid, error = ResponseValidatorSection6.validate(
        "6.5",
        "O autor apresentou hematoma no braço esquerdo e escoriação no joelho direito. Foi encaminhado ao Hospital Santa Cruz (ficha nº 2025-98765)"
    )
    test4 = is_valid
    print_test("Aceita múltiplas lesões COM hospital", test4,
               f"is_valid: {is_valid}")
    all_ok = all_ok and test4

    # Teste 5: Hospital mencionado mas sem formato de ficha - deve falhar
    is_valid, error = ResponseValidatorSection6.validate(
        "6.5",
        "O autor foi encaminhado ao hospital. Apresentava hematoma no braço"
    )
    test5 = not is_valid
    print_test("Rejeita hospital SEM número de ficha", test5,
               f"is_valid: {is_valid}")
    all_ok = all_ok and test5

    return all_ok


def main():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}  TESTES DE INTEGRAÇÃO - SEÇÃO 6 (REAÇÃO E USO DA FORÇA){Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

    tests = [
        ("Sincronização Seção 6 Incompleta", test_sync_section6_incomplete),
        ("Sincronização Completa (6 Seções)", test_sync_all_six_sections_complete),
        ("Sincronização Seção 6 Pulada", test_sync_section6_skipped),
        ("Validação Graduação Militar (6.3)", test_section6_validation_graduation),
        ("Validação Frases Proibidas (6.2)", test_section6_validation_forbidden_phrases),
        ("Validação Ferimentos e Hospital (6.5)", test_section6_ferimentos_com_hospital),
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
        print(f"{Colors.GREEN}Seção 6 está funcionando corretamente.{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}*** {total - passed} teste(s) falharam ***{Colors.END}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
