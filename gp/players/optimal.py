import csv
from collections import defaultdict
from importlib import resources

import gp.data
from gp.game import PlayerTurnState

from .scorer import Scorer


# From Optimal Pig Play paper: https://cupola.gettysburg.edu/csfac/4/
# Data extracted from VRML: http://cs.gettysburg.edu/projects/pig/pigVis.html
def open_optimal_pig_csv():
    return resources.open_text(gp.data, "optimal_pig.csv")


def parse_optimal_lookup():
    lookup = defaultdict(lambda: defaultdict(set))

    reader = csv.DictReader(open_optimal_pig_csv())
    for row in reader:
        own_score = int(float(row["own_score"]))
        opponent_score = int(float(row["opponent_score"]))
        roll_target = int(float(row["roll_target"]))
        lookup[opponent_score][own_score].add(roll_target)

    for opp_score in range(100):
        for own_score in range(100):
            lookup[opp_score][own_score] = min(lookup[opp_score][own_score])

    return lookup


OPTIMAL_ROLL_TARGET_LOOKUP = parse_optimal_lookup()


def bound(n):
    return min(99, max(0, n))


class Optimal(Scorer):
    def roll_target(self, state: PlayerTurnState):
        opp_score = bound(
            max([score for name, score in state.scores.items() if name != self.name()])
        )
        own_score = bound(state.scores[self.name()])
        return OPTIMAL_ROLL_TARGET_LOOKUP[opp_score][own_score]
