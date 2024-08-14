# Exceptions liées aux entités

class NameTooLongError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class EntityTypeError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class AvatarTooLongError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

# Exceptions pour le vote

class AlreadyVotedError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

# Ressource pas trouvée

class RessourceNotFoundError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)