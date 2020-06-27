import math
import random

from core import Player
from serialize import Tree


C = math.sqrt(2)  # Exploration parameter.


def choose_uct(options, tree, c=C):
    tree_nodes = []
    total = 0
    random.shuffle(options)
    for state in options:
        try:
            n = tree[state]["tries"]
            w = tree[state]["wins"]
            tree_nodes.append((state, n, w))
            total += n
        except KeyError:
            return state
    max_uct = 0
    selection = None
    for state, n, w in tree_nodes:
        if not n:
            return state
        else:
            uct = w/n+math.pow(1.0*math.log(total)/n, 1/c)
        if uct >= max_uct:
            selection = state
            max_uct = uct
    return selection


class MonteCarloPlayer(Player):

    def __init__(self, name, pawns, tree=Tree(), c=C):
        self.tree = tree
        self.c = c
        select_func = lambda options: choose_uct(options, self.tree, c=self.c)
        super().__init__(name=name, pawns=pawns, select_func=select_func)
