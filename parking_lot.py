# Understand & Clarify (Ask Questions!):
#
# "What types of vehicles can park (Car, Bike, Truck)? Do they have different sizes/parking requirements?"
#
# "Are there different types of parking spots (Small, Medium, Large)? How many of each?"
#
# "How are fees calculated (per hour, per day, flat rate)? Is there a minimum/maximum fee?"
#
# "What are the main operations: park, unpark, display available spots?"
#
# "Should I consider concurrency if multiple vehicles try to park at the same time?" (Likely simplified for 2 hours, but good to ask).
#
# "Is data persistence required, or can it be in-memory?" (Almost always in-memory for this round).
#
# "What are the error conditions I should handle (e.g., parking lot full, vehicle not found)?"
#
# Initial Design (High-Level OOP):
#
# Classes:
#
# Vehicle: license_plate, color, type (enum: CAR, BIKE, TRUCK).
#
# ParkingSpot: spot_id, size (enum: SMALL, MEDIUM, LARGE), is_occupied, parked_vehicle.
#
# Ticket: ticket_id, entry_time, vehicle, parking_spot.
#
# ParkingLot: name, address, collection of ParkingSpots, parking_rate (could be a PricingStrategy object).
#
# Relationships: ParkingLot has ParkingSpots. ParkingSpot has a Vehicle when occupied. Ticket references a Vehicle and ParkingSpot.
#
# Core Logic (ParkingLot methods):
#
# park_vehicle(vehicle_type, license_plate): Finds a suitable spot, marks it occupied, generates a ticket.
#
# unpark_vehicle(ticket_id): Frees the spot, calculates fee, removes vehicle.
#
# display_available_spots(): Prints status.
#
# Detailed Design & Implementation (Iterative):
#
# Data Structures: A dictionary or list to hold ParkingSpot objects. Perhaps separate lists/dictionaries for different spot sizes for faster lookup. A dictionary to map ticket_id to Ticket objects.
#
# Enums: Use Python Enum for VehicleType, SpotSize.
#
# Error Handling: Raise custom exceptions like ParkingLotFullError, InvalidTicketError.
#
# Pricing Strategy (using Strategy Pattern):
#
# Define an interface/abstract class PricingStrategy.
#
# Implement concrete strategies: HourlyPricingStrategy, DailyPricingStrategy.
#
# ParkingLot holds an instance of PricingStrategy.
#
# Coding (Python specifics):
#
# Python

# models/vehicle.py
from enum import Enum

class VehicleType(Enum):
    CAR = "CAR"
    BIKE = "BIKE"
    TRUCK = "TRUCK"

class Vehicle:
    def __init__(self, license_plate: str, vehicle_type: VehicleType):
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type
        # ... other attributes like color, etc.

# models/parking_spot.py
class SpotSize(Enum):
    SMALL = "SMALL" # for bikes
    MEDIUM = "MEDIUM" # for cars
    LARGE = "LARGE" # for trucks

class ParkingSpot:
    def __init__(self, spot_id: str, size: SpotSize):
        self.spot_id = spot_id
        self.size = size
        self.is_occupied = False
        self.parked_vehicle = None

    def assign_vehicle(self, vehicle: Vehicle):
        self.parked_vehicle = vehicle
        self.is_occupied = True

    def remove_vehicle(self):
        self.parked_vehicle = None
        self.is_occupied = False

# models/ticket.py
import datetime

class Ticket:
    def __init__(self, ticket_id: str, vehicle: Vehicle, parking_spot: ParkingSpot):
        self.ticket_id = ticket_id
        self.vehicle = vehicle
        self.parking_spot = parking_spot
        self.entry_time = datetime.datetime.now()
        self.exit_time = None
        self.fee = 0.0

# services/pricing_strategy.py (Strategy Pattern)
from abc import ABC, abstractmethod

class PricingStrategy(ABC):
    @abstractmethod
    def calculate_fee(self, ticket: Ticket) -> float:
        pass

