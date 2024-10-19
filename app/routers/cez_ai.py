from fastapi import APIRouter, HTTPException, Request
from typing import List

from app.libs import game_lib, board_lib, ai_lib

import random

router = APIRouter()

@router.post("/calculate")
async def calculate(request: Request):
  data = await request.json()
  fen = data.get("fen")
  depth = data.get("depth")
  if not depth:
    depth = 4
  game = game_lib.Game()

  try:
    game.board.load_fen(fen)
  except board_lib.FENError as e:
    print(f"could not load fen")
    return

  depth = max(1, min(6, depth))
  ai = ai_lib.AI(depth)
  
  print(f"Calculating with depth {depth}...")

  best_lines, best_score = ai.calculate_best_move(game.board)
  move = random.choice(best_lines)[-1]
  length = len(best_lines[0])

  print("All found alternatives:")
  for line in best_lines:
      print(*line[::-1], sep=", ")

  if best_score is None:
      print("Score is not calculated")

  else:
      print(f"Score: {-best_score}")

  print(f"Length: {length}")

  print(f"Gonna play {move}")
  
  return move

