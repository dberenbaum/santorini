class Tree(object):

    def __init__(self):
        self.tree = {}

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __contains__(self, state):
        return state in self.tree.keys()

    def __getitem__(self, key):
        return self.tree[key]

    def insert_state(self, state):
        self.tree[state] = {"tries": 0, "wins": 0}

    def add_try(self, state):
        self.tree[state]["tries"] += 1

    def add_win(self, state):
        self.tree[state]["wins"] += 1


def record_play(g, tree, debug=False):
    moves = {p: [] for p in g.players}
    for player in g.play():
        state = g.compact_state()
        moves[player].append(state)
        if state not in tree:
            tree.insert_state(state)
        tree.add_try(state)
        if debug:
            g.print_state()
    winner = g.winner()
    for move in moves[winner]:
        tree.add_win(move)


def repeat_plays(g, tree, n=10):
    for play in range(n):
        g.reset()
        record_play(g, tree)
        yield g
