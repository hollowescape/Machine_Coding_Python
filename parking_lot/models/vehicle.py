from parking_lot.enum.vehicle import VehicleType

class Vehicle:

    def __init__(self, license_plate: str, vehicle_type: VehicleType):
        """
        Initializes a Vehicle Instance
        :param license_plate: Vehicle's license plate number
        :param vehicle_type: Type of the vehicle (CAR, TRUCK, BIKE)
        """
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type

