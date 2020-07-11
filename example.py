import random

import click

import core
from factory import player_factory, serializer_factory


@click.command()
@click.option("-f", "format")
def play(format):
    with serializer_factory.get_serializer(format) as tree:
        x = player_factory.get_player("human", "x")
        o = player_factory.get_player("mcts", "o", tree=tree, playouts=100)
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
