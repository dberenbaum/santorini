from core import Player


class HumanPlayer(Player):

    def setup(self, game):
        for pawn in self.pawns:
            self.active_pawn = pawn
            options = pawn.placement_options(game)
            print("Select placement option by number:")
            for i, option in enumerate(options):
                print("{:d}. {:s}".format(i, str(option)))
            choice = None
            while not choice:
                try:
                    choice = options[int(input())]
                except (IndexError, ValueError):
                    pass
            self.place(choice)

    def turn(self, game):
        options = self.turn_options(game)
        print("Select (from --> to + build) option by number:")
        for i, (pawn, move, build) in enumerate(options):
            print("{:d}. {:s} --> {:s} + {:s}".format(i,
                str(pawn.space), str(move), str(build)))
        try:
            choice = None
            while not choice:
                try:
                    choice = options[int(input())]
                except (IndexError, ValueError):
                    print("Invalid choice.")
                    pass
            self.active_pawn = choice[0]
            self.move(choice[1])
            if choice[2]:
                self.build(choice[2])
        except IndexError:
            game.turns.remove(self)
