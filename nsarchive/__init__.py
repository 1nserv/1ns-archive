import time

import deta

from .cls.base import *
from .cls.entities import *
from .cls.archives import *
from .cls.republic import *
from .cls.economy import *

from .cls.exceptions import *

class EntityInstance:
    def __init__(self, token: str) -> None:
        self.db = deta.Deta(token)
        self.base = self.db.Base('entities')
        self.electors = self.db.Base('electors')
        self.archives = self.db.Base('archives')
        self.avatars = self.db.Drive('avatars')
        self.positions = self.db.Base('positions') # Liste des métiers

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
        _data = self.base.get(id)
        _votes = self.electors.get(id)

        if _data is None:
            return Entity("0")

        if _data['_type'] == 'user':
            entity = User(id)

            entity.xp = _data['xp']
            entity.boosts = _data['boosts']
            entity.votes = [ NSID(vote) for vote in _votes['votes'] ]
        elif _data['_type'] == 'organization':
            entity = Organization(id)

            entity.owner = self.get_entity(NSID(_data['owner_id']))
            
            for _member in _data['members']:
                member = GroupMember(_member['id'])
                member.permissions.__dict__ = _member['permissions']

            try:
                entity.avatar = self.avatars.get(id).read()
            except: 
                entity.avatar = None

            entity.certifications = _data['certifications']
        else:
            entity = Entity(id)

        entity.name = _data['name']
        entity.legalPosition = _data['legalPosition'] # Métier si c'est un utilisateur, domaine professionnel si c'est un collectif
        entity.registerDate = _data['registerDate']

        return entity

    def save_entity(self, entity: Entity) -> None:
        """
        Fonction permettant de créer ou modifier une entité.

        ## Paramètres
        entity: `.Entity` ( `.User | .Organization` )
            L'entité à sauvegarder
        """

        entity.id = NSID(entity.id)

        _base = self.base
        _data = {
            '_type': 'user' if type(entity) == User else 'organization' if type(entity) == Organization else 'unknown',
            'name': entity.name,
            'legalPosition': entity.legalPosition,
            'registerDate': entity.registerDate
        }

        if type(entity) == Organization:
            _data['owner_id'] = NSID(entity.owner.id) if entity.owner else NSID("0")
            _data['members'] = []
            _data['certifications'] = entity.certifications

            for member in entity.members:
                _member = {
                    'id': NSID(member.id),
                    'permissions': member.permissions.__dict__.copy()
                }

                _data['members'] += _member                

            self.avatars.put(name = entity.id, data = entity.avatar)
        elif type(entity) == User:
            _data['xp'] = entity.xp
            _data['boosts'] = entity.boosts

        _base.put(_data, entity.id, expire_in = 3 * 31536000) # Données supprimées tous les trois ans

    def delete_entity(self, entity: Entity) -> None:
        """
        Fonction permettant de supprimer le profil d'une entité
        
        ## Paramètres
        entity: `.Entity` ( `.User | .Organization` )
            L'entité à supprimer
        """

        self.base.delete(NSID(entity.id))

        if type(entity) == Organization:
            self.avatars.delete(NSID(entity.id))

    def fetch_entities(self, query: dict = None, listquery: dict | None = None) -> list[ Entity | User | Organization ]:
        _res = self.base.fetch(query).items

        if listquery is not None:
            for item in _res:
                for target, value in listquery.items():
                    if value not in item[target]:
                        _res.remove(item)

        return [ self.get_entity(NSID(entity['key'])) for entity in _res ]

    def get_entity_groups(self, id: str | NSID) -> list[Organization]:
        id = NSID(id)
        groups = self.fetch_entities({'_type': 'organization'}, {'members': id})
        
        return groups

    def get_position(self, id: str | NSID) -> Position:
        id = NSID(id)
        _data = self.positions.get(id)

        if _data is None:
            raise RessourceNotFoundError(f"No position with ID {id}")

        position = Position(id)
        position.name = _data['name']

        for _permission in _data['permissions']:
            position.permissions.__setattr__(_permission, True)

        return position

    def _add_archive(self, archive: Action) -> None:
        archive.id = NSID(archive.id)
        archive.author = NSID(archive.author)
        archive.target = NSID(archive.target)

        _data = archive.__dict__.copy()

        if type(archive) == Sanction:
            _data['type'] = "sanction"
        elif type(archive) == AdminAction:
            _data['type'] = "adminaction"
        else:
            _data['type'] = "unknown"
        
        self.archives.put(key = archive.id, data = _data)

    def _get_archive(self, id: str | NSID) -> Action | Sanction | AdminAction:
        id = NSID(id)
        _data = self.archives.get(id)

        if _data is None:
            return None
        
        if _data['type'] == "sanction": # Mute, ban, GAV, kick, détention, prune (xp seulement)
            archive = Sanction(_data['author'], _data['target'])

            archive.details = _data['details']
            archive.major = _data['major']
            archive.duration = _data['duration']
        elif _data['type'] == "adminaction": # Renommage, promotion, démotion (au niveau de l'état)
            archive = AdminAction(_data['author'], _data['target'])

            archive.details = _data['details']
            archive.new_state = _data['new_state']
        else:
            archive = Action(_data['author'], _data['target'])
        
        archive.id = id
        archive.action = _data['action']
        archive.date = _data['date']

        return archive

    def _fetch_archives(self, **query) -> list[ Action | Sanction | AdminAction ]:
        _res = self.archives.fetch(query).items
        
        return [ self._get_archive(archive['key']) for archive in _res ]

