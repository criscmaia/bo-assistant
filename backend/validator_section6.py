# -*- coding: utf-8 -*-
"""
Validador de respostas para Seção 6: Reação e Uso da Força

Implementa regras de validação específicas para perguntas sobre reação e uso da força,
incluindo:
- Validação de resposta condicional (6.1)
- Validação de frases proibidas (forbidden_phrases) em 6.2
- Validação de graduação militar obrigatória
- Validação condicional de atendimento hospitalar em 6.5

Fundamento jurídico: Súmula Vinculante 11 (STF) + Decreto 8.858/2016

Author: Cristiano Maia + Claude (Anthropic)
Date: 22/12/2025
"""
from typing import Tuple


# Regras de validação para cada pergunta da Seção 6
VALIDATION_RULES_SECTION6 = {
    "6.1": {
        "min_length": 5,
        "allow_none_response": True,
        "none_patterns": ["não", "não houve", "negativo", "sem ameaça"],
        "examples": [
            "Sim, o suspeito empunhou revólver contra a guarnição",
            "Ameaçou testemunha com faca",
            "Não houve"
        ],
        "error_message": "Descreva se houve ameaça ou uso de arma, ou informe 'Não houve'."
    },
    "6.2": {
        "valid_responses": ["SIM", "NÃO", "NAO", "S", "N", "NENHUM", "NEGATIVO"],
        "examples": ["SIM", "NÃO"],
        "error_message": "Responda com SIM ou NÃO: houve resistência durante a abordagem?"
    },
    "6.3": {
        "min_length": 30,
        "forbidden_phrases": [
            "resistiu ativamente",
            "resistência ativa",
            "uso moderado da força",
            "necessário uso da força",
            "em atitude suspeita",
            "estava exaltado",
            "ficou agressivo",
            "resistiu",  # sem complemento
            "houve resistência"  # sem detalhar
        ],
        "examples": [
            "O autor empurrou o Cabo Rezende com força no peito e tentou correr em direção ao beco lateral",
            "O suspeito desferiu um soco em direção ao rosto do Sargento Silva, sendo desviado pela defesa do policial",
            "O indivíduo recusou-se a colocar as mãos na cabeça e tentou sacar objeto da cintura durante a abordagem"
        ],
        "error_message": "Descreva o que o autor FEZ (soco, empurrão, fuga, etc). NÃO use frases genéricas como 'resistiu ativamente' ou 'uso moderado da força'. Mínimo 30 caracteres."
    },
    "6.4": {
        "min_length": 40,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Cabo Marcelo aplicou chave de braço no suspeito, imobilizando-o no chão sem lesões",
            "O Sargento Dias acertou cotovelada defensiva no rosto do agressor, que caiu e foi imobilizado pelo Soldado Nara",
            "O Soldado Pires desviou do soco e empurrou o autor contra o muro, contendo a agressão enquanto o Cabo Almeida auxiliava"
        ],
        "error_message": "Informe: GRADUAÇÃO + nome do policial, qual técnica usou (chave, cotovelada, empurrão, taser, etc) e o resultado. Mínimo 40 caracteres."
    },
    "6.5": {
        "min_length": 20,
        "required_keywords_any": ["risco", "fuga", "agressiv", "resistência", "perigo", "tentou", "ameaça"],
        "examples": [
            "Diante do risco de nova tentativa de fuga, o autor foi algemado para segurança da guarnição",
            "Em razão da agressividade demonstrada ao tentar agredir os policiais, aplicou-se algemas",
            "Considerando que o autor já havia tentado fugir duas vezes, foi algemado por medida de segurança"
        ],
        "error_message": "Justifique as algemas com FATO OBJETIVO (risco de fuga, agressividade, tentativa de agressão). Mínimo 20 caracteres."
    },
    "6.6": {
        "min_length": 30,
        "conditional_hospital": True,  # Se mencionar lesão, exigir hospital/UPA
        "examples": [
            "Não houve ferimentos. A guarnição verificou a integridade física do autor, que não apresentou lesões corpóreas.",
            "O autor apresentou escoriação no joelho esquerdo, decorrente da queda durante a imobilização. Foi atendido no Hospital João XXIII (ficha nº 2025-12345) e liberado sem restrições.",
            "Após a contenção, o nariz do autor estava sangrando. Encaminhado ao UPA Norte (ficha nº 2025-67890), constatou-se fratura nasal. Permaneceu em observação por 2 horas."
        ],
        "error_message": "Informe se houve ou não ferimentos. Se SIM: descreva a lesão, onde foi atendido (hospital/UPA) e o número da ficha. Mínimo 30 caracteres."
    }
}


