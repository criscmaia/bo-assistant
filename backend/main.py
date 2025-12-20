from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
from pathlib import Path
from datetime import datetime

# Imports compatíveis com local E Render
try:
    # Tenta import direto (funciona quando roda de dentro de backend/)
    from state_machine import BOStateMachine
    from state_machine_section2 import BOStateMachineSection2
    from llm_service import LLMService
    from validator import ResponseValidator
    from validator_section2 import ResponseValidatorSection2
    from logger import BOLogger, now_brasilia
except ImportError:
    # Fallback quando roda de fora da pasta backend/ (Render)
    from backend.state_machine import BOStateMachine
    from backend.state_machine_section2 import BOStateMachineSection2
    from backend.llm_service import LLMService
    from backend.validator import ResponseValidator
    from backend.validator_section2 import ResponseValidatorSection2
    from backend.logger import BOLogger, now_brasilia

# Versão do sistema
APP_VERSION = "0.4.0"

app = FastAPI(title="BO Inteligente API", version=APP_VERSION)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Armazenamento em memória (session_id -> session_data)
# Estrutura: {
#     session_id: {
#         "bo_id": int,
#         "sections": {
#             1: BOStateMachine(),
#             2: BOStateMachineSection2(),  # Inicializado quando usuário avançar
#         },
#         "current_section": 1,
#         "section1_text": str,
#         "section2_text": str
#     }
# }
sessions: Dict[str, Dict] = {}

# Models
class ChatRequest(BaseModel):
    session_id: str
    message: str
    current_section: Optional[int] = 1  # Novo campo
    llm_provider: Optional[str] = "gemini"

class ChatResponse(BaseModel):
    session_id: str
    bo_id: str
    question: Optional[str] = None
    generated_text: Optional[str] = None
    is_section_complete: bool = False
    current_step: str
    current_section: Optional[int] = 1  # Novo campo
    validation_error: Optional[str] = None
    event_id: Optional[str] = None

class NewSessionResponse(BaseModel):
    session_id: str
    bo_id: str
    first_question: str

class UpdateAnswerRequest(BaseModel):
    message: str
    llm_provider: Optional[str] = "gemini"

class FeedbackRequest(BaseModel):
    bo_id: str
    event_id: Optional[str] = None
    feedback_type: str  # positive, negative
    category: Optional[str] = None  # bug, suggestion
    user_message: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

# Inicializar serviço de LLM
llm_service = LLMService()

def get_client_ip(request: Request) -> str:
    """Obtém IP real do cliente (considera proxy)"""
    return request.headers.get("X-Forwarded-For", request.client.host)

# ============================================================================
# ENDPOINTS PRINCIPAIS
# ============================================================================

@app.get("/")
async def root():
    return {
        "message": "BO Inteligente API",
        "version": APP_VERSION,
        "endpoints": ["/new_session", "/chat", "/feedback", "/api/logs"]
    }

@app.get("/health")
async def health():
    return {"status": "ok", "database": "connected"}

