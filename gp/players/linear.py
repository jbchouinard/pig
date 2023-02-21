from gp.game import PlayerTurnState

from .scorer import Scorer


class Linear5(Scorer):
    LEAD_DIVISOR = 5

    def roll_target(self, state: PlayerTurnState):
        opp_scores = [
            score for name, score in state.scores.items() if name != self.name()
        ]
        high_score = max(opp_scores)
        lead = state.scores[self.name()] - high_score
        return int(20 - (lead / self.LEAD_DIVISOR))


class Linear10(Linear5):
    LEAD_DIVISOR = 10


class Linear20(Linear5):
    LEAD_DIVISOR = 20
