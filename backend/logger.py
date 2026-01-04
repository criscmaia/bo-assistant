"""
Sistema de Logs e Feedback do BO Inteligente
Suporta SQLite (local) e PostgreSQL (produção)
"""

import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, String, DateTime, JSON, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

# Timezone Brasília (UTC-3)
BRASILIA_TZ = timezone(timedelta(hours=-3))

def now_brasilia():
    """Retorna datetime atual em Brasília"""
    return datetime.now(BRASILIA_TZ)

# Detectar ambiente
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Produção: PostgreSQL (Render fornece DATABASE_URL)
    if DATABASE_URL.startswith("postgres://"):
        # Render usa postgres://, mas SQLAlchemy precisa postgresql://
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    # Local: SQLite
    DATABASE_URL = "sqlite:///./bo_logs.db"

# Criar engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Set True para debug SQL
)

Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# ============================================================================
# MODELOS
# ============================================================================

class BOSession(Base):
    """Sessão de BO - representa um BO sendo criado"""
    __tablename__ = "bo_sessions"
    
    bo_id = Column(String(50), primary_key=True)
    created_at = Column(DateTime, default=lambda: datetime.now(BRASILIA_TZ))  # ✅ Lambda callable
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="active")  # active, completed, abandoned
    app_version = Column(String(20), nullable=True)  # Versão do sistema
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    def to_dict(self):
        return {
            "bo_id": self.bo_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "app_version": self.app_version,
            "ip_address": self.ip_address
        }


class BOEvent(Base):
    """Evento individual dentro de uma sessão de BO"""
    __tablename__ = "bo_events"
    
    event_id = Column(String(50), primary_key=True)
    bo_id = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(BRASILIA_TZ))  # ✅ Lambda callable
    event_type = Column(String(50), nullable=False)
    data = Column(JSON, nullable=True)
    
    def to_dict(self):
        return {
            "event_id": self.event_id,
            "bo_id": self.bo_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "event_type": self.event_type,
            "data": self.data
        }


class Feedback(Base):
    """Feedback do usuário sobre eventos/sistema"""
    __tablename__ = "feedbacks"
    
    feedback_id = Column(String(50), primary_key=True)
    bo_id = Column(String(50), nullable=False)
    event_id = Column(String(50), nullable=True)  # Null se feedback geral
    timestamp = Column(DateTime, default=lambda: datetime.now(BRASILIA_TZ))  # ✅ Lambda callable
    feedback_type = Column(String(20), nullable=False)  # positive, negative
    category = Column(String(20), nullable=True)  # bug, suggestion
    user_message = Column(Text, nullable=True)
    context = Column(JSON, nullable=True)
    meta_data = Column(JSON, nullable=True)  # Renomeado de metadata
    status = Column(String(20), default="new")  # new, reviewed, resolved
    
    def to_dict(self):
        return {
            "feedback_id": self.feedback_id,
            "bo_id": self.bo_id,
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "feedback_type": self.feedback_type,
            "category": self.category,
            "user_message": self.user_message,
            "context": self.context,
            "metadata": self.meta_data,  # Expor como metadata no JSON
            "status": self.status
        }


# Criar tabelas
Base.metadata.create_all(engine)

# ============================================================================
# FUNÇÕES DE LOGGING
# ============================================================================

