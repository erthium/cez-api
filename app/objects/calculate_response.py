from pydantic import BaseModel
from typing import Optional

from .position import Position

class CalculateResponse(BaseModel):
  from_: Position
  to: Position
  capture: Optional[Position] = None
