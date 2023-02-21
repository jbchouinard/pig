from dataclasses import dataclass
from enum import Enum
from typing import Any


class EventType(Enum):
    ANY = "event:any"
    GAME_START = "event:game_start"
    GAME_END = "event:game_end"
    PLAYER_TURN = "event:player_turn"
    PLAYER_ACTION = "event:player_action"


def event_constructor(event_type):
    def cons(cls, game_id, **kwargs):
        return cls(event_type=event_type, game_id=game_id, data=dict(kwargs))

    return cons


@dataclass
class Event:
    event_type: EventType
    game_id: str
    data: Any

    game_start = classmethod(event_constructor(EventType.GAME_START))
    game_end = classmethod(event_constructor(EventType.GAME_END))
    player_action = classmethod(event_constructor(EventType.PLAYER_ACTION))
    player_turn = classmethod(event_constructor(EventType.PLAYER_TURN))
