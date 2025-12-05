from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
from pathlib import Path

# Imports compatíveis com local E Render
try:
    # Tenta import direto (funciona quando roda de dentro de backend/)
    from state_machine import BOStateMachine
    from llm_service import LLMService
    from validator import ResponseValidator
except ImportError:
    # Fallback quando roda de fora da pasta backend/ (Render)
    from backend.state_machine import BOStateMachine
    from backend.llm_service import LLMService
    from backend.validator import ResponseValidator

app = FastAPI(title="BO Assistant API", version="0.2.1")

# Configurar CORS para permitir frontend acessar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Armazenamento em memória das sessões (por enquanto)
# Chave: session_id, Valor: BOStateMachine
sessions: Dict[str, BOStateMachine] = {}

# Models para requests/responses
class ChatRequest(BaseModel):
    session_id: str
    message: str
    llm_provider: Optional[str] = "gemini"

class ChatResponse(BaseModel):
    session_id: str
    question: Optional[str] = None
    generated_text: Optional[str] = None
    is_section_complete: bool = False
    current_step: str
    validation_error: Optional[str] = None

class NewSessionResponse(BaseModel):
    session_id: str
    first_question: str

class UpdateAnswerRequest(BaseModel):
    message: str
    llm_provider: Optional[str] = "gemini"

# Inicializar serviço de LLM
llm_service = LLMService()

# Servir frontend (se existir)
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    @app.get("/app")
    async def serve_frontend():
        return FileResponse(frontend_path / "index.html")

@app.get("/")
async def root():
    return {
        "message": "BO Assistant API",
        "version": "0.2.1",
        "endpoints": ["/new_session", "/chat", "/health"]
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/new_session", response_model=NewSessionResponse)
async def new_session():
    """
    Inicia uma nova sessão de BO.
    Retorna o session_id e a primeira pergunta da Seção 1.
    """
    import uuid
    session_id = str(uuid.uuid4())
    
    # Criar nova state machine
    state_machine = BOStateMachine()
    sessions[session_id] = state_machine
    
    # Obter primeira pergunta
    first_question = state_machine.get_current_question()
    
    return NewSessionResponse(
        session_id=session_id,
        first_question=first_question
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Processa resposta do usuário e retorna próxima pergunta ou texto gerado.
    """
    session_id = request.session_id
    
    # Verificar se sessão existe
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    
    state_machine = sessions[session_id]
    
    # VALIDAR RESPOSTA ANTES DE ARMAZENAR
    is_valid, error_message = ResponseValidator.validate(
        state_machine.current_step, 
        request.message
    )
    
    if not is_valid:
        # Resposta inválida - retornar erro SEM avançar
        return ChatResponse(
            session_id=session_id,
            question=state_machine.get_current_question(),
            is_section_complete=False,
            current_step=state_machine.current_step,
            validation_error=error_message
        )
    
    # Armazenar resposta do usuário (apenas se válida)
    state_machine.store_answer(request.message)
    
    # Avançar para próxima pergunta
    state_machine.next_step()
    
    # Verificar se seção está completa
    if state_machine.is_section_complete():
        # Gerar texto final com LLM
        try:
            print(f"[DEBUG] Gerando texto para sessão {session_id}")
            print(f"[DEBUG] Respostas coletadas: {state_machine.get_all_answers()}")
            
            generated_text = await llm_service.generate_section_text(
                section_data=state_machine.get_all_answers(),
                provider=request.llm_provider
            )
            
            print(f"[DEBUG] Texto gerado com sucesso: {generated_text[:100]}...")
            
            return ChatResponse(
                session_id=session_id,
                generated_text=generated_text,
                is_section_complete=True,
                current_step=state_machine.current_step
            )
        except Exception as e:
            import traceback
            print(f"[ERRO] Falha ao gerar texto: {str(e)}")
            print(f"[ERRO] Traceback completo:")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Erro ao gerar texto: {str(e)}")
    
    # Retornar próxima pergunta
    next_question = state_machine.get_current_question()
    
    return ChatResponse(
        session_id=session_id,
        question=next_question,
        is_section_complete=False,
        current_step=state_machine.current_step
    )

@app.put("/chat/{session_id}/answer/{step}")
async def update_answer(session_id: str, step: str, update_request: UpdateAnswerRequest):
    """
    Atualiza resposta de uma pergunta específica.
    Útil para edição de respostas anteriores.
    """
    # Verificar se sessão existe
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    
    state_machine = sessions[session_id]
    
    # Validar step
    if step not in state_machine.QUESTIONS:
        raise HTTPException(status_code=400, detail=f"Step inválido: {step}")
    
    # Validar nova resposta
    is_valid, error_message = ResponseValidator.validate(step, update_request.message)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Atualizar resposta
    state_machine.answers[step] = update_request.message.strip()
    
    return {
        "success": True,
        "message": "Resposta atualizada com sucesso",
        "step": step
    }

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Deleta uma sessão (útil para testes).
    """
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "Sessão deletada"}
    raise HTTPException(status_code=404, detail="Sessão não encontrada")

@app.get("/session/{session_id}/status")
async def session_status(session_id: str):
    """
    Retorna status atual da sessão (útil para debug).
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    
    state_machine = sessions[session_id]
    
    return {
        "session_id": session_id,
        "current_step": state_machine.current_step,
        "is_complete": state_machine.is_section_complete(),
        "answers_count": len(state_machine.answers)
    }

if __name__ == "__main__":
    # Rodar servidor local
    # Nota: reload=True requer import string, então usamos sem reload
    # Para desenvolvimento com reload, use: uvicorn main:app --reload
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)