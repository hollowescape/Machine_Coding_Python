High-Level Design & Core Entities
The system will be built around several key Object-Oriented Programming (OOP) entities:

Enums:

DriverStatus: States for a driver (e.g., AVAILABLE, EN_ROUTE_TO_PICKUP, IN_RIDE, OFFLINE).

RideStatus: States for a ride (e.g., REQUESTED, MATCHED, ARRIVED_AT_PICKUP, IN_PROGRESS, COMPLETED, CANCELLED).

Location Class:

A simple data class to encapsulate latitude and longitude.

Provides a method for Euclidean distance calculation between two Location objects.

Driver Class:

Represents a cab driver.

Attributes: driver_id (unique), name, vehicle_details (e.g., dictionary for model, plate), current_location (a Location object), status (DriverStatus).

Methods: update_location(), update_status().

Rider Class:

Represents a user requesting a ride.

Attributes: rider_id (unique), name.

Ride Class:

Represents an individual ride booking.

Attributes: ride_id (unique), rider_id, driver_id, pickup_location, dropoff_location, start_time (of the ride itself), end_time, fare, status (RideStatus).

FareCalculator Class:

A utility class (or static methods) responsible for calculating the ride fare.

Attributes (constants): BASE_FARE, RATE_PER_KM, RATE_PER_MINUTE.

Method: calculate_fare(distance_km, duration_minutes).

BookingSystem Class (The Orchestrator):

The central class that manages all drivers, riders, and rides. It handles the core logic of booking, matching, and ride lifecycle.

Attributes (Data Structures):

_drivers: A dictionary to store all registered drivers, mapping driver_id to Driver objects (dict[str, Driver]).

_riders: A dictionary mapping rider_id to Rider objects (dict[str, Rider]).

_active_rides: A dictionary mapping ride_id to Ride objects for ongoing rides (dict[str, Ride]).

_driver_to_active_ride: A mapping of driver_id to ride_id for quick lookup (dict[str, str]).

_rider_to_active_ride: A mapping of rider_id to ride_id for quick lookup (dict[str, str]).

_next_ride_id_counter: For generating unique ride IDs.

Key Methods:

register_driver(), update_driver_location(), register_rider().

request_ride(): This is the core matching logic. It needs to efficiently find the closest available driver.

driver_arrived_at_pickup(), start_ride(), end_ride().

get_ride_status(), get_driver_status(), list_available_drivers().

Data Structures for Efficient Operations
The choice of data structures is crucial, especially for finding the closest available driver.

For _drivers, _riders, _active_rides: Standard Python dictionaries (dict) provide O(1) average time complexity for lookup by ID, which is perfect for get_driver_status, get_ride_status, etc.

For _driver_to_active_ride and _rider_to_active_ride: Also dictionaries for O(1) lookup.

For Finding the Closest Available Driver (in request_ride):

Simple Approach (Initial Design): Iterate through all drivers in _drivers. For each driver:

Check if their status is AVAILABLE.

Calculate the distance between their current_location and the pickup_location.

Filter out drivers outside the maximum matching radius.

Keep track of the closest driver found so far.

Pros: Simple to implement.

Cons: O(N) complexity where N is the total number of drivers. This is fine for a small number of drivers (tens or hundreds), but inefficient for thousands or millions.

Optimized Approach (Future Enhancement/Discussion): For a large number of drivers, we'd use geospatial indexing data structures like:

K-D Trees (K-Dimensional Trees): Efficient for finding nearest neighbors in 2D (or higher) space. Building is O(N log N), querying is O(log N) on average.

Quadtrees: Divides 2D space into quadrants. Good for finding points within a rectangular region.

Geospatial Databases: Real-world systems would leverage specialized databases like PostGIS (PostgreSQL extension) or MongoDB's Geospatial Indexes, which handle complex Earth geometry and efficient nearest-neighbor queries natively.

For this problem's scope, the simple O(N) iteration will be implemented, as it fits within typical interview time constraints and allows focus on other state management aspects.

Key Logic Flow
request_ride(rider_id, pickup_location, dropoff_location):
Validate input: Ensure rider exists, locations are valid.

Check if the rider already has an active ride. If so, deny.

Find Closest Available Driver:

Initialize closest_driver = None, min_distance = infinity.

Iterate through all driver objects in _drivers:

If driver.status is AVAILABLE:

Calculate distance = driver.current_location.distance_to(pickup_location).

If distance <= matching_radius:

If distance < min_distance or (distance == min_distance and driver.id is lexicographically smaller):

Update min_distance = distance.

Update closest_driver = driver.

If closest_driver is still None:

Raise NoDriverFoundError.

If a driver is found:

Generate a unique ride_id.

Create a Ride object with initial status = RideStatus.MATCHED and fare = 0.

Update closest_driver.status = DriverStatus.EN_ROUTE_TO_PICKUP.

Add the Ride to _active_rides.

Update _driver_to_active_ride and _rider_to_active_ride mappings.

Return the new Ride object.

end_ride(ride_id):
Validate input: Ensure ride_id exists and the ride's status is IN_PROGRESS.

Retrieve the Ride object from _active_rides.

Calculate distance_traveled (from pickup_location to dropoff_location).

Calculate duration_minutes (from ride.start_time to datetime.datetime.now()).

Calculate fare using FareCalculator.calculate_fare(distance_traveled, duration_minutes).

Update ride.status = RideStatus.COMPLETED.

Update ride.end_time = datetime.datetime.now().

Update ride.fare = calculated_fare.

Retrieve the Driver associated with this ride_id.

Update driver.status = DriverStatus.AVAILABLE.

Update driver.current_location to ride.dropoff_location.

Remove the ride from _active_rides (or move to a _completed_rides archive, for real systems).

Remove entries from _driver_to_active_ride and _rider_to_active_ride.

### Scalability of request_ride

- **Current Implementation**:
  - Iterates through all drivers in `_drivers` to find the closest available driver.
  - Time Complexity: O(N), where N is the total number of drivers.

- **Future Optimization**:
  - For large-scale systems, use geospatial indexing (e.g., K-D Trees, Quadtrees) to reduce the search space.
  - Example: A K-D Tree can reduce the complexity of finding the nearest driver to O(log N) on average.
  - Alternatively, integrate with geospatial databases like PostGIS or MongoDB for efficient nearest-neighbor queries.

### Scalability Considerations

1. **request_ride**:
   - Current implementation iterates through all drivers to find the closest available one, which is O(N).
   - For large-scale systems, consider using geospatial indexing (e.g., K-D Trees, Quadtrees) or integrating with geospatial databases like PostGIS for O(log N) complexity.

2. **Future Enhancements**:
   - Add support for ride cancellation by riders or drivers.
   - Implement driver acceptance/rejection logic for ride requests.
   - Introduce surge pricing based on demand and supply.

