from .base import NSID

class BankAccount:
    """
    Compte en banque d'une entité, individuelle ou collective.

    ## Attributs
    - id: `NSID`\n
        Identifiant du compte
    - owner: `NSID`\n
        Identifiant du titulaire du compte
    - amount: `int`\n
        Somme d'argent totale sur le compte
    - frozen: `bool`\n
        État gelé ou non du compte
    - bank: `NSID`\n
        Identifiant de la banque qui détient le compte
    - income: `int`\n
        Somme entrante sur le compte depuis la dernière réinitialisation (tous les ~ 28 jours)
    """

    def __init__(self, id: NSID) -> None:
        self.id: NSID = NSID(id)
        self.owner: NSID = NSID(0)
        self.amount: int = 0
        self.frozen: bool = False
        self.bank: NSID = NSID("6")

        self.income: int = 0

class Item:
    """
    Article d'inventaire qui peut circuler sur le serveur

    ## Attributs
    - id: `NSID`\n
        Identifiant de l'objet
    - title: `str`\n
        Nom de l'objet
    - emoji: `str`\n
        Emoji lié à l'objet
    """

    def __init__(self, id: NSID) -> None:
        self.id: NSID = NSID(id)
        self.title: str = "Unknown Object"
        self.emoji: str = ":light_bulb:"

class Inventory:
    """
    Inventaire d'un membre

    ## Attributs
    - owner_id: `NSID`\n
        ID du propriétaire de l'inventaire
    - objects: `dict[str, NSID]`\n
        Collection d'objets et leur quantité
    """

    def __init__(self, owner_id: NSID) -> None:
        self.owner_id: NSID = NSID(owner_id)
        self.objects: dict[str, NSID] = {}

    def append(self, item: Item, quantity: int = 1):
        if item.id in self.objects.keys():
            self.objects[item.id] += quantity
        else:
            self.objects[item.id] = quantity

    def throw(self, item: Item, quantity: int = 1):
        if item.id in self.objects.keys():
            if self.objects[item.id] > quantity:
                self.objects[item.id] -= quantity
            else:
                self.objects[item.id] = 0

class Sale:
    """
    Vente mettant en jeu un objet

    ## Attributs
    - id: `NSID`\n
        Identifiant de la vente
    - item: `NSID`\n
        Identifiant de l'objet mis en vente
    - quantity: `int`\n
        Quantité d'objets mis en vente
    - price: `int`\n
        Prix total du lot
    - seller_id: `NSID`\n
        Identifiant du vendeur
    """

    def __init__(self, id: NSID, item: Item) -> None:
        self.id: NSID = NSID(id)
        self.item: NSID = NSID(item.id)
        self.quantity: int = 1

        self.price: int = 0
        self.seller_id: NSID = NSID('0')