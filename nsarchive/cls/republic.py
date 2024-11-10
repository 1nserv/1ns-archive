from nsarchive.cls.base import NSID

# Votes

class Vote:
    def __init__(self, id: str | NSID, title: str, choices: tuple[str]) -> None:
        self.id: NSID = NSID(id)
        self.title: str = title
        self.choices = { choice : 0 for choice in choices }
        self.author: str = '0'
        self.startDate: int = 0
        self.endDate: int = 0

class Referendum(Vote):
    def __init__(self, id: str | NSID, title: str) -> None:
        super().__init__(id, title, ('yes', 'no', 'blank'))

class Lawsuit(Vote):
    def __init__(self, id: str | NSID, title: str) -> None:
        super().__init__(id, title, ('innocent', 'guilty', 'blank'))


# Institutions (defs)

class Official:
    def __init__(self, id: str | NSID) -> None:
        self.id: NSID = NSID(id)

        self.mandates: int = {
            'PRE_REP': 0, # Président de la République
            'MIN': 0, # Différents ministres
            'PRE_AS': 0, # Président de l'Assemblée Nationale
            'JUDGE': 0, # Juge
            'REPR': 0 # Député
        }

        self.contributions: dict = {
            'project': 0,
            'approved_project': 0, 
            'admin_action': 0, 
            'law_vote': 0
        }

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

class Court:
    def __init__(self) -> None:
        self.president: Official
        # On discutera de la mise en place d'un potentiel président. Pour l'instant c'est le Ministre de la Justice
        self.members: list[Official]

class Assembly:
    def __init__(self) -> None:
        self.president: Official
        self.members: list[Official]

class PoliceForces:
    def __init__(self) -> None:
        self.president: Official
        self.members: list[Official]

class State:
    def __init__(self) -> None:
        self.administration: Administration
        self.government: Government
        self.court: Court
        self.assembly: Assembly
        self.police: PoliceForces