import time

from .exceptions import *
from .base import NSID

from .. import utils

class PositionPermissions:
    """
    Permissions d'une position à l'échelle du serveur. Certaines sont attribuées selon l'appartenance à divers groupes ayant une position précise
    """

    def __init__(self) -> None:
        # Membres
        self.approve_laws = False # Approuver ou désapprouver les lois proposées (vaut aussi pour la Constitution)
        self.buy_items = False # Acheter des items depuis le marketplace
        self.create_organizations = False # Créer une organisation
        self.edit_constitution = False # Proposer une modification de la Constitution
        self.edit_laws = False # Proposer une modification des différents textes de loi
        self.manage_entities = False # Gérer les membres et les organisations
        self.manage_national_channel = False # Prendre la parole sur la chaîne nationale et avoir une priorité de passage sur les autres chaînes
        self.manage_reports = False # Accepter ou refuser une plainte
        self.manage_state_budgets = False # Gérer les différents budgets de l'État
        self.moderate_members = False # Envoyer des membres en garde à vue, en détention ou toute autre sanction non présente sur le client Discord
        self.propose_new_laws = self.edit_constitution # Proposer un nouveau texte de loi pris en charge par la Constitution
        self.publish_official_messages = False # Publier un message sous l'identité du bot Serveur
        self.sell_items = False # Vendre des objets ou services sur le marketplace
        self.vote_president = False # Participer aux élections présidentielles
        self.vote_representatives = False # Participer aux élections législatives

    def edit(self, **permissions: bool) -> None:
        for perm in permissions.items():
            self.__setattr__(*perm)

class Position:
    """
    Position légale d'une entité

    ## Attributs
    - name: `str`\n
        Titre de la position
    - id: `str`\n
        Identifiant de la position
    - permissions: `.PositionPermissions`\n
        Permissions accordées à l'utilisateur
    """

    def __init__(self, id: str = 'inconnu') -> None:
        self.name: str = "Inconnue"
        self.id = id
        self.permissions: PositionPermissions = PositionPermissions()

    def __repr__(self):
        return self.id

class Entity:
    """
    Classe de référence pour les entités

    ## Attributs
    - id: `NSID`\n
        Identifiant de l'entité
    - name: `str`\n
        Nom d'usage de l'entité
    - registerDate: `int`\n
        Date d'enregistrement de l'entité
    - position: `.Position`\n
        Position légale de l'entité
    - additional: `dict`\n
        Infos supplémentaires exploitables par les bots
    """

    def __init__(self, id: NSID) -> None:
        self.id: NSID = NSID(id) # ID hexadécimal de l'entité (ou nom dans le cas de l'entreprise)
        self.name: str = "Entité Inconnue"
        self.registerDate: int = 0
        self.position: Position = Position()
        self.additional: dict = {}

    def set_name(self, new_name: str) -> None:
        if len(new_name) > 32:
            raise NameTooLongError(f"Name length mustn't exceed 32 characters.")

        self.name = new_name

    def set_position(self, position: Position) -> None:
        self.position = position

    def add_link(self, key: str, value: str | int) -> None:
        if isinstance(value, str) or isinstance(value, int):
            self.additional[key] = value

    def unlink(self, key: str) -> None:
        del self.additional[key]

class User(Entity):
    """
    Entité individuelle

    ## Attributs
    - Tous les attributs de la classe `.Entity`
    - xp: `int`\n
        Points d'expérience de l'entité
    - boosts: `dict[str, int]`\n
        Ensemble des boosts dont bénéficie l'entité
    - permissions: `.PositionPermissions`\n
        Fusion des permissions offertes par la position et les groupes
    - votes: `list[NSID]`\n
        Liste des votes auxquels a participé l'entité
    """

    def __init__(self, id: NSID) -> None:
        super().__init__(NSID(id))

        self.xp: int = 0
        self.boosts: dict[str, int] = {}
        self.permissions: PositionPermissions = PositionPermissions() # Elles seront définies en récupérant les permissions de sa position
        self.votes: list[str] = []

    def add_vote(self, id: NSID):
        self.votes.append(NSID(id))

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
    """
    Permissions d'un utilisateur à l'échelle d'un groupe
    """

    def __init__(self) -> None:
        self.manage_organization = False # Renommer l'organisation, changer le logo
        self.manage_roles = False # Changer les rôles des membres
        self.manage_shares = False # Revaloriser les actions
        self.manage_members = False # Virer quelqu'un d'une entreprise, l'y inviter

    def edit(self, **permissions: bool) -> None:
        for perm in permissions.values():
            self.__setattr__(*perm)

