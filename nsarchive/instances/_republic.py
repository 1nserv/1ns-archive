import time

from supabase import create_client

from ..cls.base import *
from ..cls.archives import *
from ..cls.republic import *

from ..cls.exceptions import *


class RepublicInstance(Instance):
    """
    Gère les interactions avec les votes, les archives de la république, et les fonctionnaires.

    ## Informations
    - Résultats des votes: `.Vote | .ClosedVote`
    - Différentes institutions: `.Institutions | .Administration | .Government | .Assembly | .Court | .PoliceForces`
    - Occupants des différents rôles et historique de leurs actions: `.Official`
    """

    def __init__(self, id: str, token: str) -> None:
        super().__init__(create_client(f"https://{id}.supabase.co", token))
    
    """
    ---- VOTES & REFERENDUMS ----
    """

    def get_vote(self, id: str | NSID) -> Vote | ClosedVote | Lawsuit:
        """
        Récupère un vote spécifique.

        ## Paramètres
        id: `str | NSID`\n
            ID du vote.

        ## Renvoie
        - `.Vote | .ClosedVote`
        """

        id = NSID(id)
        _data = self._get_by_ID('votes', id)

        if _data is None:
            return None

        if _data['_type'] == 'open':
            vote = Vote(id, _data['title'], tuple(_data['choices'].keys()))
        elif _data['_type'] == 'closed':
            vote = ClosedVote(id, _data['title'])
        elif _data['_type'] == 'lawsuit':
            vote = Lawsuit(id, _data['title'])
        else:
            vote = Vote('0', 'Unknown Vote', ())

        vote.author = _data['author']
        vote.startDate = _data['startDate']
        vote.endDate = _data['endDate']
        vote.choices = _data['choices']

        return vote

    def save_vote(self, vote: Vote | ClosedVote) -> None:
        """Sauvegarde un vote dans la base de données."""

        vote.id = NSID(vote.id)

        _data = {
            '_type':'open' if type(vote) == Vote else\
                    'closed' if type(vote) == ClosedVote else\
                    'lawsuit' if type(vote) == Lawsuit else\
                    'unknown',
            'title': vote.title,
            'author': NSID(vote.author),
            'startDate': vote.startDate,
            'endDate': vote.endDate,
            'choices': vote.choices
        }

        self._put_in_db('votes', _data)

    # Aucune possibilité de supprimer un vote

    """
    ---- INSTITUTION & MANDAT ----
    """

    def get_official(self, id: str | NSID, current_mandate: bool = True) -> Official:
        """
        Récupère les informations d'un fonctionnaire (mandats, contributions).

        ## Paramètres
        id: `str | NSID`\n
            ID du fonctionnaire.
        current_mandate: `bool`\n
            Indique si l'on doit récupérer le mandat actuel ou les anciens mandats.

        ## Renvoie
        - `.Official`
        """

        id = NSID(id)

        base = 'mandate' if current_mandate else 'archives'

        _contributions = self.fetch(base, {'author': id, '_type': 'contrib'})
        _mandates = self.fetch(base, {'target': id, '_type': 'election'}) +\
                    self.fetch(base, {'target': id, '_type': 'promotion'})

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

    def get_institutions(self) -> State:
        """Récupère l'état actuel des institutions de la république."""

        admin = Administration()
        gov = Government(Official('0'))
        assembly = Assembly()
        court = Court()
        police_forces = PoliceForces()

        _get_position: list[dict] = lambda pos : self._select_from_db('functions', 'id', pos)['users']

        admin.members = [ self.get_official(user['id']) for user in _get_position('ADMIN') ]
        admin.president = self.get_official('F7DB60DD1C4300A') # happex (remplace Kheops pour l'instant)

        gov.president = self.get_official([0])

        minister = lambda code : self.get_official(_get_position(f'MIN_{code}')[0]['id'])
        gov.prime_minister = minister('PRIM')
        gov.economy_minister = minister('ECO')
        gov.inner_minister = minister('INN')
        gov.press_minister = minister('AUD')
        gov.justice_minister = minister('JUS')
        gov.outer_minister = minister('OUT')

        assembly.president = self.get_official(_get_position('PRE_AS')[0])
        assembly.members = [ self.get_official(user['id']) for user in _get_position('REPR') ]

        court.president = gov.justice_minister
        court.members = [ self.get_official(user['id']) for user in _get_position('JUDGE') ]

        police_forces.president = gov.inner_minister
        police_forces.members = [ self.get_official(user['id']) for user in _get_position('POLICE') ]

        instits = State()
        instits.administration = admin
        instits.government = gov
        instits.court = court
        instits.assembly = assembly
        instits.police = police_forces

        return instits

    def update_institutions(self, institutions: State):
        """
        Fonction communément appelée après un vote législatif ou une nomination.\n
        Celle-ci met à jour: Le gouvernement (président, ministres), les différents députés et leur président, les différents juges, les différents policiers.\n

        ## Paramètres
        institutions: `.Institutions`\n
            Le nouvel état des institutions, à sauvegarder.
        """

        get_ids = lambda institution : [ member.id for member in institutions.__getattribute__(institution).members ]

        self._put_in_db('functions', { 'users': get_ids('administration') })
        self._put_in_db('functions', { 'users': get_ids('assembly') })
        self._put_in_db('functions', { 'users': get_ids('court') })
        self._put_in_db('functions', { 'users': get_ids('police') })

        self._put_in_db('functions', { 'users': [ institutions.assembly.president.id ] })
        self._put_in_db('functions', { 'users': [ institutions.government.president.id ] })

        self._put_in_db('functions', { 'users': [ institutions.government.prime_minister.id ] })
        self._put_in_db('functions', { 'users': [ institutions.government.inner_minister.id ] })
        self._put_in_db('functions', { 'users': [ institutions.government.justice_minister.id ] })
        self._put_in_db('functions', { 'users': [ institutions.government.economy_minister.id ] })
        self._put_in_db('functions', { 'users': [ institutions.government.press_minister.id ] })
        self._put_in_db('functions', { 'users': [ institutions.government.outer_minister.id ] })

    def new_mandate(self, institutions: State, weeks: int = 4) -> None:
        """
        Fonction qui amène à supprimer toutes les archives du mandat précédent
        """

        for item in self.fetch('mandate'):
            if item['date'] >= round(time.time()) - weeks * 604800: # On évite de supprimer les informations écrites lors de la période définie
                self._delete_by_ID('mandate', item['id'])

        self.update_institutions(institutions)

    """
    ---- ARCHIVES ----
    """

    def _add_archive(self, archive: Archive) -> None:
        """Ajoute une archive d'une action (élection, promotion, ou rétrogradation) dans la base de données."""

        archive.id = NSID(archive.id)
        _data = archive.__dict__.copy()

        if type(archive) == Election:
            _data['_type'] = "election"
        elif type(archive) == Promotion:
            _data['_type'] = "promotion"
        elif type(archive) == Demotion:
            _data['_type'] = "demotion"
        else:
            _data['_type'] = "unknown"

        self._put_in_db('archives', _data)
        self._put_in_db('mandate', _data) # Ajouter les archives à celle du mandat actuel

    def _get_archive(self, id: str | NSID) -> Archive | Election | Promotion | Demotion:
        """
        Récupère une archive spécifique.

        ## Paramètres
        id: `str | NSID`\n
            ID de l'archive.

        ## Renvoie
        - `.Archive | .Election | .Promotion | .Demotion`
        """

        id = NSID(id)
        _data = self._get_by_ID('archives', id)

        if _data is None:
            return None

        if _data['_type'] == "election":
            archive = Election(_data['author'], _data['target'], _data['position'])
        elif _data['_type'] == "promotion":
            archive = Promotion(_data['author'], _data['target'], _data['position'])
        elif _data['_type'] == "demotion":
            archive = Demotion(_data['author'], _data['target'])
        else:
            archive = Archive(_data['author'], _data['target'])

        archive.id = id
        archive.action = _data['action']
        archive.date = _data['date']
        archive.details = _data['details']

        return archive

    def _fetch_archives(self, **query) -> list[ Archive | Election | Promotion | Demotion ]:
        """
        Récupère une liste d'archives correspondant à la requête.

        ## Paramètres
        query: `dict`
            Requête pour filtrer les archives.

        ## Renvoie
        - `list[.Archive | .Election | .Promotion | .Demotion]`
        """

        _res = self.fetch('archives', **query)
        
        return [ self._get_archive(archive['id']) for archive in _res ]
