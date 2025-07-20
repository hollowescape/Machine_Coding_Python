import unittest
import datetime
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Assuming models/ and services/ are in PYTHONPATH or imported correctly
from parking_lot.models.vehicle import Vehicle, VehicleType
from parking_lot.models.parking_spot import ParkingSpot
from parking_lot.models.ticket import Ticket
from parking_lot.services.pricing_strategy import HourlyPricingStrategy
from parking_lot.services.parking_lot_service import ParkingLot
from parking_lot.enum.vehicle import SpotSize

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
        self.parking_lot.park_vehicle("CAR3", VehicleType.CAR)
        with self.assertRaises(Exception) as cm: # Should use a custom exception like ParkingLotFullError
            self.parking_lot.park_vehicle("CAR2", VehicleType.CAR)
        self.assertEqual(str(cm.exception), "Parking Lot Full!")

    @patch('parking_lot.services.parking_lot_service.datetime.datetime')
    @patch('parking_lot.services.pricing_strategy.datetime.datetime')
    def test_unpark_vehicle_success(self, mock_pricing_datetime_class, mock_service_datetime_class):
        # Define real datetime objects for entry and exit
        entry_time = datetime.datetime(2025, 7, 16, 10, 0, 0)
        exit_time = datetime.datetime(2025, 7, 16, 11, 30, 0)  # 1.5 hours

        # Configure the 'now' method for the datetime object in parking_lot_service
        # This will be called when park_vehicle sets ticket.entry_time
        mock_service_datetime_class.now.return_value = entry_time

        # Park the vehicle - this will set ticket.entry_time using the mocked datetime.now()
        ticket = self.parking_lot.park_vehicle("TESTCAR1", VehicleType.CAR)

        # Confirm entry_time was set by the mock
        self.assertEqual(ticket.entry_time, entry_time)

        # Configure the 'now' method for the datetime object in pricing_strategy
        # This will be called when unpark_vehicle (which calls calculate_fee) gets the current time
        mock_pricing_datetime_class.now.return_value = exit_time

        fee = self.parking_lot.unpark_vehicle(ticket.ticket_id)
        # --- FIX ENDS HERE ---

        # 1.5 hours = 90 minutes.
        # Hourly rate $10.0
        # Rounded up to 2 hours.
        # Fee = 2 hours * $10/hour = $20.0
        self.assertEqual(fee, 20.0)
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