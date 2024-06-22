import time

from .entities import FunctionalUser

class Vote:
    def __init__(self, id: str, title: str, choices: tuple[str]) -> None:
        self.id: str = id
        self.title: str = title
        self.choices = { choice : 0 for choice in choices }
        self.author: FunctionalUser
        self.startDate: int = 0
        self.endDate: int = 0

class ClosedVote(Vote):
    def __init__(self, id: str, title: str) -> None:
        super().__init__(id, title, ('yes', 'no', 'blank'))
