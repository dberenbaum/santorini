import math
import random
import collections
import numpy as np

import cnn
from core import Game, Player, InvalidPlayError
from serialize import Tree


C = math.sqrt(2)  # Exploration parameter.
E = 0.05  # Epsilon greedy exploration parameter.
PLAYOUTS = 500  # Simulation playouts for Monte Carlo Tree Search.


class AIPlayer(Player):
    def __init__(self, name, pawns=None, tree=Tree(), lazy=False, debug=False):
        self.tree = tree
        self.lazy = lazy
        self.debug = debug
        super().__init__(name, pawns=pawns)

    def turn_options(self, game):
        state = game.compact_state()
        if self.lazy:
            try:
                options = self.tree[state]["options"]
            except KeyError:
                options = super().turn_options(game)
                self.tree.set_options(state, options)
        else:
            options = super().turn_options(game)
        if self.debug:
            for new_state, winner in options:
                game.set_state(new_state)
                game.print_state()
                try:
                    print(self.tree.dict[new_state])
                except KeyError:
                    print("No dict info")
            game.set_state(state)
        return options

    def select_func(self, options):
        states = []
        values = []
        for state, winner in options:
            if winner:
                return state
            states.append(state)
        return self.policy_func(states)

    def value_func(self, state):
        """Win probability."""
        val = None
        try:
            n = self.tree[state]["tries"]
            w = self.tree[state]["wins"]
            if n:
                val = w/n
        except KeyError:
            pass
        return val

    def policy_func(self, states):
        """Greedy."""
        max_val = 0
        selection = states[0]
        for state in states:
            val = self.value_func(state)
            if val and (val > max_val):
                selection = state
                max_val = val
        return selection


class RandomPlayer(AIPlayer):
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


class EpsilonGreedyPlayer(AIPlayer):
    def __init__(self, name, e=E, **kwargs):
        self.e = e
        super().__init__(name, **kwargs)

    def policy_func(self, states):
        if random.random() < self.e:
            random.shuffle(states)
            selection = states[0]
            return selection
        return super().policy_func(states)


class UCTPlayer(AIPlayer):
    def __init__(self, name, c=C, **kwargs):
        self.c = c
        super().__init__(name, **kwargs)

    def policy_func(self, states):
        total = 0
        max_uct = 0
        selection = None
        state_dict = {}
        untried_states = []
        for state in states:
            val = self.value_func(state)
            if val:
                n = self.tree[state]["tries"]
                total += n
                state_dict[state] = {"val": val, "n": n}
            else:
                untried_states.append(state)
        if untried_states:
            return self.untried_policy(untried_states)
        for state in state_dict:
            val = state_dict[state]["val"]
            n = state_dict[state]["n"]
            uct = val+math.pow(1.0*math.log(total)/n, 1/self.c)
            if uct > max_uct:
                selection = state
                max_uct = uct
        return selection

    def untried_policy(self, states):
        return states[0]


class MCTSPlayer(AIPlayer):
    def __init__(self, name, c=C, playouts=PLAYOUTS, **kwargs):
        self.c = c
        self.playouts = playouts
        super().__init__(name, **kwargs)

    def tree_sim(self, state, player_names):
        players = []
        for name in player_names:
            players.append(UCTPlayer(name, tree=self.tree, c=self.c))
        game = Game(players)
        game.set_state(state)
        for player in game.play():
            yield game

    def random_sim(self, state, player_names):
        players = []
        for name in player_names:
            players.append(RandomPlayer(name, tree=self.tree))
        game = Game(players)
        game.set_state(state)
        game.next_player()
        for player in game.play():
            pass
        return game.winner().name

    def search(self, game):
        orig_state = game.compact_state()
        orig_player_names = [player.name for player in game.turns]
        # simulate playouts
        for _ in range(self.playouts):
            states = []
            # choose_uct until reaching untried state or end
            for sim in self.tree_sim(orig_state, orig_player_names):
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
                winner_name = self.random_sim(states[-1][1], sim_player_names)
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

    def policy_func(self, states):
        # act greedily
        return super().policy_func(states)


class ThompsonSamplingPlayer(AIPlayer):
    def value_func(self, state):
        val = None
        try:
            n = self.tree[state]["tries"]
            w = self.tree[state]["wins"]
            if n:
                l = n - w
                val = np.random.beta(w+1, l+1)
        except KeyError:
            pass
        return val


class CNNPlayer(ThompsonSamplingPlayer):
    def __init__(self, name, model=None, **kwargs):
        self.model = model
        if not self.model:
            self.model = cnn.load_model()
        super().__init__(name, **kwargs)

    def policy_func(self, states):
        max_val = 0
        selection = None
        untried_states = []
        for state in states:
            val = self.value_func(state)
            if not val:
                untried_states.append(state)
            elif val > max_val:
                selection = state
                max_val = val
        if untried_states:
            return cnn.max_state(untried_states, self.model)
        return selection


class UctCnnPlayer(UCTPlayer):
    def __init__(self, name, c=C, model=None, **kwargs):
        self.model = model
        if not self.model:
            self.model = cnn.load_model()
        super().__init__(name, c=c, **kwargs)

    def untried_policy(self, states):
        return cnn.max_state(states, self.model)


class MctsCnnPlayer(MCTSPlayer):
    def __init__(self, name, model=None, **kwargs):
        self.model = model
        if not self.model:
            self.model = cnn.load_model()
        super().__init__(name, **kwargs)

    def tree_sim(self, state, player_names):
        players = []
        for name in player_names:
            players.append(CNNPlayer(name, tree=self.tree, model=self.model))
        game = Game(players)
        game.set_state(state)
        for player in game.play():
            yield game
