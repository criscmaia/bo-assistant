# -*- coding: utf-8 -*-
"""
State Machine para Seção 4: Entrada em Domicílio
Baseado no material de Claudio Moreira

Author: Cristiano Maia + Claude (Anthropic)
Date: 21/12/2025
"""
from typing import Dict, Optional


# Perguntas da Seção 4 (fonte: REGRAS GERAIS - GPT Tráfico, material do Claudio)
SECTION4_QUESTIONS = {
    "4.1": "Houve entrada em domicílio durante a ocorrência?",
    "4.2": "O que foi visto, ouvido ou sentido ANTES do ingresso? (descreva a justa causa concreta)",
    "4.3": "Qual policial presenciou e o que exatamente viu/ouviu? (informe graduação e nome)",
    "4.4": "Como ocorreu o ingresso? (perseguição contínua, autorização do morador, flagrante visual/auditivo)",
    "4.5": "Descreva a ação de cada policial: quem entrou primeiro, por onde, quem ficou na contenção"
}

SECTION4_STEPS = ["4.1", "4.2", "4.3", "4.4", "4.5", "complete"]


class BOStateMachineSection4:
    """
    State Machine para gerenciar o fluxo de perguntas da Seção 4 (Entrada em Domicílio).

    Comportamento especial:
    - Pergunta 4.1 é condicional: se resposta = "NÃO", pula toda a seção
    - Se resposta = "SIM", percorre perguntas 4.2 até 4.5
    """

    def __init__(self):
        self.current_step = "4.1"
        self.answers: Dict[str, str] = {}
        self.step_index = 0
        self.section_skipped = False  # True se responder "NÃO" na pergunta 4.1

    def get_current_question(self) -> str:
        """Retorna o texto da pergunta atual"""
        if self.current_step in SECTION4_QUESTIONS:
            return SECTION4_QUESTIONS[self.current_step]
        return ""

    def store_answer(self, answer: str):
        """
        Armazena a resposta da pergunta atual.

        Lógica especial para pergunta 4.1:
        - Se resposta = "NÃO", marca seção como pulada e vai direto para "complete"
        - Caso contrário, armazena normalmente
        """
        answer_clean = answer.strip()

        # Pergunta 4.1 condicional - verifica se houve entrada em domicílio
        if self.current_step == "4.1":
            answer_upper = answer_clean.upper()
            # Aceita variações: NÃO, NAO, N, NENHUM, etc.
            if answer_upper in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
                self.section_skipped = True
                self.answers["4.1"] = "NÃO"
                self.current_step = "complete"
                self.step_index = len(SECTION4_STEPS) - 1
                return

        # Armazena resposta normalmente
        self.answers[self.current_step] = answer_clean

    def next_step(self):
        """Avança para a próxima pergunta"""
        # Se seção foi pulada, não avança
        if self.section_skipped:
            return

        # Avança para próximo step
        if self.step_index < len(SECTION4_STEPS) - 1:
            self.step_index += 1
            self.current_step = SECTION4_STEPS[self.step_index]

    def is_section_complete(self) -> bool:
        """Verifica se a seção está completa"""
        return self.current_step == "complete"

    def was_section_skipped(self) -> bool:
        """Retorna True se a seção foi pulada (não houve entrada em domicílio)"""
        return self.section_skipped

    def get_skip_reason(self) -> Optional[str]:
        """Retorna texto explicativo se seção foi pulada"""
        if self.section_skipped:
            return "Não se aplica (não houve entrada em domicílio)"
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
            question = SECTION4_QUESTIONS.get(step, "Pergunta desconhecida")
            formatted.append(f"{step} - {question}\n   Resposta: {answer}")

        return "\n\n".join(formatted)

    def get_progress(self) -> Dict[str, any]:
        """
        Retorna informações de progresso para o frontend.

        Returns:
            {
                "current_step": "4.3",
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
        total_steps = len(SECTION4_STEPS) - 1
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
        if step not in SECTION4_QUESTIONS:
            return False

        # Não permite editar se seção foi pulada
        if self.section_skipped and step != "4.1":
            return False

        # Se editando 4.1 de "NÃO" para "SIM", precisa resetar seção
        if step == "4.1" and self.section_skipped:
            answer_upper = new_answer.strip().upper()
            if answer_upper not in ["NÃO", "NAO", "N", "NENHUM", "NEGATIVO"]:
                # Resetar seção
                self.section_skipped = False
                self.current_step = "4.2"
                self.step_index = 1
                self.answers = {"4.1": new_answer.strip()}
                return True

        self.answers[step] = new_answer.strip()
        return True

    def reset(self):
        """Reseta a state machine para o início da seção"""
        self.current_step = "4.1"
        self.answers = {}
        self.step_index = 0
        self.section_skipped = False
