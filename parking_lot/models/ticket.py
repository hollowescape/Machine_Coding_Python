from datetime import datetime
from parking_lot.models.vehicle import Vehicle
from parking_lot.models.parking_spot import ParkingSpot

class Ticket:
    def __init__(self, ticket_id: str, vehicle: Vehicle, parking_spot: ParkingSpot):
        self.ticket_id = ticket_id
        self.vehicle = vehicle
        self.parking_spot = parking_spot
        self.entry_time = datetime.now()
        self.exit_time = None
        self.fee = 0.0
