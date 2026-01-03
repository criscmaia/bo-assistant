"""
Funções auxiliares para endpoint /chat

Extrai lógica complexa do endpoint principal para melhorar legibilidade
e testabilidade.

v0.13.2+: Refatoração para reduzir complexidade do endpoint /chat
"""

from typing import Dict, Any, Tuple
from fastapi import HTTPException

# Imports compatíveis com local E Render
try:
    from state_machine import BOStateMachine
    from state_machine_section2 import BOStateMachineSection2
    from state_machine_section3 import BOStateMachineSection3
    from state_machine_section4 import BOStateMachineSection4
    from state_machine_section5 import BOStateMachineSection5
    from state_machine_section6 import BOStateMachineSection6
    from state_machine_section7 import BOStateMachineSection7
    from state_machine_section8 import BOStateMachineSection8
    from logger import BOLogger
except ImportError:
    from backend.state_machine import BOStateMachine
    from backend.state_machine_section2 import BOStateMachineSection2
    from backend.state_machine_section3 import BOStateMachineSection3
    from backend.state_machine_section4 import BOStateMachineSection4
    from backend.state_machine_section5 import BOStateMachineSection5
    from backend.state_machine_section6 import BOStateMachineSection6
    from backend.state_machine_section7 import BOStateMachineSection7
    from backend.state_machine_section8 import BOStateMachineSection8
    from backend.logger import BOLogger


def initialize_session_if_needed(
    session_id: str,
    sessions: Dict[str, Any]
) -> Tuple[Dict[str, Any], str]:
    """
    Inicializa sessão se não existir (útil quando backend reinicia).

    Args:
        session_id: ID da sessão
        sessions: Dicionário de sessões ativas

    Returns:
        Tupla (session_data, bo_id)
    """
    if session_id in sessions:
        session_data = sessions[session_id]
        return session_data, session_data["bo_id"]

    # Criar nova sessão
    bo_id = BOLogger.create_bo()
    session_data = {
        "bo_id": bo_id,
        "sections": {
            1: BOStateMachine()
        },
        "section1_text": "",
        "section2_text": "",
        "section3_text": "",
        "section4_text": "",
        "section5_text": "",
        "section6_text": "",
        "section7_text": "",
        "section8_text": "",
        "answer_count": 0,
        "logged_to_db": False,
        "pending_events": []
    }
    sessions[session_id] = session_data

    BOLogger.log_event(
        bo_id=bo_id,
        event_type="session_recreated",
        data={"session_id": session_id, "reason": "backend_restart"}
    )

    return session_data, bo_id


def initialize_section_if_needed(
    section_number: int,
    session_data: Dict[str, Any]
) -> None:
    """
    Inicializa state machine da seção se não existir.

    Args:
        section_number: Número da seção (1-8)
        session_data: Dados da sessão

    Raises:
        HTTPException: Se seção não for suportada
    """
    if section_number in session_data["sections"]:
        return

    # Mapa de seção → classe de state machine
    SECTION_STATE_MACHINES = {
        1: BOStateMachine,
        2: BOStateMachineSection2,
        3: BOStateMachineSection3,
        4: BOStateMachineSection4,
        5: BOStateMachineSection5,
        6: BOStateMachineSection6,
        7: BOStateMachineSection7,
        8: BOStateMachineSection8,
    }

    state_machine_class = SECTION_STATE_MACHINES.get(section_number)

    if state_machine_class is None:
        raise HTTPException(
            status_code=400,
            detail=f"Seção {section_number} não suportada"
        )

    session_data["sections"][section_number] = state_machine_class()


def log_event_with_pending_support(
    session_data: Dict[str, Any],
    bo_id: str,
    event_type: str,
    data: Dict[str, Any]
) -> str:
    """
    Loga evento no banco ou adiciona à fila de pending_events.

    Args:
        session_data: Dados da sessão
        bo_id: ID do BO
        event_type: Tipo do evento
        data: Dados do evento

    Returns:
        event_id ou pseudo-ID se pending
    """
    is_already_logged = session_data.get("logged_to_db", False)

    if is_already_logged:
        # Já está no banco - gravar diretamente
        event_id = BOLogger.log_event(
            bo_id=bo_id,
            event_type=event_type,
            data=data
        )
        return event_id
    else:
        # Ainda não está no banco - adicionar à fila
        session_data["pending_events"].append({
            "event_type": event_type,
            "data": data
        })
        # Usar um pseudo-ID para compatibilidade
        return f"pending_{len(session_data['pending_events'])}"


def determine_next_action(
    state_machine: Any,
    current_section: int
) -> Dict[str, Any]:
    """
    Determina próxima ação após resposta válida.

    Analisa se seção completou, foi pulada, tem follow-up, etc.

    Args:
        state_machine: State machine da seção atual
        current_section: Número da seção atual

    Returns:
        Dict com:
        - action: "section_complete", "section_skipped", "continue"
        - skip_reason: (opcional) motivo do skip
        - current_step: próximo step
        - question: próxima pergunta ou None
    """
    is_complete = state_machine.is_section_complete()

    if not is_complete:
        # Seção ainda em andamento
        return {
            "action": "continue",
            "current_step": state_machine.current_step,
            "question": state_machine.get_current_question()
        }

    # Seção completou - verificar se foi pulada
    sections_with_skip = [2, 3, 4, 5, 6, 7]
    is_skippable = current_section in sections_with_skip

    if is_skippable and hasattr(state_machine, 'was_section_skipped'):
        if state_machine.was_section_skipped():
            skip_reason = state_machine.get_skip_reason()
            return {
                "action": "section_skipped",
                "skip_reason": skip_reason,
                "current_step": state_machine.current_step
            }

    # Seção completou normalmente
    return {
        "action": "section_complete",
        "current_step": state_machine.current_step
    }
