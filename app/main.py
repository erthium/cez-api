from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.v1.endpoints import cez
#from app.core.config import settings

app = FastAPI()

app.include_router(cez.router, prefix="/api/v1/cez")

origins = [
  "http://localhost",
  "http://localhost:8000",
  "http://localhost:5000",
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.get("/")
def get_root():
  return {"V"} # V for Vendetta


if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=8000)
