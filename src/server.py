import logging
import pygame
import numpy as np
from pygame.time import Clock
from pygame.color import THECOLORS
from copy import deepcopy

from utils import *

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800


class GameServer:
    def __init__(self, hostname, port):
        self.server: socket.SocketType = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.server.bind((hostname, port))
        self.client_1: socket.SocketType = socket.socket()
        self.client_2: socket.SocketType = socket.socket()
        self.canvas: pygame.SurfaceType = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.board: np.ndarray = np.ones((WINDOW_WIDTH // 5, WINDOW_HEIGHT // 5), dtype=np.int8)
        pygame.font.init()
        self.font = pygame.font.Font("resources/Roboto-Regular.ttf", 24)
        self.win_text = self.font.render("YOU WIN", True, THECOLORS["black"])
        self.loose_text = self.font.render("YOU LOOSE", True, THECOLORS["black"])
        self.winner = None
        self.clock = Clock()

    def _wait_for_players(self):
        self.server.listen()
        self.client_1, address_1 = self.server.accept()
        logging.info(f"Joined {address_1}")
        self.client_2, address_2 = self.server.accept()
        logging.info(f"Joined {address_2}")

    def _run_game_loop(self):
        move_1 = "up"
        move_2 = "up"
        self.prev_1 = None
        self.prev_2 = None
        while True:
            write_object([pygame.surfarray.pixels3d(self.canvas), self.player_1, self.player_2], self.client_1)
            write_object([pygame.surfarray.pixels3d(self.canvas), self.player_1, self.player_2], self.client_2)

            new_move_1 = read_object(self.client_1)
            new_move_2 = read_object(self.client_2)

            # move_1 = new_move_1
            # move_2 = new_move_2
            move_1 = new_move_1 if new_move_1 else move_1
            move_2 = new_move_2 if new_move_2 else move_2

            if self.winner:
                break
            else:
                self.prev_1 = deepcopy(self.player_1)
                self.prev_2 = deepcopy(self.player_2)
                GameServer._process_moves(self.player_1, move_1)
                GameServer._process_moves(self.player_2, move_2)

                self._process_board()
            self.clock.tick(30)

        win_canvas = self.canvas.copy()
        loose_canvas = self.canvas.copy()
        win_canvas.blit(self.win_text, pygame.Rect(270, 350, 100, 50))
        loose_canvas.blit(self.loose_text, pygame.Rect(270, 350, 100, 50))

        while True:
            if self.winner == 1:
                write_object([pygame.surfarray.pixels3d(win_canvas), self.player_1, self.player_2], self.client_1)
                write_object([pygame.surfarray.pixels3d(loose_canvas), self.player_1, self.player_2], self.client_2)
            else:
                write_object([pygame.surfarray.pixels3d(loose_canvas), self.player_1, self.player_2], self.client_1)
                write_object([pygame.surfarray.pixels3d(win_canvas), self.player_1, self.player_2], self.client_2)
            self.clock.tick(30)

    def _get_player_values(self, player: Player) -> np.ndarray:
        return self.board[player.x: (player.x + 3), player.y: (player.y + 3)]

    @staticmethod
    def _get_center_of(player: Player) -> Player:
        return Player(player.x + 1, player.y + 1)

    def _process_board(self):

        value_1 = self.board[self.player_1.x + 1, self.player_1.y + 1]
        value_2 = self.board[self.player_2.x + 1, self.player_2.y + 1]

        if value_2 == Cell.PATH_PLAYER_1 or value_1 == Cell.BASE_PLAYER_2 or \
                (value_1 == Cell.PATH_PLAYER_1 and self.player_1 != self.prev_1):
            self.winner = 2
            return

        if value_1 == Cell.PATH_PLAYER_2 or value_2 == Cell.BASE_PLAYER_1 or \
                (value_2 == Cell.PATH_PLAYER_2 and self.player_2 != self.prev_2):
            self.winner = 1
            return

        if self.board[self.player_1.x + 1, self.player_1.y + 1] == Cell.FREE:
            self.board[self.player_1.x + 1, self.player_1.y + 1] = Cell.PATH_PLAYER_1
            pygame.draw.rect(self.canvas, THECOLORS["lightgreen"],
                             pygame.Rect(5 * self.player_1.x + 5, 5 * self.player_1.y + 5, 5, 5))

        if self.board[self.player_2.x + 1, self.player_2.y + 1] == Cell.FREE:
            self.board[self.player_2.x + 1, self.player_2.y + 1] = Cell.PATH_PLAYER_2
            pygame.draw.rect(self.canvas, THECOLORS["lightblue"],
                             pygame.Rect(5 * self.player_2.x + 5, 5 * self.player_2.y + 5, 5, 5))

        if value_1 == Cell.BASE_PLAYER_1:


    @staticmethod
    def _process_moves(player: Player, move: str):
        if move == "up":
            player.y -= 1
        elif move == "down":
            player.y += 1
        elif move == "left":
            player.x -= 1
        elif move == "right":
            player.x += 1

        if player.x < 0:
            player.x = 0
        if player.y < 0:
            player.y = 0
        if player.x > WINDOW_WIDTH // 5 - 3:
            player.x = WINDOW_WIDTH // 5 - 3
        if player.y > WINDOW_HEIGHT // 5 - 3:
            player.y = WINDOW_HEIGHT // 5 - 3

    def _init_ui(self):
        self.canvas.fill(THECOLORS["white"])
        pygame.draw.rect(self.canvas, THECOLORS["darkgreen"], pygame.Rect(150, 300, 50, 50))
        pygame.draw.rect(self.canvas, THECOLORS["darkblue"], pygame.Rect(550, 300, 50, 50))
        self.board[30:40, 60:70] = Cell.BASE_PLAYER_1
        self.board[110:120, 60:70] = Cell.BASE_PLAYER_2
        self.player_1 = Player(30, 60)
        self.player_2 = Player(110, 60)

    def start_serving(self):
        try:
            self._wait_for_players()
            self._init_ui()
            self._run_game_loop()
        except (ConnectionError, EOFError):
            pass
        finally:
            self.server.close()
            self.client_1.close()
            self.client_2.close()


def main():
    logging.basicConfig(level=logging.INFO)
    while True:
        try:
            logging.info("Starting.....")
            game = GameServer("localhost", 22000)
            game.start_serving()
            logging.info("Game has ended")
        except KeyboardInterrupt:
            break
    logging.info("Bye")


if __name__ == '__main__':
    main()
