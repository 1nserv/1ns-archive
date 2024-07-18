import time

import deta

from .cls.entities import *
from .cls.archives import *
from .cls.republic import *
from .cls.bank import *

from .cls.exceptions import *

class EntityInstance:
    def __init__(self, token: str) -> None:
        self.db = deta.Deta(token)
        self.base = self.db.Base('entities')
        self.electors = self.db.Base('electors')
        self.archives = self.db.Base('archives')
        self.avatars = self.db.Drive('avatars')

    def get_entity(self, id: str) -> User | Organization | Entity:
        id = id.upper()
        _data = self.base.get(id)

        if _data is None:
            return Entity("0")

        if _data['_type'] == 'user':
            entity = User(id)

            entity.xp = _data['xp']
            entity.boosts = _data['boosts']
        elif _data['_type'] == 'organization':
            entity = Organization(id)

            entity.owner = self.get_entity(_data['owner_id'].upper())
            entity.members = [
                self.get_entity(_id) for _id in _data['members']
            ]

            entity.avatar = self.avatars.get(id).read()

            entity.certifications = _data['certifications']
        else:
            entity = Entity(id)

        entity.name = _data['name']
        entity.legalPosition = _data['legalPosition'] # Métier si c'est un utilisateur, domaine professionnel si c'est un collectif
        entity.registerDate = _data['registerDate']

        return entity

    def save_entity(self, entity: Entity) -> None:
        _base = self.base
        _data = {
            '_type': 'user' if type(entity) == User else 'organization' if type(entity) == Organization else 'unknown',
            'name': entity.name,
            'legalPosition': entity.legalPosition,
            'registerDate': entity.registerDate
        }

        if type(entity) == Organization:
            _data['owner_id'] = entity.owner.id.upper() if entity.owner else "0"
            _data['members'] = [ member.id.upper() for member in entity.members ] if entity.members else []
            _data['certifications'] = entity.certifications

            self.avatars.put(name = entity.id, data = entity.avatar)
        elif type(entity) == User:
            _data['xp'] = entity.xp
            _data['boosts'] = entity.boosts

        _base.put(_data, entity.id.upper(), expire_in = 3 * 31536000) # Données supprimées tous les trois ans
    
    def delete_entity(self, entity: Entity) -> None:
        self.base.delete(entity.id.upper())

        if type(entity) == Organization:
            self.avatars.delete(entity.id.upper())

    def get_elector(self, id: str) -> Elector:
        id = id.upper()
        _data = self.electors.get(id)

        if _data is None:
            self.save_elector(Elector(id))
            return Elector(id)
        
        elector = Elector(id)
        elector.votes = _data['votes']
        
        return elector

    def save_elector(self, elector: Elector):
        _data = {
            "votes": elector.votes
        }

        self.electors.put(_data, elector.id.upper())
    
    # Les archives ne permettent pas de garder une trace des votes
    # Donc je préfère aucune fonction permettant de les supprimer

    def fetch_entities(self, query = None, listquery: dict | None = None) -> list[Entity | User | Organization]:
        _res = self.base.fetch(query).items

        if listquery is not None:
            for item in _res:
                for target, value in listquery.items():
                    if value not in item[target]:
                        _res.remove(item)
        
        return [ self.get_entity(entity['key']) for entity in _res ]

    def get_entity_groups(self, id: str) -> list[Organization]:
        groups = self.fetch_entities({'_type': 'organization'}, {'members': id})
        
        return [ self.get_entity(group['key']) for group in groups ]
    
    def _add_archive(self, archive: Action):
        _data = archive.__dict__.copy()

        if type(archive) == Sanction:
            _data['type'] = "sanction"
        elif type(archive) == AdminAction:
            _data['type'] = "adminaction"
        else:
            _data['type'] = "unknown"
        
        del _data['id']

        self.archives.put(key = archive.id, data = _data)

    def _get_archive(self, id: str) -> Action | Sanction | AdminAction:
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

    def get_vote(self, id: str) -> Vote | ClosedVote:
        id = id.upper()
        _data = self.votes.get(id)

        if _data is None:
            return None
        
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

    def save_vote(self, vote: Vote | ClosedVote):
        _data = {
            '_type': 'open' if type(vote) == Vote else 'closed' if type(vote) == ClosedVote else 'unknown',
            'title': vote.title,
            'author': vote.author,
            'startDate': vote.startDate,
            'endDate': vote.endDate,
            'choices': vote.choices
        }

        self.votes.put(_data, vote.id.upper())

    def get_official(self, id: str, current_mandate: bool = True) -> FunctionalUser:
        archives = self.mandate if current_mandate else self.archives

        _contributions = archives.fetch({'author': id, 'type': 'contrib'}).items
        _mandates = archives.fetch({'target': id, 'type': 'election'}).items\
                    + archives.fetch({'target': id, 'type': 'promotion'}).items

        user = FunctionalUser(id)
        for mandate in _mandates:
            if mandate['position'].startswith('MIN'): mandate['position'] = 'MIN'

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
        gov = Government(FunctionalUser('0'))
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

    def new_mandate(self, institutions: Institutions, weeks: int = 4):
        for item in self.mandate.fetch().items:
            if item['date'] >= round(time.time()) - weeks * 604800:
                self.mandate.delete(item['id'])
        
        self.update_institutions(institutions)

    def _add_archive(self, archive: Action):
        _data = archive.__dict__.copy()

        if type(archive) == Election:
            _data['type'] = "election"
        elif type(archive) == Promotion:
            _data['type'] = "promotion"
        elif type(archive) == Demotion:
            _data['type'] = "demotion"
        else:
            _data['type'] = "unknown"
        
        del _data['id']

        self.archives.put(key = archive.id, data = _data)

    def _get_archive(self, id: str) -> Action | Election | Promotion | Demotion:
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

    def get_account(self, id: str) -> BankAccount:
        id = id.upper()
        _data = self.accounts.get(id)

        if _data is None:
            return None
        
        acc = BankAccount(id)
        acc.amount = _data['amount']
        acc.locked = _data['locked']
        acc.owner = _data['owner_id']
        acc.bank = _data['bank']

        return acc

    def save_account(self, acc: BankAccount):
        _data = {
            'amount': acc.amount,
            'locked': acc.locked, 
            'owner_id': acc.owner, 
            'bank': acc.bank
        }

        self.accounts.put(_data, acc.id.upper())
    
    def lock_account(self, acc: BankAccount):
        acc.locked = True

        self.save_account(acc)

    def _add_archive(self, _archive: Action):
        _data = _archive.__dict__.copy()

        if type(_archive) == Transaction:
            _data['type'] = "transaction"
        else:
            _data['type'] = "unknown"
        
        del _data['id']

        self.archives.put(key = _archive.id, data = _data)

    def _get_archive(self, id: str) -> Action | Transaction:
        _data = self.archives.get(id)

        if _data is None:
            return None
        
        if _data['type'] == "transaction":
            archive = Transaction(_data['author'], _data['target'], _data['amount'])

            archive.reason = _data['reason']
            archive.currency = _data['currency']
        else:
            archive = Action(_data['author'], _data['target'])
        
        archive.id = id
        archive.action = _data['action']
        archive.date = _data['date']

        return archive
    
    def _fetch_archives(self, **query) -> list[ Action | Transaction ]:
        _res = self.archives.fetch(query).items
        
        return [ self._get_archive(archive['key']) for archive in _res ]