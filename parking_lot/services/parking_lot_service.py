import uuid
import datetime
from parking_lot.models.vehicle import Vehicle, VehicleType
from parking_lot.models.parking_spot import ParkingSpot
from parking_lot.enum.vehicle import SpotSize
from parking_lot.models.ticket import Ticket
from parking_lot.services.pricing_strategy import PricingStrategy, HourlyPricingStrategy

class ParkingLot:
    def __init__(self, name: str, small_spots: int, medium_spots: int, large_spots: int, pricing_strategy: PricingStrategy):
        self.name = name
        self.spots = {
            SpotSize.SMALL: [],
            SpotSize.MEDIUM: [],
            SpotSize.LARGE: []
        }
        self.tickets = {} # ticket_id -> Ticket object
        self.pricing_strategy = pricing_strategy

        # Initialize spots
        for i in range(small_spots):
            self.spots[SpotSize.SMALL].append(ParkingSpot(f"S{i+1}", SpotSize.SMALL))
        for i in range(medium_spots):
            self.spots[SpotSize.MEDIUM].append(ParkingSpot(f"M{i+1}", SpotSize.MEDIUM))
        for i in range(large_spots):
            self.spots[SpotSize.LARGE].append(ParkingSpot(f"L{i+1}", SpotSize.LARGE))

    def _find_available_spot(self, vehicle_type: VehicleType) -> ParkingSpot:
        # Logic to find a spot based on vehicle type and spot size preference
        # (e.g., Bike -> Small, Car -> Medium/Large, Truck -> Large)
        # This would be more complex in a real system (e.g., specific mapping,
        # or allowing smaller vehicles in larger spots if small spots are full)
        if vehicle_type == VehicleType.BIKE:
            for spot in self.spots[SpotSize.SMALL]:
                if not spot.is_occupied:
                    return spot
        elif vehicle_type == VehicleType.CAR:
            for spot in self.spots[SpotSize.MEDIUM]:
                if not spot.is_occupied:
                    return spot
            # Optionally, allow cars in large spots if medium are full
            for spot in self.spots[SpotSize.LARGE]:
                if not spot.is_occupied:
                    return spot
        elif vehicle_type == VehicleType.TRUCK:
            for spot in self.spots[SpotSize.LARGE]:
                if not spot.is_occupied:
                    return spot
        return None # No spot found

    def park_vehicle(self, license_plate: str, vehicle_type: VehicleType) -> Ticket:
        vehicle = Vehicle(license_plate, vehicle_type)
        spot = self._find_available_spot(vehicle_type)

        if not spot:
            raise Exception("Parking Lot Full!") # Use custom exception

        spot.assign_vehicle(vehicle)
        ticket_id = str(uuid.uuid4())
        ticket = Ticket(ticket_id, vehicle, spot)
        self.tickets[ticket_id] = ticket
        print(f"Vehicle {license_plate} parked at spot {spot.spot_id}. Ticket ID: {ticket_id}")
        return ticket

    def unpark_vehicle(self, ticket_id: str) -> float:
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            raise Exception("Invalid Ticket ID!") # Use custom exception

        ticket.exit_time = datetime.datetime.now()
        fee = self.pricing_strategy.calculate_fee(ticket)
        ticket.fee = fee

        ticket.parking_spot.remove_vehicle()
        del self.tickets[ticket_id]
        print(f"Vehicle {ticket.vehicle.license_plate} unparked from spot {ticket.parking_spot.spot_id}. Fee: ${fee:.2f}")
        return fee

    def display_available_spots(self):
        print("\n--- Parking Lot Status ---")
        for size, spots in self.spots.items():
            occupied_count = sum(1 for spot in spots if spot.is_occupied)
            print(f"{size.value} Spots: {len(spots) - occupied_count}/{len(spots)} available")
        print("--------------------------\n")


# main.py (Driver code)
if __name__ == "__main__":
    hourly_rate = 10.0
    pricing = HourlyPricingStrategy(hourly_rate)
    my_parking_lot = ParkingLot("My City Parking", 2, 3, 1, pricing)

    my_parking_lot.display_available_spots()

    try:
        ticket1 = my_parking_lot.park_vehicle("KA01AB1234", VehicleType.CAR)
        ticket2 = my_parking_lot.park_vehicle("DL05CD5678", VehicleType.BIKE)
        ticket3 = my_parking_lot.park_vehicle("MH09EF9012", VehicleType.TRUCK)
        # ticket4 = my_parking_lot.park_vehicle("UP01XY4321", VehicleType.CAR) # This might throw an exception if only 3 medium spots are present and no large spots are available after truck

        my_parking_lot.display_available_spots()

        # Simulate some time passing for fee calculation
        import time
        time.sleep(5) # In real world, this would be longer

        my_parking_lot.unpark_vehicle(ticket1.ticket_id)
        my_parking_lot.unpark_vehicle(ticket2.ticket_id)

        my_parking_lot.display_available_spots()

        # Attempt to unpark with invalid ticket
        # my_parking_lot.unpark_vehicle("non_existent_ticket")

    except Exception as e:
        print(f"Error: {e}")