@contextmanager
def get_db():
    """Context manager para sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class BOLogger:
    """Gerenciador de logs do sistema"""
    
    @staticmethod
    def create_session(
        bo_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        app_version: Optional[str] = None
    ) -> str:
        """
        Cria nova sessão de BO.

        Args:
            bo_id: ID do BO (se não fornecido, gera automaticamente)
            ip_address: IP do cliente
            user_agent: User agent do cliente
            app_version: Versão da aplicação

        Returns:
            bo_id
        """
        # Se bo_id não foi fornecido, gerar novo
        if not bo_id:
            bo_id = f"BO-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"

        # Verificar se bo_id já existe (prevenir duplicatas)
        with get_db() as db:
            existing = db.query(BOSession).filter(BOSession.bo_id == bo_id).first()
            if existing:
                # Sessão já existe, retornar o bo_id
                return bo_id

        # Criar nova sessão
        with get_db() as db:
            session = BOSession(
                bo_id=bo_id,
                ip_address=ip_address,
                user_agent=user_agent,
                app_version=app_version,
                status="active"
            )
            db.add(session)
            db.commit()

        # Log evento de início
        BOLogger.log_event(
            bo_id=bo_id,
            event_type="session_started",
            data={"ip": ip_address, "app_version": app_version}
        )

        return bo_id

    @staticmethod
    def create_bo(
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        app_version: Optional[str] = None
    ) -> str:
        """
        Alias para create_session() - mantém compatibilidade.
        Gera novo bo_id automaticamente.
        """
        return BOLogger.create_session(
            bo_id=None,
            ip_address=ip_address,
            user_agent=user_agent,
            app_version=app_version
        )

    @staticmethod
    def log_event(bo_id: str, event_type: str, data: Optional[Dict[str, Any]] = None) -> str:
        """
        Registra um evento
        Returns: event_id
        """
        event_id = f"evt_{uuid.uuid4().hex[:8]}"
        
        with get_db() as db:
            event = BOEvent(
                event_id=event_id,
                bo_id=bo_id,
                event_type=event_type,
                data=data or {}
            )
            db.add(event)
            db.commit()
        
        return event_id
    
    @staticmethod
    def update_session_status(bo_id: str, status: str):
        """Atualiza status da sessão"""
        with get_db() as db:
            session = db.query(BOSession).filter(BOSession.bo_id == bo_id).first()
            if session:
                session.status = status
                if status == "completed":
                    session.completed_at = now_brasilia()  # ✅ Usar now_brasilia()
                db.commit()
    
    @staticmethod
    def add_feedback(
        bo_id: str,
        feedback_type: str,
        event_id: Optional[str] = None,
        category: Optional[str] = None,
        user_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Adiciona feedback do usuário
        Returns: feedback_id
        """
        feedback_id = f"fb_{uuid.uuid4().hex[:8]}"
        
        with get_db() as db:
            feedback = Feedback(
                feedback_id=feedback_id,
                bo_id=bo_id,
                event_id=event_id,
                feedback_type=feedback_type,
                category=category,
                user_message=user_message,
                context=context or {},
                meta_data=metadata or {},  # Usar meta_data
                status="new"
            )
            db.add(feedback)
            db.commit()
        
        return feedback_id
    
    @staticmethod
    def get_session(bo_id: str) -> Optional[Dict]:
        """Retorna dados de uma sessão"""
        with get_db() as db:
            session = db.query(BOSession).filter(BOSession.bo_id == bo_id).first()
            return session.to_dict() if session else None
    
    @staticmethod
    def get_events(bo_id: str) -> List[Dict]:
        """Retorna todos os eventos de uma sessão"""
        with get_db() as db:
            events = db.query(BOEvent).filter(BOEvent.bo_id == bo_id).order_by(BOEvent.timestamp).all()
            return [e.to_dict() for e in events]
    
    @staticmethod
    def get_feedbacks(bo_id: str) -> List[Dict]:
        """Retorna todos os feedbacks de uma sessão"""
        with get_db() as db:
            feedbacks = db.query(Feedback).filter(Feedback.bo_id == bo_id).order_by(Feedback.timestamp).all()
            return [f.to_dict() for f in feedbacks]
    
    @staticmethod
    def list_sessions(
        status: Optional[str] = None,
        date: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Lista sessões com filtros"""
        with get_db() as db:
            query = db.query(BOSession)
            
            if status:
                query = query.filter(BOSession.status == status)
            
            if date:
                # Filtrar por data (YYYY-MM-DD)
                start = datetime.strptime(date, "%Y-%m-%d")
                end = datetime.strptime(date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
                query = query.filter(BOSession.created_at.between(start, end))
            
            total = query.count()
            sessions = query.order_by(BOSession.created_at.desc()).limit(limit).offset(offset).all()
            
            return {
                "total": total,
                "limit": limit,
                "offset": offset,
                "sessions": [s.to_dict() for s in sessions]
            }
    
    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """Retorna estatísticas gerais"""
        with get_db() as db:
            total_sessions = db.query(BOSession).count()
            completed = db.query(BOSession).filter(BOSession.status == "completed").count()
            total_feedbacks = db.query(Feedback).count()
            negative_feedbacks = db.query(Feedback).filter(Feedback.feedback_type == "negative").count()
            
            return {
                "total_bos": total_sessions,
                "completed_bos": completed,
                "abandoned_bos": total_sessions - completed,
                "total_feedbacks": total_feedbacks,
                "positive_feedbacks": total_feedbacks - negative_feedbacks,
                "negative_feedbacks": negative_feedbacks
            }


# ============================================================================
# HELPER: Tipos de Eventos Comuns
# ============================================================================

EVENT_TYPES = {
    "session_started": "Sessão iniciada",
    "question_asked": "Pergunta exibida",
    "answer_submitted": "Resposta enviada",
    "validation_error": "Erro de validação",
    "answer_edited": "Resposta editada",
    "text_generated": "Texto do BO gerado",
    "text_copied": "Texto copiado",
    "session_completed": "Sessão concluída",
    "session_abandoned": "Sessão abandonada"
}
