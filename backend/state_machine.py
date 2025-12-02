from typing import Dict, List, Optional

class BOStateMachine:
    """
    Gerencia o fluxo de perguntas da Seção 1 do BO.
    Cada pergunta é feita uma vez, aguarda resposta, depois avança.
    """
    
    # Perguntas da Seção 1 - Contexto da Ocorrência
    QUESTIONS = {
        "1.1": "Dia, data e hora do acionamento.",
        "1.2": "Composição da guarnição e prefixo.",
        "1.3": "Natureza do empenho.",
        "1.4": "O que constava na ordem de serviço, informações do COPOM, DDU.",
        "1.5": "Local exato da ocorrência (logradouro, número, bairro).",
        "1.6": "O local é ponto de tráfico? Quais evidências anteriores? Há facção?"
    }
    
    # Ordem das perguntas
    STEPS = ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "complete"]
    
    def __init__(self):
        self.current_step = "1.1"  # Começar na primeira pergunta
        self.answers: Dict[str, str] = {}  # Armazenar respostas
        self.step_index = 0
    
    def get_current_question(self) -> str:
        """
        Retorna a pergunta atual.
        """
        if self.current_step == "complete":
            return "Seção 1 completa!"
        
        return self.QUESTIONS.get(self.current_step, "Erro: pergunta não encontrada")
    
    def store_answer(self, answer: str) -> None:
        """
        Armazena a resposta do usuário para a pergunta atual.
        """
        if self.current_step != "complete":
            self.answers[self.current_step] = answer.strip()
    
    def next_step(self) -> None:
        """
        Avança para a próxima pergunta.
        """
        if self.step_index < len(self.STEPS) - 1:
            self.step_index += 1
            self.current_step = self.STEPS[self.step_index]
    
    def is_section_complete(self) -> bool:
        """
        Verifica se todas as perguntas foram respondidas.
        """
        return self.current_step == "complete"
    
    def get_all_answers(self) -> Dict[str, str]:
        """
        Retorna todas as respostas coletadas.
        """
        return self.answers
    
    def get_formatted_answers(self) -> str:
        """
        Retorna respostas formatadas para enviar ao LLM.
        Útil para debug também.
        """
        formatted = []
        for step, question in self.QUESTIONS.items():
            answer = self.answers.get(step, "Não respondido")
            formatted.append(f"{step}. {question}\nResposta: {answer}\n")
        
        return "\n".join(formatted)
    
    def reset(self) -> None:
        """
        Reinicia a sessão (útil para testes).
        """
        self.current_step = "1.1"
        self.answers = {}
        self.step_index = 0
    
    def get_progress(self) -> Dict[str, any]:
        """
        Retorna progresso atual (útil para UI mostrar barra de progresso).
        """
        total_questions = len(self.QUESTIONS)
        answered = len(self.answers)
        
        return {
            "total": total_questions,
            "answered": answered,
            "percentage": int((answered / total_questions) * 100),
            "current_question": self.current_step
        }
