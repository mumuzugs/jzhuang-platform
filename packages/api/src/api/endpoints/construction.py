# 施工模块占位符

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_constructions():
    return {"message": "施工模块开发中"}


@router.post("/plan")
async def create_plan():
    return {"message": "施工计划生成开发中"}