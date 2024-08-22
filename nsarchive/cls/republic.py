from .entities import *

# Votes

class Vote:
    def __init__(self, id: str | NSID, title: str, choices: tuple[str]) -> None:
        self.id: NSID = NSID(id)
        self.title: str = title
        self.choices = { choice : 0 for choice in choices }
        self.author: str = '0'
        self.startDate: int = 0
        self.endDate: int = 0

class ClosedVote(Vote):
    def __init__(self, id: str | NSID, title: str) -> None:
        super().__init__(id, title, ('yes', 'no', 'blank'))


# Institutions (defs)

class Administration:
    def __init__(self) -> None:
        self.president: Official
        self.members: list[Official]

class Government:
    def __init__(self, president: Official) -> None:
        self.president: Official = president
        self.prime_minister: Official

        self.inner_minister: Official
        self.economy_minister: Official
        self.justice_minister: Official
        self.press_minister: Official
        self.outer_minister: Official

class Assembly:
    def __init__(self) -> None:
        self.president: Official
        self.members: list[Official]

class Court:
    def __init__(self) -> None:
        self.president: Official
        # On discutera de la mise en place d'un potentiel président. Pour l'instant c'est le Ministre de la Justice
        self.members: list[Official]

class PoliceForces:
    def __init__(self) -> None:
        self.president: Official
        self.members: list[Official]

class Institutions:
    def __init__(self) -> None:
        self.administration: Administration
        self.government: Government
        self.court: Court
        self.assembly: Assembly
        self.police: PoliceForces