class RepublicInstance:
    def __init__(self, token: str) -> None:
        self.db = deta.Deta(token)
        self.votes = self.db.Base('votes')
        self.archives = self.db.Base('archives')
        self.mandate = self.db.Base('mandate')
        self.functions = self.db.Base('functions') # Liste des fonctionnaires

    def get_vote(self, id: str | NSID) -> Vote | ClosedVote:
        id = NSID(id)
        _data = self.votes.get(id)

        if _data is None:
            raise RessourceNotFoundError(f"The vote #{id} does not exist.")

        if _data['_type'] == 'open':
            vote = Vote(id, _data['title'], tuple(_data['choices'].keys()))
        elif _data['_type'] == 'closed':
            vote = ClosedVote(id, _data['title'])
        else:
            vote = Vote('0', 'Unknown Vote', ())

        vote.author = _data['author']
        vote.startDate = _data['startDate']
        vote.endDate = _data['endDate']
        vote.choices = _data['choices']

        return vote

    def save_vote(self, vote: Vote | ClosedVote) -> None:
        vote.id = NSID(vote.id)

        _data = {
            '_type': 'open' if type(vote) == Vote else 'closed' if type(vote) == ClosedVote else 'unknown',
            'title': vote.title,
            'author': NSID(vote.author),
            'startDate': vote.startDate,
            'endDate': vote.endDate,
            'choices': vote.choices
        }

        self.votes.put(_data, vote.id)

    def get_official(self, id: str | NSID, current_mandate: bool = True) -> Official:
        id = NSID(id)

        archives = self.mandate if current_mandate else self.archives

        _contributions = archives.fetch({'author': id, 'type': 'contrib'}).items
        _mandates = archives.fetch({'target': id, 'type': 'election'}).items\
                    + archives.fetch({'target': id, 'type': 'promotion'}).items

        user = Official(id)
        for mandate in _mandates:
            if mandate['position'].startswith('MIN'):
                mandate['position'] = 'MIN'

            try:
                user.mandates[mandate['position']] += 1
            except KeyError:
                user.mandates[mandate['position']] = 1

        for contrib in _contributions:
            try:
                user.contributions[contrib['action']] += 1
            except KeyError:
                user.contributions[contrib['action']] = 1

        return user

    def get_institutions(self) -> Organization:
        admin = Administration()
        gov = Government(Official('0'))
        assembly = Assembly()
        court = Court()
        police_forces = PoliceForces()

        _admins = self.functions.get('ADMIN')
        admin.members = [ self.get_official(user) for user in _admins['users'] ]
        admin.president = self.get_official('F7DB60DD1C4300A') # happex (remplace Kheops pour l'instant)

        gov.president = self.get_official(self.functions.get('PRE_REP')['users'][0])

        minister = lambda code : self.get_official(self.functions.get(f'MIN_{code}')['users'][0])
        gov.prime_minister = minister('PRIM')
        gov.economy_minister = minister('ECO')
        gov.inner_minister = minister('INN')
        gov.press_minister = minister('AUD')
        gov.justice_minister = minister('JUS')
        gov.outer_minister = minister('OUT')

        assembly.president = self.get_official(self.functions.get('PRE_AS')['users'][0])
        assembly.members = [ self.get_official(id) for id in self.functions.get('REPR')['users'] ]

        court.president = gov.justice_minister
        court.members = [ self.get_official(id) for id in self.functions.get('JUDGE')['users'] ]

        police_forces.president = gov.inner_minister
        police_forces.members = [ self.get_official(id) for id in self.functions.get('POLICE')['users'] ]

        instits = Institutions()
        instits.administration = admin
        instits.government = gov
        instits.court = court
        instits.assembly = assembly
        instits.police = police_forces

        return instits

    def update_institutions(self, institutions: Institutions):
        """
        Fonction communément appelée après un vote législatif ou une nomination.\n
        Celle-ci met à jour: Le gouvernement (président, ministres), les différents députés et leur président, les différents juges, les différents policiers.\n

        ## Paramètres
        institutions: `.Institutions`\n
            Le nouvel état des institutions, à sauvegarder.
        """

        get_ids = lambda institution : [ member.id for member in institutions.__getattribute__(institution).members ]

        self.functions.put(key = 'ADMIN', data = { 'users': get_ids('administration') })
        self.functions.put(key = 'REPR', data = { 'users': get_ids('assembly') })
        self.functions.put(key = 'JUDGE', data = { 'users': get_ids('court') })
        self.functions.put(key = 'POLICE', data = { 'users': get_ids('police') })

        self.functions.put(key = 'PRE_AS', data = { 'users': [ institutions.assembly.president.id ] })
        self.functions.put(key = 'PRE_REP', data = { 'users': [ institutions.government.president.id ] })

        self.functions.put(key = 'MIN_PRIM', data = { 'users': [ institutions.government.prime_minister.id ] })
        self.functions.put(key = 'MIN_INN', data = { 'users': [ institutions.government.inner_minister.id ] })
        self.functions.put(key = 'MIN_JUS', data = { 'users': [ institutions.government.justice_minister.id ] })
        self.functions.put(key = 'MIN_ECO', data = { 'users': [ institutions.government.economy_minister.id ] })
        self.functions.put(key = 'MIN_AUD', data = { 'users': [ institutions.government.press_minister.id ] })
        self.functions.put(key = 'MIN_OUT', data = { 'users': [ institutions.government.outer_minister.id ] })

    def new_mandate(self, institutions: Institutions, weeks: int = 4) -> None:
        """
        Fonction qui amène à supprimer toutes les archives du mandat précédent
        """

        for item in self.mandate.fetch().items:
            if item['date'] >= round(time.time()) - weeks * 604800: # On évite de supprimer les informations écrites lors de la période définie
                self.mandate.delete(item['id'])

        self.update_institutions(institutions)

    def _add_archive(self, archive: Action) -> None:
        archive.id = NSID(archive.id)
        _data = archive.__dict__.copy()

        if type(archive) == Election:
            _data['type'] = "election"
        elif type(archive) == Promotion:
            _data['type'] = "promotion"
        elif type(archive) == Demotion:
            _data['type'] = "demotion"
        else:
            _data['type'] = "unknown"

        self.archives.put(key = archive.id, data = _data)
        self.mandate.put(key = archive.id, data = _data) # Ajouter les archives à celle du mandat actuel

    def _get_archive(self, id: str | NSID) -> Action | Election | Promotion | Demotion:
        id = NSID(id)
        _data = self.archives.get(id)

        if _data is None:
            return None

        if _data['type'] == "election":
            archive = Election(_data['author'], _data['target'], _data['position'])

            archive.positive_votes = _data['positive_votes']
            archive.total_votes = _data['total_votes']
        elif _data['type'] == "promotion":
            archive = Promotion(_data['author'], _data['target'], _data['position'])
        elif _data['type'] == "demotion":
            archive = Demotion(_data['author'], _data['target'])

            archive.reason = _data['reason']
        else:
            archive = Action(_data['author'], _data['target'])

        archive.id = id
        archive.action = _data['action']
        archive.date = _data['date']

        return archive

    def _fetch_archives(self, **query) -> list[ Action | Election | Promotion | Demotion ]:
        _res = self.archives.fetch(query).items
        
        return [ self._get_archive(archive['key']) for archive in _res ]

