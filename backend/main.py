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
    from state_machine_section3 import BOStateMachineSection3
    from state_machine_section4 import BOStateMachineSection4
    from state_machine_section5 import BOStateMachineSection5
    from state_machine_section6 import BOStateMachineSection6
    from state_machine_section7 import BOStateMachineSection7
    from state_machine_section8 import BOStateMachineSection8
    from llm_service import LLMService
    from validator import ResponseValidator
    from validator_section2 import ResponseValidatorSection2
    from validator_section3 import ResponseValidatorSection3
    from validator_section4 import ResponseValidatorSection4
    from validator_section5 import ResponseValidatorSection5
    from validator_section6 import ResponseValidatorSection6
    from validator_section7 import ResponseValidatorSection7
    from validator_section8 import ResponseValidatorSection8
    from logger import BOLogger, now_brasilia
    from section_factory import create_section_handler
except ImportError:
    # Fallback quando roda de fora da pasta backend/ (Render)
    from backend.state_machine import BOStateMachine
    from backend.state_machine_section2 import BOStateMachineSection2
    from backend.state_machine_section3 import BOStateMachineSection3
    from backend.state_machine_section4 import BOStateMachineSection4
    from backend.state_machine_section5 import BOStateMachineSection5
    from backend.state_machine_section6 import BOStateMachineSection6
    from backend.state_machine_section7 import BOStateMachineSection7
    from backend.state_machine_section8 import BOStateMachineSection8
    from backend.llm_service import LLMService
    from backend.validator import ResponseValidator
    from backend.validator_section2 import ResponseValidatorSection2
    from backend.validator_section3 import ResponseValidatorSection3
    from backend.validator_section4 import ResponseValidatorSection4
    from backend.validator_section5 import ResponseValidatorSection5
    from backend.validator_section6 import ResponseValidatorSection6
    from backend.validator_section7 import ResponseValidatorSection7
    from backend.validator_section8 import ResponseValidatorSection8
    from backend.logger import BOLogger, now_brasilia
    from backend.section_factory import create_section_handler

# Versão do sistema
APP_VERSION = "0.12.12"

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
#             3: BOStateMachineSection3(),  # Inicializado quando usuário avançar
#             4: BOStateMachineSection4(),  # Inicializado quando usuário avançar
#             5: BOStateMachineSection5(),  # Inicializado quando usuário avançar
#             6: BOStateMachineSection6(),  # Inicializado quando usuário avançar
#             7: BOStateMachineSection7(),  # Inicializado quando usuário avançar
#         },
#         "current_section": 1,
#         "section1_text": str,
#         "section2_text": str,
#         "section3_text": str,
#         "section4_text": str,
#         "section5_text": str,
#         "section6_text": str,
#         "section7_text": str
#     }
# }
sessions: Dict[str, Dict] = {}

# Models
class ChatRequest(BaseModel):
    session_id: str
    message: str
    current_section: Optional[int] = 1  # Novo campo
    llm_provider: Optional[str] = "groq"

class ChatResponse(BaseModel):
    session_id: str
    bo_id: str
    question: Optional[str] = None
    generated_text: Optional[str] = None
    is_section_complete: bool = False
    current_step: str
    current_section: Optional[int] = 1
    section_skipped: Optional[bool] = False  # NOVO: True se seção foi pulada
    validation_error: Optional[str] = None
    event_id: Optional[str] = None

class NewSessionResponse(BaseModel):
    session_id: str
    bo_id: str
    first_question: str

