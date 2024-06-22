import time

import deta

from .cls.entities import *
from .cls.exceptions import *

class EntityInstance:
    def __init__(self, token: str) -> None:
        self.db = deta.Deta(token)
        self.base = self.db.Base('entities')

    def get_entity(self, id: str) -> User | Organization | Entity:
        _base = self.base
        _data = _base.get(id)

        if _data is None:
            return Entity("0")

        if _data['_type'] == 'user':
            entity = User(id)
        elif _data['_type'] == 'organization':
            entity = Organization(id)
        else:
            entity = Entity(id)

        entity.name = _data['name']
        entity.legalPosition = _data['legalPosition'] # Métier si c'est un utilisateur, domaine professionnel si c'est un collectif
        entity.registerDate = _data['registerDate']
        entity.xp = _data['xp']

        if type(entity) == Organization:
            entity.owner = self.get_entity(_data['owner_id'])
            entity.members = [
                self.get_entity(_id) for _id in _data['members']
            ]

            entity.certifications = _data['certifications']
        elif type(entity) == User:
            entity.boosts = _data['boosts']
        
        return entity
    
    def save_entity(self, entity: Entity) -> None:
        _base = self.base
        _data = {
            '_type': 'user' if type(entity) == User else 'organization' if type(entity) == Organization else 'unknown',
            'name': entity.name,
            'legalPosition': entity.legalPosition,
            'registerDate': entity.registerDate,
            'xp': entity.xp
        }

        if type(entity) == Organization:
            _data['owner_id'] = entity.owner.id if entity.owner else Entity(0)
            _data['members'] = [ member.id for member in entity.members ] if entity.members else []
            _data['certifications'] = entity.certifications
        elif type(entity) == User:
            _data['boosts'] = entity.boosts

        _base.put(_data, entity.id, expire_in = 3 * 31536000) # Données supprimées tous les trois ans

    def fetch(self, query = None, listquery: dict | None = None) -> list:
        _res = self.base.fetch(query).items

        if listquery is not None:
            for item in _res:
                for target, value in listquery:
                    if value not in item[target]:
                        _res.remove(item)
        
        return _res
    
    def get_entity_groups(self, id: int) -> list[Organization]:
        groups = self.fetch({'_type': 'organization'}, {'members': str(id)})
        
        return [ self.get_entity(int(group['id'], 16)) for group in groups ]