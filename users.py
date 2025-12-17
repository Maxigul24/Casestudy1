import os
from tinydb import TinyDB, Query


class User:
    # Class variable that is shared between all instances of the class
    db_connector = TinyDB(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json')).table('users')
    
    def __init__(self, id, name) -> None:
        """Create a new user based on the given name and id"""
        self.name = name
        self.id = id

    def store_data(self) -> None:
        """Save the user to the database"""
        print("Storing user data...")
        # Check if the user already exists in the database
        UserQuery = Query()
        result = User.db_connector.search(UserQuery.id == self.id)
        if result:
            # Update the existing record with the current instance's data
            result = self.db_connector.update(self.__dict__, doc_ids=[result[0].doc_id])
            print("User data updated.")
        else:
            # If the user doesn't exist, insert a new record
            self.db_connector.insert(self.__dict__)
            print("User data inserted.")

    def delete(self) -> None:
        """Delete the user from the database"""
        print("Deleting user data...")
        # Check if the user exists in the database
        UserQuery = Query()
        result = self.db_connector.search(UserQuery.id == self.id)
        if result:
            # Delete the record from the database
            self.db_connector.remove(doc_ids=[result[0].doc_id])
            print("User data deleted.")
        else:
            print("User data not found.")
    
    def __str__(self):
        return f"User {self.id} - {self.name}"
    
    def __repr__(self):
        return self.__str__()
    
    @classmethod
    def find_all(cls) -> list:
        """Find all users in the database"""
        users = []
        for user_data in cls.db_connector.all():
            users.append(cls(user_data['id'], user_data['name']))
        return users

    @classmethod
    def find_by_attribute(cls, by_attribute: str, attribute_value: str, num_to_return=1):
        """From the matches in the database, select the user with the given attribute value"""
        pass
