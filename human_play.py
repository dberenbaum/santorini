from core import Player


class HumanPlayer(Player):

    def setup(self, game):
        for pawn in self.pawns:
            self.active_pawn = pawn
            placed = False
            while not placed:
                print("Enter grid space to place pawn:")
                try:
                    gridspace = input()
                    space = None
                    for sp in game.board:
                        if str(sp) == gridspace:
                            space = sp
                            break
                    self.place(space)
                    placed = True
                except Exception as e:
                    print(str(e))

    def turn(self, game):
        options = self.turn_options(game)
        pawn_selected = False
        while not pawn_selected:
            try:
                print("Enter grid space of pawn:")
                gridspace = input()
                for pawn in self.pawns:
                    if str(pawn.space) == gridspace:
                        self.active_pawn = pawn
                        pawn_selected = True
            except Exception as e:
                print(str(e))
        moved = False
        while not moved:
            try:
                print("Enter grid space to move pawn:")
                gridspace = input()
                space = None
                for sp in game.board:
                    if str(sp) == gridspace:
                        space = sp
                        break
                self.move(space)
                moved = True
            except Exception as e:
                print(str(e))
        built = False
        while not built:
            try:
                print("Enter grid space to build:")
                gridspace = input()
                space = None
                for sp in game.board:
                    if str(sp) == gridspace:
                        space = sp
                        break
                self.build(space)
                built = True
            except Exception as e:
                print(str(e))
