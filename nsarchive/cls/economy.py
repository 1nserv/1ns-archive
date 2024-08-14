class BankAccount:
    def __init__(self, id: str) -> None:
        self.id: str = id
        self.owner: str = '0'
        self.amount: int = 0
        self.locked: bool = False
        self.bank: str = "HexaBank"

        self.income: int = 0

class Item:
    def __init__(self, id: str) -> None:
        self.id = id
        self.title: str = "Unknown Object"
        self.emoji: str = ":light_bulb:"

        self.seller_id: str = ""
        self.price: int = 0