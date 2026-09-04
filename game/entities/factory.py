import random

from game import settings


class Factory:
    """
    One factory disc holding FACTORY_TILE_COUNT tiles. Each tile's
    color is chosen independently at random from the same 5-color
    palette used by the player boards' color grid
    (settings.COLOR_GRID_PALETTE) — unlike that grid's fixed diagonal
    pattern, factory tiles have no fixed arrangement. Colors are
    rolled once, when the factory is created.
    """

    def __init__(self, index):
        self.index = index
        self.tiles = [
            random.choice(settings.COLOR_GRID_PALETTE)
            for _ in range(settings.FACTORY_TILE_COUNT)
        ]

    def take_color(self, color):
        """
        Removes every tile matching `color` from this factory (the
        ones a player is taking) and empties the factory entirely,
        returning the tiles that were left over so the caller can move
        them to the center pool. Doesn't track who took the matching
        tiles — see the README for that as a next extension.
        """
        taken = [tile for tile in self.tiles if tile == color]
        remaining = [tile for tile in self.tiles if tile != color]
        self.tiles = []
        return taken, remaining
