from nsarchive.cls.base import NSID

# Votes

class VoteOption:
    """
    Option disponible lors d'un vote

    ## Attributs
    - id: `str`\n
        Identifiant de l'option
    - title: `str`\n
        Label de l'option
    - count: `int`\n
        Nombre de sympathisants pour cette option
    """

    def __init__(self, id: str, title: str = None, count: int = 0):
        self.id = id
        self.title = title if title else id
        self.count = count

class Vote:
    """
    Classe de référence pour les différents votes du serveur

    ## Attributs
    - id: `NSID`\n
        Identifiant du vote
    - title: `str`\n
        Titre du vote
    - choices: list[.VoteOption]\n
        Liste des choix disponibles
    - author: `NSID`\n
        Identifiant de l'auteur du vote
    - startDate: `int`\n
        Date de début du vote
    - endDate: `int`\n
        Date limite pour voter
    """

    def __init__(self, id: NSID, title: str) -> None:
        self.id: NSID = NSID(id)
        self.title: str = title
        self.choices: list[VoteOption] = []
        self.author: NSID = NSID("0")
        self.startDate: int = 0
        self.endDate: int = 0

    def by_id(self, id: str) -> VoteOption:
        for opt in self.choices:
            if opt.id == id:
                return opt

    def sorted(self, titles_only: bool = False) -> list[VoteOption] | list[str]:
        sorted_list: list[VoteOption] = sorted(self.choices, lambda opt : opt.count)

        if titles_only:
            return [ opt.id for opt in sorted_list ]
        else:
            return sorted_list

class Referendum(Vote):
    """
    Vote à trois positions
    """

    def __init__(self, id: NSID, title: str) -> None:
        super().__init__(id, title)

        self.choices = [
            VoteOption('yes', 'Oui'),
            VoteOption('no', 'Non'),
            VoteOption('blank', 'Pas d\'avis'),
        ]

class Lawsuit(Vote):
    """
    Vote à trois positions pour un procès
    """

    def __init__(self, id: NSID, title: str) -> None:
        super().__init__(id, title)

        self.choices = [
            VoteOption('guilty', 'Coupable'),
            VoteOption('innocent', 'Innocent'),
            VoteOption('blank', 'Pas d\'avis'),
        ]


# Institutions (defs)

class Official:
    def __init__(self, id: NSID) -> None:
        self.id: NSID = NSID(id)

        self.mandates: int = {
            'PRE_REP': 0, # Président de la République
            'MIN': 0, # Différents ministres
            'PRE_AS': 0, # Président de l'Assemblée Nationale
            'REPR': 0 # Député
        }

        self.contributions: dict = {
            'propose_project': 0,
            'success_project': 0, 
            'vote_law': 0
        }

class Administration:
    def __init__(self) -> None:
        self.president: Official
        self.members: list[Official] = []

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
        self.members: list[Official] = []

class Assembly:
    def __init__(self) -> None:
        self.president: Official
        self.members: list[Official] = []

class PoliceForces:
    def __init__(self) -> None:
        self.president: Official
        self.members: list[Official] = []

class State:
    def __init__(self) -> None:
        self.administration: Administration
        self.government: Government
        self.court: Court
        self.assembly: Assembly
        self.police: PoliceForces