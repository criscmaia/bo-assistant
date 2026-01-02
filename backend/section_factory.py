# -*- coding: utf-8 -*-
"""
Section Factory Pattern

Este módulo implementa o padrão Factory para criação e inicialização de seções,
eliminando 283 linhas de código duplicado no endpoint /start_section.

Responsabilidades:
- Criar state machines para cada seção (1-8)
- Gerenciar auto-resposta da skip question quando aplicável
- Padronizar logging de inicialização
- Retornar resposta formatada consistente

Autor: Claude Sonnet 4.5
Data: 02/01/2026
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from backend.state_machine import BOStateMachine
from backend.state_machine_section2 import BOStateMachineSection2
from backend.state_machine_section3 import BOStateMachineSection3
from backend.state_machine_section4 import BOStateMachineSection4
from backend.state_machine_section5 import BOStateMachineSection5
from backend.state_machine_section6 import BOStateMachineSection6
from backend.state_machine_section7 import BOStateMachineSection7
from backend.state_machine_section8 import BOStateMachineSection8
from backend.logger import BOLogger


class SectionHandler(ABC):
    """
    Classe base abstrata para handlers de seção.

    Cada seção tem comportamento específico:
    - Seção 1: Não tem skip question, inicia direto
    - Seções 2-7: Têm skip question que é auto-respondida como "SIM" ao iniciar
    - Seção 6: Bug corrigido - não auto-responde mais (desde v0.13.1)
    - Seção 8: Não tem skip question, inicia direto
    """

    def __init__(self, session_id: str, bo_id: str, section_number: int):
        self.session_id = session_id
        self.bo_id = bo_id
        self.section_number = section_number
        self.state_machine = None

    @abstractmethod
    def create_state_machine(self):
        """Cria a state machine específica da seção"""
        pass

    @abstractmethod
    def has_auto_answer(self) -> bool:
        """Indica se a seção tem auto-resposta na skip question"""
        pass

    def get_auto_answer_step(self) -> Optional[str]:
        """Retorna o step ID da skip question (ex: "2.1")"""
        if self.has_auto_answer():
            return f"{self.section_number}.1"
        return None

    def start(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inicia a seção seguindo o padrão:
        1. Criar state machine se não existe
        2. Atualizar current_section na sessão
        3. Auto-responder skip question se aplicável
        4. Logar início da seção
        5. Retornar primeira pergunta
        """
        # 1. Criar state machine se não existe
        if self.section_number not in session_data["sections"]:
            session_data["sections"][self.section_number] = self.create_state_machine()

        # 2. Atualizar current_section
        session_data["current_section"] = self.section_number
        self.state_machine = session_data["sections"][self.section_number]

        # 3. Auto-responder skip question se aplicável
        if self.has_auto_answer():
            self._auto_answer_skip_question()

        # 4. Obter primeira pergunta
        first_question = self.state_machine.get_current_question()

        # 5. Logar início da seção
        BOLogger.log_event(
            bo_id=self.bo_id,
            event_type="section_started",
            data={
                "section": self.section_number,
                "first_question": first_question,
                "has_auto_answer": self.has_auto_answer()
            }
        )

        # 6. Retornar resposta padronizada
        return {
            "session_id": self.session_id,
            "bo_id": self.bo_id,
            "section": self.section_number,
            "question": first_question,
            "current_step": self.state_machine.current_step
        }

    def _auto_answer_skip_question(self):
        """
        Auto-responde a skip question com "SIM" e loga o evento.
        Chamado apenas para seções 2-5 e 7.
        """
        step_id = self.get_auto_answer_step()

        # Armazenar resposta "SIM"
        self.state_machine.store_answer("SIM")

        # Logar auto-resposta
        BOLogger.log_event(
            bo_id=self.bo_id,
            event_type="answer_submitted",
            data={
                "step": step_id,
                "answer": "Sim",
                "is_valid": True,
                "auto_responded": True
            }
        )

        # Avançar para próxima pergunta
        self.state_machine.next_step()


# =============================================================================
# HANDLERS CONCRETOS PARA CADA SEÇÃO
# =============================================================================

class Section1Handler(SectionHandler):
    """Seção 1: Contexto da Ocorrência (11 perguntas + 4 condicionais)"""

    def create_state_machine(self):
        return BOStateMachine()

    def has_auto_answer(self) -> bool:
        return False  # Seção 1 não tem skip question


