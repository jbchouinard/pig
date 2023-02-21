from gp.game import Action, Player, PlayerTurnState


class Team(Player):
    MEMBERS = None
    TIEBREAKER = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.members = [cls(*args, **kwargs) for cls in self.MEMBERS]

    def on_player_turn(self, state: PlayerTurnState) -> Action:
        votes_roll = 0
        votes_stop = 0

        for member in self.members:
            if member.on_player_turn(state) == Action.ROLL:
                votes_roll += 1
            else:
                votes_stop += 1

        if votes_roll > votes_stop:
            return Action.ROLL
        elif votes_stop > votes_roll:
            return Action.STOP
        else:
            return self.TIEBREAKER


def team(*members_cls, tiebreaker=Action.ROLL):
    return type("SomeTeam", (Team,), {"MEMBERS": members_cls, "TIEBREAKER": tiebreaker})
