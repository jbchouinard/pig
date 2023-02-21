from gp.game import Action, Player, PlayerTurnState


class Scorer(Player):
    def roll_target(self, state):
        raise NotImplementedError

    def on_player_turn(self, state: PlayerTurnState) -> Action:
        if state.current_rolls == 0:
            return Action.ROLL

        if state.current_score >= self.roll_target(state):
            return Action.STOP
        else:
            return Action.ROLL


class Scorer20(Player):
    SCORE_GOAL = 20

    def roll_target(self, state):
        return self.SCORE_GOAL

    def on_player_turn(self, state: PlayerTurnState) -> Action:
        if state.current_rolls == 0:
            return Action.ROLL

        if state.current_score >= self.roll_target(state):
            return Action.STOP
        else:
            return Action.ROLL


class Scorer25(Scorer20):
    SCORE_GOAL = 25
