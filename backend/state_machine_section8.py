# -*- coding: utf-8 -*-
"""
State Machine para Seção 8: Condução e Pós-Ocorrência
Refatorado para usar Template Method Pattern (v0.13.1)

Baseado no material de Claudio Moreira (Lei 11.343/06 - Lei de Drogas, Lei 13.869/19)

Author: Cristiano Maia + Claude (Anthropic)
Date: 02/01/2026
"""
from typing import Dict, List, Optional
from backend.base_state_machine import BaseStateMachine


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


class BOStateMachineSection8(BaseStateMachine):
    """
    State Machine para Seção 8: Condução e Pós-Ocorrência.

    Características:
    - Seção 8 é a ÚLTIMA seção do BO (8/8)
    - NÃO tem pergunta condicional: todas as 11 perguntas devem ser respondidas
    - Quando completa, marca boCompleted = true (única seção que faz isso)
    - Fundamento jurídico: Lei 11.343/06 + Lei 13.869/19 + CPP Arts. 282-284
    """

    # =========================================================================
    # IMPLEMENTAÇÃO DOS MÉTODOS ABSTRATOS
    # =========================================================================

    def _get_initial_step(self) -> str:
        """Retorna step inicial da Seção 8"""
        return "8.1"

    def _get_steps(self) -> List[str]:
        """Retorna lista de steps da Seção 8"""
        return SECTION8_STEPS

    def _get_questions(self) -> Dict[str, str]:
        """Retorna dicionário de perguntas da Seção 8"""
        return SECTION8_QUESTIONS

    # =========================================================================
    # MÉTODOS ESPECÍFICOS DA SEÇÃO 8
    # =========================================================================

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
        self.__init__()
