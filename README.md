# nsarchive

`nsarchive` est un module Python pour la gestion des entités (utilisateurs et organisations) à l'aide de la base de données Deta. Ce module permet de créer, récupérer, sauvegarder et gérer des entités et leurs attributs spécifiques.

## Pré-requis

Listes des choses à avoir afin de pouvoir utiliser le module correctement:
- [Python 3.10](https://www.python.org/downloads/) ou supérieur
- Un token [Deta](https://deta.space), donné par un administrateur ou pour votre collection personnelle
- Un bon capuccino, pour commencer la programmation en bons termes

> **Note:** Il vous faudra un token différent pour accéder aux différentes parties de la base de données. Vos tokens n'expireront pas à moins que l'ordre en aura été donné

## Installation

Vous pouvez installer ce module via pip :

```sh
pip install nsarchive
```

## Utilisation

### Importation et Initialisation

Pour utiliser `nsarchive`, commencez par importer le module et initialiser une instance d'`EntityInstance` avec votre token Deta.

```python
from nsarchive import EntityInstance

# Remplacez 'your_deta_token' par votre véritable token Deta
entity_instance = EntityInstance(token = 'your_deta_token')
```

### Récupérer une Entité

Vous pouvez récupérer une entité (Utilisateur ou Organisation) à l'aide de son ID.

```python
entity = entity_instance.get_entity(id = 'entity_id')
print(entity.name)
```

**ATTENTION: Les entités sont identifiées sous une forme hexadécimale. Pour les avoir, vous devez convertir leur ID Discord en hexadécimale puis enlever le préfixe `0x`.**

Pour les organisations, l'ID Discord correspondra à la formule suivante: `ID fondateur // 100000`.

N'oubliez pas de toujours utiliser un `str` dans les ID pour interagir avec la base de données.

### Sauvegarder une Entité

Après avoir modifié une entité, vous pouvez la sauvegarder dans la base de données.

```python
entity.rename("Nouveau Nom")
entity_instance.save_entity(entity)
```

### Rechercher des Entités

Vous pouvez rechercher des entités avec des critères spécifiques.

```python
entities = entity_instance.fetch_entity(query = {'name': 'Alice'})
for entity in entities:
    print(entity['name'])
```

### Gérer les Organisations

Les organisations peuvent avoir des membres et des certifications. Voici comment ajouter un membre ou une certification.

```python
organization = entity_instance.get_entity(id = 'org_id')
user = entity_instance.get_entity(id = 'user_id')

# Ajouter un membre
organization.add_member(user)
entity_instance.save_entity(organization)

# Ajouter une certification
organization.add_certification('Certification Example')
entity_instance.save_entity(organization)
```

Les certifications pourront être utilisées pour vérifier l'officialité d'une organisation, mais également pour déterminer si l'on peut accorder (ou non) des permissions à ses membres.

### Exemples de Classes

#### `Entity`

Classe parente des classes `User` et `Organization`, elle est utilisée lorsque le module ne peut pas déterminer l'appartenance d'une identité à l'une de ces deux classes ou à l'autre.

```python
from nsarchive.cls.entities import Entity

entity = Entity(id='entity_id')
entity.rename('New Name')
entity.add_xp(100)
print(entity.get_level())
```

#### `User`

```python
from nsarchive.cls.entities import User

user = User(id = 'user_id')
user.edit_boost(name = 'admin', multiplier = 5) # Négliger le paramètre <multiplier> ou le fixer à un nombre négatif reviendrait à supprimer le boost.
print(user.boosts)
```

> **Note:** Lorsqu'on ajoute de l'expérience à un utilisateur via la méthode `add_xp`, le nombre de points ajoutés est automatiquement multiplié par le bonus le plus important dont l'utilisateur bénéficie.

#### `Organization`

```python
from nsarchive.cls.entities import Organization

organization = Organization(id = 'org_id')
organization.set_owner(user)
organization.add_member(user)
print(organization.members)
```

> **Note:** Les attributs `owner` et `members` sont indépendants. L'owner peut être n'importe quelle personne faisant ou non partie des `members`.

## Gestion des Exceptions

`nsarchive` fournit des exceptions spécifiques pour gérer les erreurs courantes.

#### `NameTooLongError`

Lancé lorsque le nom d'une entité dépasse la longueur maximale autorisée (32 caractères).

```python
from nsarchive.cls.exceptions import NameTooLongError

try:
    entity.rename('Ce nom est long, voire même très long, je dirais même extrêmement long')
except NameTooLongError as e:
    print(e)
```

#### `EntityTypeError`

Lancé lorsque le type d'entité est incorrect. Vous ne devriez normalement pas la rencontrer en utilisant le module, mais elle pourrait vous être utile.

```python
from nsarchive.cls.exceptions import EntityTypeError

try:
    # Code qui peut lancer une EntityTypeError
except EntityTypeError as e:
    print(e)
```

## License

Ce projet est sous licence GNU GPL-3.0 - Voir le fichier [LICENSE](LICENSE) pour plus de détails.