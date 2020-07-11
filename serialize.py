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
        self.tree[state] = {"tries": 0, "wins": 0, "options": []}

    def add_try(self, state):
        if state not in self:
            self.insert_state(state)
        self._add_try(state)

    def _add_try(self, state):
        self.tree[state]["tries"] += 1

    def add_win(self, state):
        self.tree[state]["wins"] += 1

    def set_options(self, state, options):
        if state not in self:
            self.insert_state(state)
        self._set_options(state, options)

    def _set_options(self, state, options):
        self.tree[state]["options"] = options
