class BaseState:
    """
    Every screen (menu, playing, paused, game-over...) implements this.
    Keeps App dumb: it just calls these three methods every frame.
    """

    def __init__(self, app):
        self.app = app

    def handle_events(self, events):
        raise NotImplementedError

    def update(self, dt):
        raise NotImplementedError

    def draw(self, screen):
        raise NotImplementedError