class BankInstance:
    def __init__(self, token: str) -> None:
        self.db = deta.Deta(token)
        self.archives = self.db.Base('archives')
        self.accounts = self.db.Base('accounts')
        self.registry = self.db.Base('banks')
        self.marketplace = self.db.Base('shop')

    def get_account(self, id: str | NSID) -> BankAccount:
        id = NSID(id)
        _data = self.accounts.get(id)

        if _data is None:
            return None

        account = BankAccount(id)
        account.amount = _data['amount']
        account.locked = _data['locked']
        account.owner = _data['owner_id']
        account.bank = _data['bank']

        return account

    def save_account(self, account: BankAccount):
        _data = {
            'amount': account.amount,
            'locked': account.locked, 
            'owner_id': account.owner, 
            'bank': account.bank
        }

        self.accounts.put(_data, NSID(account.id))

    def lock_account(self, account: BankAccount):
        account.id = account.id.upper()
        account.locked = True

        self.save_account(account)

    def get_item(self, id: str) -> Item | None:
        id = id.upper()

        _data = self.marketplace.get(id)

        if _data is None:
            return None

        item = Item(id)
        item.title = _data['title']
        item.emoji = _data['emoji']
        item.seller_id = _data['seller']
        item.price = _data['price']

        return item

    def save_item(self, item: Item) -> None:
        item.id = item.id.upper()

        _data = item.__dict__.copy()

        self.marketplace.put(key = id, data = _data)

    def delete_item(self, item: Item) -> None:
        item.id = item.id.upper()
        self.marketplace.delete(item.id)

    def _add_archive(self, archive: Action):
        archive.id = archive.id.upper()
        archive.author = archive.author.upper()
        archive.target = archive.target.upper()

        _data = archive.__dict__.copy()

        if type(archive) == Transaction:
            _data['type'] = "transaction"
            archive.currency = archive.currency.upper()
        elif type(archive) == Sale:
            _data['type'] = "sale"
        else:
            _data['type'] = "unknown"

        self.archives.put(key = archive.id, data = _data)

    def _get_archive(self, id: str) -> Action | Transaction:
        id = id.upper()
        _data = self.archives.get(id)

        if _data is None:
            return None

        if _data['type'] == "transaction":
            archive = Transaction(_data['author'], _data['target'], _data['amount'])

            archive.reason = _data['reason']
            archive.currency = _data['currency']
        elif _data['type'] == "sale":
            archive = Sale(_data['author'], _data['target'])

            archive.price = _data['price']
        else:
            archive = Action(_data['author'], _data['target'])

        archive.id = id
        archive.action = _data['action']
        archive.date = _data['date']

        return archive

    def _fetch_archives(self, **query) -> list[ Action | Transaction ]:
        _res = self.archives.fetch(query).items

        return [ self._get_archive(archive['key']) for archive in _res ]