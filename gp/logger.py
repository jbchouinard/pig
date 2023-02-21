from .event import Event


class EventLogger:
    def __init__(self, file):
        self.file = file

    def log(self, event: Event):
        self.file.write(f"{event.event_type.value} {repr(event.data)}\n")
