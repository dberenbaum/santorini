import multiprocessing

import click

import core
from factory import player_factory, serializer_factory


def play(i, format, ai, db):
    print("Playing game %d" % i)
    with serializer_factory.get_serializer(format, db=db) as tree:
        x = player_factory.get_player(ai, "x", tree=tree)
        o = player_factory.get_player(ai, "o", tree=tree)
        players = [x, o]
        game = core.Game(players)
        for turn in game.play():
            pass


@click.command()
@click.argument("n", type=int)
@click.option("--format", "-f", "format", default="mongo_bulk")
@click.option("--ai", default=None)
@click.option("--db", default=None)
@click.option("--processes", "-p", default=1)
def main(n, format, ai, db, processes):
    args = [(i, format, ai, db) for i in range(n)]
    if processes == 1:
        for arg in args:
            play(*arg)
    else:
        pool = multiprocessing.Pool(processes)
        pool.starmap(play, args)


if __name__ == '__main__':
    main()
