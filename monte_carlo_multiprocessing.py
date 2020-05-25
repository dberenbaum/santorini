import multiprocessing

import click

import core
import monte_carlo
import random
import serialize
import mongo_serialize


CONN_STR = "mongodb://localhost:27017/"


def play(i, conn_str, explore_param):
    print("Playing game %d" % i)
    with mongo_serialize.MongoTree(conn_str) as tree:
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
@click.option("--conn", "conn_str", default=CONN_STR)
@click.option("--explore", "explore_param", default=monte_carlo.C)
@click.option("--processes", "-p", default=1)
def main(n, conn_str, explore_param, processes):
    args = [(i, conn_str, explore_param) for i in range(n)]
    pool = multiprocessing.Pool(processes)
    pool.starmap(play, args)


if __name__ == '__main__':
    main()
