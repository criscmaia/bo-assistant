"""
BaseSectionGenerator - Classe abstrata com Template Method Pattern

Define o fluxo comum de geração de texto para todas as seções:
1. Verificar skip logic
2. Construir prompt específico da seção
3. Chamar provider (Gemini ou Groq)
4. Retornar texto gerado
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class BaseSectionGenerator(ABC):
    """Template Method para geração de texto de seções do BO"""

    def __init__(self, gemini_model=None, groq_client=None):
        """
        Inicializa o gerador com os clientes LLM

        Args:
            gemini_model: Cliente do Gemini (opcional)
            groq_client: Cliente do Groq (opcional)
        """
        self.gemini_model = gemini_model
        self.groq_client = groq_client

    # ============================================================================
    # TEMPLATE METHOD (não deve ser sobrescrito)
    # ============================================================================

    def generate(self, section_data: Dict[str, str], provider: str = "groq") -> str:
        """
        Método principal - implementa o Template Method Pattern

        Fluxo:
        1. Verificar se seção deve ser pulada (_should_skip)
        2. Construir prompt específico (_build_prompt)
        3. Chamar provider apropriado (_call_gemini ou _call_groq)

        Args:
            section_data: Dicionário com respostas da seção (ex: {"1.1": "...", "1.2": "..."})
            provider: "gemini" ou "groq" (padrão: "groq")

        Returns:
            Texto gerado pela LLM ou string vazia se skip

        Raises:
            ValueError: Se provider não for suportado
        """
        # 1. Verificar skip logic
        if self._should_skip(section_data):
            return ""

        # 2. Construir prompt
        prompt = self._build_prompt(section_data)
        if not prompt:
            return ""

        # 3. Chamar provider
        if provider == "gemini":
            return self._call_gemini(prompt)
        elif provider == "groq":
            return self._call_groq(prompt)
        else:
            raise ValueError(f"Provider '{provider}' não suportado. Use 'gemini' ou 'groq'.")

    # ============================================================================
    # MÉTODOS COMUNS (não devem ser sobrescritos)
    # ============================================================================

    def _call_gemini(self, prompt: str) -> str:
        """
        Chama Gemini API para gerar texto

        Args:
            prompt: Prompt formatado

        Returns:
            Texto gerado

        Raises:
            ValueError: Se API key não configurada
            Exception: Se ocorrer erro na geração
        """
        if not self.gemini_model:
            raise ValueError("Gemini API key não configurada. Configure GEMINI_API_KEY no ambiente.")

        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return self._handle_error(e, "Gemini")

    def _call_groq(self, prompt: str) -> str:
        """
        Chama Groq API para gerar texto

        Args:
            prompt: Prompt formatado

        Returns:
            Texto gerado

        Raises:
            ValueError: Se API key não configurada
            Exception: Se ocorrer erro na geração
        """
        if not self.groq_client:
            raise ValueError("Groq API key não configurada. Configure GROQ_API_KEY no ambiente.")

        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self._get_system_message()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return self._handle_error(e, "Groq")

    def _get_system_message(self) -> str:
        """
        Retorna mensagem de sistema padrão para a LLM

        Pode ser sobrescrito por subclasses para customizar
        """
        return "Você é um assistente especializado em redigir Boletins de Ocorrência policiais no padrão da PMMG."

    def _handle_error(self, error: Exception, provider: str) -> str:
        """
        Trata erros de chamada da API

        Args:
            error: Exception capturada
            provider: Nome do provider ("Gemini" ou "Groq")

        Raises:
            Exception: Com mensagem amigável baseada no tipo de erro
        """
        error_msg = str(error)

        # Rate limit / Quota errors
        if "429" in error_msg or "quota" in error_msg.lower() or "rate_limit" in error_msg.lower():
            raise Exception(
                f"Limite de requisições do {provider} atingido. "
                f"Tente novamente em alguns minutos ou use outro provider."
            )

        # Erro genérico
        raise Exception(f"Erro ao gerar texto com {provider}: {error_msg}")

    # ============================================================================
    # MÉTODOS ABSTRATOS (devem ser implementados pelas subclasses)
    # ============================================================================

    @abstractmethod
    def _build_prompt(self, section_data: Dict[str, str]) -> str:
        """
        Constrói o prompt específico da seção

        Este método DEVE ser implementado por cada subclasse com a lógica
        específica de formatação de prompt para aquela seção.

        Args:
            section_data: Dicionário com respostas da seção

        Returns:
            Prompt formatado ou string vazia se não puder construir
        """
        pass

    # ============================================================================
    # HOOKS (podem ser sobrescritos opcionalmente)
    # ============================================================================

    def _should_skip(self, section_data: Dict[str, str]) -> bool:
        """
        Hook para implementar lógica de skip da seção

        Override este método em subclasses que têm skip logic
        (ex: Seção 2-7 com pergunta condicional X.1)

        Args:
            section_data: Dicionário com respostas da seção

        Returns:
            True se seção deve ser pulada, False caso contrário

        Default: False (nunca skip)
        """
        return False
