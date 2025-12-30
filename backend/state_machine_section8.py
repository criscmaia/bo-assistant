# -*- coding: utf-8 -*-
"""
State Machine para Seção 8: Condução e Pós-Ocorrência
Baseado no material de Claudio Moreira (Lei 11.343/06 - Lei de Drogas, Lei 13.869/19)

Author: Cristiano Maia + Claude (Anthropic)
Date: 23/12/2025
"""
from typing import Dict, Optional


# Perguntas da Seção 8 (fonte: SEÇÃO_8___CONDUÇÃO_E_PÓS-OCORRÊNCIA.md)
SECTION8_QUESTIONS = {
    "8.1": "Quem deu voz de prisão e por qual crime? (graduação + nome + artigo)",
    "8.2": "Onde e como o preso foi transportado até a delegacia?",
    "8.3": "O preso declarou algo? (transcrição literal ou \"permaneceu em silêncio\")",
    "8.4": "Qual era a função do preso no tráfico? (vapor, gerente, olheiro, etc.)",
    "8.5": "O preso possui passagens anteriores? (informar REDS se houver)",
    "8.6": "Há sinais de dedicação ao crime? O que mostra isso?",
    "8.7": "O preso tem papel relevante na facção? Atuação ocasional ou contínua?",
    "8.8": "Houve tentativa de destruir ou ocultar provas, ou intimidar alguém?",
    "8.9": "Havia menor de idade envolvido na ocorrência? Se sim, idade e participação?",
    "8.10": "Quem informou as garantias constitucionais ao preso? (graduação + nome)",
    "8.11": "Qual o destino dos presos e dos materiais apreendidos? (delegacia, CEFLAN, etc.)"
}

SECTION8_STEPS = ["8.1", "8.2", "8.3", "8.4", "8.5", "8.6", "8.7", "8.8", "8.9", "8.10", "8.11", "complete"]


class BOStateMachineSection8:
    """
    State Machine para gerenciar o fluxo de perguntas da Seção 8 (Condução e Pós-Ocorrência).

    Características:
    - Seção 8 é a ÚLTIMA seção do BO (8/8)
    - NÃO tem pergunta condicional: todas as 11 perguntas devem ser respondidas
    - Quando completa, marca boCompleted = true (única seção que faz isso)
    - Fundamento jurídico: Lei 11.343/06 + Lei 13.869/19 + CPP Arts. 282-284
    """

    def __init__(self):
        self.current_step = "8.1"
        self.answers: Dict[str, str] = {}
        self.step_index = 0

    def get_current_question(self) -> str:
        """Retorna o texto da pergunta atual"""
        if self.current_step in SECTION8_QUESTIONS:
            return SECTION8_QUESTIONS[self.current_step]
        return ""

    def store_answer(self, answer: str):
        """
        Armazena a resposta da pergunta atual.

        Args:
            answer: Resposta fornecida pelo usuário
        """
        answer_clean = answer.strip()
        self.answers[self.current_step] = answer_clean

    def next_step(self):
        """Avança para a próxima pergunta"""
        if self.step_index < len(SECTION8_STEPS) - 1:
            self.step_index += 1
            self.current_step = SECTION8_STEPS[self.step_index]

    def is_section_complete(self) -> bool:
        """Verifica se a seção está completa"""
        return self.current_step == "complete"

    def get_all_answers(self) -> Dict[str, str]:
        """Retorna todas as respostas coletadas"""
        return self.answers.copy()

    def get_formatted_answers(self) -> str:
        """Retorna respostas formatadas para debug/log"""
        if not self.answers:
            return "Nenhuma resposta coletada"

        formatted = []
        for step, answer in self.answers.items():
            question = SECTION8_QUESTIONS.get(step, "Pergunta desconhecida")
            formatted.append(f"{step} - {question}\n   Resposta: {answer}")

        return "\n\n".join(formatted)

    def get_progress(self) -> Dict[str, any]:
        """
        Retorna informações de progresso para o frontend.

        Returns:
            {
                "current_step": "8.3",
                "total_steps": 11,
                "completed_steps": 3,
                "progress_percentage": 27.3,
                "section_skipped": False
            }
        """
        total_steps = len(SECTION8_STEPS) - 1  # Excluindo "complete"
        completed_steps = len(self.answers)

        # Calcula porcentagem
        progress_percentage = (completed_steps / total_steps) * 100 if total_steps > 0 else 0

        return {
            "current_step": self.current_step,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "progress_percentage": round(progress_percentage, 1),
            "section_skipped": False  # Seção 8 nunca é pulada
        }

    def get_answer(self, step: str) -> Optional[str]:
        """Retorna a resposta de uma pergunta específica"""
        return self.answers.get(step)

    def update_answer(self, step: str, new_answer: str) -> bool:
        """
        Atualiza a resposta de uma pergunta anterior.

        Args:
            step: ID da pergunta (ex: "8.1", "8.2", etc.)
            new_answer: Nova resposta

        Returns:
            True se atualização foi bem-sucedida, False caso contrário
        """
        if step not in SECTION8_QUESTIONS:
            return False

        self.answers[step] = new_answer.strip()
        return True

    def reset(self):
        """Reseta a state machine para o início da seção"""
        self.current_step = "8.1"
        self.answers = {}
        self.step_index = 0
