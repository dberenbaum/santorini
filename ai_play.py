import math
import random
import collections

from core import Game, Player, InvalidPlayError
from serialize import Tree


C = math.sqrt(2)  # Exploration parameter.
E = 0.00  # Epsilon greedy exploration parameter.
PLAYOUTS = 500  # Simulation playouts for Monte Carlo Tree Search.


def choose_uct(options, tree, c=C):
    tree_nodes = []
    total = 0
    untried_state = None
    for state, winner in options:
        if winner:
            return state
        try:
            n = tree[state]["tries"]
            w = tree[state]["wins"]
            tree_nodes.append((state, n, w))
            total += n
        except KeyError:
            untried_state = state
    if untried_state:
        return untried_state
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
    if random.random() < e:
        random.shuffle(options)
        selection = options[0][0]
        return selection
    max_val = 0
    for state, winner in options:
        if winner:
            return state
        try:
            n = tree[state]["tries"]
            w = tree[state]["wins"]
            if n:
                val = w/n
                if val >= max_val:
                    selection = state
                    max_val = val
        except KeyError:
            pass
    return selection


def tree_sim(state, tree=Tree(), c=C, player_names=[]):
    players = []
    for name in player_names:
        players.append(MonteCarloPlayer(name, tree=tree, c=c))
    game = Game(players)
    game.set_state(state)
    for player in game.play():
        yield game


def random_sim(state, tree=Tree(), player_names=[]):
    players = []
    for name in player_names:
        players.append(RandomPlayer(name, tree=tree))
    game = Game(players)
    game.set_state(state)
    game.next_player()
    for player in game.play():
        pass
    return game.winner().name


class LazyPlayer(Player):
    def __init__(self, name, pawns=None, tree=Tree(), lazy=False):
        self.tree = tree
        self.lazy = lazy
        super().__init__(name, pawns=pawns)

    def turn_options(self, game):
        state = game.compact_state()
        if self.lazy:
            try:
                return self.tree[state]["options"]
            except KeyError:
                options = super().turn_options(game)
                self.tree.set_options(state, options)
                return options
        else:
            return super().turn_options(game)


class RandomPlayer(LazyPlayer):
    def setup(self, game):
        for pawn in self.pawns:
            self.active_pawn = pawn
            choices = pawn.placement_options(game)
            space = random.choice(choices)
            self.place(space)

    def turn(self, game):
        pawns = list(self.pawns).copy()
        random.shuffle(pawns)
        for pawn in pawns:
            self.active_pawn = pawn
            spaces = game.board.copy()
            random.shuffle(spaces)
            moved = False
            for move_space in spaces:
                try:
                    self.move(move_space)
                    if self.winner:
                        return
                    moved = True
                    break
                except InvalidPlayError:
                    pass
            if moved:
                for build_space in spaces:
                    try:
                        self.build(build_space)
                        return
                    except InvalidPlayError:
                        pass
        game.turns.remove(self)


class EpsilonGreedyPlayer(LazyPlayer):
    def __init__(self, name, pawns=None, tree=Tree(), e=E):
        self.e = e
        super().__init__(name, pawns=pawns, tree=tree)

    def select_func(self, options):
        return choose_epsilon_greedy(options, self.tree, self.e)


class MonteCarloPlayer(LazyPlayer):

    def __init__(self, name, pawns=None, tree=Tree(), c=C):
        self.c = c
        super().__init__(name, pawns=pawns, tree=tree)

    def select_func(self, options):
        return choose_uct(options, self.tree, self.c)


class MCTSPlayer(LazyPlayer):

    def __init__(self, name, pawns=None, tree=Tree(), c=C, playouts=PLAYOUTS):
        self.c = c
        self.playouts = playouts
        super().__init__(name, pawns=pawns, tree=tree)

    def search(self, game):
        orig_state = game.compact_state()
        orig_player_names = [player.name for player in game.turns]
        # simulate playouts
        for _ in range(self.playouts):
            states = []
            # choose_uct until reaching untried state or end
            for sim in tree_sim(orig_state, self.tree, self.c,
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
                winner_name = random_sim(states[-1][1], self.tree,
                                         sim_player_names)
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
