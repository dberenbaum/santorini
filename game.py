import collections
import itertools


class Space(object):
    """Board space."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.level = 0
        self.player = None

    def __str__(self):
        return "{:s}{:d}".format(chr(self.x+65), self.y)

    def is_adjacent(self, space):
        if self == space:
            return False
        if abs(self.x - space.x) > 1:
            return False
        if abs(self.y - space.y) > 1:
            return False
        return True


class Game(object):

    def __init__(self, players, size=5, tree=None):
        self.size = size
        self.board = [Space(x, y) for y in range(self.size) for x in range(self.size)]
        self.players = list(players)
        if tree:
            self.tree = tree
        else:
            self.tree = {}
        self.reset()

    def reset(self):
        for space in self.board:
            space.level = 0
            space.player = None
        self.turns = collections.deque(self.players)
        for player in self.players:
            player.reset()

    def play(self):
        for player in self.players:
            player.setup(self)
            yield self.next_player()
        while not self.winner():
            self.active_player().turn(self)
            yield self.next_player()

    def active_player(self):
        return self.turns[0]

    def next_player(self):
        self.turns.rotate(-1)
        return self.turns[0]

    def set_turn(self, player):
        player_turn = self.turns.index(player)
        self.turns.rotate(-player_turn)

    def winner(self):
        if len(self.turns) == 1:
            return self.turns[0]
        for player in self.players:
            if player.winner:
                return player
        return None

    def print_state(self):
        for space in self.board:
            if not space.x:
                print("\n|", end="")
            player = space.player or ""
            print("{:d} {:1.1s}|".format(space.level, str(player)), end="")
        print("\n")

    def compact_state(self):
        board_state = [str(s.level) for s in self.board]
        active_num = self.players.index(self.active_player())
        num_players = len(self.players)
        for s in self.board:
            if s.player:
                rel_num = (self.players.index(s.player) - active_num) \
                        % num_players + 1
            else:
                rel_num = 0
            board_state.append(rel_num)
        return "".join(str(i) for i in board_state)

    def set_state(self, state):
        active_player = self.active_player()
        self.reset()
        self.set_turn(active_player)
        levels = state[:self.size**2]
        playernums = state[self.size**2:]
        for space, level, playernum in zip(self.board, levels, playernums):
            space.level = int(level)
            playernum = int(playernum)
            if playernum:
                space.player = self.turns[playernum - 1]
                for pawn in space.player.pawns:
                    if not pawn.space:
                        pawn.space = space
                        break
            else:
                space.player = None


class Player(object):

    def __init__(self, name, pawns):
        self.name = name
        self.pawns = pawns
        self.reset()

    def reset(self):
        self.active_pawn = None
        self.winner = False
        for pawn in self.pawns:
            pawn.reset()

    def __str__(self):
        return str(self.name)

    def place(self, space):
        if not self.active_pawn.valid_placement(space):
            raise InvalidPlayError
        space.player = self
        self.active_pawn.space = space

    def move(self, space):
        if not self.active_pawn.valid_move(space):
            raise InvalidPlayError
        if space.level == 3 and self.active_pawn.space.level < 3:
            self.winner = True
        self.active_pawn.space.player = None
        self.active_pawn.space = space
        space.player = self

    def build(self, space):
        if not self.active_pawn.valid_build(space):
            raise InvalidPlayError
        space.level += 1

    def setup_options(self, game):
        pawn_options = [p.placement_options(game) for p in self.pawns]
        setup_options = []
        for setup_option in itertools.product(*pawn_options):
            if len(setup_option) == len(set(setup_option)):
                setup_options.append(setup_option)
        return setup_options

    def turn_options(self, game):
        options = []
        orig_pawn = self.active_pawn
        for pawn in self.pawns:
            self.active_pawn = pawn
            orig_space = pawn.space
            for move_space in pawn.move_options(game):
                self.move(move_space)
                for build_space in pawn.build_options(game):
                    options.append((pawn, move_space, build_space))
                move_space.player = None
                pawn.space = orig_space
                orig_space.player = self
        self.active_pawn = orig_pawn
        return options

    def setup(self, game):
        raise NotImplementedError

    def turn(self, game):
        raise NotImplementedError


class Pawn(object):

    def __init__(self):
        self.reset()

    def reset(self):
        self.space = None

    def valid_placement(self, space):
        if space.player:
            return False
        return True

    def valid_move(self, space):
        if not self.space.is_adjacent(space):
            return False
        if space.level > 3:
            return False
        if space.level - self.space.level > 1:
            return False
        if space.player:
            return False
        return True

    def valid_build(self, space, start=None):
        if not start:
            start = self.space
        if not start.is_adjacent(space):
            return False
        if space.level > 3:
            return False
        if space.player:
            return False
        return True

    def placement_options(self, game):
        return [space for space in game.board if self.valid_placement(space)]

    def move_options(self, game):
        return [space for space in game.board if self.valid_move(space)]

    def build_options(self, game):
        return [space for space in game.board if self.valid_build(space)]


class InvalidPlayError(Exception):
    pass
