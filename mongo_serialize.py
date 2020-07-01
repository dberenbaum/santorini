import copy
import sys
import pymongo

import core
import random_play
import serialize


class MongoTree(serialize.Tree):

    def __init__(self, cnxn_str="mongodb://localhost:27017/", db="santorini",
                 collection="tree"):
        self.client = pymongo.MongoClient(cnxn_str)
        self.db = self.client[db]
        self.tree = self.db[collection]

    def __exit__(self, type, value, traceback):
        self.client.close()

    def __contains__(self, state):
        if self.tree.find_one({"_id": state}):
            return True
        else:
            return False

    def __getitem__(self, state):
        if state in self:
            return self.tree.find_one({"_id": state})
        else:
            raise KeyError

    def insert_state(self, state):
        try:
            self.tree.insert_one({"_id": state, "tries": 0, "wins": 0})
        except pymongo.errors.DuplicateKeyError:
            pass

    def add_try(self, state):
        self.tree.update_one({"_id": state}, {"$inc": {"tries": 1}})

    def add_win(self, state):
        self.tree.update_one({"_id": state}, {"$inc": {"wins": 1}})
