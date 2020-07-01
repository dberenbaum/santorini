import collections
import itertools


def xchar(x):
    """Convert x coordinate to character representation."""
    return chr(x+65)


class Space(object):
    """Board space."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.level = 0
        self.player = None

    def __str__(self):
        return "{:s}{:d}".format(xchar(self.x), self.y+1)

    def is_adjacent(self, space):
        if self == space:
            return False
        if abs(self.x - space.x) > 1:
            return False
        if abs(self.y - space.y) > 1:
            return False
        return True


class Game(object):

    def __init__(self, players, size=3):
        self.size = size
        self.board = [Space(x, y) for y in range(self.size) for x in range(self.size)]
        self.players = list(players)
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
            if not player.setup_check():
                player.setup(self)
                yield self.active_player()
                self.next_player()
        while not self.winner():
            self.active_player().turn(self)
            yield self.active_player()
            self.next_player()

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
        print("  " + "   ".join([xchar(i) for i in range(self.size)]), end="")
        for space in self.board:
            if not space.x:
                print("\n{:d}|".format(space.y+1), end="")
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

        vec_level = np.vectorize(level)
        level_state = vec_level(self.board)
        vec_player = np.vectorize(player)
        player_state = vec_player(self.board)
        board_state = np.concatenate([level_state, player_state])
        board_str = np.array2string(board_state, separator="")[1:-1]
        return board_str

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


class Player(object):

    def __init__(self, name, pawns=None):
        self.name = name
        if not pawns:
            pawns = (Pawn(), Pawn())
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
            raise InvalidPlayError("Invalid placement: {:s}".format(str(space)))
        space.player = self
        self.active_pawn.space = space

    def move(self, space):
        if not self.active_pawn.valid_move(space):
            raise InvalidPlayError("Invalid move: {:s}".format(str(space)))
        if space.level == 3 and self.active_pawn.space.level < 3:
            self.winner = True
        self.active_pawn.space.player = None
        self.active_pawn.space = space
        space.player = self

    def build(self, space):
        if not self.active_pawn.valid_build(space):
            raise InvalidPlayError("Invalid build: {:s}".format(str(space)))
        space.level += 1

    def setup_options(self, game):
        pawn_options = [p.placement_options(game) for p in self.pawns]
        setup_options = []
        orig_state = game.compact_state()
        for setup_option in itertools.product(*pawn_options):
            if len(setup_option) == len(set(setup_option)):
                self.place_pawns(setup_option)
                state = game.compact_state()
                setup_options.append(state)
                game.set_state(orig_state)
        return list(set(setup_options))

    def place_pawns(self, spaces):
        for pawn, space in zip(self.pawns, spaces):
            self.active_pawn = pawn
            self.place(space)

    def turn_options(self, game):
        options = []
        orig_pawn = self.active_pawn
        for pawn in self.pawns:
            self.active_pawn = pawn
            orig_space = pawn.space
            for move_space in pawn.move_options(game):
                self.move(move_space)
                if self.winner:
                    state = game.compact_state()
                    options.append(state)
                    self.winner = False
                else:
                    for build_space in pawn.build_options(game):
                        self.build(build_space)
                        state = game.compact_state()
                        options.append(state)
                        build_space.level -= 1
                move_space.player = None
                pawn.space = orig_space
                orig_space.player = self
        self.active_pawn = orig_pawn
        return list(set(options))

    def setup(self, game):
        options = self.setup_options(game)
        selection = self.select_func(options)
        game.set_state(selection)

    def setup_check(self):
        for pawn in self.pawns:
            if not pawn.space:
                return False
        return True

    def turn(self, game):
        options = self.turn_options(game)
        if options:
            selection = self.select_func(options)
            game.set_state(selection)
        else:
            game.turns.remove(self)

    def select_func(self, options):
        raise NotImplementedError


class InvalidPlayError(Exception):
    pass
