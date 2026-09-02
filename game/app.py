import pygame

from game import settings
from game.states.menu_state import MenuState


class App:
    """
    Owns the window, the clock, and the current game state.
    States handle their own events/update/draw; App just drives the loop
    and swaps states when one requests it.
    """

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(settings.TITLE)
        self.screen = pygame.display.set_mode(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        )
        self.clock = pygame.time.Clock()
        self.running = True

        # Start on the menu. Each state gets a reference back to the app
        # so it can call self.app.change_state(...) or self.app.quit().
        self.state = MenuState(self)

    def change_state(self, new_state):
        self.state = new_state

    def quit(self):
        self.running = False

    def run(self):
        while self.running:
            dt = self.clock.tick(settings.FPS) / 1000.0  # seconds since last frame

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit()

            self.state.handle_events(events)
            self.state.update(dt)
            self.state.draw(self.screen)

            pygame.display.flip()

        pygame.quit()
