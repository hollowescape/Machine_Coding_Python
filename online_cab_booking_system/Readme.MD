# Problem Statement: Design an Online Cab Booking System

You are tasked with designing and implementing a simplified **Online Cab Booking System**, similar to Uber or Ola. The system should allow riders to request a ride, drivers to accept/complete rides, and track the state of bookings.

---

## System Requirements

### Driver Management
1. **Register Driver**:  
   - Add a new driver to the system.  
   - Each driver has:
     - A unique `driver_id`.
     - `name`.
     - `vehicle_details` (e.g., model, plate number).
     - An initial `current_location` (latitude, longitude).

2. **Update Driver Location**:  
   - Drivers continuously send their updated `current_location`.

### Rider Management
1. **Register Rider**:  
   - Add a new rider to the system.  
   - Each rider has:
     - A unique `rider_id`.
     - `name`.

### Ride Booking
1. **Request Ride**:  
   - A rider requests a ride by providing:
     - `rider_id`
     - `pickup_location` (latitude, longitude)
     - `dropoff_location` (latitude, longitude)

2. **Driver Matching**:  
   - The system finds the closest available driver within a predefined radius (e.g., 5 km) of the `pickup_location`.
   - **Matching Rules**:
     - If multiple drivers are equally close, any can be chosen.
     - If no drivers are available within the radius, the request should fail.
   - The matched driver's status changes to `EN_ROUTE_TO_PICKUP`.

3. **Booking Confirmation**:  
   - If a driver is matched, return a `Ride` object containing:
     - `ride_id`
     - `rider_id`
     - `driver_id`
     - `pickup_location`
     - `dropoff_location`
     - `status`
     - `fare` (initially 0)

### Ride Lifecycle Management
1. **Driver Arrives at Pickup**:  
   - Driver signals arrival at the pickup location.  
   - The `Ride` status changes to `ARRIVED_AT_PICKUP`.

2. **Ride Started**:  
   - Driver signals the ride has started.  
   - The `Ride` status changes to `IN_PROGRESS`.

3. **Ride Ended**:  
   - Driver signals the ride has ended at the `dropoff_location`.  
   - The `Ride` status changes to `COMPLETED`.  
   - **Fare Calculation**:
     - `fare = base_fare + (distance_traveled * rate_per_km) + (time_spent_in_ride * rate_per_minute)`
     - Use simplified straight-line distance (Euclidean or Manhattan distance).
   - The driver's status reverts to `AVAILABLE`, and their `current_location` updates to the `dropoff_location`.

### Querying/Reporting
1. **Get Ride Status**:  
   - Given a `ride_id`, return the current status of the ride.

2. **Get Driver Status**:  
   - Given a `driver_id`, return their current status and last known location.

3. **List Available Drivers**:  
   - Return a list of all drivers currently marked as `AVAILABLE`, along with their locations.

---

## Core Entities
1. **Location**:  
   - A simple class or named tuple to represent `(latitude, longitude)`.

2. **Driver**:  
   - Represents a driver in the system.

3. **Rider**:  
   - Represents a rider in the system.

4. **Ride**:  
   - Represents an ongoing or completed ride.

5. **BookingSystem**:  
   - The main orchestrator for all operations.

---

## State Machines
- **Driver States**:  
  - `AVAILABLE`, `EN_ROUTE_TO_PICKUP`, `IN_RIDE`, `IDLE`

- **Ride States**:  
  - `REQUESTED`, `MATCHED`, `ARRIVED_AT_PICKUP`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`

---

## Distance Calculation
- Use a simple Euclidean distance formula between two `(lat, lon)` points:  
  ```
  d = sqrt((x2 - x1)^2 + (y2 - y1)^2)
  ```
