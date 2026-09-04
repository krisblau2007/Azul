from game import settings


class Player:
    """
    One player's identity plus their board state. The board has three
    parts:
      - color_grid_marks: COLOR_GRID_SIZE x COLOR_GRID_SIZE booleans —
        the right-hand grid. Its cell *colors* are fixed (see
        settings.color_grid_color); marks just track which have been
        toggled.
      - pyramid_marks: a list of PYRAMID_ROWS rows, where row i has
        (i + 1) booleans — the left-hand grid (1 cell in row 0, up to
        PYRAMID_ROWS cells in the last row).
      - bottom_row_marks: one boolean per entry in
        settings.BOTTOM_ROW_LABELS — the labeled row along the bottom.
    This class only holds state; PlayState decides when a cell is
    allowed to be toggled (only on the active player's turn).
    """

    def __init__(self, index, name, color):
        self.index = index
        self.name = name
        self.color = color

        self.color_grid_marks = [
            [False for _ in range(settings.COLOR_GRID_SIZE)]
            for _ in range(settings.COLOR_GRID_SIZE)
        ]
        self.pyramid_marks = [
            [False for _ in range(row + 1)] for row in range(settings.PYRAMID_ROWS)
        ]
        self.bottom_row_marks = [False for _ in settings.BOTTOM_ROW_LABELS]

    def toggle_color_cell(self, row, col):
        self.color_grid_marks[row][col] = not self.color_grid_marks[row][col]

    def toggle_pyramid_cell(self, row, col):
        self.pyramid_marks[row][col] = not self.pyramid_marks[row][col]

    def toggle_bottom_cell(self, col):
        self.bottom_row_marks[col] = not self.bottom_row_marks[col]
