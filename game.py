import itertools
import random


def random_play(debug=False):
    player_1 = Player("x", (Pawn(), Pawn()))
    player_2 = Player("o", (Pawn(), Pawn()))
    players = (player_1, player_2)
    game = Game(players)
    for player in players:
        for pawn in player.pawns:
            choices = pawn.placement_options(game)
            space = random.choice(choices)
            player.place(pawn, space)
    if debug:
        game.print_state()
    winner = None
    while not winner:
        player = game.next_player()
        move_space, build_space = None, None
        for pawn in random.sample(player.pawns, len(player.pawns)):
            move_choices = pawn.move_options(game)
            for move_space in random.sample(move_choices, len(move_choices)):
                build_choices = pawn.build_options(game, move_space)
                if build_choices:
                    build_space = random.choice(build_choices)
                    player.move(pawn, move_space)
                    player.build(pawn, build_space)
                    break
            if move_space and build_space:
                break
        if (not move_space) or (not build_space):
            winner = game.next_player()
        elif player.winner:
            winner = player
        if debug:
            game.print_state()
    return winner


class Space(object):
    """Board space."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.level = 0
        self.player = None

    def is_adjacent(self, space):
        if self == space:
            return False
        if abs(self.x - space.x) > 1:
            return False
        if abs(self.y - space.y) > 1:
            return False
        return True


class Game(object):

    def __init__(self, players, size=5):
        self.board = [Space(x, y) for y in range(size) for x in range(size)]
        self.players = players
        self.turns = itertools.cycle(players)

    def next_player(self):
        return next(self.turns)

    def print_state(self):
        for space in self.board:
            if not space.x:
                print("\n|", end="")
            player = space.player or ""
            print("{:d} {:1.1s}|".format(space.level, str(player)), end="")
        print("\n")


class Player(object):

    def __init__(self, name, pawns):
        self.name = name
        self.pawns = pawns
        self.winner = False

    def __str__(self):
        return str(self.name)

    def place(self, pawn, space):
        if not pawn.valid_placement(space):
            raise InvalidPlayError
        space.player = self
        pawn.space = space

    def move(self, pawn, space):
        if not pawn.valid_move(space):
            raise InvalidPlayError
        if space.level == 3 and pawn.space.level < 3:
            self.winner = True
        pawn.space.player = None
        pawn.space = space
        space.player = self

    def build(self, pawn, space):
        if not pawn.valid_build(space):
            raise InvalidPlayError
        space.level += 1


class Pawn(object):

    def __init__(self):
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

    def build_options(self, game, start=None):
        return [space for space in game.board if self.valid_build(space, start)]


class InvalidPlayError(Exception):
    pass
