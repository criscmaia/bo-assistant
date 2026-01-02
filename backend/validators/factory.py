# -*- coding: utf-8 -*-
"""
Validation Factory - Configuração centralizada de validators
BO Inteligente v0.13.1

Factory Pattern para compor validators baseado na pergunta.
Elimina duplicação de código entre 8 arquivos de validators.

Author: Cristiano Maia + Claude (Anthropic)
Date: 02/01/2026
"""
from typing import Dict
from backend.validators.base import ValidationStrategy, CompositeValidator, ConditionalValidator
from backend.validators.strategies import (
    RequiredFieldValidator,
    MinLengthValidator,
    YesNoValidator,
    KeywordsValidator,
    DateTimeValidator,
    VehiclePlateValidator,
    InjuryDescriptionValidator,
    HospitalDestinationValidator,
    MilitaryRankValidator
)


class ValidationFactory:
    """
    Factory para criar validators compostos baseado na pergunta.

    Centraliza configuração de validação de todas as seções,
    eliminando duplicação de código entre validator_section*.py

    Uso:
        factory = ValidationFactory()
        validator = factory.get_validator("1.1")
        result = validator.validate(answer, context)
    """

    # ========================================================================
    # CONFIGURAÇÃO DE VALIDATORS POR PERGUNTA
    # ========================================================================

    def __init__(self):
        """Inicializa factory com configuração de validators"""
        self._validators: Dict[str, ValidationStrategy] = self._build_validators()

    def _build_validators(self) -> Dict[str, ValidationStrategy]:
        """
        Constrói mapa de validators para cada pergunta.

        Returns:
            Dict[question_id, ValidationStrategy]
        """
        validators = {}

        # ====================================================================
        # SEÇÃO 1: CONTEXTO DA OCORRÊNCIA
        # ====================================================================

        # 1.1: Data e hora (obrigatório + formato)
        validators["1.1"] = CompositeValidator(
            RequiredFieldValidator(),
            DateTimeValidator(require_time=True)
        )

        # 1.2: Composição da guarnição (obrigatório + mínimo 15 chars)
        validators["1.2"] = CompositeValidator(
            RequiredFieldValidator(),
            MinLengthValidator(15, "Informe a composição completa da guarnição")
        )

        # 1.3: Forma de acionamento (obrigatório + keywords)
        validators["1.3"] = CompositeValidator(
            RequiredFieldValidator(),
            KeywordsValidator(
                ["190", "DDU", "mandado", "patrulhamento", "denúncia", "COPOM"],
                error_message="Informe como a guarnição foi acionada"
            )
        )

        # 1.4: Informações recebidas (obrigatório + mínimo 20 chars)
        validators["1.4"] = CompositeValidator(
            RequiredFieldValidator(),
            MinLengthValidator(20, "Descreva as informações recebidas no acionamento")
        )

        # 1.5: Houve deslocamento? (sim/não)
        validators["1.5"] = CompositeValidator(
            RequiredFieldValidator(),
            YesNoValidator()
        )

        # 1.5.1: Local de partida (condicional - só se 1.5=SIM)
        validators["1.5.1"] = ConditionalValidator(
            condition=lambda ctx: ctx.get("1.5", "").upper() in ["SIM", "S"],
            validator=CompositeValidator(
                RequiredFieldValidator(),
                MinLengthValidator(10)
            )
        )

        # 1.5.2: Alteração no percurso (condicional)
        validators["1.5.2"] = ConditionalValidator(
            condition=lambda ctx: ctx.get("1.5", "").upper() in ["SIM", "S"],
            validator=RequiredFieldValidator()
        )

        # 1.6: Local exato da ocorrência (obrigatório + mínimo 15 chars)
        validators["1.6"] = CompositeValidator(
            RequiredFieldValidator(),
            MinLengthValidator(15, "Informe endereço completo com ponto de referência")
        )

        # 1.7: Ponto de tráfico? (obrigatório + mínimo 10 chars)
        validators["1.7"] = CompositeValidator(
            RequiredFieldValidator(),
            MinLengthValidator(10)
        )

        # 1.8: Facção? (obrigatório + mínimo 10 chars)
        validators["1.8"] = CompositeValidator(
            RequiredFieldValidator(),
            MinLengthValidator(10)
        )

        # 1.9: Próximo a local de interesse? (sim/não)
        validators["1.9"] = CompositeValidator(
            RequiredFieldValidator(),
            YesNoValidator()
        )

        # 1.9.1: Nome do estabelecimento (condicional)
        validators["1.9.1"] = ConditionalValidator(
            condition=lambda ctx: ctx.get("1.9", "").upper() in ["SIM", "S"],
            validator=CompositeValidator(
                RequiredFieldValidator(),
                MinLengthValidator(5)
            )
        )

        # 1.9.2: Distância (condicional)
        validators["1.9.2"] = ConditionalValidator(
            condition=lambda ctx: ctx.get("1.9", "").upper() in ["SIM", "S"],
            validator=RequiredFieldValidator()
        )

        # ====================================================================
        # SEÇÃO 2: ABORDAGEM A VEÍCULO
        # ====================================================================

        # 2.1: Havia veículo? (sim/não)
        validators["2.1"] = CompositeValidator(
            RequiredFieldValidator(),
            YesNoValidator()
        )

        # 2.2-2.13: Condicionais - só validam se 2.1=SIM
        for q_id in ["2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9", "2.10", "2.11", "2.12", "2.13"]:
            validators[q_id] = ConditionalValidator(
                condition=lambda ctx: ctx.get("2.1", "").upper() in ["SIM", "S"],
                validator=CompositeValidator(
                    RequiredFieldValidator(),
                    MinLengthValidator(10)
                )
            )

        # 2.3: Placa do veículo (adicionar validação específica)
        validators["2.3"] = ConditionalValidator(
            condition=lambda ctx: ctx.get("2.1", "").upper() in ["SIM", "S"],
            validator=CompositeValidator(
                RequiredFieldValidator(),
                VehiclePlateValidator()
            )
        )

        # ====================================================================
        # SEÇÃO 3: CAMPANA (VIGILÂNCIA VELADA)
        # ====================================================================

        # 3.1: Realizou campana? (sim/não)
        validators["3.1"] = CompositeValidator(
            RequiredFieldValidator(),
            YesNoValidator()
        )

        # 3.2: Local da campana (condicional)
        validators["3.2"] = ConditionalValidator(
            condition=lambda ctx: ctx.get("3.1", "").upper() in ["SIM", "S"],
            validator=CompositeValidator(
                RequiredFieldValidator(),
                MinLengthValidator(30, "Descreva o local exato da campana, ponto de observação e distância aproximada")
            )
        )

        # 3.3: Quem tinha visão + graduação (condicional)
        validators["3.3"] = ConditionalValidator(
            condition=lambda ctx: ctx.get("3.1", "").upper() in ["SIM", "S"],
            validator=CompositeValidator(
                RequiredFieldValidator(),
                MinLengthValidator(30),
                MilitaryRankValidator()
            )
        )

        # 3.4: Motivo da campana (condicional)
        validators["3.4"] = ConditionalValidator(
            condition=lambda ctx: ctx.get("3.1", "").upper() in ["SIM", "S"],
            validator=CompositeValidator(
                RequiredFieldValidator(),
                MinLengthValidator(20, "Descreva o que motivou a campana")
            )
        )

        # 3.5: Duração da campana (condicional)
        validators["3.5"] = ConditionalValidator(
            condition=lambda ctx: ctx.get("3.1", "").upper() in ["SIM", "S"],
            validator=CompositeValidator(
                RequiredFieldValidator(),
                MinLengthValidator(10, "Informe a duração da campana")
            )
        )

        # 3.6: O que foi visto (condicional)
        validators["3.6"] = ConditionalValidator(
            condition=lambda ctx: ctx.get("3.1", "").upper() in ["SIM", "S"],
            validator=CompositeValidator(
                RequiredFieldValidator(),
                MinLengthValidator(40, "Descreva o que foi visto durante a campana: entregas, usuários, esconderijos")
            )
        )

        # 3.7: Abordagem de usuário? (condicional)
        validators["3.7"] = ConditionalValidator(
            condition=lambda ctx: ctx.get("3.1", "").upper() in ["SIM", "S"],
            validator=RequiredFieldValidator()
        )

        # 3.8: Houve fuga? (condicional)
        validators["3.8"] = ConditionalValidator(
            condition=lambda ctx: ctx.get("3.1", "").upper() in ["SIM", "S"],
            validator=RequiredFieldValidator()
        )

        # ====================================================================
        # SEÇÃO 4: ENTRADA EM DOMICÍLIO
        # ====================================================================

        # 4.1: Houve entrada em domicílio? (sim/não)
        validators["4.1"] = CompositeValidator(
            RequiredFieldValidator(),
            YesNoValidator()
        )

        # 4.2: Justa causa (condicional)
        validators["4.2"] = ConditionalValidator(
            condition=lambda ctx: ctx.get("4.1", "").upper() in ["SIM", "S"],
            validator=CompositeValidator(
                RequiredFieldValidator(),
                MinLengthValidator(40, "Descreva o que foi visto/ouvido/sentido ANTES da entrada (justa causa)")
            )
        )

        # 4.3: Quem viu/ouviu + graduação (condicional)
        validators["4.3"] = ConditionalValidator(
            condition=lambda ctx: ctx.get("4.1", "").upper() in ["SIM", "S"],
            validator=CompositeValidator(
                RequiredFieldValidator(),
                MinLengthValidator(30),
                MilitaryRankValidator()
            )
        )

        # 4.4: Como ocorreu o ingresso (condicional)
        validators["4.4"] = ConditionalValidator(
            condition=lambda ctx: ctx.get("4.1", "").upper() in ["SIM", "S"],
            validator=CompositeValidator(
                RequiredFieldValidator(),
                MinLengthValidator(30, "Descreva como ocorreu o ingresso")
            )
        )

        # 4.5: Ações dentro do imóvel (condicional)
        validators["4.5"] = ConditionalValidator(
            condition=lambda ctx: ctx.get("4.1", "").upper() in ["SIM", "S"],
            validator=CompositeValidator(
                RequiredFieldValidator(),
                MinLengthValidator(50, "Descreva ação por ação: quem entrou, por onde, quem ficou na contenção")
            )
        )

        # ====================================================================
        # SEÇÃO 5: FUNDADA SUSPEITA
        # ====================================================================

        # 5.1: O que a equipe viu ao chegar
        validators["5.1"] = CompositeValidator(
            RequiredFieldValidator(),
            MinLengthValidator(40, "Descreva o que a equipe viu ao chegar no local com detalhes concretos")
        )

        # 5.2: Quem viu + graduação
        validators["5.2"] = CompositeValidator(
            RequiredFieldValidator(),
            MinLengthValidator(30),
            MilitaryRankValidator()
        )

        # 5.3: Descrição individual dos abordados
        validators["5.3"] = CompositeValidator(
            RequiredFieldValidator(),
            MinLengthValidator(50, "Descreva INDIVIDUALMENTE cada abordado: roupa, porte, gestos, identificação completa + vulgo")
        )

        # ====================================================================
        # SEÇÃO 6: DISPARO DE ARMA DE FOGO
        # ====================================================================

        # 6.1: Houve disparo? (sim/não)
        validators["6.1"] = CompositeValidator(
            RequiredFieldValidator(),
            YesNoValidator()
        )

        # 6.2-6.10: Condicionais
        for q_id in ["6.2", "6.3", "6.4", "6.5", "6.6", "6.7", "6.8", "6.9", "6.10"]:
            validators[q_id] = ConditionalValidator(
                condition=lambda ctx: ctx.get("6.1", "").upper() in ["SIM", "S"],
                validator=CompositeValidator(
                    RequiredFieldValidator(),
                    MinLengthValidator(10)
                )
            )

        # ====================================================================
        # SEÇÃO 7: TESTEMUNHAS E FILMAGENS
        # ====================================================================

        # 7.1: Houve testemunhas/filmagens? (sim/não)
        validators["7.1"] = CompositeValidator(
            RequiredFieldValidator(),
            YesNoValidator()
        )

        # 7.2-7.6: Condicionais
        for q_id in ["7.2", "7.3", "7.4", "7.5", "7.6"]:
            validators[q_id] = ConditionalValidator(
                condition=lambda ctx: ctx.get("7.1", "").upper() in ["SIM", "S"],
                validator=CompositeValidator(
                    RequiredFieldValidator(),
                    MinLengthValidator(10)
                )
            )

        # ====================================================================
        # SEÇÃO 8: CONDUÇÃO E PÓS-OCORRÊNCIA
        # ====================================================================

        # Seção 8 não tem skip - todas perguntas obrigatórias
        for q_id in ["8.1", "8.2", "8.3", "8.4", "8.5", "8.6", "8.7", "8.8", "8.9", "8.10", "8.11"]:
            validators[q_id] = CompositeValidator(
                RequiredFieldValidator(),
                MinLengthValidator(10)
            )

        return validators

    # ========================================================================
    # API PÚBLICA
    # ========================================================================

    def get_validator(self, question_id: str) -> ValidationStrategy:
        """
        Retorna validator para uma pergunta específica.

        Args:
            question_id: ID da pergunta (ex: "1.1", "2.3", etc.)

        Returns:
            ValidationStrategy configurado para a pergunta.
            Se pergunta não tiver validator, retorna RequiredFieldValidator padrão.
        """
        return self._validators.get(
            question_id,
            RequiredFieldValidator()  # Fallback padrão
        )

    def validate_answer(self, question_id: str, answer: str, context: Dict = None) -> Dict:
        """
        Valida resposta usando validator apropriado.

        Método de conveniência que retorna dict (compatibilidade com código legado).

        Args:
            question_id: ID da pergunta
            answer: Resposta do usuário
            context: Contexto com respostas anteriores (default: {})

        Returns:
            Dict com {"valid": bool, "error": str | None}
        """
        context = context or {}
        validator = self.get_validator(question_id)
        result = validator.validate(answer, context)
        return result.to_dict()


# ============================================================================
# SINGLETON GLOBAL (para compatibilidade com código existente)
# ============================================================================

_factory_instance = None


def get_validator(question_id: str) -> ValidationStrategy:
    """
    Função global para obter validator (compatibilidade com código existente).

    Args:
        question_id: ID da pergunta

    Returns:
        ValidationStrategy para a pergunta
    """
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = ValidationFactory()
    return _factory_instance.get_validator(question_id)


def validate_answer(question_id: str, answer: str, context: Dict = None) -> Dict:
    """
    Função global para validar resposta (compatibilidade com código existente).

    Args:
        question_id: ID da pergunta
        answer: Resposta do usuário
        context: Contexto com respostas anteriores

    Returns:
        Dict com {"valid": bool, "error": str | None}
    """
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = ValidationFactory()
    return _factory_instance.validate_answer(question_id, answer, context)
