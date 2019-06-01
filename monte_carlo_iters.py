import sys

import click

import core
import monte_carlo
import random
import serialize
import mongo_serialize


CONN_STR = "mongodb://localhost:27017/"

@click.command()
@click.argument("n", type=int)
def play(n, conn_str=CONN_STR):
    with mongo_serialize.MongoTree(conn_str) as tree:
        x = monte_carlo.MonteCarloPlayer("x", (core.Pawn(), core.Pawn()), tree)
        o = monte_carlo.MonteCarloPlayer("o", (core.Pawn(), core.Pawn()), tree)
        players = [x, o]
        random.shuffle(players)
        game = core.Game(players)
        for i, _ in enumerate(serialize.repeat_plays(game, tree, n=n)):
            print("%d games played" % i)


if __name__ == '__main__':
    play()