@app.post("/new_session", response_model=NewSessionResponse)
async def new_session(request: Request):
    """Inicia nova sessão de BO com logging (começa sempre pela Seção 1)"""
    import uuid

    # Criar session_id (UUID)
    session_id = str(uuid.uuid4())

    # Criar bo_id no banco de dados
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")
    bo_id = BOLogger.create_session(
        ip_address=ip_address,
        user_agent=user_agent,
        app_version=APP_VERSION
    )

    # Criar estrutura de sessão com múltiplas seções
    sessions[session_id] = {
        "bo_id": bo_id,
        "sections": {
            1: BOStateMachine(),
            # Seção 2 será inicializada quando usuário clicar em "Iniciar Seção 2"
        },
        "current_section": 1,
        "section1_text": "",
        "section2_text": ""
    }

    state_machine = sessions[session_id]["sections"][1]

    # Primeira pergunta
    first_question = state_machine.get_current_question()

    # Log: primeira pergunta exibida
    BOLogger.log_event(
        bo_id=bo_id,
        event_type="question_asked",
        data={
            "step": state_machine.current_step,
            "question": first_question,
            "section": 1
        }
    )

    return NewSessionResponse(
        session_id=session_id,
        bo_id=bo_id,
        first_question=first_question
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request_body: ChatRequest, request: Request):
    """Processa resposta com logging completo (suporta múltiplas seções)"""
    session_id = request_body.session_id
    current_section = request_body.current_section or 1

    # Verificar sessão
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    session_data = sessions[session_id]
    bo_id = session_data["bo_id"]

    # Obter state machine da seção atual
    if current_section not in session_data["sections"]:
        raise HTTPException(status_code=400, detail=f"Seção {current_section} não foi inicializada")

    state_machine = session_data["sections"][current_section]
    current_step = state_machine.current_step

    # Validar resposta usando validator correto
    if current_section == 1:
        is_valid, error_message = ResponseValidator.validate(
            current_step,
            request_body.message
        )
    elif current_section == 2:
        is_valid, error_message = ResponseValidatorSection2.validate(
            current_step,
            request_body.message
        )
    else:
        raise HTTPException(status_code=400, detail=f"Seção {current_section} não suportada")
    
    # Log único com is_valid correto
    event_id = BOLogger.log_event(
        bo_id=bo_id,
        event_type="answer_submitted",
        data={
            "step": current_step,
            "answer": request_body.message,
            "is_valid": is_valid
        }
    )
    
    if not is_valid:
        # Log adicional: erro de validação
        BOLogger.log_event(
            bo_id=bo_id,
            event_type="validation_error",
            data={
                "step": current_step,
                "answer": request_body.message,
                "error_message": error_message
            }
        )
        
        return ChatResponse(
            session_id=session_id,
            bo_id=bo_id,
            question=state_machine.get_current_question(),
            is_section_complete=False,
            current_step=current_step,
            current_section=current_section,
            validation_error=error_message,
            event_id=event_id
        )

    # Armazenar resposta válida
    state_machine.store_answer(request_body.message)
    state_machine.next_step()

    # Verificar se seção está completa
    if state_machine.is_section_complete():
        # Gerar texto com método correto baseado na seção
        try:
            start_time = datetime.now()

            # Gerar texto usando método específico da seção
            if current_section == 1:
                generated_text = await llm_service.generate_section_text(
                    section_data=state_machine.get_all_answers(),
                    provider=request_body.llm_provider
                )
                session_data["section1_text"] = generated_text
            elif current_section == 2:
                generated_text = llm_service.generate_section2_text(
                    section_data=state_machine.get_all_answers(),
                    provider=request_body.llm_provider
                )
                session_data["section2_text"] = generated_text
            else:
                raise ValueError(f"Seção {current_section} não suportada")

            generation_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            # Log: texto gerado
            BOLogger.log_event(
                bo_id=bo_id,
                event_type=f"section{current_section}_completed",
                data={
                    "section": current_section,
                    "llm_provider": request_body.llm_provider,
                    "generated_text": generated_text,
                    "generation_time_ms": generation_time_ms,
                    "answers": state_machine.get_all_answers()
                }
            )

            # Atualizar status da sessão apenas se todas as seções foram concluídas
            # Por enquanto, considera concluída após Seção 1
            if current_section == 1:
                pass  # Não marca como "completed" ainda, pois tem Seção 2
            elif current_section == 2:
                BOLogger.update_session_status(bo_id, "completed")

            return ChatResponse(
                session_id=session_id,
                bo_id=bo_id,
                generated_text=generated_text,
                is_section_complete=True,
                current_step=state_machine.current_step,
                current_section=current_section,
                event_id=event_id
            )
            
        except Exception as e:
            error_msg = str(e)

            # Log: erro na geração
            BOLogger.log_event(
                bo_id=bo_id,
                event_type="generation_error",
                data={
                    "error": error_msg,
                    "llm_provider": request_body.llm_provider
                }
            )

            # Mensagens mais amigáveis baseadas no tipo de erro
            if "quota" in error_msg.lower() or "429" in error_msg:
                user_msg = "⏳ Limite diário da API Gemini atingido. Aguarde ou troque de modelo."
                status_code = 429
            else:
                user_msg = f"❌ Erro ao gerar texto: {error_msg}"
                status_code = 500

            raise HTTPException(status_code=status_code, detail=user_msg)
    
    # Próxima pergunta
    next_question = state_machine.get_current_question()

    # Log: próxima pergunta
    BOLogger.log_event(
        bo_id=bo_id,
        event_type="question_asked",
        data={
            "step": state_machine.current_step,
            "question": next_question,
            "section": current_section
        }
    )

    return ChatResponse(
        session_id=session_id,
        bo_id=bo_id,
        question=next_question,
        is_section_complete=False,
        current_section=current_section,
        current_step=state_machine.current_step,
        event_id=event_id
    )

