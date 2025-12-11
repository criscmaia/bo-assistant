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
    from state_machine import BOStateMachine
    from llm_service import LLMService
    from validator import ResponseValidator
    from logger import BOLogger
except ImportError:
    from backend.state_machine import BOStateMachine
    from backend.llm_service import LLMService
    from backend.validator import ResponseValidator
    from backend.logger import BOLogger

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

# Armazenamento em memória (session_id -> (bo_id, state_machine))
sessions: Dict[str, tuple] = {}

# Models
class ChatRequest(BaseModel):
    session_id: str
    message: str
    llm_provider: Optional[str] = "gemini"

class ChatResponse(BaseModel):
    session_id: str
    bo_id: str
    question: Optional[str] = None
    generated_text: Optional[str] = None
    is_section_complete: bool = False
    current_step: str
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
    """Inicia nova sessão de BO com logging"""
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
    
    # Criar state machine
    state_machine = BOStateMachine()
    sessions[session_id] = (bo_id, state_machine)
    
    # Primeira pergunta
    first_question = state_machine.get_current_question()
    
    # Log: primeira pergunta exibida
    BOLogger.log_event(
        bo_id=bo_id,
        event_type="question_asked",
        data={
            "step": state_machine.current_step,
            "question": first_question
        }
    )
    
    return NewSessionResponse(
        session_id=session_id,
        bo_id=bo_id,
        first_question=first_question
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request_body: ChatRequest, request: Request):
    """Processa resposta com logging completo"""
    session_id = request_body.session_id
    
    # Verificar sessão
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    
    bo_id, state_machine = sessions[session_id]
    current_step = state_machine.current_step
    
    # Validar resposta
    is_valid, error_message = ResponseValidator.validate(
        current_step,
        request_body.message
    )
    
    # ✅ BUG FIX #5: Log ÚNICO com is_valid correto
    event_id = BOLogger.log_event(
        bo_id=bo_id,
        event_type="answer_submitted",
        data={
            "step": current_step,
            "answer": request_body.message,
            "is_valid": is_valid  # ✅ TRUE ou FALSE
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
            validation_error=error_message,
            event_id=event_id
        )
    
    # Armazenar resposta válida
    state_machine.store_answer(request_body.message)
    state_machine.next_step()
    
    # Verificar se seção está completa
    if state_machine.is_section_complete():
        # Gerar texto
        try:
            start_time = datetime.now()
            
            generated_text = await llm_service.generate_section_text(
                section_data=state_machine.get_all_answers(),
                provider=request_body.llm_provider
            )
            
            generation_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Log: texto gerado
            BOLogger.log_event(
                bo_id=bo_id,
                event_type="text_generated",
                data={
                    "llm_provider": request_body.llm_provider,
                    "generated_text": generated_text,
                    "generation_time_ms": generation_time_ms,
                    "answers": state_machine.get_all_answers()
                }
            )
            
            # Atualizar status da sessão
            BOLogger.update_session_status(bo_id, "completed")
            
            return ChatResponse(
                session_id=session_id,
                bo_id=bo_id,
                generated_text=generated_text,
                is_section_complete=True,
                current_step=state_machine.current_step,
                event_id=event_id
            )
            
        except Exception as e:
            # Log: erro na geração
            BOLogger.log_event(
                bo_id=bo_id,
                event_type="generation_error",
                data={
                    "error": str(e),
                    "llm_provider": request_body.llm_provider
                }
            )
            raise HTTPException(status_code=500, detail=f"Erro ao gerar texto: {str(e)}")
    
    # Próxima pergunta
    next_question = state_machine.get_current_question()
    
    # Log: próxima pergunta
    BOLogger.log_event(
        bo_id=bo_id,
        event_type="question_asked",
        data={
            "step": state_machine.current_step,
            "question": next_question
        }
    )
    
    return ChatResponse(
        session_id=session_id,
        bo_id=bo_id,
        question=next_question,
        is_section_complete=False,
        current_step=state_machine.current_step,
        event_id=event_id
    )

@app.put("/chat/{session_id}/answer/{step}")
async def update_answer(session_id: str, step: str, update_request: UpdateAnswerRequest):
    """Atualiza resposta com logging"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    
    bo_id, state_machine = sessions[session_id]
    
    if step not in state_machine.QUESTIONS:
        raise HTTPException(status_code=400, detail=f"Step inválido: {step}")
    
    # Validar nova resposta
    is_valid, error_message = ResponseValidator.validate(step, update_request.message)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Log: resposta editada
    # Tentar pegar do state_machine primeiro, senão buscar do último evento
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
    
    # CRITICAL BUG FIX #2: Se current_step ainda aponta para step editado,
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
    
    # Importar now_brasilia do logger
    from logger import now_brasilia
    
    # Coletar metadados automaticamente
    metadata = feedback.metadata or {}
    metadata.update({
        "ip_address": get_client_ip(request),
        "user_agent": request.headers.get("User-Agent"),
        "timestamp": now_brasilia().isoformat()  # ✅ BUG FIX #4
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
