import copy
import sys
import pymongo

import core
import serialize


class MongoTree(serialize.Tree):

    def __init__(self, cnxn_str="mongodb://localhost:27017/", db="santorini",
                 collection="tree"):
        self.client = pymongo.MongoClient(cnxn_str, connect=False)
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
            record = {"_id": state, "tries": 0, "wins": 0, "options": []}
            self.tree.insert_one(record)
        except pymongo.errors.DuplicateKeyError:
            pass

    def _add_try(self, state):
        self.tree.update_one({"_id": state}, {"$inc": {"tries": 1}})

    def add_win(self, state):
        self.tree.update_one({"_id": state}, {"$inc": {"wins": 1}})

    def _set_options(self, state, options):
        self.tree.update_one({"_id": state}, {"$set": {"options": options}})

    def sample(self, n):
        for r in self.tree.aggregate([{"$sample": {"size": n}}]):
            yield r


class BulkMongoTree(MongoTree):

    def __init__(self, cnxn_str="mongodb://localhost:27017/", db="santorini",
                 collection="tree"):
        self.dict = {}
        self.updates = {}
        self.options = {}
        super().__init__(cnxn_str=cnxn_str, db=db, collection=collection)

    def __exit__(self, type, value, traceback):
        self.write()
        super().__exit__(type, value, traceback)

    def __contains__(self, state):
        if state in self.dict:
            return True
        elif self.tree.find_one({"_id": state}):
            self.insert_state(state)
            return True
        else:
            return False

    def __getitem__(self, state):
        try:
            return self.dict[state]
        except KeyError:
            if state in self:
                self.dict[state] = self.tree.find_one({"_id": state})
                self.updates[state] = {"tries": 0, "wins": 0}
                return self.dict[state]
            else:
                raise KeyError

    def insert_state(self, state):
        self.dict[state] = {"tries": 0, "wins": 0, "options": []}
        self.updates[state] = {"tries": 0, "wins": 0}

    def _add_try(self, state):
        self.dict[state]["tries"] += 1
        self.updates[state]["tries"] += 1

    def add_win(self, state):
        self.dict[state]["wins"] += 1
        self.updates[state]["wins"] += 1

    def _set_options(self, state, options):
        self.dict[state]["options"] = options
        self.options[state] = options

    def write(self):
        updates = []
        for state, keys in self.updates.items():
            update_dict = {"$inc": keys}
            try:
                update_dict["$set"] = {"options": self.options[state]}
            except KeyError:
                pass
            update = pymongo.UpdateOne({"_id": state}, update_dict, upsert=True)
            updates.append(update)
        if updates:
            self.tree.bulk_write(updates)
        self.dict = {}
        self.updates = {}