class HourlyPricingStrategy(PricingStrategy):
    def __init__(self, hourly_rate: float):
        self.hourly_rate = hourly_rate

    def calculate_fee(self, ticket: Ticket) -> float:
        if not ticket.exit_time:
            raise ValueError("Exit time not set for ticket.")
        time_parked_seconds = (ticket.exit_time - ticket.entry_time).total_seconds()
        hours = max(1, (time_parked_seconds / 3600)) # Minimum 1 hour
        return hours * self.hourly_rate

# services/parking_lot_service.py
import uuid
from models.vehicle import Vehicle, VehicleType
from models.parking_spot import ParkingSpot, SpotSize
from models.ticket import Ticket
from services.pricing_strategy import PricingStrategy, HourlyPricingStrategy

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

# Testing (Self-correction/Verification):
#
# Unit Tests (tests/test_parking_lot.py):
#
# Test park_vehicle for success and full lot.
#
# Test unpark_vehicle for success and invalid ticket.
#
# Test calculate_fee logic.
#
# Test display_available_spots.
#
# Python

# tests/test_parking_lot.py
import unittest
import datetime
from unittest.mock import patch, MagicMock

# Assuming models/ and services/ are in PYTHONPATH or imported correctly
from models.vehicle import Vehicle, VehicleType
from models.parking_spot import ParkingSpot, SpotSize
from models.ticket import Ticket
from services.pricing_strategy import HourlyPricingStrategy
from services.parking_lot_service import ParkingLot

class TestParkingLot(unittest.TestCase):

    def setUp(self):
        # Set up a fresh parking lot for each test
        self.pricing = HourlyPricingStrategy(hourly_rate=10.0)
        self.parking_lot = ParkingLot("Test Lot", small_spots=1, medium_spots=1, large_spots=1, pricing_strategy=self.pricing)

    @patch('uuid.uuid4', return_value=MagicMock(hex='test_ticket_id'))
    def test_park_vehicle_success(self, mock_uuid):
        ticket = self.parking_lot.park_vehicle("TESTCAR1", VehicleType.CAR)
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.vehicle.license_plate, "TESTCAR1")
        self.assertTrue(ticket.parking_spot.is_occupied)
        self.assertEqual(len(self.parking_lot.tickets), 1)

    def test_park_vehicle_lot_full(self):
        self.parking_lot.park_vehicle("CAR1", VehicleType.CAR) # Occupy the only car spot
        with self.assertRaises(Exception) as cm: # Should use a custom exception like ParkingLotFullError
            self.parking_lot.park_vehicle("CAR2", VehicleType.CAR)
        self.assertEqual(str(cm.exception), "Parking Lot Full!")

    @patch('datetime.datetime')
    def test_unpark_vehicle_success(self, mock_datetime):
        # Mock current time for predictable fee calculation
        entry_time = datetime.datetime(2025, 7, 16, 10, 0, 0)
        exit_time = datetime.datetime(2025, 7, 16, 11, 30, 0) # 1.5 hours
        mock_datetime.now.side_effect = [entry_time, exit_time]

        ticket = self.parking_lot.park_vehicle("TESTCAR1", VehicleType.CAR)

        # Ensure ticket's entry_time is correctly set by the mocked time
        ticket.entry_time = entry_time # Manually set for the mocked scenario

        fee = self.parking_lot.unpark_vehicle(ticket.ticket_id)
        self.assertEqual(fee, 20.0) # 2 hours * 10.0/hour (min 1 hour, rounded up)
        self.assertFalse(ticket.parking_spot.is_occupied)
        self.assertEqual(len(self.parking_lot.tickets), 0)

    def test_unpark_vehicle_invalid_ticket(self):
        with self.assertRaises(Exception) as cm: # Should use InvalidTicketError
            self.parking_lot.unpark_vehicle("non_existent_id")
        self.assertEqual(str(cm.exception), "Invalid Ticket ID!")

    def test_display_available_spots(self):
        # Capture print output
        with patch('builtins.print') as mock_print:
            self.parking_lot.display_available_spots()
            # Assert that print was called with expected strings
            mock_print.assert_any_call("\n--- Parking Lot Status ---")
            mock_print.assert_any_call("SMALL Spots: 1/1 available")
            mock_print.assert_any_call("MEDIUM Spots: 1/1 available")
            mock_print.assert_any_call("LARGE Spots: 1/1 available")


if __name__ == '__main__':
    unittest.main()