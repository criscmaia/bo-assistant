# -*- coding: utf-8 -*-
"""
State Machine para Seção 6: Reação e Uso da Força
Baseado no material de Claudio Moreira (Súmula Vinculante 11 do STF)

Author: Cristiano Maia + Claude (Anthropic)
Date: 22/12/2025
"""
from typing import Dict, Optional


# Perguntas da Seção 6 (fonte: _02_uso_da_forca_e_algemas.txt)
SECTION6_QUESTIONS = {
    "6.1": "Houve resistência durante a abordagem?",
    "6.2": "Descreva a resistência com fatos concretos (o que o autor fez exatamente?)",
    "6.3": "Qual técnica foi aplicada, por quem (graduação + nome), e qual foi o resultado?",
    "6.4": "Por que foi necessário algemar? (justificativa objetiva)",
    "6.5": "Houve ferimentos? Se sim, descreva: em quem, qual lesão, atendimento e nº da ficha hospitalar"
}

SECTION6_STEPS = ["6.1", "6.2", "6.3", "6.4", "6.5", "complete"]


class BOStateMachineSection6:
    """
    State Machine para gerenciar o fluxo de perguntas da Seção 6 (Reação e Uso da Força).

    Comportamento especial:
    - Pergunta 6.1 é condicional: se resposta = "NÃO", pula toda a seção
    - Se resposta = "SIM", percorre perguntas 6.2 até 6.5
    - Fundamento jurídico: Súmula Vinculante 11 (STF) + Decreto 8.858/2016
    """

    def __init__(self):
        self.current_step = "6.1"
        self.answers: Dict[str, str] = {}
        self.step_index = 0
        self.section_skipped = False  # True se responder "NÃO" na pergunta 6.1

    def get_current_question(self) -> str:
        """Retorna o texto da pergunta atual"""
        if self.current_step in SECTION6_QUESTIONS:
            return SECTION6_QUESTIONS[self.current_step]
        return ""

    def store_answer(self, answer: str):
        """
        Armazena a resposta da pergunta atual.

        Lógica especial para pergunta 6.1:
        - Se resposta = "NÃO", marca seção como pulada e vai direto para "complete"
        - Caso contrário, armazena normalmente
        """
        answer_clean = answer.strip()

        # Pergunta 6.1 condicional - verifica se houve resistência
        if self.current_step == "6.1":
            answer_upper = answer_clean.upper()
            # Aceita variações: NÃO, NAO, N, NENHUM, etc.
            if answer_upper in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
                self.section_skipped = True
                self.answers["6.1"] = "NÃO"
                self.current_step = "complete"
                self.step_index = len(SECTION6_STEPS) - 1
                return

        # Armazena resposta normalmente
        self.answers[self.current_step] = answer_clean

    def next_step(self):
        """Avança para a próxima pergunta"""
        # Se seção foi pulada, não avança
        if self.section_skipped:
            return

        # Avança para próximo step
        if self.step_index < len(SECTION6_STEPS) - 1:
            self.step_index += 1
            self.current_step = SECTION6_STEPS[self.step_index]

    def is_section_complete(self) -> bool:
        """Verifica se a seção está completa"""
        return self.current_step == "complete"

    def was_section_skipped(self) -> bool:
        """Retorna True se a seção foi pulada (não houve resistência)"""
        return self.section_skipped

    def get_skip_reason(self) -> Optional[str]:
        """Retorna texto explicativo se seção foi pulada"""
        if self.section_skipped:
            return "Não se aplica (não houve resistência durante a abordagem)"
        return None

    def get_all_answers(self) -> Dict[str, str]:
        """Retorna todas as respostas coletadas"""
        return self.answers.copy()

    def get_formatted_answers(self) -> str:
        """Retorna respostas formatadas para debug/log"""
        if not self.answers:
            return "Nenhuma resposta coletada"

        formatted = []
        for step, answer in self.answers.items():
            question = SECTION6_QUESTIONS.get(step, "Pergunta desconhecida")
            formatted.append(f"{step} - {question}\n   Resposta: {answer}")

        return "\n\n".join(formatted)

    def get_progress(self) -> Dict[str, any]:
        """
        Retorna informações de progresso para o frontend.

        Returns:
            {
                "current_step": "6.3",
                "total_steps": 5,
                "completed_steps": 3,
                "progress_percentage": 60.0,
                "section_skipped": False
            }
        """
        # Se seção foi pulada, considera 100% completo
        if self.section_skipped:
            return {
                "current_step": "complete",
                "total_steps": 5,
                "completed_steps": 5,
                "progress_percentage": 100.0,
                "section_skipped": True
            }

        # Total de steps (excluindo "complete")
        total_steps = len(SECTION6_STEPS) - 1
        completed_steps = len(self.answers)

        # Calcula porcentagem
        progress_percentage = (completed_steps / total_steps) * 100 if total_steps > 0 else 0

        return {
            "current_step": self.current_step,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "progress_percentage": round(progress_percentage, 1),
            "section_skipped": False
        }

    def get_answer(self, step: str) -> Optional[str]:
        """Retorna a resposta de uma pergunta específica"""
        return self.answers.get(step)

    def update_answer(self, step: str, new_answer: str) -> bool:
        """
        Atualiza a resposta de uma pergunta anterior.

        Returns:
            True se atualização foi bem-sucedida, False caso contrário
        """
        if step not in SECTION6_QUESTIONS:
            return False

        # Não permite editar se seção foi pulada
        if self.section_skipped and step != "6.1":
            return False

        # Se editando 6.1 de "NÃO" para "SIM", precisa resetar seção
        if step == "6.1" and self.section_skipped:
            answer_upper = new_answer.strip().upper()
            if answer_upper not in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
                # Resetar seção
                self.section_skipped = False
                self.current_step = "6.2"
                self.step_index = 1
                self.answers = {"6.1": new_answer.strip()}
                return True

        self.answers[step] = new_answer.strip()
        return True

    def reset(self):
        """Reseta a state machine para o início da seção"""
        self.current_step = "6.1"
        self.answers = {}
        self.step_index = 0
        self.section_skipped = False
