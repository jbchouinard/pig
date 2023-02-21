import abc
import math
from dataclasses import dataclass
from enum import Enum
from queue import Queue
from random import randint
from typing import Any, Dict, List, Optional, Tuple, Type

from .event import Event


TO_WIN = 100


def dice(faces: int):
    def roll():
        return randint(1, faces)

    return roll


d6 = dice(6)


class Action(Enum):
    ROLL = "roll"
    STOP = "stop"


@dataclass
class PlayerTurnState:
    scores: Dict[str, int]
    current_round: int
    current_score: int
    current_rolls: int

    @property
    def lead(self):
        return self.score - max(self.other_scores)

    def __str__(self):
        return (
            f"Round {self.current_round}  "
            + "  ".join(f"{name}: {score}" for name, score in self.scores.items())
            + f"\n{self.current_score} ({self.current_rolls})"
        )


@dataclass
class GameState:
    players: List["Player"]
    n_players: int
    scores: List[int]
    current_round: int
    current_player: int
    current_points: int
    current_rolls_count: int

    def __init__(self, players: List["Player"]):
        self.players = players
        self.n_players = len(players)
        self.scores = [0] * self.n_players
        self.current_round = 1
        self.current_player = 0
        self.current_points = 0
        self.current_rolls_count = 0

    def finish_turn(self):
        self.scores[self.current_player] += self.current_points
        self.current_points = 0
        self.current_rolls_count = 0

        if self.current_player == (self.n_players - 1):
            self.current_round += 1
            self.current_player = 0
        else:
            self.current_player += 1

    def add_roll(self, x):
        self.current_rolls_count += 1
        if x == 1:
            self.current_points = 0
            self.finish_turn()
        else:
            self.current_points += x

    def winner(self):
        scores = zip(self.scores, self.players)
        highest, player = max(scores, key=lambda t: t[0])
        if highest >= TO_WIN:
            return player
        else:
            return None

    def player_turn_state(self) -> PlayerTurnState:
        scores = {
            player.name(): score for player, score in zip(self.players, self.scores)
        }

        return PlayerTurnState(
            scores=scores,
            current_round=self.current_round,
            current_score=self.current_points,
            current_rolls=self.current_rolls_count,
        )


class Player(abc.ABC):
    def __init__(self, player_number: int, name=None):
        self.player_number = int(player_number)
        self._name = name

    def name(self):
        return self._name or f"{self.__class__.__name__}<{self.player_number}>"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.player_number}, {self._name})"

    @abc.abstractmethod
    def on_player_turn(self, state: PlayerTurnState) -> Action:
        pass

    def on_player_action(self, action: "PlayerAction"):
        pass

    def on_game_start(self, player_number: int):
        pass

    def on_game_end(self, winner: "Player"):
        pass


@dataclass
class PlayerAction:
    player: str
    action: Action
    value: Any


class Game:
    def __init__(self, game_id: str, players: List[Player]):
        self.game_id = game_id
        self.players = players
        self.state = GameState(self.players)
        self.winner = None
        self.events = None

    def set_event_queue(self, queue: Optional[Queue]):
        self.events = queue

    def send(self, event):
        if self.events is not None:
            self.events.put(event)

    def play_turn(self):
        player = self.players[self.state.current_player]
        action = player.on_player_turn(self.state.player_turn_state())

        if action == Action.ROLL:
            roll = d6()
            player_action = PlayerAction(
                player=player.name(), action=action, value=roll
            )
            self.state.add_roll(roll)
        else:
            player_action = PlayerAction(
                player=player.name(), action=action, value=None
            )
            self.state.finish_turn()

        player.on_player_action(player_action)
        # self.send(Event.player_action(self.game_id, player_action=player_action))
        self.winner = self.state.winner()

    def run(self):
        for i, player in enumerate(self.players, 1):
            player.on_game_start(i)

        # self.send(
        #     Event.game_start(self.game_id, players=[p.name() for p in self.players])
        # )

        while self.winner is None:
            self.play_turn()

        for player in self.players:
            player.on_game_end(winner=self.winner)

        self.send(Event.game_end(self.game_id, winner=self.winner))
