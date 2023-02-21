from collections import defaultdict
from multiprocessing import cpu_count, Pool, Queue
from typing import List

from gp.event import Event, EventType
from gp.game import Game, Player


QUEUE = None


def run_game(game_id: str, players: List[Player]):
    game = Game(game_id, players)
    game.set_event_queue(QUEUE)
    game.run()


def pool_init(queue):
    global QUEUE
    QUEUE = queue


class ProcessPoolGameRunner:
    def __init__(self, workers=cpu_count()):
        self.callbacks = defaultdict(list)
        self.queue = Queue()
        self.pool: Pool = Pool(
            processes=workers, initializer=pool_init, initargs=(self.queue,)
        )
        self.results = []
        self.count = 0

    def register_callback(self, event_type: EventType, callback):
        self.callbacks[event_type].append(callback)

    def start(self, players: List[Player]):
        game_id = f"ProcessPoolGameRunner-{self.count}"
        self.count += 1
        res = self.pool.apply_async(run_game, (game_id, players))
        self.results.append(res)

    def join(self):
        game_count = len(self.results)
        game_end_count = 0
        while game_end_count < game_count:
            event: Event = self.queue.get()
            callbacks = self.callbacks[EventType.ANY] + self.callbacks[event.event_type]
            for callback in callbacks:
                callback(event)
            if event.event_type == EventType.GAME_END:
                game_end_count += 1

        for res in self.results:
            res.wait()

        self.pool.close()
        self.pool.join()
