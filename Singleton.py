from tinydb import TinyDB, table
import os
from serializer import serializer

class Databaseconnector():

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json')
        return cls.__instance
    
    def get_table(self, table_name) -> table:
        return TinyDB(self.path, storage=serializer).table(table_name)

if __name__ == "__main__":

    s1 = Databaseconnector()
    print(s1.get_table("devices").all())