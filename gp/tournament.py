from .event import Event, EventType
from .runner import ProcessPoolGameRunner, GameRunner


class Tournament:
    def __init__(self, matches, players, callbacks=None, workers=0):
        self.matches = matches
        self.players = players
        self.scores = {player.name(): 0 for player in players}

        if workers > 0:
            self.runner = ProcessPoolGameRunner(workers=workers)
        else:
            self.runner = GameRunner()

        self.runner.register_callback(EventType.GAME_END, self.record_win)
        if callbacks:
            for event_type, f in callbacks:
                self.runner.register_callback(event_type, f)

    def record_win(self, event: Event):
        self.scores[event.data["winner"].name()] += 1

    def run(self):
        for _ in range(self.matches):
            self.runner.start(self.players)
            self.players = self.players[1:] + self.players[:1]

        self.runner.join()
        return self.scores
