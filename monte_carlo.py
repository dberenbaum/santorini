import math
import random

from core import Player


C = math.sqrt(2)  # Exploration parameter.


def choose_uct(options, tree, c=C):
    tree_nodes = []
    total = 0
    for state in options:
        try:
            n = tree[state]["tries"]
            w = tree[state]["wins"]
            tree_nodes.append((state, n, w))
            total += n
        except KeyError:
            return state
    selection = None
    max_uct = 0
    for state, n, w in tree_nodes:
        uct = w/n+math.pow(1.0*math.log(total)/n, 1/c)
        if uct >= max_uct:
            selection = state
            max_uct = uct
    return selection


class MonteCarloPlayer(Player):

    def __init__(self, name, pawns, tree, c=C):
        super().__init__(name=name, pawns=pawns)
        self.tree = tree
        self.c = c

    def setup(self, game):
        options = []
        orig_state = game.compact_state()
        for option in self.setup_options(game):
            # Simulate each placement.
            self.place_pawns(option)
            state = game.compact_state()
            options.append(state)
            game.set_state(orig_state)
        selection = choose_uct(options, self.tree, c=self.c)
        game.set_state(selection)

    def place_pawns(self, spaces):
        for pawn, space in zip(self.pawns, spaces):
            self.active_pawn = pawn
            self.place(space)

    def turn(self, game):
        options = []
        orig_state = game.compact_state()
        for pawn, move_space, build_space in self.turn_options(game):
            # Simulate each placement.
            self.active_pawn = pawn
            self.move(move_space)
            if build_space:
                self.build(build_space)
                state = game.compact_state()
                options.append(state)
                game.set_state(orig_state)
            else:
                # Move without build means winning move.
                state = game.compact_state()
                options = [state]
                game.set_state(orig_state)
                break
        if options:
            selection = choose_uct(options, self.tree, c=self.c)
            game.set_state(selection)
        else:
            game.turns.remove(self)
