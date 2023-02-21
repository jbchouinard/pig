from dataclasses import dataclass

from gp.game import Action, Player, PlayerAction, PlayerTurnState


@dataclass
class PlayerStats:
    total_rounds: int = 0
    total_rolls: int = 0
    total_points: int = 0
    total_games: int = 0
    total_wins: int = 0


class WithStats(Player):
    def __init__(self, player_cls, *args, **kwargs):
        self.player = player_cls(*args, **kwargs)
        self.last_state = None
        self.stats = PlayerStats()

    def __repr__(self):
        return f"WithStats({repr(self.player)})"

    def name(self):
        return self.player.name()

    def on_player_turn(self, state: PlayerTurnState) -> Action:
        self.last_state = state
        return self.player.on_player_turn(state)

    def on_player_action(self, action: PlayerAction):
        if action.action == Action.STOP:
            self.stats.total_points += self.last_state.current_score
            self.stats.total_rounds += 1
        else:
            self.stats.total_rolls += 1
            if action.value == 1:
                self.__states.total_rounds += 1
        self.player.on_player_action(action)

    def on_game_start(self, player_number):
        self.player.on_game_start(player_number)

    def on_game_end(self, winner: Player):
        self.stats.total_games += 1
        if winner is self:
            self.stats.total_wins += 1
        self.player.on_game_end(winner)
