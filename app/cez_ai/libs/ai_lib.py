from app.cez_ai.libs import position_lib
import math
import random


# todo: move to board lib
def get_loose_pieces(pieces):
    loose_pieces = pieces.copy()
    favoured_positions = list(position_lib.get_all_centrals())

    while True:
        for piece in loose_pieces:
            if piece.pos in favoured_positions:
                loose_pieces.remove(piece)

                for delta in position_lib.get_deltas():
                    pos = piece.pos + delta

                    if pos.is_valid and pos not in favoured_positions:
                        favoured_positions.append(pos)

                break

        else:
            return len(loose_pieces), favoured_positions


def get_possible_moves(board, depth):
    if depth:
        for move in board.possible_moves:
            new_board = board.copy()
            new_board.make_move(move)

            for line in get_possible_moves(new_board, depth - 1):
                yield (move,) + line

    else:
        yield ()


class AI:
    def __init__(self, depth):
        self.PAWN_CELL_ADVANTAGE = 55
        self.KNIGHT_CELL_ADVANTAGE = 3
        self.PAWN_ADVANTAGE = 115
        self.KNIGHT_ADVANTAGE = 389
        self.FAVOURED_CELL_NUMBER_ADVANTAGE = 10
        self.SQUARE_COLOR_ADVANTAGE = -11
        self.LOOSE_PIECE_ADVANTAGE = -39
        self.STALEMATE_ADVANTAGE = -2

        self.DEPTH = depth

    def get_evaluation_color(self, my_pieces):
        score = 0

        white = 0
        black = 0

        for piece in my_pieces:
            if piece.type:
                score += piece.pos.advantage * self.KNIGHT_CELL_ADVANTAGE + self.KNIGHT_ADVANTAGE

            else:
                score += piece.pos.advantage * self.PAWN_CELL_ADVANTAGE + self.PAWN_ADVANTAGE

                if piece.pos.is_white:
                    white += 1

                else:
                    black += 1

        return score + abs(white - black) * self.SQUARE_COLOR_ADVANTAGE

    def get_evaluation(self, my_pieces, opponent_pieces,
                       my_loose, opponent_loose,
                       my_favoured, opponent_favoured):

        return self.get_evaluation_color(my_pieces) - \
               self.get_evaluation_color(opponent_pieces) + \
               (my_favoured - opponent_favoured) * self.FAVOURED_CELL_NUMBER_ADVANTAGE + \
               (my_loose - opponent_loose) * self.LOOSE_PIECE_ADVANTAGE

    def get_evaluation_from_board(self, board):
        return self.get_evaluation(*board.get_pieces())

    def calculate_best_move(self, board, depth=None, start=True,
                            my_loose=None, opponent_loose=None,
                            my_favoured=None, opponent_favoured=None,
                            alpha=-math.inf, beta=math.inf):

        if board.last_capture >= 50:
            return [], 0

        if start:
            depth = self.DEPTH
            my_pieces, opponent_pieces = board.get_pieces()

            my_loose, my_favoured = get_loose_pieces(my_pieces)
            opponent_loose, opponent_favoured = get_loose_pieces(opponent_pieces)

        possible_moves_count = len(board.possible_moves)

        if possible_moves_count == 0:
            raise ValueError("No possible moves")

        new_depth = depth

        if possible_moves_count == 1:
            if start:
                return [[board.possible_moves[0]]], 0

        else:
            new_depth -= 1

        line_length = 0
        best_lines = []
        best_score = -math.inf
        for move in board.possible_moves:
            new_board = board.copy()
            new_board.make_move(move, depth > 1)

            opponent_new_pieces, my_new_pieces = new_board.get_pieces()

            # Get my loose if needed
            if move.from_ in my_favoured or move.to in my_favoured:
                my_new_loose, my_new_favoured = get_loose_pieces(my_new_pieces)

            else:
                my_new_loose, my_new_favoured = my_loose, my_favoured

            # Get opponent loose if needed
            if move.capture and move.capture in opponent_favoured:
                opponent_new_loose, opponent_new_favoured = get_loose_pieces(opponent_new_pieces)

            else:
                opponent_new_loose, opponent_new_favoured = opponent_loose, opponent_favoured

            if not (opponent_new_pieces and my_new_loose):
                if start:
                    return [[move]], math.inf

                else:
                    return [move], math.inf

            elif not (my_new_pieces and opponent_new_loose):
                line = [move]
                score = -math.inf

            elif depth > 1:  # Check if there is still depth we can go
                line, score = self.calculate_best_move(new_board, new_depth, False,
                                                       opponent_new_loose, my_new_loose,
                                                       opponent_new_favoured, my_new_favoured,
                                                       None if beta is None else -beta,
                                                       None if alpha is None else -alpha)
                score *= -1

                line.append(move)

            else:  # Check the evaluation
                line = [move]
                score = self.get_evaluation(my_new_pieces, opponent_new_pieces,
                                            my_new_loose, opponent_new_loose,
                                            len(my_new_favoured),
                                            len(opponent_new_favoured)) + board.last_capture * self.STALEMATE_ADVANTAGE

            # Try to maximize score
            if score > best_score:
                best_lines = [line]
                best_score = score
                line_length = len(line)

            elif score == best_score:
                if (score < 0) ^ (len(line) < line_length):
                    best_lines = [line]
                    line_length = len(line)

                elif len(line) == line_length:
                    best_lines.append(line)

            if beta is not None and best_score > beta:
                break

            if alpha is None or best_score > alpha:
                alpha = best_score

        if start:
            return best_lines, best_score

        else:
            return random.choice(best_lines), best_score

    def copy(self):
        ai = AI(self.DEPTH)

        ai.SQUARE_COLOR_ADVANTAGE = self.SQUARE_COLOR_ADVANTAGE
        ai.PAWN_ADVANTAGE = self.PAWN_ADVANTAGE
        ai.KNIGHT_ADVANTAGE = self.KNIGHT_ADVANTAGE
        ai.PAWN_CELL_ADVANTAGE = self.PAWN_CELL_ADVANTAGE
        ai.KNIGHT_CELL_ADVANTAGE = self.KNIGHT_CELL_ADVANTAGE
        ai.STALEMATE_ADVANTAGE = self.STALEMATE_ADVANTAGE
        ai.LOOSE_PIECE_ADVANTAGE = self.LOOSE_PIECE_ADVANTAGE
        ai.FAVOURED_CELL_NUMBER_ADVANTAGE = self.FAVOURED_CELL_NUMBER_ADVANTAGE

        return ai

    def mutate(self):
        x = random.uniform(-1, 1)
        self.SQUARE_COLOR_ADVANTAGE += x ** 9
        print(f"SQUARE_COLOR_ADVANTAGE: {self.SQUARE_COLOR_ADVANTAGE}")
        x = random.uniform(-1, 1)
        self.PAWN_ADVANTAGE += x ** 9 * 10
        print(f"PAWN_ADVANTAGE: {self.PAWN_ADVANTAGE}")
        x = random.uniform(-1, 1)
        self.KNIGHT_ADVANTAGE += x ** 9 * 10
        print(f"KNIGHT_ADVANTAGE: {self.KNIGHT_ADVANTAGE}")
        x = random.uniform(-1, 1)
        self.PAWN_CELL_ADVANTAGE += x ** 9 * 5
        print(f"PAWN_CELL_ADVANTAGE: {self.PAWN_CELL_ADVANTAGE}")
        x = random.uniform(-1, 1)
        self.KNIGHT_CELL_ADVANTAGE += x ** 9 * 5
        print(f"KNIGHT_CELL_ADVANTAGE: {self.KNIGHT_CELL_ADVANTAGE}")
        x = random.uniform(-1, 1)
        self.STALEMATE_ADVANTAGE += x ** 9
        print(f"STALEMATE_ADVANTAGE: {self.STALEMATE_ADVANTAGE}")
        x = random.uniform(-1, 1)
        self.LOOSE_PIECE_ADVANTAGE += x ** 9
        print(f"LOOSE_PIECE_ADVANTAGE: {self.LOOSE_PIECE_ADVANTAGE}")
        x = random.uniform(-1, 1)
        self.FAVOURED_CELL_NUMBER_ADVANTAGE += x ** 9
        print(f"FAVOURED_CELL_NUMBER_ADVANTAGE: {self.FAVOURED_CELL_NUMBER_ADVANTAGE}")
