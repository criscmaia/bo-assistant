# -*- coding: utf-8 -*-
"""
Validador de respostas para Seção 2: Abordagem a Veículo

Implementa regras de validação específicas para perguntas sobre veículos,
incluindo validação de placas no formato Mercosul.

Author: Cristiano Maia + Claude (Anthropic)
Date: 19/12/2025
"""
import re
from typing import Tuple


# Regras de validação para cada pergunta da Seção 2
VALIDATION_RULES_SECTION2 = {
    "2.1": {
        "valid_responses": ["SIM", "NÃO", "NAO", "S", "N", "NENHUM", "NEGATIVO"],
        "examples": ["SIM", "NÃO"],
        "error_message": "Responda com SIM ou NÃO. Havia veículo envolvido na ocorrência?"
    },
    "2.2": {
        "min_length": 30,
        "examples": [
            "Na Rua das Flores, altura do nº 123, Bairro Centro. O veículo estava estacionado em frente ao bar.",
            "Rodovia BR-381, km 450, sentido BH. O veículo transitava em alta velocidade.",
            "Esquina da Av. Brasil com Rua Rio. O veículo parou ao ver a viatura."
        ],
        "error_message": "Informe o local exato E o contexto (estacionado, em movimento, parado, etc.). Mínimo 30 caracteres."
    },
    "2.3": {
        "min_length": 15,
        "custom_check": "vehicle_plate",
        "examples": [
            "VW Gol branco, placa ABC-1D23",
            "Fiat Palio preto, placa DXY9876",
            "Honda CG 160 vermelha, placa ABC1A23"
        ],
        "error_message": "Informe marca, modelo, cor e placa do veículo. Ex: 'VW Gol branco, placa ABC-1D23'"
    },
    "2.4": {
        "min_length": 40,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Sargento Silva, de dentro da viatura estacionada a 30 metros, viu o condutor arremessar objeto pela janela",
            "O Cabo Almeida, posicionado na esquina, observou o veículo mudar bruscamente de direção ao notar a viatura"
        ],
        "error_message": "Informe: QUEM viu (graduação + nome), DE ONDE viu e O QUE exatamente observou. Mínimo 40 caracteres."
    },
    "2.5": {
        "min_length": 20,
        "allow_none_response": True,
        "none_patterns": ["não houve reação", "nao houve reacao", "sem reação", "nenhuma reação", "parou normalmente"],
        "examples": [
            "O condutor acelerou bruscamente ao ver a viatura, tentando fugir pela contramão",
            "O passageiro arremessou objeto pela janela durante a aproximação da viatura",
            "Não houve reação, o veículo prosseguiu normalmente até a ordem de parada",
            "Manobra evasiva brusca ao avistar a viatura, mudou de direção repentinamente"
        ],
        "error_message": "Descreva se houve reação do motorista ou ocupantes (manobra brusca, fuga, descarte). Aceita 'Não houve reação'."
    },
    "2.6": {
        "min_length": 20,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Sargento Silva acionou sirene e deu ordem verbal pelo megafone: 'Parado, Polícia Militar!'",
            "O Cabo Almeida fez sinal manual para encostar e acionou o giroflex",
            "Comando verbal direto pela janela da viatura pelo Soldado Faria: 'Encosta o veículo!'"
        ],
        "error_message": "Informe QUEM deu a ordem (graduação + nome) e COMO (sirene, apito, gesto, farol). Mínimo 20 caracteres."
    },
    "2.7": {
        "min_length": 15,
        "examples": [
            "Parou imediatamente no acostamento",
            "Houve perseguição por aproximadamente 500 metros pela Rua Sete até a Praça Central",
            "Tentou fugir pela contramão, percorreu 200 metros"
        ],
        "error_message": "Informe se parou imediatamente ou houve perseguição."
    },
    "2.8": {
        "min_length": 10,
        "allow_none_response": True,
        "none_patterns": ["não se aplica", "nao se aplica", "n/a", "não houve perseguição", "nao houve perseguicao"],
        "examples": [
            "Desistiu da fuga e parou no acostamento",
            "Foi cercado por outra viatura na esquina",
            "Bateu no meio-fio ao tentar fazer curva em alta velocidade",
            "Capotou ao perder controle na curva",
            "Não se aplica - parou imediatamente"
        ],
        "error_message": "Se houve perseguição, informe o motivo da parada (desistiu, cercado, bateu, capotou). Se não houve, informe 'Não se aplica'."
    },
    "2.9": {
        "min_length": 40,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Sargento Silva abordou o condutor pelo lado esquerdo e ordenou que descesse. O Cabo Almeida abordou o passageiro pelo lado direito. Havia 2 ocupantes.",
            "O Soldado Faria ordenou que os 3 ocupantes descessem com as mãos na cabeça. O Cabo posicionou-se na contenção."
        ],
        "error_message": "Descreva: QUEM abordou (graduação + nome), quantos ocupantes e como foi o posicionamento. Mínimo 40 caracteres."
    },
    "2.10": {
        "min_length": 40,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Soldado Faria vistoriou o porta-luvas, console central e sob os bancos. O Cabo Silva verificou o porta-malas.",
            "O Sargento Alves realizou busca completa: painel, bancos dianteiros e traseiros, porta-malas e compartimento do estepe"
        ],
        "error_message": "Informe QUEM (graduação + nome) fez a busca veicular e QUAIS PARTES do veículo foram vistoriadas. Mínimo 40 caracteres."
    },
    "2.11": {
        "min_length": 30,
        "required_keywords": ["sargento", "soldado", "cabo", "tenente", "capitão", "sgt", "sd", "cb", "ten", "cap"],
        "examples": [
            "O Cabo Almeida realizou busca pessoal no condutor. O Soldado Faria revistou o passageiro.",
            "A Soldado Pires realizou busca pessoal na ocupante feminina"
        ],
        "error_message": "Informe QUEM (graduação + nome) realizou a busca pessoal em cada ocupante. Mínimo 30 caracteres."
    },
    "2.12": {
        "min_length": 30,
        "allow_none_response": True,
        "none_patterns": ["nada encontrado", "nada localizado", "sem material", "não foi encontrado", "negativo"],
        "examples": [
            "No porta-luvas, o Soldado Faria localizou 20 porções de cocaína. No bolso do condutor João Silva, foram encontradas R$ 350,00 em notas diversas.",
            "Sob o banco traseiro, encontradas 15 pedras de crack. Com o passageiro, 2 celulares.",
            "Nada de ilícito foi localizado no veículo ou com os ocupantes"
        ],
        "error_message": "Informe O QUE foi encontrado, COM QUEM ou EM QUAL PARTE do veículo/corpo. Se nada, informe 'Nada localizado'."
    },
    "2.13": {
        "min_length": 3,
        "allow_none_response": True,
        "none_patterns": ["não", "nao", "negativo", "nenhuma", "sem irregularidade", "regular"],
        "examples": [
            "NÃO",
            "Veículo com queixa de furto, consta no REDS 2024-001234",
            "Placa clonada - chassi divergente do registrado no documento",
            "Veículo com registro de roubo em Contagem/MG, REDS 2023-005678"
        ],
        "error_message": "Informe irregularidades (furto, roubo, clonagem) com REDS se houver. Se não, responda 'NÃO'."
    }
}


