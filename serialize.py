import copy
import sys

import ujson

import game
import random_play


def record_play(g, debug=False):
    moves = {p: [] for p in g.players}
    for player in g.play():
        state = g.compact_state()
        moves[player].append(state)
        if state not in g.tree:
            g.tree[state] = {"tries": 1, "wins": 0}
        else:
            g.tree[state]["tries"] += 1
        if debug:
            g.print_state()
    winner = g.winner()
    for move in moves[winner]:
        g.tree[move]["wins"] += 1


def repeat_plays(g, n=10):
    for play in range(n):
        g.reset()
        record_play(g)


def read_tree(infile):
    with open(infile) as jsonin:
        tree = ujson.load(jsonin)
    return tree


def write_tree(tree, outfile):
    with open(outfile, "w") as jsonout:
        ujson.dump(tree, jsonout)