@app.post("/start_section/{section_number}")
async def start_section(section_number: int, request_body: dict):
    """
    Inicia uma nova seção do BO.

    Body: {"session_id": "uuid"}
    """
    session_id = request_body.get("session_id")

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id é obrigatório")

    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    session_data = sessions[session_id]
    bo_id = session_data["bo_id"]

    # Validar número da seção
    if section_number not in [2]:  # Por enquanto só Seção 2
        raise HTTPException(status_code=400, detail=f"Seção {section_number} não disponível ainda")

    # Inicializar state machine da seção solicitada
    if section_number == 2:
        if 2 not in session_data["sections"]:
            session_data["sections"][2] = BOStateMachineSection2()

        session_data["current_section"] = 2
        state_machine = session_data["sections"][2]

        first_question = state_machine.get_current_question()

        # Log: seção iniciada
        BOLogger.log_event(
            bo_id=bo_id,
            event_type="section_started",
            data={
                "section": section_number,
                "first_question": first_question
            }
        )

        return {
            "session_id": session_id,
            "bo_id": bo_id,
            "section": section_number,
            "question": first_question,
            "current_step": state_machine.current_step
        }

    raise HTTPException(status_code=400, detail="Seção inválida")

@app.put("/chat/{session_id}/answer/{step}")
async def update_answer(session_id: str, step: str, update_request: UpdateAnswerRequest):
    """Atualiza resposta com logging"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    session_data = sessions[session_id]
    bo_id = session_data["bo_id"]

    # Determinar qual seção baseado no step
    if step.startswith("1."):
        state_machine = session_data["sections"][1]
    elif step.startswith("2."):
        state_machine = session_data["sections"][2]
    else:
        raise HTTPException(status_code=400, detail=f"Step inválido: {step}")

    if step not in state_machine.QUESTIONS:
        raise HTTPException(status_code=400, detail=f"Step inválido: {step}")

    # Validar nova resposta usando validator correto
    if step.startswith("1."):
        is_valid, error_message = ResponseValidator.validate(step, update_request.message)
    elif step.startswith("2."):
        is_valid, error_message = ResponseValidatorSection2.validate(step, update_request.message)
    else:
        raise HTTPException(status_code=400, detail=f"Step inválido: {step}")

    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Log: resposta editada
    old_answer = state_machine.answers.get(step, "")

    # Se vazio, buscar do último answer_submitted desse step
    if not old_answer:
        recent_events = BOLogger.get_events(bo_id)
        for event in reversed(recent_events):
            if (event.get('event_type') == 'answer_submitted' and 
                event.get('data', {}).get('step') == step):
                old_answer = event.get('data', {}).get('answer', '')
                break
            
    BOLogger.log_event(
        bo_id=bo_id,
        event_type="answer_edited",
        data={
            "step": step,
            "old_answer": old_answer,
            "new_answer": update_request.message
        }
    )
    
    # Atualizar
    state_machine.answers[step] = update_request.message.strip()
    
    # Se current_step ainda aponta para step editado,
    # significa que usuário estava travado por erro de validação.
    # Avançar state_machine para próxima pergunta!
    if state_machine.current_step == step:
        state_machine.next_step()
        print(f"[BUG FIX] Avançando state_machine de {step} para {state_machine.current_step}")
    
    return {
        "success": True,
        "message": "Resposta atualizada com sucesso",
        "step": step,
        "next_step": state_machine.current_step
    }

# ============================================================================
# ENDPOINTS DE FEEDBACK
# ============================================================================

@app.post("/feedback")
async def add_feedback(feedback: FeedbackRequest, request: Request):
    """Adiciona feedback do usuário"""
    
    # Coletar metadados automaticamente
    metadata = feedback.metadata or {}
    metadata.update({
        "ip_address": get_client_ip(request),
        "user_agent": request.headers.get("User-Agent"),
        "timestamp": now_brasilia().isoformat()
    })
    
    feedback_id = BOLogger.add_feedback(
        bo_id=feedback.bo_id,
        feedback_type=feedback.feedback_type,
        event_id=feedback.event_id,
        category=feedback.category,
        user_message=feedback.user_message,
        context=feedback.context,
        metadata=metadata
    )
    
    return {
        "success": True,
        "feedback_id": feedback_id,
        "message": "Feedback recebido com sucesso!"
    }

# ============================================================================
# ENDPOINTS DE LOGS (API Pública)
# ============================================================================

@app.get("/api/logs")
async def list_logs(
    status: Optional[str] = None,
    date: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """Lista todos os BOs"""
    result = BOLogger.list_sessions(
        status=status,
        date=date,
        limit=limit,
        offset=offset
    )
    
    # Adicionar contagem de feedbacks para cada sessão
    for session in result["sessions"]:
        feedbacks = BOLogger.get_feedbacks(session["bo_id"])
        session["feedback_count"] = len(feedbacks)
        session["positive_count"] = len([f for f in feedbacks if f["feedback_type"] == "positive"])
        session["negative_count"] = len([f for f in feedbacks if f["feedback_type"] == "negative"])
    
    return result

@app.get("/api/logs/{bo_id}")
async def get_log_detail(bo_id: str):
    """Detalhes completos de um BO"""
    session = BOLogger.get_session(bo_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="BO não encontrado")
    
    events = BOLogger.get_events(bo_id)
    feedbacks = BOLogger.get_feedbacks(bo_id)
    
    return {
        "session": session,
        "events": events,
        "feedbacks": feedbacks,
        "stats": {
            "total_events": len(events),
            "total_feedbacks": len(feedbacks),
            "positive_feedbacks": len([f for f in feedbacks if f["feedback_type"] == "positive"]),
            "negative_feedbacks": len([f for f in feedbacks if f["feedback_type"] == "negative"])
        }
    }

@app.get("/api/stats")
async def get_stats():
    """Estatísticas gerais do sistema"""
    return BOLogger.get_stats()

@app.get("/api/feedbacks")
async def list_feedbacks(
    feedback_type: Optional[str] = None,
    limit: int = 50
):
    """Lista feedbacks (útil para análise)"""
    from logger import get_db, Feedback
    
    with get_db() as db:
        query = db.query(Feedback)
        
        if feedback_type:
            query = query.filter(Feedback.feedback_type == feedback_type)
        
        feedbacks = query.order_by(Feedback.timestamp.desc()).limit(limit).all()
        
        return {
            "total": len(feedbacks),
            "feedbacks": [f.to_dict() for f in feedbacks]
        }

# ============================================================================
# ENDPOINTS LEGADOS (manter compatibilidade)
# ============================================================================

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Deleta sessão"""
    if session_id in sessions:
        bo_id, _ = sessions[session_id]
        BOLogger.update_session_status(bo_id, "abandoned")
        del sessions[session_id]
        return {"message": "Sessão deletada"}
    raise HTTPException(status_code=404, detail="Sessão não encontrada")

@app.get("/session/{session_id}/status")
async def session_status(session_id: str):
    """Status da sessão"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    
    bo_id, state_machine = sessions[session_id]
    
    return {
        "session_id": session_id,
        "bo_id": bo_id,
        "current_step": state_machine.current_step,
        "is_complete": state_machine.is_section_complete(),
        "answers_count": len(state_machine.answers)
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
