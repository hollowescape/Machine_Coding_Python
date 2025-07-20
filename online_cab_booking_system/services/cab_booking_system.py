import datetime
from typing import Dict, List, Optional, Any
import collections # For defaultdict

# Import local modules
from ..enums.enums import DriverStatus, RideStatus
from ..exceptions import (
    InvalidInputError, DriverNotFoundError, RiderNotFoundError,
    NoDriverFoundError, RideNotFoundError, InvalidRideStatusError,
    DriverNotAvailableError
)
from ..models.location import Location
from ..models.driver import Driver
from ..models.rider import Rider
from ..models.ride import Ride
from ..services.farecalulator import FareCalculator


class BookingSystem:
    # Define a reasonable matching radius for finding drivers
    _MATCHING_RADIUS_KM = 5.0  # Drivers within 5 km of pickup location

    def __init__(self):
        self._drivers: Dict[str, Driver] = {}  # driver_id -> Driver object
        self._riders: Dict[str, Rider] = {}  # rider_id -> Rider object
        self._active_rides: Dict[str, Ride] = {}  # ride_id -> Ride object (for MATCHED, ARRIVED, IN_PROGRESS rides)

        # Mappings for quick lookup
        self._driver_to_active_ride: Dict[str, str] = {}  # driver_id -> ride_id
        self._rider_to_active_ride: Dict[str, str] = {}  # rider_id -> ride_id

        self._next_ride_id_counter = 1

        print("Cab Booking System Initialized.")

    def _generate_ride_id(self) -> str:
        """Generates a unique ride ID."""
        new_id = f"RIDE_{self._next_ride_id_counter:05d}"
        self._next_ride_id_counter += 1
        return new_id

    # --- Driver Management ---
    def register_driver(self, driver_id: str, name: str, vehicle_details: Dict[str, str],
                        current_location: Location, status: DriverStatus = DriverStatus.AVAILABLE):
        """Registers a new driver."""
        if driver_id in self._drivers:
            raise InvalidInputError(f"Driver with ID '{driver_id}' already exists.")

        driver = Driver(driver_id, name, vehicle_details, current_location, status)
        self._drivers[driver_id] = driver
        print(f"Driver '{name}' ({driver_id}) registered.")
        return driver

    def update_driver_location(self, driver_id: str, new_location: Location):
        """Updates a driver's current location."""
        driver = self._drivers.get(driver_id)
        if not driver:
            raise DriverNotFoundError(f"Driver with ID '{driver_id}' not found.")

        driver.update_location(new_location)
        print(f"Driver '{driver_id}' location updated to {new_location}.")

        # --- Rider Management ---

    def register_rider(self, rider_id: str, name: str):
        """Registers a new rider."""
        if rider_id in self._riders:
            raise InvalidInputError(f"Rider with ID '{rider_id}' already exists.")

        rider = Rider(rider_id, name)
        self._riders[rider_id] = rider
        print(f"Rider '{name}' ({rider_id}) registered.")
        return rider

    # --- Ride Booking ---
    def request_ride(self, rider_id: str, pickup_location: Location, dropoff_location: Location) -> Ride:
        """
        Rider requests a ride. System finds closest available driver.
        Returns the created Ride object.
        """
        rider = self._riders.get(rider_id)
        if not rider:
            raise RiderNotFoundError(f"Rider with ID '{rider_id}' not found.")

        if rider_id in self._rider_to_active_ride:
            raise InvalidInputError(
                f"Rider '{rider_id}' already has an active ride ({self._rider_to_active_ride[rider_id]}).")

        closest_driver: Optional[Driver] = None
        min_distance = float('inf')

        # Find the closest available driver (O(N) scan)
        available_drivers_in_range: List[Driver] = []
        for driver_id, driver in self._drivers.items():
            if driver.get_status() == DriverStatus.AVAILABLE:
                distance = driver.get_current_location().get_distance_to(pickup_location)
                if distance <= self._MATCHING_RADIUS_KM:
                    available_drivers_in_range.append(driver)

        # Apply tie-breaker: sort by distance, then by driver ID for determinism
        available_drivers_in_range.sort(
            key=lambda d: (d.get_current_location().get_distance_to(pickup_location), d.get_id()))

        if not available_drivers_in_range:
            raise NoDriverFoundError(
                f"No available drivers found within {self._MATCHING_RADIUS_KM} km of {pickup_location}.")

        closest_driver = available_drivers_in_range[0]

        # Assign driver and create ride
        ride_id = self._generate_ride_id()
        new_ride = Ride(ride_id, rider_id, closest_driver.get_id(), pickup_location, dropoff_location)
        new_ride.set_status(RideStatus.MATCHED)

        # Update driver status
        closest_driver.update_status(DriverStatus.EN_ROUTE_TO_PICKUP)

        # Store ride in active rides and mappings
        self._active_rides[ride_id] = new_ride
        self._driver_to_active_ride[closest_driver.get_id()] = ride_id
        self._rider_to_active_ride[rider_id] = ride_id

        print(f"Ride {ride_id} requested by {rider.get_name()}. Matched with Driver {closest_driver.get_name()}.")
        return new_ride

        # --- Ride Lifecycle Management ---
    def driver_arrived_at_pickup(self, ride_id: str):
            """Driver signals arrival at pickup location."""
            ride = self._active_rides.get(ride_id)
            if not ride:
                raise RideNotFoundError(f"Ride with ID '{ride_id}' not found or already completed/cancelled.")

            if ride.get_status() != RideStatus.MATCHED:
                raise InvalidRideStatusError(
                    f"Ride '{ride_id}' cannot arrive from status {ride.get_status().name}. Expected {RideStatus.MATCHED.name}.")

            ride.set_status(RideStatus.ARRIVED_AT_PICKUP)
            print(f"Ride {ride_id}: Driver {ride.get_driver_id()} has arrived at pickup.")

    def start_ride(self, ride_id: str):
        """Driver signals the ride has started."""
        ride = self._active_rides.get(ride_id)
        if not ride:
            raise RideNotFoundError(f"Ride with ID '{ride_id}' not found or already completed/cancelled.")

        if ride.get_status() != RideStatus.ARRIVED_AT_PICKUP:
            raise InvalidRideStatusError(
                f"Ride '{ride_id}' cannot start from status {ride.get_status().name}. Expected {RideStatus.ARRIVED_AT_PICKUP.name}.")

        ride.set_status(RideStatus.IN_PROGRESS)
        ride.set_start_time(datetime.datetime.now())  # Record actual ride start time
        print(f"Ride {ride_id}: Ride started with driver {ride.get_driver_id()}.")

    def end_ride(self, ride_id: str):
        """Driver signals the ride has ended at the dropoff location."""
        ride = self._active_rides.get(ride_id)
        if not ride:
            raise RideNotFoundError(f"Ride with ID '{ride_id}' not found or already completed/cancelled.")

        if ride.get_status() != RideStatus.IN_PROGRESS:
            raise InvalidRideStatusError(
                f"Ride '{ride_id}' cannot end from status {ride.get_status().name}. Expected {RideStatus.IN_PROGRESS.name}.")

        ride.set_status(RideStatus.COMPLETED)
        ride.set_end_time(datetime.datetime.now())  # Record actual ride end time

        # Calculate fare
        distance_traveled = ride.get_pickup_location().get_distance_to(ride.get_dropoff_location())

        # Ensure start_time is set before calculating duration
        if not ride.get_start_time():
            # This indicates an error in flow, but handle defensively
            print(f"Warning: Ride {ride_id} start time not set, assuming 0 duration for fare calculation.")
            duration_seconds = 0
        else:
            duration_seconds = (ride.get_end_time() - ride.get_start_time()).total_seconds()

        duration_minutes = duration_seconds / 60.0

        fare = FareCalculator.calculate_fare(distance_traveled, duration_minutes)
        ride.set_fare(fare)

        # Update driver status and location
        driver = self._drivers.get(ride.get_driver_id())
        if driver:  # Should always exist, but defensive check
            driver.update_status(DriverStatus.AVAILABLE)
            driver.update_location(ride.get_dropoff_location())

        # Clean up active ride mappings
        del self._active_rides[ride_id]
        if driver:
            del self._driver_to_active_ride[driver.get_id()]
        del self._rider_to_active_ride[ride.get_rider_id()]

        print(
            f"Ride {ride_id} completed. Fare: ${fare:.2f}. Driver {driver.get_name()} now AVAILABLE at {driver.get_current_location()}.")
        return fare

        # --- Querying/Reporting ---
    def get_ride_status(self, ride_id: str) -> Ride:
            """Returns the current status of a ride."""
            ride = self._active_rides.get(ride_id)
            if not ride:
                # Check if it was a completed ride
                # For simplicity, if not active, we assume it's not found by ID.
                # In a real system, you'd have _completed_rides and search there too.
                raise RideNotFoundError(f"Ride with ID '{ride_id}' not found or not active.")
            return ride

    def get_driver_status(self, driver_id: str) -> Dict[str, Any]:
            """Returns a driver's current status and last known location."""
            driver = self._drivers.get(driver_id)
            if not driver:
                raise DriverNotFoundError(f"Driver with ID '{driver_id}' not found.")

            return {
                "driver_id": driver.get_id(),
                "name": driver.get_name(),
                "status": driver.get_status().name,
                "location": driver.get_current_location(),
                "current_ride_id": self._driver_to_active_ride.get(driver_id)
            }

    def list_available_drivers(self) -> List[Dict[str, Any]]:
            """Returns a list of all drivers currently marked as AVAILABLE."""
            available_drivers = []
            for driver_id, driver in self._drivers.items():
                if driver.get_status() == DriverStatus.AVAILABLE:
                    available_drivers.append({
                        "driver_id": driver.get_id(),
                        "name": driver.get_name(),
                        "location": driver.get_current_location()
                    })
            return available_drivers

    def get_system_overview(self) -> Dict[str, int]:
            """Provides a high-level overview of the system's state."""
            return {
                "total_drivers": len(self._drivers),
                "total_riders": len(self._riders),
                "active_rides": len(self._active_rides),
                "available_drivers": len(
                    [d for d in self._drivers.values() if d.get_status() == DriverStatus.AVAILABLE])
            }