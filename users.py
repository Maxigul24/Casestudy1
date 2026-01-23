from typing import Self
from datetime import datetime

from serializable import Serializable
from database import DatabaseConnector

class User(Serializable):

    db_connector = DatabaseConnector().get_table("users")

    def __init__(self, id: str, name: str, creation_date: datetime = None, last_update: datetime = None) -> None:
        super().__init__(id, creation_date, last_update)
        self.name = name

    @classmethod
    def instantiate_from_dict(cls, data: dict) -> Self:
        return cls(data['id'], data['name'], data.get('creation_date'), data.get('last_update'))

    def __str__(self):
        return f"User: {self.name} ({self.id})"
