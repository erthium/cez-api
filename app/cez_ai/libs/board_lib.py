from app.cez_ai.libs import move_lib, position_lib, piece_lib


class FENError(Exception):
    pass


class Board:
    def __init__(self):
        self.board = [None for _ in range(64)]
        self.white_pawns = []
        self.white_knights = []
        self.black_pawns = []
        self.black_knights = []
        self.color = True
        self.move_no = 0
        self.last_capture = 0
        self.possible_moves = []

    def copy(self):
        board = Board()
        board.color = self.color
        board.move_no = self.move_no
        board.possible_moves = self.possible_moves
        board.last_capture = self.last_capture

        for piece in self.pieces:
            board.add_piece(piece.piece, piece.pos.copy())

        return board

    @property
    def white_pieces(self):
        return self.white_knights + self.white_pawns

    @property
    def black_pieces(self):
        return self.black_knights + self.black_pawns

    @property
    def pieces(self):
        return self.white_pieces + self.black_pieces

    def clear(self):
        self.board = [None for _ in range(64)]
        self.white_pawns = []
        self.white_knights = []
        self.black_pawns = []
        self.black_knights = []

    def load_fen(self, fen):
        self.clear()
        self.last_capture = 0

        fen = fen.split(" ")

        if len(fen) != 2:
            raise FENError("Invalid FEN")

        if fen[1] == "b":
            self.color = False

        elif fen[1] == "w":
            self.color = True

        else:
            raise FENError("Invalid FEN")

        fen = fen[0]

        if fen.count("/") != 7:
            raise FENError("Invalid FEN")

        for row_no, row in enumerate(fen.split("/")):
            column = 0

            for char in row:
                if char in "12345678":
                    column += int(char)

                elif char in "pnPN":
                    self.add_piece("pnPN".index(char), position_lib.Position(column, row_no))
                    column += 1

                else:
                    raise FENError("Invalid FEN")

            if column != 8:
                raise FENError("Invalid FEN")

        self.get_moves()

    def get_fen(self):
        text = " "

        for pos in position_lib.get_all_positions():
            if self[pos] is None:
                if text[-1] in "12345678":
                    text = text[:-1] + str(int(text[-1]) + 1)

                else:
                    text += "1"

            else:
                text += "pnPN"[self[pos].piece]

            if pos.column == 7:
                text += "/"

        return text[1:-1] + " " + "bw"[self.color]

    def is_draw(self):
        return self.last_capture >= 50

    def go(self, from_, to):
        self[to] = self[from_]
        self[from_].pos = to
        self[from_] = None

    def make_move(self, move_, get_moves=True):
        self.last_capture += 1

        if move_.capture:
            self.remove_piece_from_pos(move_.capture)
            self.last_capture = 0

        self.go(move_.from_, move_.to)

        self.next()
        self.move_no += 1

        if get_moves:
            self.get_moves()

    def make_moves(self, moves, get_moves=True):
        for move in moves:
            self.make_move(move, False)

        if get_moves:
            self.get_moves()

    def add_piece(self, piece_type, pos):
        piece = piece_lib.Piece(piece_type, pos)
        self[pos] = piece
        self.get_piece_list(piece.piece).append(piece)

    def remove_piece(self, piece):
        self.get_piece_list(piece.piece).remove(piece)

        self[piece.pos] = None

    def remove_piece_from_pos(self, pos):
        piece = self[pos]
        self.remove_piece(piece)

    def get_piece_list(self, piece_type):
        if piece_type == 0:
            return self.black_pawns

        if piece_type == 1:
            return self.black_knights

        if piece_type == 2:
            return self.white_pawns

        if piece_type == 3:
            return self.white_knights

        raise ValueError()

    def __setitem__(self, key, value):
        self.board[key.id] = value

    def __getitem__(self, item):
        return self.board[item.id]

    def get_moves(self):
        can_capture = False
        self.possible_moves = []

        for piece in self.get_turn_pieces():
            normal_jump = (1, 2)[piece.type]

            for delta in position_lib.get_deltas():
                to = piece.pos + delta * normal_jump

                if not to.is_valid:
                    continue

                if self[to] is None:
                    if not can_capture:
                        # No capture
                        move = move_lib.Move(piece.pos, to, None)
                        
                        if to.advantage > piece.pos.advantage:
                            self.possible_moves.insert(0, move)

                        else:
                            self.possible_moves.append(move)

                elif self[to].color ^ self.color:
                    capture = to
                    to += delta

                    if not (to.is_valid and self[to] is None):
                        continue

                    # Capture
                    if not can_capture:
                        can_capture = True
                        self.possible_moves.clear()

                    if to.advantage > piece.pos.advantage:
                        self.possible_moves.insert(0, move_lib.Move(piece.pos, to, capture))

                    else:
                        self.possible_moves.append(move_lib.Move(piece.pos, to, capture))

    def next(self):
        self.color = not self.color

    def get_pieces(self):
        if self.color:
            return self.white_pieces, self.black_pieces

        else:
            return self.black_pieces, self.white_pieces

    def get_turn_pieces(self):
        if self.color:
            return self.white_pieces

        else:
            return self.black_pieces
