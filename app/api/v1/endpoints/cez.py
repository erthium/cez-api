from fastapi import APIRouter, HTTPException
from typing import List

from app.cez_ai.libs import game_lib, board_lib, ai_lib

import random

router = APIRouter()

@router.get("/calculate")
async def calculate(fen: str = ''):
  print(f'Collected fen notation: {fen}')
  game = game_lib.Game()

  try:
    game.board.load_fen(fen)
  except board_lib.FENError as e:
    print(f"could not load fen")
    return

  ai = ai_lib.AI(5)
  
  print("Calculating...")

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

