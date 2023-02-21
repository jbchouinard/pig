from gp.game import Action, Player, PlayerTurnState


class Roller5(Player):
    ROLLS_GOAL = 5

    def on_player_turn(self, state: PlayerTurnState) -> Action:
        if state.current_rolls >= self.ROLLS_GOAL:
            return Action.STOP
        else:
            return Action.ROLL


class Roller3(Roller5):
    ROLLS_GOAL = 3


class Roller7(Roller5):
    ROLLS_GOAL = 7
