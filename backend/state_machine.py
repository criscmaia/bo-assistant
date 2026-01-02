# -*- coding: utf-8 -*-
"""
State Machine para Seção 1: Contexto da Ocorrência
Refatorado para usar Template Method Pattern (v0.13.1)

Author: Cristiano Maia + Claude (Anthropic)
Date: 02/01/2026
"""
from typing import Dict, List
from backend.base_state_machine import BaseStateMachine


# Perguntas da Seção 1 - Contexto da Ocorrência
SECTION1_QUESTIONS = {
    "1.1": "Dia, data e hora do acionamento.",
    "1.2": "Composição da guarnição e prefixo da viatura.",
    "1.3": "Como foi acionado? (190, DDU, mandado de prisão/busca, patrulhamento preventivo, outro)",
    "1.4": "Descreva as informações recebidas no acionamento (ordem de serviço, despacho COPOM, denúncia).",
    "1.5": "Houve deslocamento entre o ponto de acionamento e o local da ocorrência?",
    "1.5.1": "Local de onde a guarnição partiu.",
    "1.5.2": "Houve alguma alteração durante o percurso? (radar, sinal fechado, acidente)",
    "1.6": "Local exato da ocorrência (logradouro, número, bairro, ponto de referência).",
    "1.7": "O local é conhecido como ponto de tráfico? Descreva histórico de ocorrências ou denúncias.",
    "1.8": "O local é dominado por facção criminosa? Qual? Descreva evidências.",
    "1.9": "O local é ou fica próximo de espaço de interesse público qualificado? (escola, hospital, transporte público, unidade prisional/militar)",
    "1.9.1": "Nome do estabelecimento.",
    "1.9.2": "Distância aproximada (ex: dois quarteirões, 300 metros)."
}

# Ordem das perguntas
SECTION1_STEPS = ["1.1", "1.2", "1.3", "1.4", "1.5", "1.5.1", "1.5.2", "1.6", "1.7", "1.8", "1.9", "1.9.1", "1.9.2", "complete"]


class BOStateMachine(BaseStateMachine):
    """
    State Machine para Seção 1: Contexto da Ocorrência.

    Características:
    - Perguntas condicionais: 1.5.x (se 1.5=SIM) e 1.9.x (se 1.9=SIM)
    - Total de perguntas varia de 9 a 13 dependendo das respostas
    """

    # Compatibilidade com código legado (será removido em v0.14.0)
    QUESTIONS = SECTION1_QUESTIONS
    STEPS = SECTION1_STEPS

    # =========================================================================
    # IMPLEMENTAÇÃO DOS MÉTODOS ABSTRATOS
    # =========================================================================

    def _get_initial_step(self) -> str:
        """Retorna step inicial da Seção 1"""
        return "1.1"

    def _get_steps(self) -> List[str]:
        """Retorna lista de steps da Seção 1"""
        return SECTION1_STEPS

    def _get_questions(self) -> Dict[str, str]:
        """Retorna dicionário de perguntas da Seção 1"""
        return SECTION1_QUESTIONS

    # =========================================================================
    # LÓGICA CONDICIONAL - Sobrescreve hook _should_skip_step
    # =========================================================================

    def _should_skip_step(self, step: str) -> bool:
        """
        Implementa lógica condicional para sub-perguntas 1.5.x e 1.9.x

        Args:
            step: Step a verificar

        Returns:
            bool: True se deve pular o step
        """
        # Lógica condicional para 1.5.x
        if step in ["1.5.1", "1.5.2"]:
            answer_1_5 = self.answers.get("1.5", "")
            if self._is_negative_answer(answer_1_5):
                return True  # Pular 1.5.1 e 1.5.2

        # Lógica condicional para 1.9.x
        if step in ["1.9.1", "1.9.2"]:
            answer_1_9 = self.answers.get("1.9", "")
            if self._is_negative_answer(answer_1_9):
                return True  # Pular 1.9.1 e 1.9.2

        return False

    # =========================================================================
    # MÉTODOS ESPECÍFICOS DA SEÇÃO 1
    # =========================================================================

    def get_progress(self) -> Dict[str, any]:
        """
        Retorna progresso com cálculo dinâmico de total de perguntas.

        Seção 1 tem perguntas condicionais:
        - Base: 9 perguntas obrigatórias (1.1-1.4, 1.6-1.9)
        - Se 1.5 = SIM: +2 (1.5.1, 1.5.2)
        - Se 1.9 = SIM: +2 (1.9.1, 1.9.2)
        - Máximo: 13 perguntas

        Returns:
            Dict com progresso detalhado
        """
        base_questions = 9  # Perguntas obrigatórias
        answered = len(self.answers)

        # Calcular total baseado em respostas condicionais
        total = base_questions

        # Se resposta 1.5 = SIM, adiciona 2 perguntas condicionais
        answer_1_5 = self.answers.get("1.5", "")
        if self._is_positive_answer(answer_1_5):
            total += 2

        # Se resposta 1.9 = SIM, adiciona 2 perguntas condicionais
        answer_1_9 = self.answers.get("1.9", "")
        if self._is_positive_answer(answer_1_9):
            total += 2

        return {
            "total": total,              # 9, 11, ou 13 dependendo das respostas
            "total_base": base_questions, # Sempre 9 (perguntas obrigatórias)
            "answered": answered,
            "percentage": int((answered / total) * 100) if total > 0 else 0,
            "current_question": self.current_step,
            # Campos adicionais do BaseStateMachine
            "current_step": self.current_step,
            "total_steps": total,
            "completed_steps": answered,
            "progress_percentage": round((answered / total) * 100, 1) if total > 0 else 0,
            "section_skipped": self.section_skipped
        }

    def reset(self) -> None:
        """
        Reinicia a state machine (útil para testes).
        """
        self.__init__()
