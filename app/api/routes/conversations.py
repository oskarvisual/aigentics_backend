from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import TenantScope
from app.db.session import get_db
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from app.services.conversation_service import ConversationService

router = APIRouter()


@router.get("", response_model=list[ConversationResponse])
def list_conversations(
    context: TenantScope, db: Session = Depends(get_db)
) -> list[ConversationResponse]:
    return ConversationService(db).list(context.tenant_id)


@router.post("", response_model=ConversationResponse)
def create_conversation(
    payload: ConversationCreate, context: TenantScope, db: Session = Depends(get_db)
) -> ConversationResponse:
    return ConversationService(db).create(context, payload)


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
def add_message(
    conversation_id: str,
    payload: MessageCreate,
    context: TenantScope,
    db: Session = Depends(get_db),
) -> MessageResponse:
    return ConversationService(db).add_message(context, conversation_id, payload)

