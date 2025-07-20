# main.py
import datetime
import time  # For simulating delays and duration
from typing import Dict, Any

from online_cab_booking_system.services.cab_booking_system import BookingSystem
from .models.location import Location
from .models.driver import Driver
from .models.rider import Rider
from .enums.enums import DriverStatus, RideStatus
from exceptions import BookingSystemError, InvalidInputError


def parse_location(loc_str: str) -> Location:
    """Helper to parse 'lat,lon' string into a Location object."""
    try:
        lat, lon = map(float, loc_str.split(','))
        return Location(lat, lon)
    except (ValueError, IndexError):
        raise InvalidInputError(f"Invalid location format: '{loc_str}'. Expected 'latitude,longitude'.")


def run_cli():
    system = BookingSystem()

    # --- Initial Setup for Demo ---
    print("\n--- Initializing Demo Data ---")
    system.register_driver("D1", "Alice", {"model": "Sedan", "plate": "KA01A1234"}, Location(12.9716, 77.5946),
                           DriverStatus.AVAILABLE)  # Bangalore City Center
    system.register_driver("D2", "Bob", {"model": "SUV", "plate": "KA02B5678"}, Location(12.9800, 77.5800),
                           DriverStatus.AVAILABLE)  # Near Majestic
    system.register_driver("D3", "Charlie", {"model": "Hatchback", "plate": "KA03C9101"}, Location(12.9500, 77.6500),
                           DriverStatus.AVAILABLE)  # Near Koramangala
    system.register_driver("D4", "David", {"model": "Mini", "plate": "KA04D1122"}, Location(12.9700, 77.5900),
                           DriverStatus.AVAILABLE)  # Close to D1
    system.register_driver("D5", "Eve", {"model": "Luxury", "plate": "KA05E3344"}, Location(13.0000, 77.5600),
                           DriverStatus.AVAILABLE)  # Farther North

    system.register_rider("R1", "John Doe")
    system.register_rider("R2", "Jane Smith")
    system.register_rider("R3", "Alice Brown")

    print("\n--- Cab Booking System CLI ---")
    print("Commands:")
    print("  register_driver <id> <name> <vehicle_model> <plate_num> <lat,lon>")
    print("  update_driver_loc <id> <lat,lon>")
    print("  register_rider <id> <name>")
    print("  request_ride <rider_id> <pickup_lat,lon> <dropoff_lat,lon>")
    print("  driver_arrived <ride_id>")
    print("  start_ride <ride_id>")
    print("  end_ride <ride_id>")
    print("  get_ride_status <ride_id>")
    print("  get_driver_status <driver_id>")
    print("  list_available_drivers")
    print("  system_overview")
    print("  exit")

    while True:
        try:
            command_line = input("\nEnter command: ").strip()
            parts = command_line.split(maxsplit=4)  # Use maxsplit for commands with multiple arguments
            cmd = parts[0].lower()

            if cmd == "register_driver":
                if len(parts) >= 5:
                    driver_id, name, model, plate, loc_str = parts[1], parts[2], parts[3], parts[4], parts[5] if len(
                        parts) > 5 else "0,0"
                    if len(parts) > 5:
                        model = parts[3]
                        plate = parts[4]
                        loc_str = parts[5]
                    else:
                        print("Usage: register_driver <id> <name> <vehicle_model> <plate_num> <lat,lon>")
                        continue

                    vehicle_details = {"model": model, "plate": plate}
                    loc = parse_location(loc_str)
                    system.register_driver(driver_id, name, vehicle_details, loc)
                else:
                    print("Usage: register_driver <id> <name> <vehicle_model> <plate_num> <lat,lon>")

            elif cmd == "update_driver_loc":
                if len(parts) == 3:
                    driver_id = parts[1]
                    loc = parse_location(parts[2])
                    system.update_driver_location(driver_id, loc)
                else:
                    print("Usage: update_driver_loc <id> <lat,lon>")

            elif cmd == "register_rider":
                if len(parts) == 3:
                    rider_id, name = parts[1], parts[2]
                    system.register_rider(rider_id, name)
                else:
                    print("Usage: register_rider <id> <name>")

            elif cmd == "request_ride":
                if len(parts) == 4:
                    rider_id = parts[1]
                    pickup_loc = parse_location(parts[2])
                    dropoff_loc = parse_location(parts[3])
                    ride = system.request_ride(rider_id, pickup_loc, dropoff_loc)
                    print(f"Ride requested successfully: {ride}")
                else:
                    print("Usage: request_ride <rider_id> <pickup_lat,lon> <dropoff_lat,lon>")

            elif cmd == "driver_arrived":
                if len(parts) == 2:
                    ride_id = parts[1]
                    system.driver_arrived_at_pickup(ride_id)
                else:
                    print("Usage: driver_arrived <ride_id>")

            elif cmd == "start_ride":
                if len(parts) == 2:
                    ride_id = parts[1]
                    system.start_ride(ride_id)
                else:
                    print("Usage: start_ride <ride_id>")

            elif cmd == "end_ride":
                if len(parts) == 2:
                    ride_id = parts[1]
                    fare = system.end_ride(ride_id)
                    print(f"Ride {ride_id} ended. Final Fare: ${fare:.2f}")
                else:
                    print("Usage: end_ride <ride_id>")

            elif cmd == "get_ride_status":
                if len(parts) == 2:
                    ride_id = parts[1]
                    ride = system.get_ride_status(ride_id)
                    print(f"Ride Status: {ride}")
                else:
                    print("Usage: get_ride_status <ride_id>")

            elif cmd == "get_driver_status":
                if len(parts) == 2:
                    driver_id = parts[1]
                    status = system.get_driver_status(driver_id)
                    print(f"Driver Status for {driver_id}: {status}")
                else:
                    print("Usage: get_driver_status <driver_id>")

            elif cmd == "list_available_drivers":
                drivers = system.list_available_drivers()
                print("\n--- Available Drivers ---")
                if drivers:
                    for d in drivers:
                        print(f"  ID: {d['driver_id']}, Name: {d['name']}, Location: {d['location']}")
                else:
                    print("  No drivers currently available.")
                print("-------------------------")

            elif cmd == "system_overview":
                overview = system.get_system_overview()
                print("\n--- System Overview ---")
                for key, value in overview.items():
                    print(f"  {key.replace('_', ' ').title()}: {value}")
                print("-----------------------")

            elif cmd == "exit":
                print("Exiting Cab Booking System. Goodbye!")
                break

            else:
                print("Unknown command.")

        except (BookingSystemError, InvalidInputError, ValueError, IndexError, KeyError) as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            # Optional: for debugging, uncomment traceback
            # import traceback
            # traceback.print_exc()


if __name__ == "__main__":
    run_cli()