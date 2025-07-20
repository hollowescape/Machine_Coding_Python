# tests/test_booking_system.py
import sys
import os
import unittest
import datetime
import time  # For simulating duration for fare calculation

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Adjust imports based on how you run tests (e.g., from root or from tests dir)
# Assuming run from cab_booking_system/
from online_cab_booking_system.services.cab_booking_system import BookingSystem
from online_cab_booking_system.enums.enums import DriverStatus, RideStatus
from online_cab_booking_system.models.location import Location
from online_cab_booking_system.models.driver import Driver
from online_cab_booking_system.models.rider import Rider
from online_cab_booking_system.services.farecalulator import FareCalculator
from online_cab_booking_system.exceptions import (
    InvalidInputError, DriverNotFoundError, RiderNotFoundError,
    NoDriverFoundError, RideNotFoundError, InvalidRideStatusError,
    DriverNotAvailableError, BookingSystemError
)


class TestCabBookingSystem(unittest.TestCase):

    def setUp(self):
        self.system = BookingSystem()
        # Register some test drivers
        self.loc_center = Location(12.9716, 77.5946)  # Bangalore City Center
        self.loc_north = Location(13.0100, 77.5700)  # North Bangalore
        self.loc_south = Location(12.9100, 77.6100)  # South Bangalore
        self.loc_east = Location(12.9800, 77.6800)  # East Bangalore for D4

        self.driver1 = self.system.register_driver("D1", "Alice", {"model": "Sedan", "plate": "D1-111"},
                                                   self.loc_center, DriverStatus.AVAILABLE)
        self.driver2 = self.system.register_driver("D2", "Bob", {"model": "SUV", "plate": "D2-222"}, self.loc_north,
                                                   DriverStatus.AVAILABLE)
        self.driver3 = self.system.register_driver("D3", "Charlie", {"model": "Hatchback", "plate": "D3-333"},
                                                   self.loc_south, DriverStatus.OFFLINE)  # Offline driver
        # ADD D4 FOR test_list_available_drivers
        self.driver4 = self.system.register_driver("D4", "David", {"model": "MiniVan", "plate": "D4-444"},
                                                   self.loc_east, DriverStatus.AVAILABLE)

        # Register some test riders
        self.rider1 = self.system.register_rider("R1", "John Doe")
        self.rider2 = self.system.register_rider("R2", "Jane Smith")

    # --- Location Tests ---
    def test_location_distance(self):
        loc1 = Location(0, 0)
        loc2 = Location(3, 4)
        self.assertEqual(loc1.get_distance_to(loc2), 5.0)
        self.assertEqual(loc2.get_distance_to(loc1), 5.0)
        self.assertEqual(loc1.get_distance_to(loc1), 0.0)

        with self.assertRaises(InvalidInputError):
            loc1.get_distance_to("not a location")

    # --- FareCalculator Tests ---
    def test_fare_calculation(self):
        # Base fare + (10km * 1.5) + (20min * 0.2) = 2 + 15 + 4 = 21
        self.assertAlmostEqual(FareCalculator.calculate_fare(10, 20), 21.0)
        # Only base fare if 0 distance/duration
        self.assertAlmostEqual(FareCalculator.calculate_fare(0, 0), FareCalculator.BASE_FARE)
        # Negative inputs should raise error
        with self.assertRaises(ValueError):
            FareCalculator.calculate_fare(-10, 20)
        with self.assertRaises(ValueError):
            FareCalculator.calculate_fare(10, -20)

    # --- Driver & Rider Management Tests ---
    def test_register_driver(self):
        driver_id = "D_NEW"
        driver = self.system.register_driver(driver_id, "New Driver", {"m": "car"}, Location(1, 1))
        self.assertIn(driver_id, self.system._drivers)
        self.assertEqual(self.system._drivers[driver_id].get_name(), "New Driver")
        self.assertEqual(self.system._drivers[driver_id].get_status(), DriverStatus.AVAILABLE)

        with self.assertRaises(InvalidInputError):
            self.system.register_driver("D1", "Existing Driver", {"m": "car"}, Location(1, 1))  # Duplicate ID
        with self.assertRaises(InvalidInputError):
            self.system.register_driver("D_BAD", "", {"m": "car"}, Location(1, 1))  # Empty name

    def test_update_driver_location(self):
        new_loc = Location(10, 20)
        self.system.update_driver_location("D1", new_loc)
        self.assertEqual(self.system._drivers["D1"].get_current_location(), new_loc)

        with self.assertRaises(DriverNotFoundError):
            self.system.update_driver_location("D99", Location(0, 0))  # Non-existent driver

    def test_register_rider(self):
        rider_id = "R_NEW"
        rider = self.system.register_rider(rider_id, "New Rider")
        self.assertIn(rider_id, self.system._riders)
        self.assertEqual(self.system._riders[rider_id].get_name(), "New Rider")

        with self.assertRaises(InvalidInputError):
            self.system.register_rider("R1", "Existing Rider")  # Duplicate ID

    # --- Ride Booking Tests ---
    def test_request_ride_success(self):
        pickup = Location(12.9716, 77.5946)  # Same as D1
        dropoff = Location(12.9000, 77.6000)

        ride = self.system.request_ride("R1", pickup, dropoff)
        self.assertIsNotNone(ride)
        self.assertEqual(ride.get_rider_id(), "R1")
        self.assertEqual(ride.get_status(), RideStatus.MATCHED)

        # D1 is closest and available at loc_center (same as pickup)
        self.assertEqual(ride.get_driver_id(), "D1")
        self.assertEqual(self.system._drivers["D1"].get_status(), DriverStatus.EN_ROUTE_TO_PICKUP)
        self.assertIn(ride.get_id(), self.system._active_rides)
        self.assertEqual(self.system._rider_to_active_ride["R1"], ride.get_id())
        self.assertEqual(self.system._driver_to_active_ride["D1"], ride.get_id())

    def test_request_ride_no_driver_found(self):
        # Make all available drivers unavailable
        self.system._drivers["D1"].update_status(DriverStatus.IN_RIDE)
        self.system._drivers["D2"].update_status(DriverStatus.IN_RIDE)
        self.system._drivers["D4"].update_status(DriverStatus.IN_RIDE)  # D4 is now also unavailable

        # Request ride far away from D3 (still offline)
        far_pickup = Location(0, 0)
        with self.assertRaises(NoDriverFoundError):
            self.system.request_ride("R1", far_pickup, Location(1, 1))

    def test_request_ride_non_existent_rider(self):
        with self.assertRaises(RiderNotFoundError):
            self.system.request_ride("R99", Location(0, 0), Location(1, 1))

    def test_request_ride_rider_has_active_ride(self):
        pickup = Location(12.9716, 77.5946)
        dropoff = Location(12.9000, 77.6000)
        self.system.request_ride("R1", pickup, dropoff)  # R1 now has an active ride

        with self.assertRaises(InvalidInputError):
            self.system.request_ride("R1", Location(1, 1), Location(2, 2))  # R1 tries to request another

    # --- Ride Lifecycle Tests ---
    def test_driver_arrived_at_pickup(self):
        pickup = Location(12.9716, 77.5946)
        dropoff = Location(12.9000, 77.6000)
        ride = self.system.request_ride("R1", pickup, dropoff)

        self.system.driver_arrived_at_pickup(ride.get_id())
        self.assertEqual(ride.get_status(), RideStatus.ARRIVED_AT_PICKUP)

        with self.assertRaises(RideNotFoundError):
            self.system.driver_arrived_at_pickup("NON_EXISTENT_RIDE")
        # Corrected: Test cannot start directly from MATCHED. Needs ARRIVED_AT_PICKUP first.
        # This test ensures driver_arrived_at_pickup works, so we don't put subsequent valid transitions here
        # Test invalid double-arrive
        with self.assertRaises(InvalidRideStatusError):  # Expecting error for arriving again
            self.system.driver_arrived_at_pickup(ride.get_id())

    def test_start_ride(self):
        pickup = Location(12.9716, 77.5946)
        dropoff = Location(12.9000, 77.6000)
        ride = self.system.request_ride("R1", pickup, dropoff)
        self.system.driver_arrived_at_pickup(ride.get_id())

        self.system.start_ride(ride.get_id())
        self.assertEqual(ride.get_status(), RideStatus.IN_PROGRESS)
        self.assertIsNotNone(ride.get_start_time())

        with self.assertRaises(RideNotFoundError):
            self.system.start_ride("NON_EXISTENT_RIDE")
        with self.assertRaises(InvalidRideStatusError):
            self.system.start_ride(ride.get_id())  # Cannot start again

    def test_end_ride_success(self):
        pickup = Location(12.9716, 77.5946)
        dropoff = Location(12.9000, 77.6000)
        ride = self.system.request_ride("R1", pickup, dropoff)
        self.system.driver_arrived_at_pickup(ride.get_id())
        self.system.start_ride(ride.get_id())

        # Simulate some duration
        time.sleep(0.01)

        fare = self.system.end_ride(ride.get_id())
        self.assertEqual(ride.get_status(), RideStatus.COMPLETED)
        self.assertIsNotNone(ride.get_end_time())
        self.assertGreater(fare, FareCalculator.BASE_FARE)  # Fare should be more than just base
        self.assertGreater(ride.get_fare(), FareCalculator.BASE_FARE)

        # Check driver status and location update
        driver = self.system._drivers[ride.get_driver_id()]
        self.assertEqual(driver.get_status(), DriverStatus.AVAILABLE)
        self.assertEqual(driver.get_current_location(), dropoff)

        # Check clean up from active rides
        self.assertNotIn(ride.get_id(), self.system._active_rides)
        self.assertNotIn(ride.get_driver_id(), self.system._driver_to_active_ride)
        self.assertNotIn(ride.get_rider_id(), self.system._rider_to_active_ride)

    def test_end_ride_invalid_status(self):
        pickup = Location(12.9716, 77.5946)
        dropoff = Location(12.9000, 77.6000)
        ride = self.system.request_ride("R1", pickup, dropoff)  # Status MATCHED

        with self.assertRaises(InvalidRideStatusError):
            self.system.end_ride(ride.get_id())  # Cannot end directly from MATCHED

    # --- Querying Tests ---
    def test_get_ride_status(self):
        pickup = Location(12.9716, 77.5946)
        dropoff = Location(12.9000, 77.6000)
        ride = self.system.request_ride("R1", pickup, dropoff)

        retrieved_ride = self.system.get_ride_status(ride.get_id())
        self.assertEqual(retrieved_ride.get_id(), ride.get_id())
        self.assertEqual(retrieved_ride.get_status(), RideStatus.MATCHED)

        # FIX: Call the actual system method to change status, not directly on the retrieved object if it's not meant to be mutable
        # Also, the goal of this test is to *get* the status, not change it and then try to get it again if it's inactive.
        # This part of the test should be removed or moved to a lifecycle test.
        # retrieved_ride.set_status("IN_PROGRESS") # This was the original error line
        # self.system.end_ride(ride.get_id())  # End the ride
        # with self.assertRaises(RideNotFoundError):
        #     self.system.get_ride_status(ride.get_id())  # Should not be found in active rides

        # Simpler test for get_ride_status: Check status at different points
        self.system.driver_arrived_at_pickup(ride.get_id())
        retrieved_ride_arrived = self.system.get_ride_status(ride.get_id())
        self.assertEqual(retrieved_ride_arrived.get_status(), RideStatus.ARRIVED_AT_PICKUP)

        # Test getting status of a non-existent ride
        with self.assertRaises(RideNotFoundError):
            self.system.get_ride_status("NON_EXISTENT_RIDE_ID")

    def test_get_driver_status(self):
        status = self.system.get_driver_status("D1")
        self.assertEqual(status["driver_id"], "D1")
        self.assertEqual(status["status"], DriverStatus.AVAILABLE.name)
        self.assertEqual(status["location"], self.loc_center)
        self.assertIsNone(status["current_ride_id"])

        ride = self.system.request_ride("R1", self.loc_center, self.loc_south)
        status_after_request = self.system.get_driver_status("D1")
        self.assertEqual(status_after_request["status"], DriverStatus.EN_ROUTE_TO_PICKUP.name)
        self.assertEqual(status_after_request["current_ride_id"], ride.get_id())

        with self.assertRaises(DriverNotFoundError):
            self.system.get_driver_status("D99")

    def test_list_available_drivers(self):
        # D1, D2, D4 are AVAILABLE (3 total)
        # D3 is OFFLINE (1 total)
        available_drivers_before = self.system.list_available_drivers()
        self.assertEqual(len(available_drivers_before), 3)  # Corrected from 2 to 3 after adding D4 in setUp

        # Take D1 and D2 out of availability
        self.system.request_ride("R1", self.loc_center, self.loc_south)  # D1 gets matched
        self.system.request_ride("R2", self.loc_north, self.loc_south)  # D2 gets matched

        available_drivers_after = self.system.list_available_drivers()
        # After D1 and D2 are in rides, only D4 should be available. D3 is OFFLINE.
        self.assertEqual(len(available_drivers_after), 1)
        self.assertEqual(available_drivers_after[0]['driver_id'], 'D4')
        self.assertEqual(available_drivers_after[0]['name'], 'David')


if __name__ == '__main__':
    # Use argv=[] to prevent unittest from trying to parse command-line args for itself
    unittest.main(argv=['first-arg-is-ignored'], exit=False)