class ResponseValidatorSection6:
    """
    Validador de respostas para Seção 6 (Reação e Uso da Força).

    Aplica regras específicas para cada pergunta, incluindo:
    - Validação de ameaça/arma com "Não houve" aceito (6.1)
    - Validação de resposta condicional (6.2)
    - Validação de frases proibidas (6.3)
    - Validação de presença de graduação militar (6.4)
    - Validação de justificativa objetiva para algemas (6.5)
    - Validação condicional de atendimento hospitalar (6.6)

    Fundamento jurídico: Súmula Vinculante 11 (STF) - "Só é lícito o uso de algemas
    em caso de resistência, fundado receio de fuga ou perigo à integridade física própria
    ou alheia, devendo ser justificada por escrito, sob pena de responsabilidade."
    """

    @staticmethod
    def validate(step: str, answer: str) -> Tuple[bool, str]:
        """
        Valida uma resposta para uma pergunta específica da Seção 6.

        Args:
            step: ID da pergunta (ex: "6.1", "6.2", etc.)
            answer: Resposta fornecida pelo usuário

        Returns:
            Tupla (is_valid, error_message)
            - is_valid: True se válida, False caso contrário
            - error_message: Mensagem de erro (vazia se válida)
        """
        # Verifica se step existe
        if step not in VALIDATION_RULES_SECTION6:
            return False, f"Pergunta {step} não encontrada"

        # Remove espaços extras
        answer = answer.strip()

        # Verifica se resposta está vazia
        if not answer:
            return False, "Por favor, forneça uma resposta."

        rules = VALIDATION_RULES_SECTION6[step]

        # Validação especial para pergunta 6.1 (arma/ameaça - aceita "Não houve")
        if step == "6.1":
            answer_lower = answer.lower().strip()
            if rules.get("allow_none_response"):
                for pattern in rules.get("none_patterns", []):
                    if pattern in answer_lower:
                        return True, ""
            # Se não for "Não houve", valida comprimento mínimo
            if len(answer) < rules.get("min_length", 5):
                return False, rules["error_message"]
            return True, ""

        # Validação especial para pergunta 6.2 (condicional - SIM/NÃO)
        if step == "6.2":
            return ResponseValidatorSection6._validate_yes_no(answer, rules)

        # Validação de frases proibidas (para 6.3)
        if step == "6.3" and "forbidden_phrases" in rules:
            has_forbidden, matched = ResponseValidatorSection6._check_forbidden_phrases(
                answer, rules["forbidden_phrases"]
            )
            if has_forbidden:
                return False, f"NÃO use a expressão '{matched}'. {rules['error_message']}"

        # Validação de comprimento mínimo
        if "min_length" in rules:
            if len(answer) < rules["min_length"]:
                return False, rules["error_message"]

        # Validação de palavras-chave obrigatórias (ex: graduação militar)
        if "required_keywords" in rules:
            has_keyword = ResponseValidatorSection6._check_required_keywords(
                answer, rules["required_keywords"]
            )
            if not has_keyword:
                return False, rules["error_message"]

        # Validação de palavras-chave "qualquer uma de" (para 6.5)
        if "required_keywords_any" in rules:
            has_any_keyword = ResponseValidatorSection6._check_required_keywords_any(
                answer, rules["required_keywords_any"]
            )
            if not has_any_keyword:
                return False, rules["error_message"]

        # Validação condicional de hospital para 6.6
        if step == "6.6" and rules.get("conditional_hospital"):
            # Se resposta começa com "Não houve", não exige hospital
            answer_lower = answer.lower().strip()
            if not answer_lower.startswith("não houve"):
                has_injury = ResponseValidatorSection6._check_has_injury(answer)
                if has_injury:
                    has_hospital = ResponseValidatorSection6._check_hospital_info(answer)
                    if not has_hospital:
                        return False, rules["error_message"]

        # Se passou todas as validações
        return True, ""

    @staticmethod
    def _validate_yes_no(answer: str, rules: dict) -> Tuple[bool, str]:
        """Valida resposta SIM/NÃO para pergunta 6.1"""
        answer_upper = answer.strip().upper()

        # Remove acentos para comparação
        answer_normalized = answer_upper.replace("Ã", "A")

        valid_responses_normalized = [
            resp.replace("Ã", "A") for resp in rules["valid_responses"]
        ]

        if answer_normalized in valid_responses_normalized:
            return True, ""

        return False, rules["error_message"]

    @staticmethod
    def _check_forbidden_phrases(answer: str, forbidden_phrases: list) -> Tuple[bool, str]:
        """
        Verifica se a resposta contém frases proibidas (generalizações).

        Args:
            answer: Resposta do usuário
            forbidden_phrases: Lista de frases proibidas

        Returns:
            Tupla (has_forbidden, matched_phrase)
            - has_forbidden: True se contém frase proibida
            - matched_phrase: A frase que foi encontrada (para mensagem de erro)
        """
        answer_lower = answer.lower()

        for phrase in forbidden_phrases:
            if phrase.lower() in answer_lower:
                return True, phrase

        return False, ""

    @staticmethod
    def _check_required_keywords(answer: str, keywords: list) -> bool:
        """
        Verifica se a resposta contém pelo menos uma das palavras-chave.

        Args:
            answer: Resposta do usuário
            keywords: Lista de palavras-chave (case-insensitive)

        Returns:
            True se contém ao menos uma keyword, False caso contrário
        """
        answer_lower = answer.lower()

        for keyword in keywords:
            if keyword.lower() in answer_lower:
                return True

        return False

    @staticmethod
    def _check_required_keywords_any(answer: str, keywords: list) -> bool:
        """
        Verifica se a resposta contém pelo menos uma das palavras-chave.
        (Alias para _check_required_keywords)

        Args:
            answer: Resposta do usuário
            keywords: Lista de palavras-chave (case-insensitive)

        Returns:
            True se contém ao menos uma keyword, False caso contrário
        """
        return ResponseValidatorSection6._check_required_keywords(answer, keywords)

    @staticmethod
    def _check_has_injury(answer: str) -> bool:
        """
        Verifica se a resposta menciona ferimentos/lesões.

        Args:
            answer: Resposta do usuário

        Returns:
            True se menciona ferimentos, False caso contrário
        """
        answer_lower = answer.lower()

        injury_keywords = [
            "ferimento",
            "lesão",
            "sangramento",
            "escoriação",
            "hematoma",
            "fratura",
            "contusão",
            "ferido",
            "machucado",
            "machucou",
            "bateu",
            "cortou",
            "machucadinhas"
        ]

        for keyword in injury_keywords:
            if keyword in answer_lower:
                return True

        # Se resposta começa com "Não houve", considera sem ferimentos
        if answer_lower.strip().startswith("não houve"):
            return False

        return False

    @staticmethod
    def _check_hospital_info(answer: str) -> bool:
        """
        Verifica se a resposta contém informação de atendimento hospitalar/UPA.

        Args:
            answer: Resposta do usuário

        Returns:
            True se menciona hospital/UPA com ficha, False caso contrário
        """
        answer_lower = answer.lower()

        hospital_keywords = ["hospital", "upa", "pronto socorro", "ps"]
        ficha_keywords = ["ficha", "nº", "numero", "número"]

        has_hospital = any(keyword in answer_lower for keyword in hospital_keywords)
        has_ficha = any(keyword in answer_lower for keyword in ficha_keywords)

        return has_hospital and has_ficha

    @staticmethod
    def get_validation_examples(step: str) -> list:
        """
        Retorna exemplos de respostas válidas para uma pergunta.

        Args:
            step: ID da pergunta (ex: "6.3")

        Returns:
            Lista de exemplos ou lista vazia se step não existe
        """
        if step not in VALIDATION_RULES_SECTION6:
            return []

        return VALIDATION_RULES_SECTION6[step].get("examples", [])

    @staticmethod
    def get_error_message(step: str) -> str:
        """Retorna mensagem de erro padrão para uma pergunta"""
        if step not in VALIDATION_RULES_SECTION6:
            return "Pergunta não encontrada"

        return VALIDATION_RULES_SECTION6[step].get("error_message", "Resposta inválida")
