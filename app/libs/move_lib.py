from app.libs import position_lib
import re


class Move:
    def __init__(self, from_, to, capture):
        self.from_ = from_
        self.to = to
        self.capture = capture

    def copy(self):
        return Move(self.from_.copy(), self.to.copy(), self.capture.copy())

    @property
    def delta(self):
        return self.to - self.from_

    @property
    def name(self):
        if self.capture is None:
            return f"{self.from_} -> {self.to}"

        else:
            return f"{self.from_} -> {self.to}x{self.capture}"

    def __repr__(self):
        return self.name

    @property
    def advantage(self):
        if self.capture:
            return self.to.advantage - self.from_.advantage - self.capture.advantage

        else:
            return self.to.advantage - self.from_.advantage


def from_text(move):
    match = re.match("^([a-h][1-8]) -> ([a-h][1-8])$", move)

    if match:
        from_, to = match.groups()
        from_, to = position_lib.from_text(from_), position_lib.from_text(to)
        return Move(from_, to, None)

    match = re.match("^([a-h][1-8]) -> ([a-h][1-8])x([a-h][1-8])$", move)

    if match:
        from_, to, capture = match.groups()
        from_, to, capture = position_lib.from_text(from_), position_lib.from_text(to), position_lib.from_text(capture)
        return Move(from_, to, capture)

    raise ValueError("Invalid syntax")


def moves_from_text(moves: str):
    if moves.startswith("[") and moves.endswith("]"):
        moves = moves[1:-1]

    m = []
    for item in moves.split(", "):
        m.append(from_text(item))

    return m
