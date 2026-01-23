from typing import Self
from datetime import datetime, timedelta
from serializable import Serializable
from database import DatabaseConnector

class Device(Serializable):

    db_connector = DatabaseConnector().get_table("devices")

    def __init__(self, id: str, name: str, managed_by_user_id: str, device_type: str = "Standard", status: str = "Verfügbar", 
                 end_of_life: datetime = None, creation_date: datetime = None, last_update: datetime = None):
        super().__init__(id, creation_date, last_update)
        self.name = name
        self.device_type = device_type      
        self.status = status  
        self.managed_by_user_id = managed_by_user_id
        self.is_active = True
        self.end_of_life = end_of_life
        self.__maintenance_interval = 90
        self.__maintenance_cost = 0.0
        self.first_maintenance = self.creation_date + timedelta(days=self.__maintenance_interval)
        self.next_maintenance = self.creation_date + timedelta(days=self.__maintenance_interval)
        self.__last_maintenance_date = None
        
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
            self.next_maintenance = self.creation_date + timedelta(days=days)
        self.last_update = datetime.now()
    
    @property
    def maintenance_cost(self):
        return self.__maintenance_cost
    
    @maintenance_cost.setter
    def maintenance_cost(self, cost: float):
        if cost < 0:
            raise ValueError("Wartungskosten können nicht negativ sein")
        self.__maintenance_cost = cost
        self.last_update = datetime.now()
    
    @property
    def last_maintenance_date(self):
        return self.__last_maintenance_date
    
    @classmethod
    def instantiate_from_dict(cls, data: dict) -> Self:
        # Rückwärtskompatibilität: unterstütze alte Feldnamen (device_id, device_name, device_status)
        device_id = data.get('id') or data.get('device_id')
        device_name = data.get('name') or data.get('device_name')
        device_status = data.get('status') or data.get('device_status', 'Verfügbar')
        
        return cls(
            device_id, 
            device_name, 
            data['managed_by_user_id'],
            data.get('device_type', 'Standard'),
            device_status,
            data.get('end_of_life'),
            data.get('creation_date'),
            data.get('last_update')
        )
    
    # String representation of the class
    def __str__(self):
        return f'Device: {self.name} ({self.managed_by_user_id})'
    
    def set_managed_by_user_id(self, managed_by_user_id: str):
        """Expects `managed_by_user_id` to be a valid user id that exists in the database."""
        self.managed_by_user_id = managed_by_user_id
        self.last_update = datetime.now()
    
    def complete_maintenance(self):
        self.__last_maintenance_date = datetime.now()
        self.next_maintenance = self.__last_maintenance_date + timedelta(days=self.__maintenance_interval)
        self.last_update = datetime.now()
        print(f"Wartung für {self.name} abgeschlossen. Nächste Wartung: {self.next_maintenance.strftime('%d.%m.%Y')}")
    
    def get_days_until_maintenance(self) -> int:
        delta = self.next_maintenance - datetime.now()
        return delta.days
    
    def calculate_quarterly_maintenance_cost(self) -> float:
        maintenances_per_quarter = 90 / self.__maintenance_interval
        return maintenances_per_quarter * self.__maintenance_cost



    

# if __name__ == "__main__":
#     # Create a device
#     device1 = Device(1, "Device1", "one@mci.edu")
#     device2 = Device(2, "Device2", "two@mci.edu") 
#     device3 = Device(3, "Device3", "two@mci.edu") 
#     device4 = Device(4, "Device4", "two@mci.edu") 
    
#     device1.maintenance_cost = 150.50
#     device2.maintenance_cost = 200.00
    
#     device1.store_data()
#     device2.store_data()
#     device3.store_data()
#     device4.store_data()
    
#     print(f"Tage bis zur nächsten Wartung: {device1.get_days_until_maintenance()}")
#     print(f"Wartungskosten pro Quartal: {device1.calculate_quarterly_maintenance_cost():.2f} €")
    
#     device1.complete_maintenance()
    
#     #loaded_device = Device.find_by_attribute("device_name", "Device2")
#     loaded_device = Device.find_by_attribute("managed_by_user_id", "two@mci.edu")
#     if loaded_device:
#         print(f"Loaded Device: {loaded_device}")
#     else:
#         print("Device not found.")

#     devices = Device.find_all()
#     print("All devices:")
#     for device in devices:
#         print(device)

    