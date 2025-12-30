from typing import Dict, List, Optional

class BOStateMachine:
    """
    Gerencia o fluxo de perguntas da Seção 1 do BO.
    Cada pergunta é feita uma vez, aguarda resposta, depois avança.
    """
    
    # Perguntas da Seção 1 - Contexto da Ocorrência
    QUESTIONS = {
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
    STEPS = ["1.1", "1.2", "1.3", "1.4", "1.5", "1.5.1", "1.5.2", "1.6", "1.7", "1.8", "1.9", "1.9.1", "1.9.2", "complete"]
    
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
        Implementa lógica condicional para sub-perguntas.
        """
        if self.step_index < len(self.STEPS) - 1:
            self.step_index += 1
            next_step_candidate = self.STEPS[self.step_index]

            # Lógica condicional para 1.5.x
            if next_step_candidate in ["1.5.1", "1.5.2"]:
                answer_1_5 = self.answers.get("1.5", "").strip().upper()
                if answer_1_5 in ["NÃO", "NAO", "N", "NEGATIVO"]:
                    # Pular 1.5.1 e 1.5.2, ir direto para 1.6
                    while self.step_index < len(self.STEPS) - 1 and self.STEPS[self.step_index] in ["1.5.1", "1.5.2"]:
                        self.step_index += 1
                    next_step_candidate = self.STEPS[self.step_index]

            # Lógica condicional para 1.9.x
            if next_step_candidate in ["1.9.1", "1.9.2"]:
                answer_1_9 = self.answers.get("1.9", "").strip().upper()
                if answer_1_9 in ["NÃO", "NAO", "N", "NEGATIVO"]:
                    # Pular 1.9.1 e 1.9.2, ir direto para complete
                    while self.step_index < len(self.STEPS) - 1 and self.STEPS[self.step_index] in ["1.9.1", "1.9.2"]:
                        self.step_index += 1
                    next_step_candidate = self.STEPS[self.step_index]

            self.current_step = next_step_candidate
    
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
