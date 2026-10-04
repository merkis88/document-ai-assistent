from fastapi import APIRouter
from app.modules.auth.schemas import RegisterRequest
from app.modules.auth import service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(data: RegisterRequest):
    return await service.registration(data)

