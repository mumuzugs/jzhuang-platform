# 设计模块占位符

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/")
async def get_designs():
    return {"message": "设计模块开发中"}


@router.post("/generate")
async def generate_design():
    return {"message": "设计生成开发中"}