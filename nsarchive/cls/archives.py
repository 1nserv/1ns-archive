import time

class Action:
    def __init__(self, author: str = '0', target: str = '0') -> None:
        self.id: str = hex(round(time.time()))[2:].upper()
        self.date: int = int(self.id, 16)
        self.action: str = ""
        self.author: str = author
        self.target: str = target


# Entities

class Sanction(Action):
    def __init__(self, author: str, target: str) -> None:
        super().__init__(author, target)

        self.details: str = ""
        self.major: bool = False # Sanction majeure ou non
        self.duration: int = 0 # Durée en secondes, 0 = définitif

class AdminAction(Action):
    def __init__(self, author: str, target: str) -> None:
        super().__init__(author, target)

        self.details: str = ""
        self.new_state: str | int | bool = None


# Community

class Election(Action):
    def __init__(self, author: str, target: str, position: str) -> None:
        super().__init__(author, target)

        self.position: str = position
        self.positive_votes: int = 0
        self.total_votes: int = 0

class Promotion(Action):
    def __init__(self, author: str, target: str, position: str) -> None:
        super().__init__(author, target)

        self.position: str = position

class Demotion(Action):
    def __init__(self, author: str, target: str) -> None:
        super().__init__(author, target)

        self.reason: str = None


# Bank

class Transaction(Action):
    def __init__(self, author: str, target: str, amount: int) -> None:
        super().__init__(author, target)

        self.amount: int = amount
        self.currency: str = 'HC'
        self.reason: str = None

class Sale(Action):
    def __init__(self, author: str = '0', target: str = '0') -> None:
        super().__init__(author, target)

        self.price: int = 0