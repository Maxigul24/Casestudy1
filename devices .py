import os

from datetime import datetime, timedelta
from tinydb import TinyDB, Query
from serializer import serializer


class Device():
    # Class variable that is shared between all instances of the class
    db_connector = TinyDB(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json'), storage=serializer).table('devices')
    # Constructor
    def __init__(self, device_id: int, device_name: str, managed_by_user_id: str):
        self.device_id = device_id
        self.device_name = device_name
        self.managed_by_user_id = managed_by_user_id
        self.is_active = True
        self.__creation_date = datetime.now()
        self.__last_update = datetime.now()
        self.__maintenance_interval = 90
        self.__maintenance_cost = 0.0
        self.end_of_life = None
        self.first_maintenance = self.__creation_date + timedelta(days=self.__maintenance_interval)
        self.next_maintenance = self.__creation_date + timedelta(days=self.__maintenance_interval)
        self.__last_maintenance_date = None
        
    @property
    def creation_date(self):
        return self.__creation_date
    
    @property
    def last_update(self):
        return self.__last_update
    
    @property
    def maintenance_interval(self):
        return self.__maintenance_interval
    
    @maintenance_interval.setter
    def maintenance_interval(self, days: int):
        if days < 1:
            raise ValueError("Wartungsintervall muss mindestens 1 Tag sein")
        self.__maintenance_interval = days
        if self.__last_maintenance_date:
            self.next_maintenance = self.__last_maintenance_date + timedelta(days=days)
        else:
            self.next_maintenance = self.__creation_date + timedelta(days=days)
        self.__last_update = datetime.now()
    
    @property
    def maintenance_cost(self):
        return self.__maintenance_cost
    
    @maintenance_cost.setter
    def maintenance_cost(self, cost: float):
        if cost < 0:
            raise ValueError("Wartungskosten können nicht negativ sein")
        self.__maintenance_cost = cost
        self.__last_update = datetime.now()
    
    @property
    def last_maintenance_date(self):
        return self.__last_maintenance_date
    
    # String representation of the class
    def __str__(self):
        return f'Device (Object) {self.device_name} ({self.managed_by_user_id})'

    # String representation of the class
    def __repr__(self):
        return self.__str__()
    
    def store_data(self):
        print("Storing data...")
        # Check if the device already exists in the database
        DeviceQuery = Query()
        result = self.db_connector.search(DeviceQuery.device_name == self.device_name)
        if result:
            # Update the existing record with the current instance's data
            result = self.db_connector.update(self.__dict__, doc_ids=[result[0].doc_id])
            print("Data updated.")
        else:
            # If the device doesn't exist, insert a new record
            self.db_connector.insert(self.__dict__)
            print("Data inserted.")
    
    def delete(self):
        print("Deleting data...")
        # Check if the device exists in the database
        DeviceQuery = Query()
        result = self.db_connector.search(DeviceQuery.device_name == self.device_name)
        if result:
            # Delete the record from the database
            self.db_connector.remove(doc_ids=[result[0].doc_id])
            print("Data deleted.")
        else:
            print("Data not found.")

    def set_managed_by_user_id(self, managed_by_user_id: str):
        """Expects `managed_by_user_id` to be a valid user id that exists in the database."""
        self.managed_by_user_id = managed_by_user_id
        self.__last_update = datetime.now()
    
    def complete_maintenance(self):
        self.__last_maintenance_date = datetime.now()
        self.next_maintenance = self.__last_maintenance_date + timedelta(days=self.__maintenance_interval)
        self.__last_update = datetime.now()
        print(f"Wartung für {self.device_name} abgeschlossen. Nächste Wartung: {self.next_maintenance.strftime('%d.%m.%Y')}")
    
    def get_days_until_maintenance(self) -> int:
        delta = self.next_maintenance - datetime.now()
        return delta.days
    
    def calculate_quarterly_maintenance_cost(self) -> float:
        maintenances_per_quarter = 90 / self.__maintenance_interval
        return maintenances_per_quarter * self.__maintenance_cost

    # Class method that can be called without an instance of the class to construct an instance of the class
    @classmethod
    def find_by_attribute(cls, by_attribute: str, attribute_value: str, num_to_return=1):
        # Load data from the database and create an instance of the Device class
        DeviceQuery = Query()
        result = cls.db_connector.search(DeviceQuery[by_attribute] == attribute_value)

        if result:
            data = result[:num_to_return]
            device_results = [cls(d['device_id'], d['device_name'], d['managed_by_user_id']) for d in data]
            return device_results if num_to_return > 1 else device_results[0]
        else:
            return None

    @classmethod
    def find_all(cls) -> list:
        # Load all data from the database and create instances of the Device class
        devices = []
        for device_data in Device.db_connector.all():
            devices.append(Device(device_data['device_id'], device_data['device_name'], device_data['managed_by_user_id']))
        return devices



    

if __name__ == "__main__":
    # Create a device
    device1 = Device(1, "Device1", "one@mci.edu")
    device2 = Device(2, "Device2", "two@mci.edu") 
    device3 = Device(3, "Device3", "two@mci.edu") 
    device4 = Device(4, "Device4", "two@mci.edu") 
    
    device1.maintenance_cost = 150.50
    device2.maintenance_cost = 200.00
    
    device1.store_data()
    device2.store_data()
    device3.store_data()
    device4.store_data()
    
    print(f"Tage bis zur nächsten Wartung: {device1.get_days_until_maintenance()}")
    print(f"Wartungskosten pro Quartal: {device1.calculate_quarterly_maintenance_cost():.2f} €")
    
    device1.complete_maintenance()
    
    #loaded_device = Device.find_by_attribute("device_name", "Device2")
    loaded_device = Device.find_by_attribute("managed_by_user_id", "two@mci.edu")
    if loaded_device:
        print(f"Loaded Device: {loaded_device}")
    else:
        print("Device not found.")

    devices = Device.find_all()
    print("All devices:")
    for device in devices:
        print(device)

    