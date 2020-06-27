import random

from core import Player


class RandomPlayer(Player):

    def __init__(self, name, pawns):
        super().__init__(name=name, pawns=pawns, select_func=random.choice)
