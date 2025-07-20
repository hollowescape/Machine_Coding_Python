from parking_lot.models.vehicle import Vehicle

class ParkingSpot:

    def __init__(self, spot_id: int, spot_type: str):
        """
        Initializes a ParkingSpot Instance
        :param spot_id: Unique identifier for the parking spot
        :param spot_type: Type of the parking spot (COMPACT, REGULAR, HANDICAPPED)
        """
        self.spot_id = spot_id
        self.spot_type = spot_type
        self.is_occupied = False
        self.parked_vehicle = None

    def assign_vehicle(self, vehicle: Vehicle):
        self.parked_vehicle = vehicle
        self.is_occupied = True

    def remove_vehicle(self):
        self.parked_vehicle = None
        self.is_occupied = False