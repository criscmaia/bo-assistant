# -*- coding: utf-8 -*-
"""
State Machine para Seção 3: Campana (Vigilância Velada)
Baseado no material de Claudio Moreira

Author: Cristiano Maia + Claude (Anthropic)
Date: 19/12/2025
"""
from typing import Dict, Optional


# Perguntas da Seção 3 (fonte: REGRAS GERAIS - GPT Tráfico, material do Claudio)
SECTION3_QUESTIONS = {
    "3.1": "A equipe realizou campana antes da abordagem?",
    "3.2": "Onde foi feita a campana? (local, ponto de observação, distância aproximada)",
    "3.3": "Qual policial tinha visão direta e o que cada um via?",
    "3.4": "O que motivou a campana?",
    "3.5": "Quanto tempo durou a campana? (contínua ou alternada)",
    "3.6": "O que foi observado durante a campana? (descreva atos CONCRETOS)",
    "3.7": "Houve abordagem de usuários durante a campana?",
    "3.8": "Houve fuga ao notar a equipe? Como ocorreu?"
}

SECTION3_STEPS = ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "complete"]


class BOStateMachineSection3:
    """
    State Machine para gerenciar o fluxo de perguntas da Seção 3 (Campana - Vigilância Velada).

    Comportamento especial:
    - Pergunta 3.1 é condicional: se resposta = "NÃO", pula toda a seção
    - Se resposta = "SIM", percorre perguntas 3.2 até 3.8
    """

    def __init__(self):
        self.current_step = "3.1"
        self.answers: Dict[str, str] = {}
        self.step_index = 0
        self.section_skipped = False  # True se responder "NÃO" na pergunta 3.1

    def get_current_question(self) -> str:
        """Retorna o texto da pergunta atual"""
        if self.current_step in SECTION3_QUESTIONS:
            return SECTION3_QUESTIONS[self.current_step]
        return ""

    def store_answer(self, answer: str):
        """
        Armazena a resposta da pergunta atual.

        Lógica especial para pergunta 3.1:
        - Se resposta = "NÃO", marca seção como pulada e vai direto para "complete"
        - Caso contrário, armazena normalmente
        """
        answer_clean = answer.strip()

        # Pergunta 3.1 condicional - verifica se houve campana
        if self.current_step == "3.1":
            answer_upper = answer_clean.upper()
            # Aceita variações: NÃO, NAO, N, NENHUM, etc.
            if answer_upper in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
                self.section_skipped = True
                self.answers["3.1"] = "NÃO"
                self.current_step = "complete"
                self.step_index = len(SECTION3_STEPS) - 1
                return

        # Armazena resposta normalmente
        self.answers[self.current_step] = answer_clean

    def next_step(self):
        """Avança para a próxima pergunta"""
        # Se seção foi pulada, não avança
        if self.section_skipped:
            return

        # Avança para próximo step
        if self.step_index < len(SECTION3_STEPS) - 1:
            self.step_index += 1
            self.current_step = SECTION3_STEPS[self.step_index]

    def is_section_complete(self) -> bool:
        """Verifica se a seção está completa"""
        return self.current_step == "complete"

    def was_section_skipped(self) -> bool:
        """Retorna True se a seção foi pulada (não havia campana)"""
        return self.section_skipped

    def get_skip_reason(self) -> Optional[str]:
        """Retorna texto explicativo se seção foi pulada"""
        if self.section_skipped:
            return "Não se aplica (não houve campana antes da abordagem)"
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
            question = SECTION3_QUESTIONS.get(step, "Pergunta desconhecida")
            formatted.append(f"{step} - {question}\n   Resposta: {answer}")

        return "\n\n".join(formatted)

    def get_progress(self) -> Dict[str, any]:
        """
        Retorna informações de progresso para o frontend.

        Returns:
            {
                "current_step": "3.3",
                "total_steps": 8,
                "completed_steps": 3,
                "progress_percentage": 37.5,
                "section_skipped": False
            }
        """
        # Se seção foi pulada, considera 100% completo
        if self.section_skipped:
            return {
                "current_step": "complete",
                "total_steps": 8,
                "completed_steps": 8,
                "progress_percentage": 100.0,
                "section_skipped": True
            }

        # Total de steps (excluindo "complete")
        total_steps = len(SECTION3_STEPS) - 1
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
        if step not in SECTION3_QUESTIONS:
            return False

        # Não permite editar se seção foi pulada
        if self.section_skipped and step != "3.1":
            return False

        # Se editando 3.1 de "NÃO" para "SIM", precisa resetar seção
        if step == "3.1" and self.section_skipped:
            answer_upper = new_answer.strip().upper()
            if answer_upper not in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
                # Resetar seção
                self.section_skipped = False
                self.current_step = "3.2"
                self.step_index = 1
                self.answers = {"3.1": new_answer.strip()}
                return True

        self.answers[step] = new_answer.strip()
        return True

    def reset(self):
        """Reseta a state machine para o início da seção"""
        self.current_step = "3.1"
        self.answers = {}
        self.step_index = 0
        self.section_skipped = False
