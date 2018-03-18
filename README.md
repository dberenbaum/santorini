# Santorini board game

To simulate a random game:

    from game import Game, Pawn, Player
    from random_play import RandomPlayer
    from serialize import record_play
    player_1 = RandomPlayer("x", (Pawn(), Pawn()))
    player_2 = RandomPlayer("o", (Pawn(), Pawn()))
    players = (player_1, player_2)
    game = Game(players)
    record_play(game, debug=True)
