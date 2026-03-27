from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import AuditActorType, ConversationStatus, WorkspaceRole
from app.models.conversation import Conversation, Message
from app.schemas.conversation import ConversationCreate, MessageCreate
from app.services.audit_service import AuditService
from app.services.base import TenantContext, ensure_role


class ConversationService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditService(db)

    def list(self, tenant_id: str) -> list[Conversation]:
        return list(
            self.db.scalars(
                select(Conversation)
                .where(Conversation.tenant_id == tenant_id)
                .order_by(Conversation.updated_at.desc())
            )
        )

    def create(self, context: TenantContext, payload: ConversationCreate) -> Conversation:
        ensure_role(
            context,
            [WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.MANAGER, WorkspaceRole.HUMAN_AGENT],
        )
        conversation = Conversation(
            tenant_id=context.tenant_id,
            tenant_agent_id=payload.tenant_agent_id,
            assigned_user_id=context.user.id,
            conversation_type=payload.conversation_type,
            subject=payload.subject,
            status=ConversationStatus.OPEN,
            external_channel=payload.external_channel,
            channel_metadata=payload.channel_metadata,
            last_message_at=datetime.now(UTC),
        )
        self.db.add(conversation)
        self.db.flush()
        self.audit.log(
            tenant_id=context.tenant_id,
            actor_type=AuditActorType.USER,
            actor_user_id=context.user.id,
            actor_agent_id=None,
            action="conversation.create",
            entity_type="conversation",
            entity_id=conversation.id,
        )
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def add_message(
        self, context: TenantContext, conversation_id: str, payload: MessageCreate
    ) -> Message:
        ensure_role(
            context,
            [WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.MANAGER, WorkspaceRole.HUMAN_AGENT],
        )
        conversation = self.db.scalar(
            select(Conversation).where(
                Conversation.id == conversation_id, Conversation.tenant_id == context.tenant_id
            )
        )
        if conversation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
        message = Message(
            tenant_id=context.tenant_id,
            conversation_id=conversation_id,
            sender_user_id=context.user.id,
            role=payload.role,
            content=payload.content,
            content_structured=payload.content_structured,
            tool_name=payload.tool_name,
            tool_call_id=payload.tool_call_id,
            parent_message_id=payload.parent_message_id,
            requires_approval=payload.requires_approval,
        )
        conversation.last_message_at = datetime.now(UTC)
        self.db.add(message)
        self.db.flush()
        self.audit.log(
            tenant_id=context.tenant_id,
            actor_type=AuditActorType.USER,
            actor_user_id=context.user.id,
            actor_agent_id=None,
            action="conversation.add_message",
            entity_type="message",
            entity_id=message.id,
        )
        self.db.commit()
        self.db.refresh(message)
        return message
