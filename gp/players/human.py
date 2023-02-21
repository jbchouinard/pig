from gp.game import Action, Player, PlayerAction, PlayerTurnState


class Human(Player):
    def on_player_turn(self, state: PlayerTurnState) -> Action:
        print(str(state))
        while True:
            choice = input(f"{self._name}: Roll or stop? ").lower()
            if choice in ("r", "roll"):
                return Action.ROLL
            elif choice in ("s", "stop"):
                return Action.STOP
            else:
                print("Invalid choice.")

    def on_player_action(self, action: PlayerAction):
        print("\033[H\033[J", end="")
        if action.action == Action.ROLL:
            print(f"{self._name} rolled {action.value}\n")
        else:
            print(f"{self._name} stopped\n")

    def on_game_start(self):
        print("\033[H\033[J", end="")
