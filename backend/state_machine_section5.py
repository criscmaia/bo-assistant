# -*- coding: utf-8 -*-
"""
State Machine para Seção 5: Fundada Suspeita
Baseado no material de Claudio Moreira

Author: Cristiano Maia + Claude (Anthropic)
Date: 22/12/2025
"""
from typing import Dict, Optional


# Perguntas da Seção 5 (fonte: REGRAS GERAIS - GPT Tráfico e material do Claudio)
SECTION5_QUESTIONS = {
    "5.1": "Houve abordagem por fundada suspeita (sem veículo, campana ou entrada em domicílio)?",
    "5.2": "O que a equipe viu ao chegar no local da ocorrência?",
    "5.3": "Quem viu, de onde viu, o que exatamente viu? (informe graduação e nome)",
    "5.4": "Descreva as características e ações dos abordados (roupa, porte, gestos, nome completo e vulgo)"
}

SECTION5_STEPS = ["5.1", "5.2", "5.3", "5.4", "complete"]


class BOStateMachineSection5:
    """
    State Machine para gerenciar o fluxo de perguntas da Seção 5 (Fundada Suspeita).

    Comportamento especial:
    - Pergunta 5.1 é condicional: se resposta = "NÃO", pula toda a seção
    - Se resposta = "SIM", percorre perguntas 5.2 até 5.4
    """

    def __init__(self):
        self.current_step = "5.1"
        self.answers: Dict[str, str] = {}
        self.step_index = 0
        self.section_skipped = False  # True se responder "NÃO" na pergunta 5.1

    def get_current_question(self) -> str:
        """Retorna o texto da pergunta atual"""
        if self.current_step in SECTION5_QUESTIONS:
            return SECTION5_QUESTIONS[self.current_step]
        return ""

    def store_answer(self, answer: str):
        """
        Armazena a resposta da pergunta atual.

        Lógica especial para pergunta 5.1:
        - Se resposta = "NÃO", marca seção como pulada e vai direto para "complete"
        - Caso contrário, armazena normalmente
        """
        answer_clean = answer.strip()

        # Pergunta 5.1 condicional - verifica se houve abordagem por fundada suspeita
        if self.current_step == "5.1":
            answer_upper = answer_clean.upper()
            # Aceita variações: NÃO, NAO, N, NENHUM, etc.
            if answer_upper in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
                self.section_skipped = True
                self.answers["5.1"] = "NÃO"
                self.current_step = "complete"
                self.step_index = len(SECTION5_STEPS) - 1
                return

        # Armazena resposta normalmente
        self.answers[self.current_step] = answer_clean

    def next_step(self):
        """Avança para a próxima pergunta"""
        # Se seção foi pulada, não avança
        if self.section_skipped:
            return

        # Avança para próximo step
        if self.step_index < len(SECTION5_STEPS) - 1:
            self.step_index += 1
            self.current_step = SECTION5_STEPS[self.step_index]

    def is_section_complete(self) -> bool:
        """Verifica se a seção está completa"""
        return self.current_step == "complete"

    def was_section_skipped(self) -> bool:
        """Retorna True se a seção foi pulada (não houve abordagem por fundada suspeita)"""
        return self.section_skipped

    def get_skip_reason(self) -> Optional[str]:
        """Retorna texto explicativo se seção foi pulada"""
        if self.section_skipped:
            return "Não se aplica (não houve abordagem por fundada suspeita)"
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
            question = SECTION5_QUESTIONS.get(step, "Pergunta desconhecida")
            formatted.append(f"{step} - {question}\n   Resposta: {answer}")

        return "\n\n".join(formatted)

    def get_progress(self) -> Dict[str, any]:
        """
        Retorna informações de progresso para o frontend.

        Returns:
            {
                "current_step": "5.3",
                "total_steps": 4,
                "completed_steps": 3,
                "progress_percentage": 75.0,
                "section_skipped": False
            }
        """
        # Se seção foi pulada, considera 100% completo
        if self.section_skipped:
            return {
                "current_step": "complete",
                "total_steps": 4,
                "completed_steps": 4,
                "progress_percentage": 100.0,
                "section_skipped": True
            }

        # Total de steps (excluindo "complete")
        total_steps = len(SECTION5_STEPS) - 1
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
        if step not in SECTION5_QUESTIONS:
            return False

        # Não permite editar se seção foi pulada
        if self.section_skipped and step != "5.1":
            return False

        # Se editando 5.1 de "NÃO" para "SIM", precisa resetar seção
        if step == "5.1" and self.section_skipped:
            answer_upper = new_answer.strip().upper()
            if answer_upper not in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
                # Resetar seção
                self.section_skipped = False
                self.current_step = "5.2"
                self.step_index = 1
                self.answers = {"5.1": new_answer.strip()}
                return True

        self.answers[step] = new_answer.strip()
        return True

    def reset(self):
        """Reseta a state machine para o início da seção"""
        self.current_step = "5.1"
        self.answers = {}
        self.step_index = 0
        self.section_skipped = False
