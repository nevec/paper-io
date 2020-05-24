from dataclasses import dataclass
from enum import IntEnum, auto
from pickle import loads, dumps
from typing import Any
import socket


class Cell(IntEnum):
    FREE = auto()
    BASE_PLAYER_1 = auto()
    BASE_PLAYER_2 = auto()
    PATH_PLAYER_1 = auto()
    PATH_PLAYER_2 = auto()


@dataclass
class Player:
    x: int
    y: int


@dataclass
class GameBoard:
    width: int
    height: int
    player_1: Player
    player_2: Player


def read_object(conn: socket.socket) -> Any:
    buffer = bytearray()
    bufsize = 1024
    while True:
        data = conn.recv(bufsize)
        if len(data) == 0:
            raise EOFError("expected data from server")
        buffer.extend(data)
        if buffer[-2:] == b"\r\n":
            break
    return loads(buffer[:-2])


def write_object(obj: Any, conn: socket.socket) -> None:
    dump = dumps(obj)
    conn.sendall(dump + b"\r\n")
