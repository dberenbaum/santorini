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
@click.option("--conn", "conn_str", default=CONN_STR)
@click.option("--explore", "explore_param", default=monte_carlo.C)
def play(n, conn_str, explore_param):
    with mongo_serialize.MongoTree(conn_str) as tree:
        x = monte_carlo.MonteCarloPlayer("x", (core.Pawn(), core.Pawn()), tree,
                c=explore_param)
        o = monte_carlo.MonteCarloPlayer("o", (core.Pawn(), core.Pawn()), tree,
                c=explore_param)
        players = [x, o]
        random.shuffle(players)
        game = core.Game(players)
        for i, _ in enumerate(serialize.repeat_plays(game, tree, n=n)):
            print("%d games played" % i)


if __name__ == '__main__':
    play()
