import math
import random
import collections

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


def tree_sim(state, tree, c=C, player_names=[]):
    players = []
    for name in player_names:
        players.append(MonteCarloPlayer(name, tree=tree, c=c))
    game = Game(players)
    game.set_state(state)
    for player in game.play():
        yield game


def random_sim(state, player_names=[]):
    players = []
    for name in player_names:
        players.append(RandomPlayer(name))
    game = Game(players)
    game.set_state(state)
    game.next_player()
    for player in game.play():
        pass
    return game.winner().name


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

    def search(self, game):
        orig_state = game.compact_state()
        orig_player_names = [player.name for player in game.turns]
        # simulate playouts
        for _ in range(self.playouts):
            states = []
            # choose_uct until reaching untried state or end
            for sim in tree_sim(orig_state, self.tree, self.c,
                    orig_player_names):
                player = sim.active_player().name
                sim_state = sim.compact_state()
                states.append((player, sim_state))
                self.tree.add_try(sim_state)
                if self.tree[sim_state]["tries"] == 1:
                    break
            # if untried state, random playout from leaf
            winner = sim.winner()
            if not winner:
                sim_player_names = [player.name for player in sim.turns]
                winner = random_sim(states[-1][1], sim_player_names)
            # update tree for all states from root option to leaf
            for player, state in states:
                if winner == player:
                    self.tree.add_win(state)

    def setup_options(self, game):
        self.search(game)
        return super().setup_options(game)

    def turn_options(self, game):
        self.search(game)
        return super().turn_options(game)

    def select_func(self, options):
        if "write" in dir(self.tree):
            self.tree.write()
        # act greedily
        return choose_epsilon_greedy(options, self.tree, e=0)
