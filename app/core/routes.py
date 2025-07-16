from fastapi import APIRouter

from app.modules.auth.routes import auth_router
from app.modules.channels.routes import channel_router
from app.modules.files.routes import files_router
from app.modules.messages.routes import message_router
from app.modules.users.routes import user_router
from app.modules.workspaces.routes import workspace_router

api_router = APIRouter()


api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(user_router, prefix="/users")
api_router.include_router(workspace_router, prefix="/workspaces")
api_router.include_router(channel_router, prefix="/workspaces/{workspace_id}/channels")
api_router.include_router(message_router, prefix="/workspaces/{workspace_id}")
api_router.include_router(files_router, prefix="/files")
