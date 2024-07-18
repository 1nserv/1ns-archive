import io
import time

from .exceptions import *

from ..utils import assets

class Entity:
    def __init__(self, id: str) -> None:
        self.id: str = id # ID hexadécimal de l'entité (ou nom dans le cas de l'entreprise)
        self.name: str = "Entité Inconnue"
        self.registerDate: int = 0
        self.legalPosition: str = 'Membre'
    
    def set_name(self, new_name: str) -> None:
        if len(new_name) > 32:
            raise NameTooLongError(f"Name length mustn't exceed 32 characters.")
        
        self.name = new_name
    
    def set_position(self, position: str) -> None:
        self.legalPosition = position

class User(Entity):
    def __init__(self, id: str) -> None:
        super().__init__(id)

        self.xp: int = 0
        self.boosts: dict[str, int] = {}

    def get_level(self) -> None:
        i = 0
        while self.xp > int(round(25 * (i * 2.5) ** 2, -2)):
            i += 1

        return i
    
    def add_xp(self, amount: int) -> None:
        boost = 0 if 0 in self.boosts.values() else max(list(self.boosts.values()) + [ 1 ])

        self.xp += amount * boost

    def edit_boost(self, name: str, multiplier: int = -1) -> None:
        if multiplier >= 0:
            self.boosts[name] = multiplier
        else:
            del self.boosts[name]

class MemberPermissions:
    def __init__(self) -> None:
        self.manage_organization = False # Renommer ou changer le logo
        self.manage_members = False # Virer quelqu'un d'une entreprise, l'y inviter, changer ses rôles
        self.manage_roles = False # Promouvoir ou rétrograder les membres
    
    def edit(self, **permissions: bool) -> None:
        for perm in permissions.values():
            self.__setattr__(*perm)

class GroupMember(User):
    def __init__(self, id: str) -> None:
        super().__init__(id)

        self.permissions: MemberPermissions = MemberPermissions()

class FunctionalUser:
    def __init__(self, id: str) -> None:
        self.id: str = id

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

class Organization(Entity):
    def __init__(self, id: str) -> None:
        super().__init__(id)

        self.owner: Entity
        self.certifications: dict = {}
        self.members: list[GroupMember] = []
        self.avatar: bytes = assets.open('default_avatar.png')

    def add_certification(self, certif: str) -> None:
        self.certifications[certif] = round(time.time())
    
    def add_member(self, member: GroupMember) -> None:
        self.members.append(member)
    
    def remove_member(self, member: User) -> None:
        if member in self.members:
            self.members.remove(member)
    
    def set_owner(self, member: User) -> None:
        self.owner = member

    def get_member_id(self) -> list[str]:
        return [ member.id for member in self.members ]

class Elector(User):
    def __init__(self, id: str) -> None:
        super().__init__(id)
        self.votes: list[str] = []