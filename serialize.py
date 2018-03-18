import copy
import sys

import ujson

import game
import random_play


def record_play(g, tree=None, debug=False):
    if not tree:
        tree = {}
    moves = {p: [] for p in g.players}
    for player in g.play():
        state = g.compact_state()
        moves[player].append(state)
        if state not in tree:
            tree[state] = {"tries": 1, "wins": 0}
        else:
            tree[state]["tries"] += 1
        if debug:
            g.print_state()
    winner = g.winner()
    for move in moves[winner]:
        tree[move]["wins"] += 1
    return tree


def repeat_plays(g, n=10, tree=None):
    if not tree:
        tree = {}
    for play in range(n):
        new_game = copy.deepcopy(g)
        tree = record_play(new_game, tree)
    return tree


def read_tree(infile):
    with open(infile) as jsonin:
        tree = ujson.load(jsonin)
    return tree


def write_tree(tree, outfile):
    with open(outfile, "w") as jsonout:
        ujson.dump(tree, jsonout)