class GroupMember(User):
    """
    Membre au sein d'une entité collective

    ## Attributs
    - Tous les attributs de la classe `.User`
    - permission_level: `int`\n
        Niveau d'accréditation du membre (0 = salarié, 4 = administrateur)
    """

    def __init__(self, id: NSID) -> None:
        super().__init__(id)

        self.permission_level: int = 0

    def group_permissions(self) -> MemberPermissions:
        p = MemberPermissions()

        if self.permission_level >= 1:
            p.manage_members = True

        if self.permission_level >= 2:
            p.manage_shares = True

        if self.permission_level >= 3:
            p.manage_roles = True

        if self.permission_level >= 4:
            p.manage_organization = True

        return p

class Share:
    """
    Action d'une entreprise

    ## Attributs
    - owner: `NSID`\n
        Identifiant du titulaire de l'action
    - price: `int`\n
        Prix de l'action
    """

    def __getstate__(self) -> dict:
        return {
            "owner": self.owner,
            "price": self.price
        }

    def __setstate__(self, state: dict):
        self.owner: NSID = state['owner']
        self.price: int = state['price']

    def __init__(self, owner: NSID = NSID(0x0), price: int = 10):
        self.owner: NSID = owner
        self.price: int = price

    def assign_owner(self, owner: NSID):
        self.owner = owner

    def set_price(self, price: int):
        self.price = price

class Organization(Entity):
    """
    Entité collective

    ## Attributs
    - Tous les attributs de la classe `.Entity`
    - owner: `.Entity`\n
        Utilisateur ou entreprise propriétaire de l'entité collective
    - avatar: `bytes`\n
        Avatar/logo de l'entité collective
    - certifications: `dict[str, int]`\n
        Liste des certifications et de leur date d'ajout
    - members: `list[.GroupMember]`\n
        Liste des membres de l'entreprise
    - parts: `list[.Share]`\n
        Liste des actions émises par l'entreprise
    """

    def __init__(self, id: NSID) -> None:
        super().__init__(NSID(id))

        self.owner: Entity = User(NSID(0x0))
        self.avatar: bytes = utils.open_asset('default_avatar.png')

        self.certifications: dict = {}
        self.members: list[GroupMember] = []

        self.parts: list[Share] = 50 * [ Share(self.owner.id, 0) ]

    def add_certification(self, certification: str) -> None:
        self.certifications[certification] = round(time.time())

    def has_certification(self, certification: str) -> bool:
        return certification in self.certifications.keys()

    def remove_certification(self, certification: str) -> None:
        del self.certifications[certification]

    def add_member(self, member: GroupMember) -> None:
        if not isinstance(member, GroupMember):
            raise TypeError("Le membre doit être de type GroupMember")

        self.members.append(member)

    def remove_member(self, member: GroupMember) -> None:
        for _member in self.members:
            if _member.id == member.id:
                self.members.remove(_member)

    def append(self, member: GroupMember) -> None:
        self.add_member(member)

    def remove(self, member: GroupMember) -> None:
        self.remove_member(member)

    def set_owner(self, member: User) -> None:
        self.owner = member

    def get_members_by_attr(self, attribute: str = "id") -> list[str]:
        return [ member.__getattribute__(attribute) for member in self.members ]

    def get_shares(self, include_worth: bool = False) -> dict[str, int] | dict[str, dict[str, int]]:
        shares = {}

        for share in self.parts:
            if include_worth:
                if share.owner in shares.keys():
                    shares[share.owner]['count'] += 1
                    shares[share.owner]['worth'] += share.price
                else:
                    shares[share.owner] = {
                        'count': 1,
                        'worth': share.price
                    }
            else:
                if share.owner in shares.keys():
                    shares[share.owner] += 1
                else:
                    shares[share.owner] = 1

        return shares