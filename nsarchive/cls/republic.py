from .entities import *

# Votes

class Vote:
    def __init__(self, id: str, title: str, choices: tuple[str]) -> None:
        self.id: str = id
        self.title: str = title
        self.choices = { choice : 0 for choice in choices }
        self.author: str = '0'
        self.startDate: int = 0
        self.endDate: int = 0

class ClosedVote(Vote):
    def __init__(self, id: str, title: str) -> None:
        super().__init__(id, title, ('yes', 'no', 'blank'))


# Institutions (defs)

class Administration:
    def __init__(self) -> None:
        self.president: FunctionalUser
        self.members: list[FunctionalUser]

class Government:
    def __init__(self, president: FunctionalUser) -> None:
        self.president: FunctionalUser = president
        self.prime_minister: FunctionalUser

        self.inner_minister: FunctionalUser
        self.economy_minister: FunctionalUser
        self.justice_minister: FunctionalUser
        self.press_minister: FunctionalUser
        self.outer_minister: FunctionalUser

class Assembly:
    def __init__(self) -> None:
        self.president: FunctionalUser
        self.members: list[FunctionalUser]

class Court:
    def __init__(self) -> None:
        self.president: FunctionalUser
        # On discutera de la mise en place d'un potentiel président. Pour l'instant c'est le Ministre de la Justice
        self.members: list[FunctionalUser]

class PoliceForces:
    def __init__(self) -> None:
        self.president: FunctionalUser
        self.members: list[FunctionalUser]

class Institutions:
    def __init__(self) -> None:
        self.administration: Administration
        self.government: Government
        self.court: Court
        self.assembly: Assembly
        self.police: PoliceForces