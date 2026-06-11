from fastapi import APIRouter
from app.services.indicator_service import indicator_service

router = APIRouter()


@router.get("/macro")
async def get_macro_indicators():
    return await indicator_service.get_all_indicators()


@router.get("/global")
async def get_global_indicators():
    return await indicator_service.get_global_indicators()
