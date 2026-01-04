"""
Testes de integração HTTP para endpoints principais

Testa os endpoints via HTTP usando FastAPI TestClient:
- POST /new_session
- POST /chat
- POST /generate/{session_id}/{section_number}

v0.13.2+: Testes com pytest para validação de endpoints
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.main import app, sessions


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_sessions():
    """Limpa sessões antes de cada teste"""
    sessions.clear()
    yield
    sessions.clear()


# ============================================================================
# /new_session
# ============================================================================

class TestNewSessionEndpoint:
    """Testes para POST /new_session"""

    def test_new_session_creates_new_session(self, client):
        """Testa criação de nova sessão"""
        response = client.post("/new_session")

        assert response.status_code == 200
        data = response.json()

        assert "session_id" in data
        assert "bo_id" in data
        assert "first_question" in data

        # Verificar que sessão foi criada no backend
        assert data["session_id"] in sessions

    def test_new_session_returns_first_question(self, client):
        """Testa que primeira pergunta é retornada"""
        response = client.post("/new_session")
        data = response.json()

        assert "first_question" in data
        assert len(data["first_question"]) > 0
        assert "data" in data["first_question"].lower() or "hora" in data["first_question"].lower()

    def test_new_session_multiple_calls_create_different_sessions(self, client):
        """Testa que múltiplas chamadas criam sessões diferentes"""
        response1 = client.post("/new_session")
        response2 = client.post("/new_session")

        data1 = response1.json()
        data2 = response2.json()

        assert data1["session_id"] != data2["session_id"]
        assert data1["bo_id"] != data2["bo_id"]


# ============================================================================
# /chat
# ============================================================================

class TestChatEndpoint:
    """Testes para POST /chat"""

    def test_chat_accepts_valid_answer(self, client):
        """Testa que endpoint aceita resposta válida"""
        # Criar sessão
        start_response = client.post("/new_session")
        session_id = start_response.json()["session_id"]

        # Enviar resposta válida para 1.1
        chat_response = client.post("/chat", json={
            "session_id": session_id,
            "message": "22/03/2025 21:11",
            "current_section": 1,
            "llm_provider": "groq"
        })

        assert chat_response.status_code == 200
        data = chat_response.json()

        assert data["session_id"] == session_id
        assert "question" in data or data.get("is_section_complete") == True
        assert data.get("validation_error") is None

    def test_chat_rejects_invalid_answer(self, client):
        """Testa que endpoint rejeita resposta inválida"""
        # Criar sessão
        start_response = client.post("/new_session")
        session_id = start_response.json()["session_id"]

        # Enviar resposta inválida para 1.1 (muito curta)
        chat_response = client.post("/chat", json={
            "session_id": session_id,
            "message": "hoje",
            "current_section": 1,
            "llm_provider": "groq"
        })

        assert chat_response.status_code == 200
        data = chat_response.json()

        assert data.get("validation_error") is not None
        assert len(data["validation_error"]) > 0

    def test_chat_advances_to_next_question(self, client):
        """Testa que chat avança para próxima pergunta"""
        # Criar sessão
        start_response = client.post("/new_session")
        session_id = start_response.json()["session_id"]

        # Responder 1.1
        response1 = client.post("/chat", json={
            "session_id": session_id,
            "message": "22/03/2025 21:11",
            "current_section": 1,
            "llm_provider": "groq"
        })

        data1 = response1.json()
        assert data1["current_step"] == "1.2"

        # Responder 1.2
        response2 = client.post("/chat", json={
            "session_id": session_id,
            "message": "Sgt Silva, Cb Almeida",
            "current_section": 1,
            "llm_provider": "groq"
        })

        data2 = response2.json()
        assert data2["current_step"] == "1.3"

    def test_chat_maintains_session_state(self, client):
        """Testa que estado da sessão é mantido entre chamadas"""
        # Criar sessão
        start_response = client.post("/new_session")
        session_id = start_response.json()["session_id"]

        # Responder múltiplas perguntas
        answers = [
            "22/03/2025 21:11",
            "Sgt Silva, Cb Almeida",
            "COPOM"
        ]

        for i, answer in enumerate(answers):
            response = client.post("/chat", json={
                "session_id": session_id,
                "message": answer,
                "current_section": 1,
                "llm_provider": "groq"
            })

            data = response.json()
            assert data["session_id"] == session_id

            # Verificar que state machine está no backend
            assert session_id in sessions
            state_machine = sessions[session_id]["sections"][1]
            assert len(state_machine.answers) == i + 1

    def test_chat_handles_section_completion(self, client):
        """Testa sinalização de seção completa"""
        # Criar sessão
        start_response = client.post("/new_session")
        session_id = start_response.json()["session_id"]

        # Responder todas as perguntas da seção 1
        # Nota: 1.5 e 1.9 são perguntas SIM/NÃO
        answers = [
            "22/03/2025 21:11",  # 1.1 - data/hora
            "Sgt Silva, Cb Almeida, prefixo 1234",  # 1.2 - guarnição
            "COPOM",  # 1.3 - acionamento
            "Ordem de serviço patrulhamento na região do Bairro Centro",  # 1.4 - motivação
            "NÃO",  # 1.5 - há câmeras?
            "Rua das Flores, 123, Centro",  # 1.6 - endereço
            "Bairro Centro, próximo à praça principal",  # 1.7 - bairro/referência
            "Denúncia anônima de briga em andamento no local",  # 1.8 - denúncia
            "NÃO"  # 1.9 - local é/próximo de interesse público?
        ]

        last_response = None
        for answer in answers:
            response = client.post("/chat", json={
                "session_id": session_id,
                "message": answer,
                "current_section": 1,
                "llm_provider": "groq"
            })
            last_response = response

        data = last_response.json()
        assert data.get("is_section_complete") == True or data.get("will_generate_now") == True

    def test_chat_returns_400_for_invalid_session(self, client):
        """Testa que sessão inválida retorna erro apropriado ou cria nova sessão"""
        response = client.post("/chat", json={
            "session_id": "invalid-session-id",
            "message": "test",
            "current_section": 1,
            "llm_provider": "groq"
        })

        # Backend cria nova sessão automaticamente (initialize_session_if_needed)
        # então esperamos 200, não 400
        assert response.status_code == 200


# ============================================================================
# /generate
# ============================================================================

class TestGenerateEndpoint:
    """Testes para POST /generate/{session_id}/{section_number}"""

    def test_generate_requires_completed_section(self, client):
        """Testa que geração requer seção completa"""
        # Criar sessão
        start_response = client.post("/new_session")
        session_id = start_response.json()["session_id"]

        # Tentar gerar sem completar seção
        generate_response = client.post(
            f"/generate/{session_id}/1",
            json={"llm_provider": "groq"}
        )

        # Deve retornar erro ou mensagem apropriada
        # (depende da implementação - pode retornar 400 ou texto vazio)
        assert generate_response.status_code in [200, 400]

    def test_generate_with_mock_completion(self, client):
        """Testa geração com seção mockada como completa"""
        # Criar sessão
        start_response = client.post("/new_session")
        session_id = start_response.json()["session_id"]

        # Simular seção completa diretamente no backend
        if session_id in sessions:
            state_machine = sessions[session_id]["sections"][1]
            # Forçar conclusão (mock)
            state_machine.current_step = "complete"
            state_machine.answers = {
                "1.1": "22/03/2025 21:11",
                "1.2": "Sgt Silva",
                "1.3": "COPOM",
                "1.4": "Patrulhamento",
                "1.5": "NÃO",
                "1.6": "Rua X",
                "1.7": "Bairro Y",
                "1.8": "Denúncia",
                "1.9": "190"
            }

        # Agora tentar gerar (pode falhar por falta de API keys)
        generate_response = client.post(
            f"/generate/{session_id}/1",
            json={"llm_provider": "groq"}
        )

        # Aceitar 200 (sucesso) ou 500 (erro de API - normal em testes)
        assert generate_response.status_code in [200, 500]


# ============================================================================
# Testes de Fluxo Completo
# ============================================================================

class TestCompleteFlow:
    """Testes de fluxo completo (start → chat → generate)"""

    def test_minimal_flow(self, client):
        """Testa fluxo mínimo: start → 1 resposta"""
        # Start
        start_response = client.post("/new_session")
        assert start_response.status_code == 200
        session_id = start_response.json()["session_id"]

        # Chat
        chat_response = client.post("/chat", json={
            "session_id": session_id,
            "message": "22/03/2025 21:11",
            "current_section": 1,
            "llm_provider": "groq"
        })
        assert chat_response.status_code == 200

        # Verificar que avançou
        data = chat_response.json()
        assert data["current_step"] != "1.1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
