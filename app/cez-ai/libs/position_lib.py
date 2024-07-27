class Position:
    def __init__(self, column, row):
        self.column = column
        self.row = row

    def copy(self):
        return Position(self.column, self.row)

    def deepcopy(self):
        return self.copy()

    def __add__(self, other):
        return Position(self.column + other.column, self.row + other.row)

    def __mul__(self, other):
        return Position(self.column * other, self.row * other)

    def set(self, to):
        self.column = to.column
        self.row = to.row

    def add(self, inc):
        self.column += inc.column
        self.row += inc.row

    @property
    def name(self):
        return "abcdefgh"[self.column] + str(self.row + 1)

    @property
    def is_white(self):
        return (self.column + self.row) % 2

    @property
    def id(self):
        return self.column + self.row * 8

    def __repr__(self):
        return self.name

    @property
    def is_valid(self):
        return 8 > self.column >= 0 and 8 > self.row >= 0

    @property
    def is_central(self):
        return 5 > self.column >= 3 and 5 > self.row >= 3

    def __eq__(self, other):
        return self.column == other.column and self.row == other.row

    @property
    def advantage(self):
        x = abs(2 * self.column - 7) + abs(2 * self.row - 7)
        return -x * x


def get_all_positions():
    for id_ in range(64):
        yield from_id(id_)


def get_all_centrals():
    for column in range(3, 5):
        for row in range(3, 5):
            yield Position(column, row)


def get_deltas():
    return Position(-1, 0), Position(1, 0), Position(0, -1), Position(0, 1)


def from_id(id_):
    return Position(id_ % 8, int(id_ / 8))


def from_text(position):
    if len(position) != 2:
        raise ValueError("Invalid syntax")

    return Position("abcdefgh".index(position[0]), int(position[1]) - 1)
