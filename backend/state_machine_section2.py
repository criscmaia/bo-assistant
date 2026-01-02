# -*- coding: utf-8 -*-
"""
State Machine para Seção 2: Abordagem a Veículo
Refatorado para usar Template Method Pattern (v0.13.1)

Author: Cristiano Maia + Claude (Anthropic)
Date: 02/01/2026
"""
from typing import Dict, List, Optional
from backend.base_state_machine import BaseStateMachine


# Perguntas da Seção 2 (fonte: Seções Revisadas 2025-12-30.md - Claudio Moreira)
# v0.12.9: Expandido de 11 para 13 perguntas + reordenação (contexto antes de placa)
SECTION2_QUESTIONS = {
    "2.1": "Havia veículo envolvido na ocorrência?",
    "2.2": "Onde e em que contexto o veículo foi visualizado?",
    "2.3": "Qual a marca, modelo, cor e placa do veículo?",
    "2.4": "Quem da equipe viu o veículo? (nome do policial + o que chamou atenção)",
    "2.5": "Descreva se houve reação do motorista ou ocupantes (manobra brusca, tentativa de fuga, descarte de objeto).",
    "2.6": "Quem deu a ordem de parada e como? (sirene, apito, gesto, farol)",
    "2.7": "O veículo parou imediatamente ou houve perseguição?",
    "2.8": "Se houve perseguição, por qual motivo o veículo parou? (desistiu, cercado, bateu, capotou)",
    "2.9": "Descreva como foi a abordagem (quem mandou descer, posicionamento)",
    "2.10": "Quem realizou a busca veicular e em quais partes do veículo?",
    "2.11": "Quem realizou a busca pessoal nos ocupantes?",
    "2.12": "O que foi localizado, com quem ou em qual parte do veículo/corpo estava cada material?",
    "2.13": "O veículo apresentava irregularidade? (furto, roubo, clonagem, adulteração)"
}

SECTION2_STEPS = ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9", "2.10", "2.11", "2.12", "2.13", "complete"]


class BOStateMachineSection2(BaseStateMachine):
    """
    State Machine para Seção 2: Abordagem a Veículo.

    Características:
    - Pergunta 2.1 é condicional: se resposta = "NÃO", pula toda a seção
    - Se resposta = "SIM", percorre perguntas 2.2 até 2.13
    - Total: 13 perguntas
    """

    # =========================================================================
    # IMPLEMENTAÇÃO DOS MÉTODOS ABSTRATOS
    # =========================================================================

    def _get_initial_step(self) -> str:
        """Retorna step inicial da Seção 2"""
        return "2.1"

    def _get_steps(self) -> List[str]:
        """Retorna lista de steps da Seção 2"""
        return SECTION2_STEPS

    def _get_questions(self) -> Dict[str, str]:
        """Retorna dicionário de perguntas da Seção 2"""
        return SECTION2_QUESTIONS

    # =========================================================================
    # LÓGICA CONDICIONAL - Sobrescreve hooks
    # =========================================================================

    def _on_answer_stored(self, step: str, answer: str) -> None:
        """
        Hook executado após armazenar resposta.

        Lógica especial para pergunta 2.1:
        - Se resposta = "NÃO", marca seção como pulada e vai direto para "complete"
        """
        if step == "2.1" and self._is_negative_answer(answer):
            # Marcar seção como pulada
            self.section_skipped = True
            self.current_step = "complete"
            self.step_index = len(SECTION2_STEPS) - 1

    def _get_skip_reason(self) -> Optional[str]:
        """Retorna razão pela qual seção foi pulada"""
        if self.section_skipped:
            return "Não se aplica (não havia veículo envolvido na ocorrência)"
        return None

    # =========================================================================
    # MÉTODOS ESPECÍFICOS DA SEÇÃO 2
    # =========================================================================

    def get_answer(self, step: str) -> Optional[str]:
        """Retorna a resposta de uma pergunta específica"""
        return self.answers.get(step)

    def update_answer(self, step: str, new_answer: str) -> bool:
        """
        Atualiza a resposta de uma pergunta anterior.

        Returns:
            True se atualização foi bem-sucedida, False caso contrário
        """
        if step not in SECTION2_QUESTIONS:
            return False

        # Não permite editar se seção foi pulada (exceto 2.1)
        if self.section_skipped and step != "2.1":
            return False

        # Se editando 2.1 de "NÃO" para "SIM", precisa resetar seção
        if step == "2.1" and self.section_skipped:
            if not self._is_negative_answer(new_answer):
                # Resetar seção
                self.section_skipped = False
                self.current_step = "2.2"
                self.step_index = 1
                self.answers = {"2.1": new_answer.strip()}
                return True

        self.answers[step] = new_answer.strip()
        return True

    def reset(self):
        """Reseta a state machine para o início da seção"""
        self.__init__()

    # =========================================================================
    # MÉTODOS LEGADOS (mantidos para compatibilidade)
    # =========================================================================

    def was_section_skipped(self) -> bool:
        """
        Alias para self.section_skipped (compatibilidade).

        DEPRECATED: Use self.section_skipped diretamente
        """
        return self.section_skipped

    def get_skip_reason(self) -> Optional[str]:
        """
        Alias para _get_skip_reason() (compatibilidade).

        DEPRECATED: Use self.get_skip_reason() do BaseStateMachine
        """
        return self._get_skip_reason()
