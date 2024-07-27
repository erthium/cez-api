from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()

@router.get("/calculate")
async def calculate():
  return
