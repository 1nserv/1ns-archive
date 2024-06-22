import time

class Vote:
    def __init__(self, id: int, title: str, choices: list[str]) -> None:
        self.id: int = id
        self.title: str = title
        self.choices = { choice : 0 for choice in choices }