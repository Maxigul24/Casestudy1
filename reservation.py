from serializable import Serializable
from database import DatabaseConnector
from datetime import datetime
from typing import Self

class Reservation(Serializable):

    db_connector = DatabaseConnector().get_table("reservations")

    def __init__(self, user_id: str, device_id: str, start_date: datetime, end_date: datetime, 
                 reason: str = "", status: str = "Aktiv", creation_date: datetime = None, 
                 last_update: datetime = None, id: str = None) -> None:

        if not id:
            id = f"{user_id}_{device_id}_{start_date.strftime('%Y%m%d%H%M%S')}"

        super().__init__(id, creation_date, last_update)
        self.user_id = user_id
        self.device_id = device_id
        self.start_date = start_date
        self.end_date = end_date
        self.reason = reason
        self.status = status
        
    @classmethod
    def instantiate_from_dict(cls, data: dict) -> Self:
        return cls(
            data['user_id'], 
            data['device_id'], 
            data['start_date'], 
            data['end_date'], 
            data.get('reason', ''),
            data.get('status', 'Aktiv'),
            data.get('creation_date'), 
            data.get('last_update'), 
            data['id']
        )

    def __str__(self):
        return f"Reservation: {self.user_id} → {self.device_id}: {self.start_date.strftime('%d.%m.%Y')} - {self.end_date.strftime('%d.%m.%Y')}"
    
    def is_active(self) -> bool:
        """Check if the reservation is currently active"""
        now = datetime.now()
        return self.start_date <= now <= self.end_date and self.status == "Aktiv"
    
    def has_conflict(self, start_date: datetime, end_date: datetime) -> bool:
        """Check if this reservation conflicts with the given date range"""
        return not (end_date < self.start_date or start_date > self.end_date)
    
    @classmethod
    def check_availability(cls, device_id: str, start_date: datetime, end_date: datetime) -> bool:
        """Check if a device is available for the given date range"""
        all_reservations = cls.find_by_attribute("device_id", device_id, num_to_return=-1)
        
        if not all_reservations:
            return True
        
        if isinstance(all_reservations, list):
            reservations = all_reservations
        else:
            reservations = [all_reservations]
        
        for reservation in reservations:
            if reservation.status == "Aktiv" and reservation.has_conflict(start_date, end_date):
                return False
        
        return True

if __name__ == "__main__":
    # Test the Reservation class
    from devices import Device
    from users import User
    
    # Create test reservations
    reservation1 = Reservation("one@mci.edu", "Device1", datetime(2026, 1, 25), datetime(2026, 1, 28), "Testing")
    reservation2 = Reservation("two@mci.edu", "Device2", datetime(2026, 2, 1), datetime(2026, 2, 5), "Production")
    
    reservation1.store_data()
    reservation2.store_data()
    
    # Test availability check
    available = Reservation.check_availability("Device1", datetime(2026, 1, 26), datetime(2026, 1, 27))
    print(f"Device1 available for 26-27 Jan: {available}")
    
    # Load reservations
    loaded_reservations = Reservation.find_by_attribute("device_id", "Device1", num_to_return=-1)
    if loaded_reservations:
        for res in (loaded_reservations if isinstance(loaded_reservations, list) else [loaded_reservations]):
            print(f"Loaded: {res}")
