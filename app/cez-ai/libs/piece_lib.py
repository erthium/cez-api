class Piece:
    def __init__(self, piece, pos):
        # 0: black pawn
        # 1: black knight
        # 2: white pawn
        # 3: white knight

        self.piece = piece
        self.pos = pos

    @property
    def color(self):
        # 0: black
        # 1: white

        return self.piece > 1

    @property
    def type(self):
        # 0: pawn
        # 1: knight

        return self.piece % 2

    @property
    def name(self):
        return f"{self.pos.name} ({'pnPN'[self.piece]})"

    def __repr__(self):
        return self.name

    def copy(self):
        return Piece(self.piece, self.pos.copy())
