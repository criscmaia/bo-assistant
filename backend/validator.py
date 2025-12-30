# -*- coding: utf-8 -*-
from typing import Tuple, Optional

class ResponseValidator:
    """
    Valida respostas do usuário antes de avançar para próxima pergunta.
    Evita respostas vagas/incompletas que fariam o LLM inventar informações.
    """
    
    # Regras de validação por pergunta
    VALIDATION_RULES = {
        "1.1": {
            "min_length": 10,
            "custom_check": "datetime",  # Validação customizada
            "examples": ["22/03/2025, às 19h03", "15 de março de 2024, 14h30"],
            "error_message": "Por favor, informe dia, data E hora completos. Ex: '22/03/2025, às 19h03'"
        },
        "1.2": {
            "min_length": 15,
            "required_keywords": ["prefixo", "viatura"],
            "examples": ["Sgt João Silva e Cb Pedro Santos, prefixo 1234", "Sargento Silva, Cabo Almeida e Soldado Faria, viatura 2234"],
            "error_message": "Informe graduação + nome completo de TODOS os policiais + prefixo/viatura. Ex: 'Sgt João Silva e Cb Pedro Santos, prefixo 1234'"
        },
        "1.3": {
            "min_length": 10,
            "examples": ["190", "DDU", "Mandado de prisão", "Patrulhamento preventivo para combater tráfico", "Operação NOME"],
            "error_message": "Informe como foi acionado: 190, DDU, mandado, patrulhamento, etc."
        },
        "1.4": {
            "min_length": 20,
            "examples": ["Denúncia anônima via COPOM reportando venda de drogas na esquina", "Ordem de serviço 123/2024 para verificar tráfico no bairro Centro"],
            "error_message": "Descreva o que foi informado no acionamento: quem acionou e o que foi reportado."
        },
        "1.5": {
            "min_length": 3,
            "custom_check": "yes_no",
            "examples": ["SIM", "NÃO"],
            "error_message": "Responda apenas SIM ou NÃO."
        },
        "1.5.1": {
            "min_length": 10,
            "examples": ["Batalhão PM, bairro Centro", "Base da PM na Rua XV, próximo ao shopping"],
            "error_message": "Informe o local de onde a guarnição partiu."
        },
        "1.5.2": {
            "min_length": 3,
            "examples": ["Sim, radar na Av. Principal registrou passagem", "Não houve alterações", "Sinal fechado na Rua X atrasou em 2 minutos"],
            "error_message": "Informe se houve alguma alteração no percurso. Se não, responda 'Não houve alterações'."
        },
        "1.6": {
            "min_length": 20,
            "required_keywords": ["rua", "número", "bairro"],
            "examples": ["Rua das Acácias, número 456, bairro Floresta, próximo ao Bar do Zé"],
            "error_message": "Informe logradouro + número + bairro + referência. Ex: 'Rua das Acácias, número 456, bairro Floresta, próximo ao Bar do Zé'"
        },
        "1.7": {
            "min_length": 10,
            "examples": ["Sim, 3 ocorrências em 2024 conforme BO 123/24, 456/24 e 789/24", "Não há histórico de ocorrências anteriores", "Local conhecido por denúncias de tráfico"],
            "error_message": "Descreva o histórico do local: ocorrências anteriores, denúncias, BOs. Se não houver, informe 'Não há histórico'."
        },
        "1.8": {
            "min_length": 10,
            "examples": ["Sim, facção XYZ domina a região conforme relatório de inteligência", "Não há indícios de facção criminosa", "Área controlada pelo PCC segundo moradores"],
            "error_message": "Informe se há facção e descreva evidências. Se não houver, informe 'Não há indícios de facção'."
        },
        "1.9": {
            "min_length": 3,
            "custom_check": "yes_no",
            "examples": ["SIM", "NÃO"],
            "error_message": "Responda apenas SIM ou NÃO."
        },
        "1.9.1": {
            "min_length": 5,
            "examples": ["Escola Estadual João XXIII", "Hospital Municipal", "Terminal Rodoviário", "Presídio Central"],
            "error_message": "Informe o nome do estabelecimento."
        },
        "1.9.2": {
            "min_length": 5,
            "examples": ["Dois quarteirões", "Aproximadamente 300 metros", "50 metros"],
            "error_message": "Informe a distância aproximada. Ex: 'dois quarteirões', '300 metros'."
        }
    }
    
    @staticmethod
    def validate(step: str, answer: str) -> Tuple[bool, Optional[str]]:
        """
        Valida resposta do usuário.
        
        Returns:
            (is_valid, error_message)
            - is_valid: True se resposta é válida
            - error_message: Mensagem de erro se inválida, None se válida
        """
        answer = answer.strip()
        
        # Verificar se resposta está vazia
        if not answer or len(answer) < 3:
            return False, "Por favor, forneça uma resposta. Se não se aplica, escreva 'NÃO'."

        # Buscar regras específicas da pergunta
        rules = ResponseValidator.VALIDATION_RULES.get(step)

        # Validação especial para perguntas SIM/NÃO (1.5 e 1.9)
        if rules and rules.get("custom_check") == "yes_no":
            if answer.upper() in ["SIM", "NÃO", "NAO", "S", "N"]:
                return True, None
            else:
                return False, rules.get("error_message", "Responda apenas SIM ou NÃO.")

        # Verificar se é só "NÃO" (válido apenas para algumas perguntas)
        if answer.upper() == "NÃO":
            # Perguntas que aceitam NÃO como resposta válida
            if step in ["1.7", "1.8"]:  # Histórico e facção podem ser NÃO
                return True, None
            else:
                return False, "Esta pergunta é obrigatória. 'NÃO' não é uma resposta válida aqui."

        # Verificar se é só "SIM" (inválido para perguntas que exigem detalhes)
        if answer.upper() == "SIM":
            # Apenas 1.5 e 1.9 aceitam SIM sozinho (já validado acima)
            return False, "Esta pergunta exige detalhes. 'SIM' sozinho não é suficiente."

        if not rules:
            return True, None  # Sem regras específicas, aceitar
        
        # Validar tamanho mínimo
        if len(answer) < rules.get("min_length", 0):
            return False, rules.get("error_message", "Resposta muito curta. Forneça mais detalhes.")
        
        # Validação customizada para data/hora (1.1)
        if rules.get("custom_check") == "datetime":
            import re
            from datetime import datetime as dt, timedelta
            
            # Verificar se tem formato de data (números e barras OU palavras como "março")
            has_date = "/" in answer or any(mes in answer.lower() for mes in [
                "janeiro", "fevereiro", "março", "marco", "abril", "maio", "junho",
                "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
            ])
            
            if not has_date:
                return False, "Faltou a data. " + rules.get("error_message")
            
            # Verificar se tem horário e se é válido
            time_match = re.search(r'(\d{1,2})[h:](\d{0,2})', answer)
            
            if not time_match:
                return False, "Faltou o horário. " + rules.get("error_message")
            
            # Validar hora e minuto
            hour = int(time_match.group(1))
            minute_str = time_match.group(2)
            minute = int(minute_str) if minute_str else 0
            
            if hour > 23:
                return False, f"Hora inválida ({hour}h). Use formato 24h (0-23). Ex: '21h03' ou '09h30'"
            
            if minute > 59:
                return False, f"Minuto inválido ({minute}min). Use 0-59. Ex: '21h03' ou '09h59'"
            
            # Validar data se estiver no formato DD/MM
            date_match = re.search(r'(\d{1,2})/(\d{1,2})(?:/(\d{4}))?', answer)
            if date_match:
                day = int(date_match.group(1))
                month = int(date_match.group(2))
                year = int(date_match.group(3)) if date_match.group(3) else dt.now().year
                
                # Validar mês
                if month < 1 or month > 12:
                    return False, f"Mês inválido ({month}). Use 1-12. Ex: '22/03/2025'"
                
                # Validar dia usando datetime (valida dias por mês automaticamente)
                try:
                    input_date = dt(year, month, day, hour, minute)
                except ValueError:
                    return False, f"Data inválida ({day}/{month:02d}/{year}). Verifique o dia para este mês."
                
                # Validar se data/hora não é futura (com margem de 5 minutos)
                now = dt.now() + timedelta(minutes=5)
                if input_date > now:
                    return False, "Data/hora futura não permitida. A ocorrência deve ter acontecido no passado."
            
            # Verificar se tem ano (aviso, mas não bloqueia)
            has_year = bool(re.search(r'20\d{2}', answer))
            if not has_year:
                # Não bloquear, mas poderia adicionar warning no futuro
                pass
            
            return True, None
        
        # Validar palavras-chave obrigatórias
        required = rules.get("required_keywords", [])
        answer_lower = answer.lower()

        # Para 1.6 (local exato), ser mais flexível com sinônimos
        if step == "1.6":
            # Aceitar variações: rua/avenida/travessa, numero/nº/n, bairro/região
            has_street = any(word in answer_lower for word in ["rua", "avenida", "av", "travessa", "alameda"])
            has_number = any(word in answer_lower for word in ["número", "numero", "nº", "n°", "n."])
            has_neighborhood = any(word in answer_lower for word in ["bairro", "região", "setor"])

            if not (has_street and has_number and has_neighborhood):
                return False, rules.get("error_message")
        else:
            # Para outras perguntas, verificar palavras-chave normalmente
            # Se step é 1.2, aceitar QUALQUER uma das keywords (prefixo OU viatura)
            if step == "1.2":
                has_any_keyword = any(kw in answer_lower for kw in required)
                if not has_any_keyword:
                    return False, rules.get("error_message")
            else:
                # Para outras perguntas, exigir TODAS as keywords
                missing_keywords = [kw for kw in required if kw not in answer_lower]
                if missing_keywords:
                    return False, rules.get("error_message")
        
        # Validar palavras proibidas (respostas muito vagas)
        forbidden = rules.get("forbidden_words", [])
        if forbidden:
            # Se a resposta contém APENAS palavras proibidas (muito vaga)
            words_in_answer = set(answer_lower.split())
            if words_in_answer.issubset(set(forbidden + ["de", "e", "a", "o"])):
                return False, rules.get("error_message")
        
        return True, None
    
    @staticmethod
    def get_examples(step: str) -> list:
        """
        Retorna exemplos de respostas válidas para uma pergunta.
        """
        rules = ResponseValidator.VALIDATION_RULES.get(step, {})
        return rules.get("examples", [])
