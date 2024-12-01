import time

from .base import *

class Archive:
    def __init__(self, author: NSID = '0', target: NSID = '0'):
        """
        Classe de référence pour toutes les archives.

        ## Attributs de base
        - date: `int`\n
            Date (timestamp) de l'exécution de l'archive
        - id: `NSID`\n
            Clé d'identification des archives (basée sur la date)
        - author: `NSID`\n
            ID de l'auteur de l'action
        - target: `NSID`:
            ID de la cible de l'action
        - action: `str`:\n
            Action effectuée
        - details: `dict`\n
            Ensemble de détails que les différents bots peuvent utiliser
        """
        self.date: int = round(time.time())

        self.id: NSID = NSID(self.date)
        self.author: NSID = NSID(author)
        self.target: NSID = NSID(target)

        self.action: str = ""
        self.details: dict = {
            "reason": None
        }


# Entities

class Sanction(Archive):
    def __init__(self, author: NSID, target: NSID) -> None:
        super().__init__(author, target)

        self.details: dict = {
            "reason": None,
            "major": False, # Sanction majeure ou non
            "duration": 0 # Durée en secondes , 0 = définitif
        }

class Report(Archive):
    def __init__(self, author: NSID, target: NSID) -> None:
        super().__init__(author, target)

        self.details: dict = {
            "reason": None,
            "elements": [] # Liste des pièces jointes
        }


# Community

class Election(Archive):
    def __init__(self, author: NSID, target: NSID, position: str) -> None:
        super().__init__(author, target)

        self.details = {
            "position": position,
            "positive_votes": 0,
            "total_votes": 0
        }

class Promotion(Archive):
    def __init__(self, author: NSID, target: NSID, position: str) -> None:
        super().__init__(author, target)

        self.details = {
            "position": position
        }

class Demotion(Archive):
    def __init__(self, author: NSID, target: NSID) -> None:
        super().__init__(author, target)


# Bank

class Transaction(Archive):
    def __init__(self, author: NSID, target: NSID) -> None:
        super().__init__(author, target)

        self.details = {
            "amount": 0,
            "currency": "HC",
            "reason": None
        }