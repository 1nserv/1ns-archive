class BankAccount:
    def __init__(self, id: str) -> None:
        self.id: str = id
        self.owner: str = '0'
        self.amount: int = 0
        self.locked: bool = False
        self.bank: str = "HexaBank"