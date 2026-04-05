# 验房模块占位符

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_inspections():
    return {"message": "验房模块开发中"}


@router.post("/report")
async def create_report():
    return {"message": "验房报告生成开发中"}