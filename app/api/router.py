from fastapi import APIRouter

from app.api.routes import (
    agents,
    analytics,
    approvals,
    auth,
    conversations,
    integrations,
    knowledge,
    manager,
    notifications,
    settings,
    tools,
    uploads,
    users,
    workspaces,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["approvals"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(manager.router, prefix="/manager-insights", tags=["manager-insights"])
