from .base import *

class BankAccount:
    def __init__(self, id: str | NSID) -> None:
        self.id: NSID = NSID(id)
        self.owner: NSID = NSID(0)
        self.amount: int = 0
        self.locked: bool = False
        self.bank: str = "HexaBank"

        self.income: int = 0

class Item:
    def __init__(self, id: str | NSID) -> None:
        self.id: NSID = NSID(id)
        self.title: str = "Unknown Object"
        self.emoji: str = ":light_bulb:"

        self.seller_id: NSID = NSID(0)
        self.price: int = 0