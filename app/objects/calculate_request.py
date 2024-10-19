from pydantic import BaseModel

class CalculateRequest(BaseModel):
  fen: str
  depth: int
