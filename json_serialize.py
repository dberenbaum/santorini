import json

import serialize


class JsonTree(serialize.Tree):

    def __init__(self, filepath="santorini.json"):
        self.filepath = filepath
        self.tree = {}

    def __enter__(self):
        with open(self.filepath) as jsonin:
            self.tree = json.load(jsonin)
        return self

    def __exit__(self, type, value, traceback):
        with open(self.filepath, "w") as jsonout:
            json.dump(self.tree, jsonout)
