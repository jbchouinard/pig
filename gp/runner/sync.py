import logging
from collections import defaultdict
from queue import Empty, Queue
from typing import List

from gp.event import Event, EventType
from gp.game import Game, Player


class GameRunner:
    def __init__(self):
        self.callbacks = defaultdict(list)
        self.queue = Queue()
        self.count = 0

    def register_callback(self, event_type: EventType, callback):
        self.callbacks[event_type].append(callback)

    def start(self, players: List[Player]):
        game = Game(f"GameRunner-{self.count}", players)
        game.set_event_queue(self.queue)
        self.count += 1
        game.run()

        while True:
            try:
                event: Event = self.queue.get(timeout=3)
            except Empty:
                logging.error("Expected an end of game event")
                break
            else:
                callbacks = (
                    self.callbacks[EventType.ANY] + self.callbacks[event.event_type]
                )
                for callback in callbacks:
                    callback(event)
                if event.event_type == EventType.GAME_END:
                    break

    def join(self):
        pass