class UpdateAnswerRequest(BaseModel):
    message: str
    llm_provider: Optional[str] = "groq"

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
        "endpoints": ["/new_session", "/chat", "/sync_session", "/feedback", "/api/logs"]
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

    # Criar bo_id (formato) mas NÃO registrar no banco ainda
    # Só será registrado após 2 respostas válidas (lazy session creation)
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")
    bo_id = f"BO-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"

    # Criar estrutura de sessão com múltiplas seções
    sessions[session_id] = {
        "bo_id": bo_id,
        "logged_to_db": False,        # Flag para controlar se já foi registrado no banco
        "answer_count": 0,             # Contador de respostas válidas
        "pending_events": [],          # Eventos a serem registrados quando atingir 2 respostas
        "ip_address": ip_address,      # Guardar para usar no create_session depois
        "user_agent": user_agent,      # Guardar para usar no create_session depois
        "sections": {
            1: BOStateMachine(),
            # Seções 2, 3, 4, 5 e 6 serão inicializadas quando usuário clicar em "Iniciar Seção X"
        },
        "current_section": 1,
        "section1_text": "",
        "section2_text": "",
        "section3_text": "",
        "section4_text": "",
        "section5_text": "",
        "section6_text": "",
        "section7_text": "",
        "section8_text": ""
    }

    state_machine = sessions[session_id]["sections"][1]

    # Primeira pergunta
    first_question = state_machine.get_current_question()

    # Armazenar evento para logar depois (quando atingir 2 respostas)
    # ao invés de logar imediatamente
    sessions[session_id]["pending_events"].append({
        "event_type": "question_asked",
        "data": {
            "step": state_machine.current_step,
            "question": first_question,
            "section": 1
        }
    })

    return NewSessionResponse(
        session_id=session_id,
        bo_id=bo_id,
        first_question=first_question
    )

def ensure_session_logged(session_id: str) -> bool:
    """
    Garante que a sessão foi registrada no banco de dados.
    Só registra quando answer_count >= 2.

    Args:
        session_id: ID da sessão em memória

    Returns:
        True se sessão foi registrada (agora ou anteriormente), False caso contrário
    """
    if session_id not in sessions:
        return False

    session_data = sessions[session_id]

    # Já foi registrado anteriormente
    if session_data.get("logged_to_db", False):
        return True

    # Verificar se atingiu o threshold de 2 respostas
    if session_data.get("answer_count", 0) < 2:
        return False

    # Threshold atingido! Registrar no banco agora
    bo_id = session_data["bo_id"]
    ip_address = session_data.get("ip_address")
    user_agent = session_data.get("user_agent")

    # Criar sessão no banco com o bo_id já definido
    BOLogger.create_session(
        bo_id=bo_id,
        ip_address=ip_address,
        user_agent=user_agent,
        app_version=APP_VERSION
    )

    # Marcar como registrado
    session_data["logged_to_db"] = True

    # Logar eventos pendentes (primeira pergunta, primeiras respostas, etc)
    for pending_event in session_data.get("pending_events", []):
        BOLogger.log_event(
            bo_id=bo_id,
            event_type=pending_event["event_type"],
            data=pending_event["data"]
        )

    # Limpar fila de eventos pendentes
    session_data["pending_events"] = []

    return True

