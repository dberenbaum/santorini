import multiprocessing

import click

import core
import monte_carlo
from factory import player_factory, serializer_factory


def play(i, format, explore_param):
    print("Playing game %d" % i)
    with serializer_factory.get_serializer(format) as tree:
        x = player_factory.get_player("monte_carlo", "x", tree=tree,
                                      c=explore_param)
        o = player_factory.get_player("monte_carlo", "o", tree=tree,
                                      c=explore_param)
        players = [x, o]
        game = core.Game(players)
        monte_carlo.record_play(game, tree)


@click.command()
@click.argument("n", type=int)
@click.option("--format", "-f", "format", default=None)
@click.option("--explore", "-e", "explore_param", default=monte_carlo.C)
@click.option("--processes", "-p", default=1)
def main(n, format, explore_param, processes):
    args = [(i, format, explore_param) for i in range(n)]
    if processes == 1:
        for arg in args:
            play(*arg)
    else:
        pool = multiprocessing.Pool(processes)
        pool.starmap(play, args)


if __name__ == '__main__':
    main()
