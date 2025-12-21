# -*- coding: utf-8 -*-
"""
Fixtures pytest compartilhadas para todos os testes
"""
import pytest
import requests
from typing import Dict

@pytest.fixture
def api_base_url():
    """Base URL do backend para testes"""
    return "http://localhost:8000"

@pytest.fixture
def new_session(api_base_url) -> Dict:
    """Cria nova sessão de teste e retorna dados da sessão"""
    response = requests.post(f"{api_base_url}/new_session")
    response.raise_for_status()
    return response.json()

@pytest.fixture
def section1_answers() -> Dict:
    """Respostas válidas para Seção 1 (todas as 6 perguntas)"""
    return {
        "1.1": "19/12/2025, 14h30min",
        "1.2": "Sargento João Silva, Cabo Pedro Almeida e Soldado Carlos Faria, viatura 2234",
        "1.3": "Patrulhamento preventivo de combate ao tráfico de drogas",
        "1.4": "Ordem de serviço nº 145/2025 determinava patrulhamento no Bairro Santa Rita. COPOM informou denúncia anônima de veículo transportando drogas na região.",
        "1.5": "Rua das Acácias, altura do número 789, Bairro Santa Rita, Contagem/MG",
        "1.6": "Sim, local consta em 12 registros anteriores de tráfico de drogas. Há denúncias recorrentes de comercialização de entorpecentes. Área sob influência da facção Comando Vermelho segundo relatórios de inteligência."
    }

@pytest.fixture
def section2_answers() -> Dict:
    """Respostas válidas para Seção 2 (todas as 8 perguntas)"""
    return {
        "2.1": "SIM",
        "2.2": "VW Gol branco, placa ABC-1D23, ano 2018",
        "2.3": "Na Rua das Acácias, esquina com Avenida Brasil, próximo ao Bar do João, Bairro Santa Rita",
        "2.4": "O Sargento Silva visualizou o veículo transitando em alta velocidade pela Rua das Acácias. O condutor mudou bruscamente o sentido de direção ao notar a viatura e acelerou tentando fugir.",
        "2.5": "Foi acionada a sirene da viatura e o Sargento Silva utilizou o megafone ordenando 'Parado, Polícia Militar! Encoste o veículo imediatamente!'",
        "2.6": "O condutor acelerou tentando fugir pela Avenida Brasil, percorreu aproximadamente 300 metros em alta velocidade, desobedeceu dois semáforos vermelhos e só parou após cercar o veículo em um beco sem saída.",
        "2.7": "O Cabo Almeida procedeu a abordagem ao motorista determinando que saísse do veículo com as mãos na cabeça. O Soldado Faria realizou busca no interior do veículo, revistando porta-luvas, painel, banco traseiro e porta-malas. No banco do motorista, embaixo do assento, foram localizados 28 invólucros plásticos contendo substância análoga à cocaína.",
        "2.8": "Consultado o sistema REDS, consta registro de furto do veículo em Betim/MG, REDS nº 45678/2024 de 10/11/2024. Placa original BCD-5E67."
    }

@pytest.fixture
def section3_answers() -> Dict:
    """Respostas válidas para Seção 3 (todas as 8 perguntas)"""
    return {
        "3.1": "SIM",
        "3.2": "Esquina da Rua das Flores com Avenida Brasil, atrás do muro da casa 145, a aproximadamente 30 metros do bar do João",
        "3.3": "O Sargento Silva tinha visão desobstruída da porta do bar. O Cabo Almeida observava a lateral do estabelecimento pela janela da viatura.",
        "3.4": "Denúncia anônima recebida via COPOM informando comercialização de drogas no local há pelo menos 3 meses",
        "3.5": "15 minutos de vigilância contínua atrás do muro da casa 145",
        "3.6": "Foi observado um homem de camiseta vermelha retirando pequenos invólucros de uma mochila preta e entregando a dois indivíduos que chegaram de motocicleta. Após receberem os invólucros, os indivíduos entregaram dinheiro ao homem de vermelho.",
        "3.7": "Sim, foi abordado um usuário que estava saindo do local. Ele portava 2 porções de substância análoga à cocaína e relatou ter comprado do 'cara de vermelho' por R$ 50,00.",
        "3.8": "Sim, ao perceber a movimentação policial, o homem de vermelho correu para o beco ao lado do bar, tentando fugir em direção à Rua Sete."
    }

@pytest.fixture
def section4_answers() -> Dict:
    """Respostas válidas para Seção 4 (todas as 5 perguntas)"""
    return {
        "4.1": "SIM",
        "4.2": "Vimos o suspeito arremessando uma sacola branca para dentro da casa enquanto corria em direção ao imóvel nº 120 da Rua das Acácias",
        "4.3": "O Sargento Silva viu o suspeito entrando na casa com a sacola e manteve contato visual ininterrupto com o alvo",
        "4.4": "Perseguição contínua: a equipe iniciou acompanhamento no final da Rua das Acácias e manteve contato visual ininterrupto até o interior da residência",
        "4.5": "O Sargento Silva entrou primeiro pela porta principal que estava aberta. O Cabo Almeida ficou na contenção do portão monitorando saídas. O Soldado Faria entrou em seguida pela cozinha e localizou a sacola branca embaixo da pia contendo invólucros de cocaína."
    }

@pytest.fixture
def send_answer(api_base_url):
    """Helper para enviar resposta ao endpoint /chat"""
    def _send(session_id: str, message: str, current_section: int, llm_provider: str = "gemini"):
        response = requests.post(
            f"{api_base_url}/chat",
            json={
                "session_id": session_id,
                "message": message,
                "current_section": current_section,
                "llm_provider": llm_provider
            }
        )
        response.raise_for_status()
        return response.json()
    return _send
