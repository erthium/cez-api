from libs import board_lib, position_lib, ai_lib
import os
import pygame

WHITE_COLOR = 255, 200, 120
BLACK_COLOR = 130, 60, 0
CENTRAL_WHITE_COLOR = 220, 170, 90
CENTRAL_BLACK_COLOR = 95, 30, 0
POSSIBLE_MOVE_COLOR = 50, 20, 0
CAPTURE_COLOR = 200, 0, 0
HELD_COLOR = 100, 200, 255
CENTRAL_SQUARE_COLOR = 255, 255, 200
CENTRAL_SQUARE_WIDTH = 1

MOVE_RADIUS = 15
CAPTURE_RADIUS = 20

SCREEN_SIZE = 800, 800
FLAGS = 0

CELL_SIZE = 100


class State:
    pass


class Going(State):
    pass


class Mate(State):
    def __init__(self, color, by):
        self.color = color
        self.by = by


class Stalemate(State):
    pass


class Game:
    def __init__(self):
        self.board = board_lib.Board()

        self.board_history = []
        self.move_history = []

        self.state = Going()

        self.window = pygame.display.set_mode(SCREEN_SIZE, flags=FLAGS)

        self.board_background = pygame.Surface((CELL_SIZE * 8, CELL_SIZE * 8))
        self.draw_background()

        self.sprites = []
        self.load_sprites()

        self.held = None

        self.when_game_ended = None

    def dump_data(self):
        files = os.listdir("games/")
        no = 1

        while True:
            name = f"game_data_{str(no).rjust(4, '0')}.txt"

            if name not in files:
                self.dump_data_to_file("games/" + name)
                return

            no += 1

    def dump_data_to_file(self, file_name):
        with open(file_name, "w") as file:
            file.write("")

        with open(file_name, "a") as file:
            for no, board in enumerate(self.board_history):
                file.write(f"{no + 1}: {board} {self.move_history[no]}\n")

            if type(self.state) is Going:
                file.write("INTERRUPTED")

            elif type(self.state) is Mate:
                if self.state.color:
                    file.write(f"White mated by {self.state.by}")

                else:
                    file.write(f"Black mated by {self.state.by}")

            elif type(self.state) is Stalemate:
                file.write("Stalemate")

    def make_move(self, move):
        self.board_history.append(self.board.get_fen())
        self.move_history.append(repr(move))

        self.board.make_move(move)

        white_pieces = list(self.board.white_pieces)
        black_pieces = list(self.board.black_pieces)

        if not len(white_pieces):
            self.won(False, "no pieces left")

        if not len(black_pieces):
            self.won(True, "no pieces left")

        loose, _ = ai_lib.get_loose_pieces(white_pieces)
        if loose == 0:
            self.won(True, "no loose pieces")

        loose, _ = ai_lib.get_loose_pieces(black_pieces)
        if loose == 0:
            self.won(False, "no loose pieces")

        if self.board.is_draw():
            self.stalemate()

    def won(self, color, by):
        self.state = Mate(color, by)

        if self.when_game_ended is not None:
            self.when_game_ended()

    def stalemate(self):
        self.state = Stalemate()

        if self.when_game_ended is not None:
            self.when_game_ended()

    def draw(self):
        self.window.blit(self.board_background, (0, 0))

        if self.held:
            self.draw_cell_on_window(self.held, HELD_COLOR)

        for piece in self.board.pieces:
            if self.held and piece.pos == self.held:
                rect = pygame.Rect(0, 0, CELL_SIZE, CELL_SIZE)
                rect.center = pygame.mouse.get_pos()
                self.window.blit(self.sprites[piece.piece], rect)

            else:
                self.window.blit(self.sprites[piece.piece], get_rect_from_position(piece.pos))

        for move in self.board.possible_moves:
            if self.held and move.from_ == self.held:
                self.draw_circle_on_window(move.to, POSSIBLE_MOVE_COLOR,
                                           MOVE_RADIUS)

                if move.capture:
                    self.draw_circle_on_window(move.capture, CAPTURE_COLOR,
                                               CAPTURE_RADIUS)

        pygame.display.update()

    def draw_background(self):
        self.board_background.fill(BLACK_COLOR)

        for position in position_lib.get_all_positions():
            if position.is_white:
                if position.is_central:
                    self.draw_cell_on_board(position, CENTRAL_WHITE_COLOR)

                else:
                    self.draw_cell_on_board(position, WHITE_COLOR)

            elif position.is_central:
                self.draw_cell_on_board(position, CENTRAL_BLACK_COLOR)

    def load_sprites(self):
        self.sprites.clear()

        for piece in range(4):
            self.load_sprite(piece)

    def load_sprite(self, piece):
        self.sprites.append(pygame.transform.scale(pygame.image.load(f"theme/{piece}.png"),
                                                   (CELL_SIZE, CELL_SIZE)))

    def draw_cell_on_window(self, position, color):
        self.window.fill(color, get_rect_from_position(position))

    def draw_circle_on_window(self, position, color, radius):
        pygame.draw.circle(self.window, color, get_rect_from_position(position).center, radius)

    def draw_cell_on_board(self, position, color):
        self.board_background.fill(color, get_rect_from_position(position))

    def draw_circle_on_board(self, position, color, radius):
        pygame.draw.circle(self.board_background, color, get_rect_from_position(position).center, radius)


def get_position_from_rect(rect):
    return position_lib.Position(int(rect[0] / CELL_SIZE), int(8 - rect[1] / CELL_SIZE))


def get_rect_from_position(pos):
    return pygame.rect.Rect(pos.column * CELL_SIZE, (7 - pos.row) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
