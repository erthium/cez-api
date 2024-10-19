from pydantic import BaseModel

class Position(BaseModel):
  column: int
  row: int