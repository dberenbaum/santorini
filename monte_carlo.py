import math
import random
import collections

from core import Game, Player
from serialize import Tree


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


def tree_sim(state, tree, options={}, c=C, player_names=[]):
    players = []
    for name in player_names:
        players.append(MonteCarloPlayer(name, tree=tree, options=options, c=c))
    game = Game(players)
    game.set_state(state)
    for player in game.play():
        yield game


def random_sim(state, options={}, player_names=[]):
    players = []
    for name in player_names:
        players.append(RandomPlayer(name, options=options))
    game = Game(players)
    game.set_state(state)
    game.next_player()
    for player in game.play():
        pass
    return game.winner().name


class LazyPlayer(Player):
    def __init__(self, name, pawns=None, options={}):
        print("LazyPlayer __init__")
        self.options = options
        super().__init__(name, pawns=pawns)

    def turn_options(self, game):
        state = game.compact_state()
        try:
            return self.options[state]
        except KeyError:
            self.options[state] = super().turn_options(game)
            return self.options[state]


class RandomPlayer(LazyPlayer):

    def select_func(self, options):
        return random.choice(options)


class EpsilonGreedyPlayer(LazyPlayer):
    def __init__(self, name, pawns=None, options={}, tree=Tree(), e=E):
        self.tree = tree
        self.e = e
        super().__init__(name, pawns=pawns, options={})

    def select_func(self, options):
        return choose_epsilon_greedy(options, self.tree, self.e)


class MonteCarloPlayer(LazyPlayer):

    def __init__(self, name, pawns=None, options={}, tree=Tree(), c=C):
        self.tree = tree
        self.c = c
        super().__init__(name, pawns=pawns, options=options)

    def select_func(self, options):
        return choose_uct(options, self.tree, self.c)


class MCTSPlayer(LazyPlayer):

    def __init__(self, name, pawns=None, options={}, tree=Tree(), c=C, playouts=PLAYOUTS):
        print("MCTSPlayer __init__")
        self.tree = tree
        self.c = c
        self.playouts = playouts
        super().__init__(name, pawns=pawns, options=options)

    def search(self, game):
        orig_state = game.compact_state()
        orig_player_names = [player.name for player in game.turns]
        # simulate playouts
        for _ in range(self.playouts):
            states = []
            # choose_uct until reaching untried state or end
            for sim in tree_sim(orig_state, self.tree, self.options, self.c,
                    orig_player_names):
                player_name = sim.active_player().name
                sim_state = sim.compact_state()
                states.append((player_name, sim_state))
                self.tree.add_try(sim_state)
                if self.tree[sim_state]["tries"] == 1:
                    break
            # if untried state, random playout from leaf
            winner = sim.winner()
            if winner:
                winner_name = winner.name
            else:
                sim_player_names = [player.name for player in sim.turns]
                winner_name = random_sim(states[-1][1], sim_player_names)
            # update tree for all states from root option to leaf
            for player_name, state in states:
                if winner_name == player_name:
                    self.tree.add_win(state)

    def setup_options(self, game):
        self.search(game)
        return super().setup_options(game)

    def turn_options(self, game):
        self.search(game)
        return super().turn_options(game)

    def select_func(self, options):
        # act greedily
        return choose_epsilon_greedy(options, self.tree, e=0)
