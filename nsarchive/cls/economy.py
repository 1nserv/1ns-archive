from .base import NSID

class BankAccount:
    def __init__(self, id: str | NSID) -> None:
        self.id: NSID = NSID(id)
        self.owner: NSID = NSID(0)
        self.amount: int = 0
        self.frozen: bool = False
        self.bank: str = "HexaBank"

        self.income: int = 0

class Item:
    def __init__(self, id: str | NSID) -> None:
        self.id: NSID = NSID(id)
        self.title: str = "Unknown Object"
        self.emoji: str = ":light_bulb:"

class Inventory:
    def __init__(self, owner_id: NSID) -> None:
        self.owner_id: NSID = NSID(owner_id)
        self.objects: dict[str, NSID] = {}

    def append(self, item: Item, quantity: int = 1):
        if item.id in self.objects.keys():
            self.objects[item.id] += quantity
        else:
            self.objects[item.id] = quantity

    def throw(self, item: Item, quantity: int = 1):
        if item.id in self.objects.keys():
            if self.objects[item.id] > quantity:
                self.objects[item.id] -= quantity
            else:
                self.objects[item.id] = 0

class Sale:
    def __init__(self, id: NSID, item: Item) -> None:
        self.id: NSID = NSID(id)
        self.item: NSID = NSID(item.id)
        self.quantity: int = 1

        self.price: int = 0
        self.seller_id: NSID = NSID('0')