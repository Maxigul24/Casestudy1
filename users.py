import json

class User:
    def __init__(self, id, name) -> None:
        """Create a new user based on the given name and id"""
        self.name = name
        self.id = id

    def store_data(self)-> None:
        """Save the user to the database"""
        # Load existing database
        with open('database.json', 'r') as f:
            data = json.load(f)
        
        # Create users section if it doesn't exist
        if 'users' not in data:
            data['users'] = {}
        data['users'][self.id] = {
            'name': self.name,
            'id': self.id
        }

        with open('database.json', 'w') as f:
            json.dump(data, f, indent=2)


    def delete(self) -> None:
        """Delete the user from the database"""
       
        with open('database.json', 'r') as f:
            data = json.load(f)
        
        if 'users' in data and self.id in data['users']:
            del data['users'][self.id]

        with open('database.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def __str__(self):
        return f"User {self.id} - {self.name}"
    
    def __repr__(self):
        return self.__str__()
    
    @staticmethod
    def find_all(cls) -> list:
        """Find all users in the database"""
        with open('database.json', 'r') as f:
            data = json.load(f)
        users = []
        if 'users' in data:
            for user_id, user_data in data['users'].items():
                users.append(User(user_data['id'], user_data['name']))
        return users

    @classmethod
    def find_by_attribute(cls, by_attribute : str, attribute_value : str) -> 'User':
        """From the matches in the database, select the user with the given attribute value"""
        pass
