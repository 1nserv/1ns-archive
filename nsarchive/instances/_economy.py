import time

from supabase import create_client

from ..cls.base import *
from ..cls.archives import *
from ..cls.economy import *

from ..cls.exceptions import *

class EconomyInstance(Instance):
    """Gère les interactions avec les comptes bancaires, les transactions, et le marché."""

    def __init__(self, id: str, token: str) -> None:
        super().__init__(create_client(f"https://{id}.supabase.co", token))

    """
    ---- COMPTES EN BANQUE ----
    """

    def get_account(self, id: NSID) -> BankAccount:
        """
        Récupère les informations d'un compte bancaire.

        ## Paramètres
        id: `NSID`\n
            ID du compte.

        ## Renvoie
        - `.BankAccount`
        """

        id = NSID(id)
        _data = self._get_by_ID('accounts', id)

        if _data is None:
            return None

        account = BankAccount(id)
        account.amount = _data['amount']
        account.frozen = _data['frozen']
        account.owner = NSID(_data['owner_id'])
        account.bank = _data['bank']
        account.income = _data['income']

        return account

    def save_account(self, account: BankAccount):
        """
        Sauvegarde un compte bancaire dans la base de données.

        ## Paramètres
        - account: `.BankAccount`\n
            Compte à sauvegarder
        """

        _data = {
            'id': NSID(account.id),
            'amount': account.amount,
            'frozen': account.frozen, 
            'owner_id': account.owner, 
            'bank': account.bank,
            'income': account.income
        }

        self._put_in_db('accounts', _data)

    def freeze_account(self, account: BankAccount):
        """
        Gèle un compte bancaire pour empêcher toute transaction.

        ## Paramètres
        - account: `.BankAccount`\n
            Compte à geler
        """

        account.id = NSID(account.id)
        account.frozen = True

        self.save_account(account)

    """
    ---- OBJETS & VENTES ----
    """

    def save_item(self, item: Item):
        """
        Sauvegarde des infos à propos d'un item.

        ## Paramètres
        item: `.Item`\n
            Article à sauvegarder
        """

        _item = item.__dict__
        self._put_in_db('items', _item)

    def get_item(self, id: NSID) -> Item | None:
        """
        Récupère des informations à propos d'un item.

        ## Paramètres
        id: `NSID`\n
            ID de l'item

        ## Retourne
        - `.Item` si quelque chose est trouvé, sinon
        - `None`
        """

        _item = self._get_by_ID('items', id)

        if _item is None:
            return

        item = Item(id)
        item.title = _item['title']
        item.emoji = _item['emoji']

        return item

    def delete_item(self, item: Item):
        """
        Annule le référencement d'un item.

        ## Paramètres
        item: `.Item`\n
            Item à supprimer
        """

        self._delete_by_ID('items', item.id)

    def get_sale(self, id: NSID) -> Sale | None:
        """
        Récupère une vente disponible sur le marketplace.

        ## Paramètres
        id: `NSID`\n
            ID de la vente.

        ## Renvoie
        - `.Sale | None`: Le résultat de la vente
        """

        id = NSID(id)

        _data = self._get_by_ID('market', id)

        if _data is None:
            return None

        item = self.get_item(_data['id'])

        sale = Sale(NSID(id), Item(_data['id']) if item is None else item)
        sale.__dict__ = _data

        return sale

    def sell_item(self, item: Item, quantity: int, price: int, seller: NSID):
        """
        Vend un item sur le marché.

        ## Paramètres
        item: `.Item`\n
            Item à vendre
        quantity: `int`\n
            Nombre d'items à vendre
        price: `int`\n
            Prix à l'unité de chaque objet
        seller: `NSID`\n
            ID de l'auteur de la vente
        """

        sale = Sale(NSID(round(time.time()) * 16 ** 3), item)
        sale.quantity = quantity
        sale.price = price
        sale.seller_id = seller

        _data = sale.__dict__.copy()

        self._put_in_db('market', _data)

    def delete_sale(self, sale: Sale) -> None:
        """Annule une vente sur le marketplace."""

        sale.id = NSID(sale.id)
        self._delete_by_ID('market', NSID(sale.id))

    """
    ---- INVENTAIRES ----
    """

    def get_inventory(self, id: NSID) -> Inventory | None:
        """
        Récupérer un inventaire dans la base des inventaires.

        ## Paramètres
        id: `NSID`\n
            ID du propriétaire de l'inventaire

        ## Retourne
        - `.Inventory | None`: L'inventaire s'il a été trouvé
        """

        _data = self._get_by_ID('inventories', id)

        if _data is None:
            return None

        inventory = Inventory(id)

        for _item in _data['objects']:
            item = self.get_item(_item)

            inventory.objects.append(item)

        return inventory

    def save_inventory(self, inventory: Inventory):
        """
        Sauvegarder un inventaire

        ## Paramètres
        inventory: `.Inventory`\n
            Inventaire à sauvegarder
        """

        _data = inventory.__dict__

        self._put_in_db('inventories', _data)

    def delete_inventory(self, inventory: Inventory):
        """
        Supprime un inventaire

        ## Paramètres
        inventory: `.Inventory`
            Inventaire à supprimer
        """

        self._delete_by_ID('inventories', inventory.owner_id)

    """
    ---- ARCHIVES ----
    """

    def _add_archive(self, archive: Archive):
        """
        Ajoute une archive d'une transaction ou d'une vente dans la base de données.

        ## Paramètres
        - archive: `.Archive`\n
            Archive à ajouter
        """

        archive.id = NSID(archive.id)
        archive.author = NSID(archive.author)
        archive.target = NSID(archive.target)

        _data = archive.__dict__.copy()

        if type(archive) == Transaction:
            _data['_type'] = "transaction"
        else:
            _data['_type'] = "action"

        self._put_in_db('archives', _data)

    def _get_archive(self, id: NSID) -> Archive | Transaction:
        """
        Récupère une archive spécifique.

        ## Paramètres
        id: `NSID`\n
            ID de l'archive.

        ## Renvoie
        - `.Archive | .Transaction`
        """

        id = NSID(id)
        _data = self._get_by_ID('archives', id)

        if _data is None:
            return None

        if _data['_type'] == "transaction":
            archive = Transaction(_data['author'], _data['target'])
        else:
            archive = Archive(_data['author'], _data['target'])

        archive.id = id
        archive.action = _data['action']
        archive.date = _data['date']
        archive.details = _data['details']

        return archive

    def _fetch_archives(self, **query) -> list[ Archive | Transaction ]:
        """
        Récupère une liste d'archives correspondant à la requête.

        ## Paramètres
        query: `dict`\n
            Requête pour filtrer les archives.

        ## Renvoie
        - `list[.Archive | .Transaction]`
        """

        _res = self.fetch('archives', **query)

        return [ self._get_archive(archive['id']) for archive in _res ]