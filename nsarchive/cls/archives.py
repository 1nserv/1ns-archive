class Action:
    def __init__(self, id: str, author: str = '11625D9061021010', target: str = '0') -> None:
        self.id: str = id
        self.date: int = 0
        self.action: str = ""
        self.author: str = author
        self.target: str = target

# Entities

class ModAction(Action):
    def __init__(self, id: str, author: str, target: str) -> None:
        super().__init__(id, author, target)
        self.details: str = ""
        self.major: bool = False # Sanction majeure ou non
        self.duration: int = 0 # Durée en secondes, 0 = définitif

class AdminAction(Action):
    def __init__(self, id: str, author: str, target: str) -> None:
        super().__init__(id, author, target)
        self.details: str = ""
        self.new_state: str | int | bool = None


# Community

class Election(Action):
    def __init__(self, id: str, author: str, target: str, position: str) -> None:
        super().__init__(id, author, target)
        self.position: str = position
        self.positive_votes: int = 0
        self.total_votes: int = 0

class Promotion(Action):
    def __init__(self, id: str, author: str, target: str, position: str) -> None:
        super().__init__(id, author, target)
        self.position: str = position

class Demotion(Action):
    def __init__(self, id: str, author: str, target: str) -> None:
        super().__init__(id, author, target)
        self.reason: str = None

# Bank

class Transaction(Action):
    def __init__(self, id: str, author: str, target: str, amount: int) -> None:
        super().__init__(id, author, target)

        self.amount: int = amount
        self.currency: str = 'XC'
        self.reason: str = None
