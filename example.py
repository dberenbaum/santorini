import random

import core
import human_play
import random_play

x = human_play.HumanPlayer("x", (core.Pawn(), core.Pawn()))
o = random_play.RandomPlayer("o", (core.Pawn(), core.Pawn()))
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