@app.post("/chat", response_model=ChatResponse)
async def chat(request_body: ChatRequest, request: Request):
    """Processa resposta com logging completo (suporta múltiplas seções)"""
    session_id = request_body.session_id
    current_section = request_body.current_section or 1

    # Verificar sessão - se não existir, recriar (útil quando backend reinicia)
    if session_id not in sessions:
        # Recriar sessão automaticamente
        bo_id = BOLogger.create_bo()
        sessions[session_id] = {
            "bo_id": bo_id,
            "sections": {
                1: BOStateMachine()
            },
            "section1_text": "",
            "section2_text": "",
            "section3_text": "",
            "section4_text": "",
            "section5_text": "",
            "section6_text": "",
            "section7_text": "",
            "section8_text": ""
        }
        BOLogger.log_event(
            bo_id=bo_id,
            event_type="session_recreated",
            data={"session_id": session_id, "reason": "backend_restart"}
        )

    session_data = sessions[session_id]
    bo_id = session_data["bo_id"]

    # Obter state machine da seção atual - criar se não existir
    if current_section not in session_data["sections"]:
        if current_section == 1:
            session_data["sections"][1] = BOStateMachine()
        elif current_section == 2:
            session_data["sections"][2] = BOStateMachineSection2()
        elif current_section == 3:
            session_data["sections"][3] = BOStateMachineSection3()
        elif current_section == 4:
            session_data["sections"][4] = BOStateMachineSection4()
        elif current_section == 5:
            session_data["sections"][5] = BOStateMachineSection5()
        elif current_section == 6:
            session_data["sections"][6] = BOStateMachineSection6()
        elif current_section == 7:
            session_data["sections"][7] = BOStateMachineSection7()
        elif current_section == 8:
            session_data["sections"][8] = BOStateMachineSection8()
        else:
            raise HTTPException(status_code=400, detail=f"Seção {current_section} não suportada")

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
    elif current_section == 3:
        is_valid, error_message = ResponseValidatorSection3.validate(
            current_step,
            request_body.message
        )
    elif current_section == 4:
        is_valid, error_message = ResponseValidatorSection4.validate(
            current_step,
            request_body.message
        )
    elif current_section == 5:
        is_valid, error_message = ResponseValidatorSection5.validate(
            current_step,
            request_body.message
        )
    elif current_section == 6:
        is_valid, error_message = ResponseValidatorSection6.validate(
            current_step,
            request_body.message
        )
    elif current_section == 7:
        is_valid, error_message = ResponseValidatorSection7.validate(
            current_step,
            request_body.message
        )
    elif current_section == 8:
        is_valid, error_message = ResponseValidatorSection8.validate(
            current_step,
            request_body.message
        )
    else:
        raise HTTPException(status_code=400, detail=f"Seção {current_section} não suportada")

    # Log único com is_valid correto
    event_id = None
    if is_valid:
        # Verificar se sessão já está registrada no banco
        is_already_logged = session_data.get("logged_to_db", False)

        if is_already_logged:
            # Já está no banco - gravar diretamente
            event_id = BOLogger.log_event(
                bo_id=bo_id,
                event_type="answer_submitted",
                data={
                    "step": current_step,
                    "answer": request_body.message,
                    "is_valid": is_valid
                }
            )
        else:
            # Ainda não está no banco - adicionar à fila para ser logado depois
            session_data["pending_events"].append({
                "event_type": "answer_submitted",
                "data": {
                    "step": current_step,
                    "answer": request_body.message,
                    "is_valid": is_valid
                }
            })
            # Usar um pseudo-ID para compatibilidade
            event_id = f"pending_{len(session_data['pending_events'])}"

    if not is_valid:
        # Verificar se sessão já está registrada no banco
        is_already_logged = session_data.get("logged_to_db", False)

        if is_already_logged:
            # Já está no banco - gravar erro diretamente
            BOLogger.log_event(
                bo_id=bo_id,
                event_type="validation_error",
                data={
                    "step": current_step,
                    "answer": request_body.message,
                    "error_message": error_message
                }
            )
        else:
            # Ainda não está no banco - adicionar à fila
            session_data["pending_events"].append({
                "event_type": "validation_error",
                "data": {
                    "step": current_step,
                    "answer": request_body.message,
                    "error_message": error_message
                }
            })

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

    # AGORA incrementar contador e garantir que sessão está no banco
    # (após armazenar resposta no state machine)
    session_data["answer_count"] = session_data.get("answer_count", 0) + 1
    is_logged = ensure_session_logged(session_id)

    # Verificar se seção está completa
    if state_machine.is_section_complete():
        # Se seção foi pulada (Seção 2, 3, 4, 5, 6 ou 7 com "NÃO")
        if current_section in [2, 3, 4, 5, 6, 7] and hasattr(state_machine, 'was_section_skipped') and state_machine.was_section_skipped():
            skip_reason = state_machine.get_skip_reason()

            # Log: seção pulada
            BOLogger.log_event(
                bo_id=bo_id,
                event_type="section_skipped",
                data={
                    "section": current_section,
                    "reason": skip_reason
                }
            )

            # Atualizar status como finalizado apenas se for a última seção (Seção 8)
            # IMPORTANTE: Seção 6 e 7 NÃO marcam como "completed" - apenas Seção 8
            if current_section == 8:
                BOLogger.update_session_status(bo_id, "completed")

            return ChatResponse(
                session_id=session_id,
                bo_id=bo_id,
                generated_text=skip_reason,  # Texto explicativo
                is_section_complete=True,
                current_step="complete",
                current_section=current_section,
                section_skipped=True,
                event_id=event_id
            )

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
            elif current_section == 3:
                generated_text = llm_service.generate_section3_text(
                    section_data=state_machine.get_all_answers(),
                    provider=request_body.llm_provider
                )
                session_data["section3_text"] = generated_text
            elif current_section == 4:
                generated_text = llm_service.generate_section4_text(
                    section_data=state_machine.get_all_answers(),
                    provider=request_body.llm_provider
                )
                session_data["section4_text"] = generated_text
            elif current_section == 5:
                generated_text = llm_service.generate_section5_text(
                    section_data=state_machine.get_all_answers(),
                    provider=request_body.llm_provider
                )
                session_data["section5_text"] = generated_text
            elif current_section == 6:
                generated_text = llm_service.generate_section6_text(
                    section_data=state_machine.get_all_answers(),
                    provider=request_body.llm_provider
                )
                session_data["section6_text"] = generated_text
            elif current_section == 7:
                generated_text = llm_service.generate_section7_text(
                    section_data=state_machine.get_all_answers(),
                    provider=request_body.llm_provider
                )
                session_data["section7_text"] = generated_text
            elif current_section == 8:
                generated_text = llm_service.generate_section8_text(
                    section_data=state_machine.get_all_answers(),
                    provider=request_body.llm_provider
                )
                session_data["section8_text"] = generated_text
                # IMPORTANTE: Seção 8 é a ÚLTIMA - marcar BO como completo
                BOLogger.update_session_status(bo_id, "completed")
            else:
                raise ValueError(f"Seção {current_section} não suportada")

            generation_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            # Log: texto gerado
            if is_logged:
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
            else:
                # Adicionar à fila de eventos pendentes
                session_data["pending_events"].append({
                    "event_type": f"section{current_section}_completed",
                    "data": {
                        "section": current_section,
                        "llm_provider": request_body.llm_provider,
                        "generated_text": generated_text,
                        "generation_time_ms": generation_time_ms,
                        "answers": state_machine.get_all_answers()
                    }
                })

            # Atualizar status da sessão apenas se todas as seções foram concluídas
            if current_section == 1:
                pass  # Não marca como "completed" ainda, pois tem Seção 2, 3, 4, 5, 6 e 7
            elif current_section == 2:
                pass  # Não marca como "completed" ainda, pois tem Seção 3, 4, 5, 6 e 7
            elif current_section == 3:
                pass  # Não marca como "completed" ainda, pois tem Seção 4, 5, 6 e 7
            elif current_section == 4:
                pass  # Não marca como "completed" ainda, pois tem Seção 5, 6 e 7
            elif current_section == 5:
                pass  # Não marca como "completed" ainda, pois tem Seção 6 e 7
            elif current_section == 6:
                pass  # Não marca como "completed" ainda, pois tem Seção 7
            elif current_section == 7:
                pass  # Não marca como "completed" ainda, pois tem Seção 8
            # Seção 8 marcará como "completed" quando implementada

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
            if is_logged:
                BOLogger.log_event(
                    bo_id=bo_id,
                    event_type="generation_error",
                    data={
                        "error": error_msg,
                        "llm_provider": request_body.llm_provider
                    }
                )
            else:
                # Adicionar à fila de eventos pendentes
                session_data["pending_events"].append({
                    "event_type": "generation_error",
                    "data": {
                        "error": error_msg,
                        "llm_provider": request_body.llm_provider
                    }
                })

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
    if is_logged:
        BOLogger.log_event(
            bo_id=bo_id,
            event_type="question_asked",
            data={
                "step": state_machine.current_step,
                "question": next_question,
                "section": current_section
            }
        )
    else:
        # Adicionar à fila de eventos pendentes
        session_data["pending_events"].append({
            "event_type": "question_asked",
            "data": {
                "step": state_machine.current_step,
                "question": next_question,
                "section": current_section
            }
        })

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
    Inicia uma nova seção do BO usando Factory Pattern.

    Body: {"session_id": "uuid"}

    Refatorado em v0.13.1 para usar section_factory.py,
    eliminando 283 linhas de código duplicado.
    """
    session_id = request_body.get("session_id")

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id é obrigatório")

    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    session_data = sessions[session_id]
    bo_id = session_data["bo_id"]

    # Validar número da seção
    if section_number not in [1, 2, 3, 4, 5, 6, 7, 8]:
        raise HTTPException(status_code=400, detail=f"Seção {section_number} inválida")

    # Usar Factory Pattern para inicializar a seção (v0.13.1+)
    # Elimina 283 linhas de código duplicado
    try:
        handler = create_section_handler(session_id, bo_id, section_number)
        response = handler.start(session_data)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/skip_section/{section_number}")
async def skip_section(section_number: int, request_body: dict):
    """
    Pula uma seção opcional (2-7) sem iniciar.
    Equivalente a responder "NÃO" na primeira pergunta.
    """
    session_id = request_body.get("session_id")

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id é obrigatório")

    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    # Validar que seção é pulável
    if section_number not in [2, 3, 4, 5, 6, 7]:
        raise HTTPException(status_code=400, detail="Esta seção não pode ser pulada")

    session_data = sessions[session_id]
    bo_id = session_data["bo_id"]

    # Criar state machine da seção
    state_machine_classes = {
        2: BOStateMachineSection2,
        3: BOStateMachineSection3,
        4: BOStateMachineSection4,
        5: BOStateMachineSection5,
        6: BOStateMachineSection6,
        7: BOStateMachineSection7,
    }

    state_machine = state_machine_classes[section_number]()
    state_machine.store_answer("NÃO")  # Simula resposta "NÃO"

    # Armazenar na sessão
    session_data["sections"][section_number] = state_machine
    session_data["current_section"] = section_number

    skip_reason = state_machine.get_skip_reason()

    # Log: seção pulada
    BOLogger.log_event(
        bo_id=bo_id,
        event_type="section_skipped",
        data={
            "section": section_number,
            "reason": skip_reason,
            "skipped_from_button": True  # Diferencia de pular via chat
        }
    )

    return {
        "session_id": session_id,
        "bo_id": bo_id,
        "generated_text": skip_reason,
        "is_section_complete": True,
        "current_step": "complete",
        "current_section": section_number,
        "section_skipped": True
    }

@app.post("/sync_session")
async def sync_session(request_body: dict):
    """
    Sincroniza sessão inteira de uma vez (restauração de rascunho).

    Body: {
        "session_id": "uuid",
        "answers": {"1.1": "...", "1.2": "...", "2.1": "..."},
        "llm_provider": "groq"
    }

    Returns: {
        "success": true,
        "current_step": "2.5",
        "current_section": 2,
        "section1_complete": true,
        "section2_complete": false
    }
    """
    session_id = request_body.get("session_id")
    answers = request_body.get("answers", {})

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id é obrigatório")

    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    session_data = sessions[session_id]
    bo_id = session_data["bo_id"]

    # Contar quantas respostas válidas existem antes de sincronizar
    valid_answer_count = 0
    for step in answers.keys():
        step_section = int(step.split('.')[0])
        answer = answers[step]

        # Validação rápida
        if step_section == 1:
            is_valid, _ = ResponseValidator.validate(step, answer)
        elif step_section == 2:
            is_valid, _ = ResponseValidatorSection2.validate(step, answer)
        elif step_section == 3:
            is_valid, _ = ResponseValidatorSection3.validate(step, answer)
        elif step_section == 4:
            is_valid, _ = ResponseValidatorSection4.validate(step, answer)
        elif step_section == 5:
            is_valid, _ = ResponseValidatorSection5.validate(step, answer)
        elif step_section == 6:
            is_valid, _ = ResponseValidatorSection6.validate(step, answer)
        elif step_section == 7:
            is_valid, _ = ResponseValidatorSection7.validate(step, answer)
        else:
            is_valid = False

        if is_valid:
            valid_answer_count += 1

    # Atualizar contador na sessão
    session_data["answer_count"] = valid_answer_count

    # Se tiver >= 2 respostas, garantir que sessão está no banco
    if valid_answer_count >= 2:
        ensure_session_logged(session_id)

    # Ordenar steps (1.1, 1.2, ..., 2.1, 2.2, ...)
    sorted_steps = sorted(answers.keys(), key=lambda s: tuple(map(int, s.split('.'))))

    current_section = 1

    for step in sorted_steps:
        answer = answers[step]

        # Detectar mudança de seção
        step_section = int(step.split('.')[0])
        if step_section != current_section:
            # Inicializar nova seção
            if step_section not in session_data["sections"]:
                if step_section == 2:
                    session_data["sections"][2] = BOStateMachineSection2()
                elif step_section == 3:
                    session_data["sections"][3] = BOStateMachineSection3()
                elif step_section == 4:
                    session_data["sections"][4] = BOStateMachineSection4()
                elif step_section == 5:
                    session_data["sections"][5] = BOStateMachineSection5()
                elif step_section == 6:
                    session_data["sections"][6] = BOStateMachineSection6()
                elif step_section == 7:
                    session_data["sections"][7] = BOStateMachineSection7()

            current_section = step_section
            session_data["current_section"] = current_section

        # Obter state machine da seção
        state_machine = session_data["sections"][current_section]

        # Validar resposta
        if current_section == 1:
            is_valid, error_message = ResponseValidator.validate(step, answer)
        elif current_section == 2:
            is_valid, error_message = ResponseValidatorSection2.validate(step, answer)
        elif current_section == 3:
            is_valid, error_message = ResponseValidatorSection3.validate(step, answer)
        elif current_section == 4:
            is_valid, error_message = ResponseValidatorSection4.validate(step, answer)
        elif current_section == 5:
            is_valid, error_message = ResponseValidatorSection5.validate(step, answer)
        elif current_section == 6:
            is_valid, error_message = ResponseValidatorSection6.validate(step, answer)
        elif current_section == 7:
            is_valid, error_message = ResponseValidatorSection7.validate(step, answer)
        else:
            continue  # Seção não suportada, pular

        if not is_valid:
            # Log: erro de validação durante sincronização
            BOLogger.log_event(
                bo_id=bo_id,
                event_type="sync_validation_error",
                data={"step": step, "error": error_message}
            )
            continue  # Pular resposta inválida

        # Armazenar e avançar
        state_machine.store_answer(answer)
        state_machine.next_step()

    # Retornar estado final
    final_section = current_section
    final_state_machine = session_data["sections"][final_section]

    return {
        "success": True,
        "current_step": final_state_machine.current_step,
        "current_section": final_section,
        "section1_complete": session_data["sections"][1].is_section_complete(),
        "section2_complete": session_data["sections"].get(2, None) and session_data["sections"][2].is_section_complete(),
        "section3_complete": session_data["sections"].get(3, None) and session_data["sections"][3].is_section_complete(),
        "section4_complete": session_data["sections"].get(4, None) and session_data["sections"][4].is_section_complete(),
        "section5_complete": session_data["sections"].get(5, None) and session_data["sections"][5].is_section_complete(),
        "section6_complete": session_data["sections"].get(6, None) and session_data["sections"][6].is_section_complete(),
        "section7_complete": session_data["sections"].get(7, None) and session_data["sections"][7].is_section_complete(),
        "section8_complete": session_data["sections"].get(8, None) and session_data["sections"][8].is_section_complete(),
        "bo_id": bo_id
    }

@app.put("/chat/{session_id}/answer/{step}")
async def update_answer(session_id: str, step: str, update_request: UpdateAnswerRequest):
    """Atualiza resposta com logging"""
    # Verificar sessão - recriar se necessário
    if session_id not in sessions:
        bo_id = BOLogger.create_bo()
        sessions[session_id] = {
            "bo_id": bo_id,
            "sections": {
                1: BOStateMachine()
            },
            "section1_text": "",
            "section2_text": "",
            "section3_text": "",
            "section4_text": "",
            "section5_text": "",
            "section6_text": "",
            "section7_text": "",
            "section8_text": ""
        }

    session_data = sessions[session_id]
    bo_id = session_data["bo_id"]

    # Determinar qual seção baseado no step
    if step.startswith("1."):
        state_machine = session_data["sections"][1]
        valid_steps = state_machine.QUESTIONS
    elif step.startswith("2."):
        state_machine = session_data["sections"][2]
        # Importar SECTION2_QUESTIONS para validação
        from backend.state_machine_section2 import SECTION2_QUESTIONS
        valid_steps = SECTION2_QUESTIONS
    elif step.startswith("3."):
        state_machine = session_data["sections"][3]
        # Importar SECTION3_QUESTIONS para validação
        from backend.state_machine_section3 import SECTION3_QUESTIONS
        valid_steps = SECTION3_QUESTIONS
    elif step.startswith("4."):
        state_machine = session_data["sections"][4]
        # Importar SECTION4_QUESTIONS para validação
        from backend.state_machine_section4 import SECTION4_QUESTIONS
        valid_steps = SECTION4_QUESTIONS
    elif step.startswith("5."):
        state_machine = session_data["sections"][5]
        # Importar SECTION5_QUESTIONS para validação
        from backend.state_machine_section5 import SECTION5_QUESTIONS
        valid_steps = SECTION5_QUESTIONS
    elif step.startswith("6."):
        state_machine = session_data["sections"][6]
        # Importar SECTION6_QUESTIONS para validação
        from backend.state_machine_section6 import SECTION6_QUESTIONS
        valid_steps = SECTION6_QUESTIONS
    elif step.startswith("7."):
        state_machine = session_data["sections"][7]
        # Importar SECTION7_QUESTIONS para validação
        from backend.state_machine_section7 import SECTION7_QUESTIONS
        valid_steps = SECTION7_QUESTIONS
    elif step.startswith("8."):
        state_machine = session_data["sections"][8]
        # Importar SECTION8_QUESTIONS para validação
        from backend.state_machine_section8 import SECTION8_QUESTIONS
        valid_steps = SECTION8_QUESTIONS
    else:
        raise HTTPException(status_code=400, detail=f"Step inválido: {step}")

    if step not in valid_steps:
        raise HTTPException(status_code=400, detail=f"Step inválido: {step}")

    # Validar nova resposta usando validator correto
    if step.startswith("1."):
        is_valid, error_message = ResponseValidator.validate(step, update_request.message)
    elif step.startswith("2."):
        is_valid, error_message = ResponseValidatorSection2.validate(step, update_request.message)
    elif step.startswith("3."):
        is_valid, error_message = ResponseValidatorSection3.validate(step, update_request.message)
    elif step.startswith("4."):
        is_valid, error_message = ResponseValidatorSection4.validate(step, update_request.message)
    elif step.startswith("5."):
        is_valid, error_message = ResponseValidatorSection5.validate(step, update_request.message)
    elif step.startswith("6."):
        is_valid, error_message = ResponseValidatorSection6.validate(step, update_request.message)
    elif step.startswith("7."):
        is_valid, error_message = ResponseValidatorSection7.validate(step, update_request.message)
    elif step.startswith("8."):
        is_valid, error_message = ResponseValidatorSection8.validate(step, update_request.message)
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
