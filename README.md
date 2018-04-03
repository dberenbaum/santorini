# Santorini board game

To simulate a random game:

    from game import Game, Pawn, Player
    from random_play import RandomPlayer
    from serialize import record_play
    x = RandomPlayer("x", (Pawn(), Pawn()))
    o = RandomPlayer("o", (Pawn(), Pawn()))
    players = (x, o)
    game = Game(players)
    record_play(game, debug=True)
