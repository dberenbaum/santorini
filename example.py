import random

import click

import core
import human_play
import monte_carlo
import mongo_serialize


CONN_STR = "mongodb://localhost:27017/"

@click.command()
@click.option("-c", "conn_str", default=CONN_STR)
def play(conn_str=CONN_STR):
    with mongo_serialize.MongoTree(conn_str) as tree:
        x = human_play.HumanPlayer("x", (core.Pawn(), core.Pawn()))
        o = monte_carlo.MonteCarloPlayer("o", (core.Pawn(), core.Pawn()), tree)
        print("You are player x.")
        players = [x, o]
        random.shuffle(players)
        game = core.Game(players)
        print("Wait for data to load.")
        print("Player {:s} starts".format(str(players[0])))
        game.print_state()
        for player in game.play():
            game.print_state()
        print("Player {:s} has won!".format(str(game.winner())))


if __name__ == '__main__':
    play()
