from supabase import create_client

from ..cls.base import *
from ..cls.entities import *
from ..cls.archives import *

from ..cls.exceptions import *

class EntityInstance(Instance):
    """
    Instance qui vous permettra d'interagir avec les profils des membres ainsi que les différents métiers et secteurs d'activité.

    ## Informations disponibles
    - Profil des membres et des entreprises: `.User | .Organization | .Entity`
    - Participation d'un membre à différent votes: `.User | .Organization | .Entity`
    - Appartenance et permissions d'un membre dans un groupe: `.GroupMember.MemberPermissions`
    - Position légale et permissions d'une entité: `.Position.Permissions`
    - Sanctions et modifications d'une entité: `.Action[ .AdminAction | .Sanction ]`
    """

    def __init__(self, id: str, token: str) -> None:
        super().__init__(create_client(f"https://{id}.supabase.co", token))

    """
    ---- ENTITÉS ----
    """

    def get_entity(self, id: str | NSID) -> User | Organization | Entity:
        """
        Fonction permettant de récupérer le profil public d'une entité.\n

        ## Paramètres
        id: `NSID`\n
            ID héxadécimal de l'entité à récupérer

        ## Renvoie
        - `.User` dans le cas où l'entité choisie est un membre
        - `.Organization` dans le cas où c'est un groupe
        - `.Entity` dans le cas où c'est indéterminé
        """

        id = NSID(id)

        _data = self._get_by_ID('individuals', id)

        if _data is None: # Aucune entité individuelle sous cet ID
            _data = self._get_by_ID('organizations', id) # On cherche du côté des groupes
        else:
            _data['_type'] = 'user'

        if _data is None: # ID inexistant chez les entités
            return None
        elif '_type' not in _data.keys(): # S'il existe chez les organisations, clé '_type' pas encore initialisée
            _data['_type'] = 'organization'

        if _data['_type'] == 'user':
            entity = User(id)

            entity.xp = _data['xp']
            entity.boosts = _data['boosts']

            entity.votes = [ NSID(vote) for vote in _data['votes'] ]
        elif _data['_type'] == 'organization':
            entity = Organization(id)

            entity.owner = self.get_entity(NSID(_data['owner_id']))

            for _member in _data['members']:
                member = GroupMember(_member['id'])
                member.permission_level = _member['level']

                _member_profile = self.get_entity(member.id)

                member.set_name(_member_profile.name)
                member.legalPosition = _member_profile.legalPosition
                member.registerDate = _member_profile.registerDate

                member.xp = _member_profile.xp
                member.boosts = _member_profile.boosts

                member.permissions = _member_profile.permissions
                member.votes = _member_profile.votes

                entity.append(member)

            entity.certifications = _data['certifications']
            entity.parts = _data['parts']
        else:
            entity = Entity(id)

        entity.name = _data['name']
        entity.legalPosition = _data['position'] # Métier si c'est un utilisateur, domaine professionnel si c'est un collectif
        entity.registerDate = _data['register_date']

        for  key, value in _data.get('additional', {}).items():
            if isinstance(value, str) and value.startswith('\n'):
                entity.add_link(key, int(value[1:]))
            else:
                entity.add_link(key, value)

        return entity

    def save_entity(self, entity: Entity) -> None:
        """
        Fonction permettant de créer ou modifier une entité.

        ## Paramètres
        entity: `.Entity` ( `.User | .Organization` )
            L'entité à sauvegarder
        """

        entity.id = NSID(entity.id)

        _data = {
            'id': entity.id,
            'name': entity.name,
            'position': entity.legalPosition,
            'register_date': entity.registerDate,
            'additional': {},
        }

        for key, value in entity.additional.items():
            if isinstance(value, int) and len(str(int)) >= 15:
                _data['additional'][key] = '\n' + str(value)
            elif type(value) in (str, int):
                _data['additional'][key] = value

        if type(entity) == Organization:
            _data['owner_id'] = NSID(entity.owner.id) if entity.owner else NSID("0")
            _data['members'] = []
            _data['certifications'] = entity.certifications

            for member in entity.members:
                _member = {
                    'id': NSID(member.id),
                    'position': member.permission_level
                }

                _data['members'] += [_member]                
        elif type(entity) == User:
            _data['xp'] = entity.xp
            _data['boosts'] = entity.boosts
            _data['votes'] = [ NSID(vote) for vote in entity.votes]

        self._put_in_db('individuals' if isinstance(entity, User) else 'organizations', _data)

    def delete_entity(self, entity: Entity) -> None:
        """
        Fonction permettant de supprimer le profil d'une entité

        ## Paramètres
        entity: `.Entity` ( `.User | .Organization` )
            L'entité à supprimer
        """

        self._delete_by_ID('individuals' if isinstance(entity, User) else 'organizations', NSID(entity.id))

    def fetch_entities(self, **query: dict) -> list[ Entity | User | Organization ]:
        """
        Récupère une liste d'entités en fonction d'une requête.

        ## Paramètres
        query: `dict`
            La requête pour filtrer les entités.

        ## Renvoie
        - `list[Entity | User | Organization]`
        """

        _res = self.fetch('entities', **query)

        return [ self.get_entity(NSID(entity['key'])) for entity in _res if entity is not None ]

    def get_entity_groups(self, id: str | NSID) -> list[Organization]:
        """
        Récupère les groupes auxquels appartient une entité.

        ## Paramètres
        id: `str | NSID`
            ID de l'entité.

        ## Renvoie
        - `list[Organization]`
        """

        id = NSID(id)
        groups = self.fetch_entities(_type = 'organization')
        groups.extend(self.fetch_entities(_type = 'organization', owner_id = id))

        for group in groups:
            if group is None:
                groups.remove(group)
                continue

            if group.owner.id == id:
                continue

            for member in group.members:
                if member.id == id:
                    break
            else:
                groups.remove(group)

        return [ group for group in groups if group is not None ]

    def get_position(self, id: str) -> Position:
        """
        Récupère une position légale (métier, domaine professionnel).

        ## Paramètres
        id: `str`
            ID de la position (SENSIBLE À LA CASSE !)

        ## Renvoie
        - `.Position`
        """

        _data = self._get_by_ID('positions', id)

        if _data is None:
            return None

        position = Position(id)
        position.name = _data['name']
        position.permissions.edit(dict(zip(_data['permissions'], True)))

        return position

    """
    ---- ARCHIVES --
    """

    def _add_archive(self, archive: Archive) -> None:
        """
        Ajoute une archive d'une action (modification au sein d'un groupe ou sanction) dans la base de données.
        """

        archive.id = NSID(archive.id)
        archive.author = NSID(archive.author)
        archive.target = NSID(archive.target)

        _data = archive.__dict__.copy()

        if type(archive) == Sanction:
            _data['_type'] = "sanction"
        elif type(archive) == Report:
            _data['_type'] = "report"
        else:
            _data['_type'] = "unknown"

        self._put_in_db('archives', _data)

    def _get_archive(self, id: str | NSID) -> Archive | Sanction:
        """
        Récupère une archive spécifique.

        ## Paramètres
        id: `str | NSID`
            ID de l'archive.

        ## Renvoie
        - `.Archive | .Sanction `
        """

        id = NSID(id)
        _data = self._get_by_ID('archives', id)

        if _data is None:
            return None

        if _data['_type'] == "sanction": # Mute, ban, GAV, kick, détention, prune (xp seulement)
            archive = Sanction(_data['author'], _data['target'])
        elif _data['_type'] == "report": # Plainte
            archive = Report(_data['author'], _data['target'])
        else:
            archive = Archive(_data['author'], _data['target'])

        archive.id = id
        archive.date = _data['date']
        archive.action = _data['action']
        archive.details = _data['details']

        return archive

    def _fetch_archives(self, **query) -> list[ Archive | Sanction ]:
        """
        Récupère une liste d'archives correspondant à la requête.

        ## Paramètres
        query: `dict`
            Requête pour filtrer les archives.

        ## Renvoie
        - `list[.Archive | .Sanction]`
        """

        _res = self.fetch('archives', **query)

        return [ self._get_archive(archive['id']) for archive in _res ]
