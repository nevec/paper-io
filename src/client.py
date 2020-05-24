import socket
import pygame
from pygame.locals import *
from pygame.color import THECOLORS

from utils import read_object, write_object

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800


class GameClient:
    def __init__(self, hostname, port):
        self.client = socket.create_connection((hostname, port))

    def _prepare_gui(self):
        pygame.init()
        self.canvas: pygame.Surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

    def _run_event_loop(self):
        while True:
            canvas, green_player, blue_player = read_object(self.client)
            pygame.surfarray.pixels3d(self.canvas)[:, :] = canvas

            if green_player and blue_player:
                pygame.draw.rect(self.canvas, THECOLORS["green"],
                             pygame.Rect(green_player.x * 5, green_player.y * 5, 15, 15))
                pygame.draw.rect(self.canvas, THECOLORS["blue"], pygame.Rect(blue_player.x * 5, blue_player.y * 5, 15, 15))

            if pygame.event.get(eventtype=QUIT) or pygame.key.get_pressed()[K_ESCAPE]:
                return
            self._process_keyboard_events()

            pygame.display.flip()
            self.clock.tick(30)

    def _process_keyboard_events(self):
        move = ""
        keys = pygame.key.get_pressed()
        if keys[K_w]:
            move = "up"
        elif keys[K_a]:
            move = "left"
        elif keys[K_d]:
            move = "right"
        elif keys[K_s]:
            move = "down"
        write_object(move, self.client)

    def play(self):
        try:
            self._prepare_gui()
            self._run_event_loop()
        except (ConnectionError, EOFError):
            pass
        finally:
            print("bye")
            self.client.close()
            pygame.quit()


def main():
    game = GameClient("127.0.0.1", 22000)
    game.play()


if __name__ == "__main__":
    main()
