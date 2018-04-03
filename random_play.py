import random

from game import Player


class RandomPlayer(Player):

    def setup(self, game):
        for pawn in self.pawns:
            self.active_pawn = pawn
            choices = pawn.placement_options(game)
            space = random.choice(choices)
            self.place(space)

    def turn(self, game):
        options = self.turn_options(game)
        try:
            pawn, move_space, build_space = random.choice(options)
            self.active_pawn = pawn
            self.move(move_space)
            if build_space:
                self.build(build_space)
        except IndexError:
            game.turns.remove(self)
