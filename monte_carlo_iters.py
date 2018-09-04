import sys

import core
import monte_carlo
import random
import serialize
import mongo_serialize


n = int(sys.argv[1])  # Number of games to simulate.

with mongo_serialize.MongoTree("mongodb://localhost:9999/") as tree:
    x = monte_carlo.MonteCarloPlayer("x", (core.Pawn(), core.Pawn()), tree)
    o = monte_carlo.MonteCarloPlayer("o", (core.Pawn(), core.Pawn()), tree)
    players = [x, o]
    random.shuffle(players)
    game = core.Game(players)
    for i, _ in enumerate(serialize.repeat_plays(game, tree, n=n)):
        print("%d games played" % i)
