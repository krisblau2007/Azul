from game import settings


class Player:
    """
    One player's identity plus their personal board. `marks` is a
    BOARD_ROWS x BOARD_COLS grid of booleans — True means that cell has
    been marked. This class only holds state; PlayState decides when a
    cell is allowed to be toggled (only on the active player's turn).
    """

    def __init__(self, index, name, color):
        self.index = index
        self.name = name
        self.color = color
        self.marks = [
            [False for _ in range(settings.BOARD_COLS)]
            for _ in range(settings.BOARD_ROWS)
        ]

    def toggle_cell(self, row, col):
        self.marks[row][col] = not self.marks[row][col]