class Section2Handler(SectionHandler):
    """Seção 2: Abordagem a Veículo (13 perguntas)"""

    def create_state_machine(self):
        return BOStateMachineSection2()

    def has_auto_answer(self) -> bool:
        return True  # Skip question 2.1: "Havia veículo envolvido?"


class Section3Handler(SectionHandler):
    """Seção 3: Campana (8 perguntas)"""

    def create_state_machine(self):
        return BOStateMachineSection3()

    def has_auto_answer(self) -> bool:
        return True  # Skip question 3.1: "Houve campana?"


class Section4Handler(SectionHandler):
    """Seção 4: Entrada em Domicílio (6 perguntas)"""

    def create_state_machine(self):
        return BOStateMachineSection4()

    def has_auto_answer(self) -> bool:
        return True  # Skip question 4.1: "Houve entrada em domicílio?"


class Section5Handler(SectionHandler):
    """Seção 5: Fundada Suspeita (7 perguntas)"""

    def create_state_machine(self):
        return BOStateMachineSection5()

    def has_auto_answer(self) -> bool:
        return True  # Skip question 5.1: "Houve fundada suspeita?"


class Section6Handler(SectionHandler):
    """
    Seção 6: Uso de Força (6 perguntas)

    IMPORTANTE: A partir da v0.13.1, esta seção NÃO tem mais auto-resposta.
    Bug corrigido: 6.1 é pergunta aberta, não SIM/NÃO.
    """

    def create_state_machine(self):
        return BOStateMachineSection6()

    def has_auto_answer(self) -> bool:
        return False  # BUG CORRIGIDO: 6.1 não é skip question


class Section7Handler(SectionHandler):
    """Seção 7: Apreensões (9 perguntas)"""

    def create_state_machine(self):
        return BOStateMachineSection7()

    def has_auto_answer(self) -> bool:
        return True  # Skip question 7.1: "Houve apreensão?"


class Section8Handler(SectionHandler):
    """Seção 8: Qualificação Completa (7 perguntas)"""

    def create_state_machine(self):
        return BOStateMachineSection8()

    def has_auto_answer(self) -> bool:
        return False  # Seção 8 não tem skip question


# =============================================================================
# FACTORY
# =============================================================================

# Mapeamento seção → Handler
SECTION_HANDLERS = {
    1: Section1Handler,
    2: Section2Handler,
    3: Section3Handler,
    4: Section4Handler,
    5: Section5Handler,
    6: Section6Handler,
    7: Section7Handler,
    8: Section8Handler,
}


def create_section_handler(
    session_id: str,
    bo_id: str,
    section_number: int
) -> SectionHandler:
    """
    Factory method: Cria o handler apropriado para a seção.

    Args:
        session_id: ID da sessão UUID
        bo_id: ID do BO (BO-YYYYMMDD-xxxxx)
        section_number: Número da seção (1-8)

    Returns:
        SectionHandler: Handler concreto para a seção

    Raises:
        ValueError: Se section_number não estiver entre 1-8

    Examples:
        >>> handler = create_section_handler("abc-123", "BO-20260102-001", 2)
        >>> response = handler.start(session_data)
        >>> print(response["question"])  # Primeira pergunta da seção 2
    """
    if section_number not in SECTION_HANDLERS:
        raise ValueError(
            f"Seção {section_number} inválida. "
            f"Esperado: 1-8, recebido: {section_number}"
        )

    handler_class = SECTION_HANDLERS[section_number]
    return handler_class(session_id, bo_id, section_number)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_section_metadata(section_number: int) -> Dict[str, Any]:
    """
    Retorna metadados sobre uma seção.

    Útil para debugging e documentação.

    Returns:
        Dict com: name, has_skip_question, question_count, handler_class
    """
    metadata = {
        1: {"name": "Contexto da Ocorrência", "has_skip": False, "questions": 11},
        2: {"name": "Abordagem a Veículo", "has_skip": True, "questions": 13},
        3: {"name": "Campana", "has_skip": True, "questions": 8},
        4: {"name": "Entrada em Domicílio", "has_skip": True, "questions": 6},
        5: {"name": "Fundada Suspeita", "has_skip": True, "questions": 7},
        6: {"name": "Uso de Força", "has_skip": False, "questions": 6},
        7: {"name": "Apreensões", "has_skip": True, "questions": 9},
        8: {"name": "Qualificação Completa", "has_skip": False, "questions": 7},
    }

    if section_number not in metadata:
        raise ValueError(f"Seção {section_number} não existe")

    data = metadata[section_number]
    data["handler_class"] = SECTION_HANDLERS[section_number].__name__

    return data
