import math
import random

from core import Game, Player
from serialize import Tree
from random_play import RandomPlayer


C = math.sqrt(2)  # Exploration parameter.
E = 0.00  # Epsilon greedy exploration parameter.
PLAYOUTS = 100  # Simulation playouts for Monte Carlo Tree Search.


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


def choose_epsilon_greedy(options, tree, e=E):
    random.shuffle(options)
    selection = options[0]
    if random.random() < e:
        return selection
    tree_nodes = []
    for state in options:
        try:
            n = tree[state]["tries"]
            w = tree[state]["wins"]
            tree_nodes.append((state, n, w))
        except KeyError:
            pass
    max_val = 0
    for state, n, w in tree_nodes:
        if n:
            val = w/n
            if val >= max_val:
                selection = state
                max_val = val
    return selection


def tree_sim(state, tree, c=C):
    players = (MonteCarloPlayer("x", tree=tree, c=c),
               MonteCarloPlayer("o", tree=tree, c=c))
    game = Game(players)
    game.set_state(state)
    game.next_player()
    for player in game.play():
        state = game.compact_state()
        yield (player, game.compact_state())
        if (state not in tree) or (not tree[state]["tries"]):
            tree.insert_state(state)
            tree.add_try(state)
            return
        else:
            tree.add_try(state)



def random_sim(state):
    players = (RandomPlayer("x"), RandomPlayer("o"))
    game = Game(players)
    game.set_state(state)
    game.next_player()
    for player in game.play():
        pass
    if game.winner().name == "x":
        return True
    return False


class EpsilonGreedyPlayer(Player):
    def __init__(self, name, pawns=None, tree=Tree(), e=E):
        self.tree = tree
        self.e = e
        super().__init__(name=name, pawns=pawns)

    def select_func(self, options):
        return choose_epsilon_greedy(options, self.tree, self.e)


class MonteCarloPlayer(Player):

    def __init__(self, name, pawns=None, tree=Tree(), c=C):
        self.tree = tree
        self.c = c
        super().__init__(name=name, pawns=pawns)

    def select_func(self, options):
        return choose_uct(options, self.tree, self.c)


class MCTSPlayer(Player):

    def __init__(self, name, pawns=None, tree=Tree(), c=C, playouts=PLAYOUTS):
        self.tree = tree
        self.c = c
        self.playouts = playouts
        super().__init__(name=name, pawns=pawns)

    def select_func(self, options):
        # simulate playouts
        for playout in range(self.playouts):
            root = choose_uct(options, tree=self.tree, c=self.c)
            if root not in self.tree:
                self.tree.insert_state(root)
                self.tree.add_try(root)
            our_states = [root]
            their_states = []
            # choose_uct until reaching untried state or end
            for player, state in tree_sim(root, self.tree, c=self.c):
                if player.name == "x":
                    our_states.append(state)
                else:
                    their_states.append(state)
            # if untried state, random playout from leaf
            win = random_sim(state)
            # update tree for all states from root option to leaf
            if win ^ (player.name == "o"):
                for state in our_states:
                    self.tree.add_win(state)
            else:
                for state in their_states:
                    self.tree.add_win(state)
        # act greedily
        return choose_epsilon_greedy(options, self.tree, e=0)


def record_play(g, tree, debug=False):
    moves = {p: [] for p in g.players}
    for player in g.play():
        state = g.compact_state()
        moves[player].append(state)
        if state not in tree:
            tree.insert_state(state)
        tree.add_try(state)
        if debug:
            g.print_state()
    winner = g.winner()
    for move in moves[winner]:
        tree.add_win(move)
