import typing

from supabase import Client

class NSID(str):
    unknown = "0"
    admin = "1"
    gov = "2"
    court = "3"
    assembly = "4"
    office = "5"
    hexabank = "6"
    archives = "7"

    maintenance_com = "101"
    audiovisual_dept = "102"
    interior_dept = "103"
    justice_dept = "104"
    egalitary_com = "105"
    antifraud_dept = "106"

    def __new__(cls, value):
        if type(value) == int:
            value = hex(value)
        elif type(value) in (str, NSID):
            value = hex(int(value, 16))
        else:
            raise TypeError(f"<{value}> is not NSID serializable")

        if value.startswith("0x"):
            value = value[2:]

        instance = super(NSID, cls).__new__(cls, value.upper())
        return instance

class Instance:
    def __init__(self, client: Client):
        self.db = client

    def _select_from_db(self, table: str, key: str, value: str) -> list:
        """
        Récupère des données JSON d'une table Supabase en fonction de l'ID.

        ## Paramètres
        table: `str`:\n
            Nom de la base
        key: `str`\n
            Clé à vérifier
        value: `str`\n
            Valeur de la clé à vérifier

        ## Renvoie
        - `list` de tous les élements correspondants
        - `None` si aucune donnée n'est trouvée
        """

        res = self.db.from_(table).select("*").eq(key, value).execute()

        if res.data:
            return res.data
        else:
            return None

    def _get_by_ID(self, table: str, id: NSID) -> dict:
        _data = self._select_from_db(table, 'id', id)

        if _data is not None:
            _data = _data[0]

        return _data

    def _put_in_db(self, table: str, data: dict) -> None:
        """
        Publie des données JSON dans une table Supabase en utilisant le client Supabase.

        :param table: Nom de la table dans laquelle les données doivent être insérées
        :param data: Dictionnaire contenant les données à publier
        :return: Résultat de l'insertion
        """

        res = self.db.from_(table).upsert(data).execute()

        return res

    def _delete_from_db(self, table: str, key: str, value: str):
        """
        Supprime un enregistrement d'une table Supabase en fonction d'une clé et de sa valeur.

        ## Paramètres
        table: `str`
            Nom de la table dans laquelle les données doivent être supprimées
        key: `str`
            Clé à vérifier (par exemple "id" ou autre clé unique)
        value: `str`
            Valeur de la clé à vérifier pour trouver l'enregistrement à supprimer

        ## Renvoie
        - `True` si la suppression a réussi
        - `False` si aucune donnée n'a été trouvée ou si la suppression a échoué
        """

        res = self.db.from_(table).delete().eq(key, value).execute()

        return res

    def _delete_by_ID(self, table: str, id: NSID):
        res = self._delete_from_db(table, 'id', id)

        return res

    def fetch(self, table: str, **query: typing.Any) -> list:
        matches = []

        for key, value in query.items():
            entity = self._select_from_db(table, key, value)

            if entity is not None:
                matches.append(entity)

        if not matches or len(matches) != len(query):
            return []

        _res = [ item for item in matches[0] if all(item in match for match in matches[1:]) ]

        return _res

    def _upload_to_storage(self, bucket: str, data: bytes, path: str, overwrite: bool = False) -> dict:
        """
        Envoie un fichier dans un bucket Supabase.

        ## Paramètres
        bucket: `str`\n
            Nom du bucket où le fichier sera stocké
        data: `bytes`\n
            Données à uploader
        path: `str`\n
            Chemin dans le bucket où le fichier sera stocké

        ## Renvoie
        - `dict` contenant les informations de l'upload si réussi
        - `None` en cas d'échec
        """

        if len(data) > 5 * 10 ** 3:
            raise ValueError("La limite d'un fichier à upload est de 1Mo")

        existing_files = self.db.storage.from_(bucket).list({ "path": path })

        if existing_files and not overwrite:
            raise FileExistsError("Le fichier existe déjà")

        res = self.db.storage.from_(bucket).upload(path, data)

        if res.get("error"):
            print("Erreur lors de l'upload:", res["error"])

        return res

    def _download_from_storage(self, bucket: str, path: str) -> bytes:
        """
        Télécharge un fichier depuis le stockage Supabase.

        ## Paramètres
        bucket: `str`\n
            Nom du bucket où il faut chercher le fichier 
        path: `str`\n
            Chemin du fichier dans le bucket

        ## Renvoie
        - Le fichier demandé en `bytes`
        """

        existing_files = self.db.storage.from_(bucket).list({ "path": path })
        if not existing_files: return None

        res = self.db.storage.from_(bucket).download(path)

        if res.get("error"):
            raise Exception("Erreur lors du téléchargement:", res["error"])
        else:
            return res["data"]
