# main.py or app.py
import datetime
from services.meeting_room_booking_system import MeetingRoomBookingSystem
from exceptions import (
    BookingSystemException, InvalidInputException, RoomNotFoundException,
    BookingOverLapException, BookingNotFoundException
)


def parse_time(time_str: str) -> datetime.datetime:
    """Helper to parse HH:MM string into today's datetime object."""
    try:
        hour, minute = map(int, time_str.split(':'))
        # Using a fixed date for simplicity, can be extended to handle dates
        today = datetime.date.today()  # Or a fixed date like datetime.date(2025, 7, 19)
        return datetime.datetime(today.year, today.month, today.day, hour, minute)
    except ValueError:
        raise InvalidInputException("Time format must be HH:MM (e.g., 09:30).")


def run_booking_cli():
    system = MeetingRoomBookingSystem()

    print("Welcome to the Meeting Room Booking System!")

    # Initialize rooms
    initial_rooms = input("Enter room IDs to register (comma-separated, e.g., A101,B202): ").strip()
    if initial_rooms:
        system.register_rooms([r.strip() for r in initial_rooms.split(',')])
    else:
        print("No rooms registered. Please restart or manually register rooms later.")
        print("Register default rooms: A101,B202,C303")
        system.register_rooms(["A101", "B202", "C303"])

    while True:
        print("\n--- Booking System Commands ---")
        print("  book <room_id> <user_id> <start_time_HH:MM> <end_time_HH:MM>")
        print("  cancel <booking_id>")
        print("  check_available <room_id> <start_time_HH:MM> <end_time_HH:MM>")
        print("  room_bookings <room_id>")
        print("  user_bookings <user_id>")
        print("  exit")

        command_line = input("Enter command: ").strip()
        parts = command_line.split(maxsplit=4)  # maxsplit for book command

        try:
            cmd = parts[0].lower()

            if cmd == "book":
                if len(parts) == 5:
                    room_id, user_id, start_time_str, end_time_str = parts[1], parts[2], parts[3], parts[4]
                    start_time = parse_time(start_time_str)
                    end_time = parse_time(end_time_str)
                    booking_id = system.book_room(room_id, user_id, start_time, end_time)
                    print(f"Successfully booked. Your booking ID: {booking_id}")
                else:
                    print("Usage: book <room_id> <user_id> <start_time_HH:MM> <end_time_HH:MM>")

            elif cmd == "cancel":
                if len(parts) == 2:
                    booking_id = parts[1]
                    system.cancel_booking(booking_id)
                else:
                    print("Usage: cancel <booking_id>")

            elif cmd == "check_available":
                if len(parts) == 4:
                    room_id, start_time_str, end_time_str = parts[1], parts[2], parts[3]
                    start_time = parse_time(start_time_str)
                    end_time = parse_time(end_time_str)
                    available = system.check_room_availability_for_slot(room_id, start_time, end_time)
                    print(f"Room '{room_id}' available from {start_time_str} to {end_time_str}: {available}")
                else:
                    print("Usage: check_available <room_id> <start_time_HH:MM> <end_time_HH:MM>")

            elif cmd == "room_bookings":
                if len(parts) == 2:
                    room_id = parts[1]
                    bookings = system.get_room_bookings(room_id)
                    if bookings:
                        print(f"--- Bookings for Room '{room_id}' ---")
                        for b in bookings:
                            print(f"- {b}")
                    else:
                        print(f"No active bookings for Room '{room_id}'.")
                else:
                    print("Usage: room_bookings <room_id>")

            elif cmd == "user_bookings":
                if len(parts) == 2:
                    user_id = parts[1]
                    bookings = system.list_user_bookings(user_id)
                    if bookings:
                        print(f"--- Bookings by User '{user_id}' ---")
                        for b in bookings:
                            print(f"- {b}")
                    else:
                        print(f"No active bookings found for User '{user_id}'.")
                else:
                    print("Usage: user_bookings <user_id>")

            elif cmd == "exit":
                print("Exiting Meeting Room Booking System. Goodbye!")
                break

            else:
                print("Unknown command.")

        except (BookingSystemException, ValueError, TypeError) as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    run_booking_cli()