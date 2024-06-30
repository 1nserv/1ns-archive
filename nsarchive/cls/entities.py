import time

from .exceptions import *

class Entity:
    def __init__(self, id: str):
        self.id: str = id # ID hexadécimal de l'entité
        self.name: str = 'Entité Inconnue'
        self.registerDate: int = 0
        self.legalPosition: int = 'Normal'
        self.xp: int = 0

    def get_level(self) -> None:
        i = 0
        while self.xp > int(round(25 * (i * 2.5) ** 2, -2)):
            i += 1

        return i
    
    def rename(self, new_name: str) -> None:
        if len(new_name) > 32:
            raise NameTooLongError(f"Name length mustn't exceed 32 characters.")
        
        self.name = new_name
    
    def set_position(self, position: str) -> None:
        self.legalPosition = position
    
    def add_xp(self, amount: int) -> None:
        boost = 0 if 0 in self.boosts.values() else max(list(self.boosts.values()) + [ 1 ])

        self.xp += amount * boost
    
class User(Entity):
    def __init__(self, id: str):
        super().__init__(id)

        self.boosts: dict[str, int] = {}
    
    def edit_boost(self, name: str, multiplier: int = -1) -> None:
        if multiplier >= 0:
            self.boosts[name] = multiplier
        else:
            del self.boosts[name]

class Organization(Entity):
    def __init__(self, id: str):
        super().__init__(id)

        self.owner: Entity
        self.certifications: dict = {}
        self.members: list = []
    
    def add_certification(self, certif: str) -> None:
        self.certifications[certif] = round(time.time())
    
    def add_member(self, member: User) -> None:
        self.members.append(member)
    
    def remove_member(self, member: User) -> None:
        if member in self.members:
            self.members.remove(member)
    
    def set_owner(self, member: User) -> None:
        self.owner = member

class Elector(User):
    def __init__(self, id: str) -> None:
        self.id: str = id
        self.votes: list[str] = []

class FunctionalUser(User):
    def __init__(self, id: str):
        super().__init__(id)

        self.permissions: dict = {
            'approve_project': False,
            'create_org': False,
            'destroy_gov': False,
            'destroy_org': False,
            'propose_projects': False
        }

        self.mandates: int = 0
        self.contribs: dict = {
            'projects': 0,
            'approved_projects': 0, 
            'admin_actions': 0, 
            'law_votes': 0
        }