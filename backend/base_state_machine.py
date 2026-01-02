# -*- coding: utf-8 -*-
"""
BaseStateMachine - Classe base para todas as State Machines do BO

Template Method Pattern - Define o fluxo comum e permite que subclasses
implementem apenas os métodos específicos de cada seção.

Author: Cristiano Maia + Claude (Anthropic)
Date: 02/01/2026
Version: v0.13.1
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class BaseStateMachine(ABC):
    """
    Classe base abstrata para State Machines do BO.

    Implementa Template Method Pattern:
    - Define fluxo comum (store_answer, next_step, is_complete)
    - Subclasses implementam métodos abstratos (_get_initial_step, _get_steps, _get_questions)
    - Subclasses podem sobrescrever hooks para lógica condicional

    Elimina ~550 linhas de código duplicado entre 8 state machines.
    """

    def __init__(self):
        """Inicializa state machine com estado inicial"""
        self.current_step = self._get_initial_step()
        self.answers: Dict[str, str] = {}
        self.step_index = 0
        self.section_skipped = False  # Para seções com skip condicional

    # =========================================================================
    # MÉTODOS ABSTRATOS - Devem ser implementados por subclasses
    # =========================================================================

    @abstractmethod
    def _get_initial_step(self) -> str:
        """
        Retorna o step inicial da seção (ex: "1.1", "2.1", etc.)

        Returns:
            str: ID do primeiro step
        """
        pass

    @abstractmethod
    def _get_steps(self) -> List[str]:
        """
        Retorna lista ordenada de todos os steps da seção.
        Deve incluir "complete" como último step.

        Returns:
            List[str]: Lista de IDs dos steps (ex: ["1.1", "1.2", ..., "complete"])
        """
        pass

    @abstractmethod
    def _get_questions(self) -> Dict[str, str]:
        """
        Retorna dicionário com as perguntas da seção.

        Returns:
            Dict[str, str]: Mapeamento step_id -> texto da pergunta
        """
        pass

    # =========================================================================
    # HOOKS - Podem ser sobrescritos para lógica específica
    # =========================================================================

    def _should_skip_step(self, step: str) -> bool:
        """
        Hook: determina se um step deve ser pulado baseado em respostas anteriores.

        Exemplo: Pular 1.5.1 e 1.5.2 se resposta de 1.5 for "NÃO"

        Args:
            step: ID do step a verificar

        Returns:
            bool: True se deve pular o step
        """
        return False

    def _on_answer_stored(self, step: str, answer: str) -> None:
        """
        Hook: executado após armazenar resposta.
        Útil para lógica condicional (ex: marcar seção como skipada)

        Args:
            step: ID do step respondido
            answer: Resposta fornecida
        """
        pass

    def _get_skip_reason(self) -> Optional[str]:
        """
        Hook: retorna texto explicativo se seção foi pulada.

        Returns:
            str | None: Mensagem explicativa ou None
        """
        if self.section_skipped:
            return "Seção não se aplica às circunstâncias da ocorrência"
        return None

    # =========================================================================
    # TEMPLATE METHOD - Fluxo comum (não sobrescrever)
    # =========================================================================

    def get_current_question(self) -> str:
        """
        Retorna o texto da pergunta atual.

        Returns:
            str: Texto da pergunta ou string vazia se completa
        """
        if self.current_step == "complete":
            return ""

        questions = self._get_questions()
        return questions.get(self.current_step, "Erro: pergunta não encontrada")

    def store_answer(self, answer: str) -> None:
        """
        Armazena resposta da pergunta atual.

        Template Method: aplica validação básica e chama hook para lógica específica.

        Args:
            answer: Resposta fornecida pelo usuário
        """
        if self.current_step == "complete":
            return

        answer_clean = answer.strip()
        self.answers[self.current_step] = answer_clean

        # Hook para lógica específica após armazenar
        self._on_answer_stored(self.current_step, answer_clean)

    def next_step(self) -> None:
        """
        Avança para a próxima pergunta.

        Template Method: implementa lógica de navegação com suporte a skip condicional.
        """
        # Se seção foi pulada, não avança
        if self.section_skipped:
            return

        steps = self._get_steps()

        # Avançar step_index até encontrar próximo step válido ou complete
        while self.step_index < len(steps) - 1:
            self.step_index += 1
            next_step_candidate = steps[self.step_index]

            # Verificar se deve pular este step (lógica condicional)
            if not self._should_skip_step(next_step_candidate):
                self.current_step = next_step_candidate
                break

            # Se deve pular, continua o loop para próximo step

    def is_section_complete(self) -> bool:
        """
        Verifica se a seção está completa.

        Returns:
            bool: True se todas perguntas foram respondidas
        """
        return self.current_step == "complete"

    def was_section_skipped(self) -> bool:
        """
        Verifica se a seção foi pulada.

        Returns:
            bool: True se seção foi marcada como skipada
        """
        return self.section_skipped

    def get_skip_reason(self) -> Optional[str]:
        """
        Retorna razão pela qual seção foi pulada.

        Returns:
            str | None: Texto explicativo ou None
        """
        return self._get_skip_reason()

    def get_all_answers(self) -> Dict[str, str]:
        """
        Retorna todas as respostas coletadas.

        Returns:
            Dict[str, str]: Cópia do dicionário de respostas
        """
        return self.answers.copy()

    def get_formatted_answers(self) -> str:
        """
        Retorna respostas formatadas para debug/log.

        Returns:
            str: Respostas formatadas com perguntas e respostas
        """
        if not self.answers:
            return "Nenhuma resposta coletada"

        questions = self._get_questions()
        formatted = []

        for step, answer in self.answers.items():
            question = questions.get(step, "Pergunta desconhecida")
            formatted.append(f"{step} - {question}\n   Resposta: {answer}")

        return "\n\n".join(formatted)

    def get_progress(self) -> Dict[str, Any]:
        """
        Retorna informações de progresso para o frontend.

        Returns:
            Dict com:
            - current_step: Step atual
            - total_steps: Total de perguntas (excluindo "complete")
            - completed_steps: Número de respostas armazenadas
            - progress_percentage: Porcentagem de progresso
            - section_skipped: Se seção foi pulada
        """
        steps = self._get_steps()
        total_steps = len(steps) - 1  # Excluir "complete"
        completed_steps = len(self.answers)

        progress_percentage = 0.0
        if total_steps > 0:
            progress_percentage = (completed_steps / total_steps) * 100

        return {
            "current_step": self.current_step,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "progress_percentage": round(progress_percentage, 1),
            "section_skipped": self.section_skipped
        }

    # =========================================================================
    # MÉTODOS AUXILIARES
    # =========================================================================

    def _is_negative_answer(self, answer: str) -> bool:
        """
        Verifica se resposta é negativa (útil para lógica condicional).

        Args:
            answer: Resposta a verificar

        Returns:
            bool: True se resposta é negativa
        """
        answer_upper = answer.strip().upper()
        negative_variants = ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO", "NADA"]
        return answer_upper in negative_variants

    def _is_positive_answer(self, answer: str) -> bool:
        """
        Verifica se resposta é positiva (útil para lógica condicional).

        Args:
            answer: Resposta a verificar

        Returns:
            bool: True se resposta é positiva
        """
        answer_upper = answer.strip().upper()
        positive_variants = ["SIM", "S", "POSITIVO", "AFIRMATIVO"]
        return answer_upper in positive_variants
