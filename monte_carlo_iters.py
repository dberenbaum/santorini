import multiprocessing

import click

import core
import monte_carlo
import random
import serialize
from serialize_factory import serializer_factory


def play(i, format, explore_param):
    print("Playing game %d" % i)
    with serializer_factory.get_serializer(format) as tree:
        x = monte_carlo.MonteCarloPlayer("x", (core.Pawn(), core.Pawn()), tree,
                c=explore_param)
        o = monte_carlo.MonteCarloPlayer("o", (core.Pawn(), core.Pawn()), tree,
                c=explore_param)
        players = [x, o]
        random.shuffle(players)
        game = core.Game(players)
        serialize.record_play(game, tree)


@click.command()
@click.argument("n", type=int)
@click.option("--format", "-f", "format", default=None)
@click.option("--explore", "-e", "explore_param", default=monte_carlo.C)
@click.option("--processes", "-p", default=1)
def main(n, format, explore_param, processes):
    args = [(i, format, explore_param) for i in range(n)]
    pool = multiprocessing.Pool(processes)
    pool.starmap(play, args)


if __name__ == '__main__':
    main()