class ResponseValidatorSection2:
    """
    Validador de respostas para Seção 2 (Abordagem a Veículo).

    Aplica regras específicas para cada pergunta (13 perguntas), incluindo:
    - Validação de resposta condicional (2.1)
    - Validação de placa Mercosul (2.3)
    - Validação de presença de graduação militar (2.4, 2.6, 2.9, 2.10, 2.11)
    - Validações de comprimento mínimo
    - Validações com allow_none_response (2.5, 2.8, 2.12, 2.13)
    """

    @staticmethod
    def validate(step: str, answer: str) -> Tuple[bool, str]:
        """
        Valida uma resposta para uma pergunta específica da Seção 2.

        Args:
            step: ID da pergunta (ex: "2.1", "2.2", etc.)
            answer: Resposta fornecida pelo usuário

        Returns:
            Tupla (is_valid, error_message)
            - is_valid: True se válida, False caso contrário
            - error_message: Mensagem de erro (vazia se válida)
        """
        # Verifica se step existe
        if step not in VALIDATION_RULES_SECTION2:
            return False, f"Pergunta {step} não encontrada"

        # Remove espaços extras
        answer = answer.strip()

        # Verifica se resposta está vazia
        if not answer:
            return False, "Por favor, forneça uma resposta."

        rules = VALIDATION_RULES_SECTION2[step]

        # Validação especial para pergunta 2.1 (condicional)
        if step == "2.1":
            return ResponseValidatorSection2._validate_yes_no(answer, rules)

        # Validação de comprimento mínimo
        if "min_length" in rules:
            if len(answer) < rules["min_length"]:
                return False, rules["error_message"]

        # Validação custom de placa para pergunta 2.3
        if "custom_check" in rules and rules["custom_check"] == "vehicle_plate":
            plate_valid, plate_error = ResponseValidatorSection2._validate_vehicle_plate(answer)
            if not plate_valid:
                return False, f"{rules['error_message']}\n{plate_error}"

        # Validação de palavras-chave obrigatórias (ex: graduação militar)
        if "required_keywords" in rules:
            has_keyword = ResponseValidatorSection2._check_required_keywords(
                answer, rules["required_keywords"]
            )
            if not has_keyword:
                return False, rules["error_message"]

        # Validação de allow_none_response para perguntas 2.10 e 2.11
        if "allow_none_response" in rules and rules["allow_none_response"]:
            if ResponseValidatorSection2._check_none_response(answer, rules.get("none_patterns", [])):
                return True, ""

        # Se passou todas as validações
        return True, ""

    @staticmethod
    def _validate_yes_no(answer: str, rules: dict) -> Tuple[bool, str]:
        """Valida resposta SIM/NÃO para pergunta 2.0"""
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
    def _validate_vehicle_plate(answer: str) -> Tuple[bool, str]:
        """
        Valida presença de placa no formato Mercosul.

        Formatos aceitos:
        - ABC1D23
        - ABC-1D23
        - ABC 1D23

        Args:
            answer: Resposta completa (ex: "VW Gol branco, placa ABC-1D23")

        Returns:
            Tupla (is_valid, error_message)
        """
        # Padrão Mercosul: 3 letras + 1 número + 1 letra + 2 números
        # Com ou sem hífen/espaço
        plate_pattern = r'[A-Z]{3}[-\s]?[0-9][A-Z][0-9]{2}'

        # Busca padrão na resposta (case-insensitive)
        if re.search(plate_pattern, answer.upper()):
            return True, ""

        # Se não encontrou, retorna erro específico
        return False, "⚠️ Placa não encontrada ou em formato inválido. Use formato Mercosul: ABC-1D23 ou ABC1D23"

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
    def _check_none_response(answer: str, none_patterns: list) -> bool:
        """
        Verifica se a resposta indica ausência de material/irregularidade.

        Args:
            answer: Resposta do usuário
            none_patterns: Lista de padrões que indicam "nada encontrado"

        Returns:
            True se a resposta indica negativo, False caso contrário
        """
        answer_lower = answer.lower()

        for pattern in none_patterns:
            if pattern.lower() in answer_lower:
                return True

        return False

    @staticmethod
    def get_validation_examples(step: str) -> list:
        """
        Retorna exemplos de respostas válidas para uma pergunta.

        Args:
            step: ID da pergunta (ex: "2.3")

        Returns:
            Lista de exemplos ou lista vazia se step não existe
        """
        if step not in VALIDATION_RULES_SECTION2:
            return []

        return VALIDATION_RULES_SECTION2[step].get("examples", [])

    @staticmethod
    def get_error_message(step: str) -> str:
        """Retorna mensagem de erro padrão para uma pergunta"""
        if step not in VALIDATION_RULES_SECTION2:
            return "Pergunta não encontrada"

        return VALIDATION_RULES_SECTION2[step].get("error_message", "Resposta inválida")
