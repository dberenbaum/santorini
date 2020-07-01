import random

from core import Player


class RandomPlayer(Player):

    def select_func(self, options):
        return random.choice(options)
