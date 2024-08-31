import time

from .base import *

class Action:
    def __init__(self, author: str | NSID = '0', target: str | NSID = '0') -> None:
        self.date: int = round(time.time())

        self.id: NSID = NSID(self.date)
        self.action: str = ""
        self.author: NSID = NSID(author)
        self.target: NSID = NSID(target)


# Entities

class Sanction(Action):
    def __init__(self, author: str | NSID, target: str | NSID) -> None:
        super().__init__(author, target)

        self.details: str = ""
        self.major: bool = False # Sanction majeure ou non
        self.duration: int = 0 # Durée en secondes, 0 = définitif

class AdminAction(Action):
    def __init__(self, author: str | NSID, target: str | NSID) -> None:
        super().__init__(author, target)

        self.details: str = ""
        self.new_state: str | int | bool = None

class Report(Action):
    def __init__(self, author: str | NSID, target: str | NSID) -> None:
        super().__init__(author, target)

        self.details: str = ""


# Community

class Election(Action):
    def __init__(self, author: str | NSID, target: str | NSID, position: str) -> None:
        super().__init__(author, target)

        self.position: str = position
        self.positive_votes: int = 0
        self.total_votes: int = 0

class Promotion(Action):
    def __init__(self, author: str | NSID, target: str | NSID, position: str) -> None:
        super().__init__(author, target)

        self.position: str = position

class Demotion(Action):
    def __init__(self, author: str | NSID, target: str | NSID) -> None:
        super().__init__(author, target)

        self.reason: str = None


# Bank

class Transaction(Action):
    def __init__(self, author: str | NSID, target: str | NSID, amount: int) -> None:
        super().__init__(author, target)

        self.amount: int = amount
        self.currency: str = 'HC'
        self.reason: str = None