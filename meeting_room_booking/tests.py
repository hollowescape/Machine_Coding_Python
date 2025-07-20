# tests/test_booking_system.py
import unittest
import datetime
from services.meeting_room_booking_system import MeetingRoomBookingSystem
from models.room import Room
from models.booking import Booking
from exceptions import (
    InvalidInputException, RoomNotFoundException, BookingOverLapException,
    BookingNotFoundException
)


class TestMeetingRoomBookingSystem(unittest.TestCase):

    def setUp(self):
        self.system = MeetingRoomBookingSystem()
        self.system.register_rooms(["RoomA", "RoomB"])

        # Define some common times for testing
        self.t9 = datetime.datetime(2025, 7, 20, 9, 0)
        self.t10 = datetime.datetime(2025, 7, 20, 10, 0)
        self.t11 = datetime.datetime(2025, 7, 20, 11, 0)
        self.t12 = datetime.datetime(2025, 7, 20, 12, 0)
        self.t13 = datetime.datetime(2025, 7, 20, 13, 0)
        self.t14 = datetime.datetime(2025, 7, 20, 14, 0)

    # --- Room Model Tests ---
    def test_room_init_valid(self):
        room = Room("TestRoom")
        self.assertEqual(room.get_id(), "TestRoom")
        self.assertEqual(room.get_all_bookings(), [])

    def test_room_init_invalid_id(self):
        with self.assertRaises(InvalidInputException):
            Room("")
        with self.assertRaises(InvalidInputException):
            Room("   ")
        with self.assertRaises(InvalidInputException):
            Room(123)

    def test_booking_overlaps(self):
        booking1 = Booking("b1", "r1", "u1", self.t10, self.t12)

        # Exact overlap
        self.assertTrue(booking1.overlaps(self.t10, self.t12))

        # Partial overlap (new starts inside)
        self.assertTrue(booking1.overlaps(self.t11, self.t13))

        # Partial overlap (new ends inside)
        self.assertTrue(booking1.overlaps(self.t9, self.t11))

        # New encompasses old
        self.assertTrue(booking1.overlaps(self.t9, self.t13))

        # Old encompasses new
        self.assertTrue(
            booking1.overlaps(self.t10 + datetime.timedelta(minutes=10), self.t12 - datetime.timedelta(minutes=10)))

        # No overlap (abutting)
        self.assertFalse(booking1.overlaps(self.t9, self.t10))
        self.assertFalse(booking1.overlaps(self.t12, self.t13))

    def test_room_add_booking_maintains_sort_order(self):
        room = Room("TestRoom")
        b1 = Booking("b1", "TestRoom", "u1", self.t11, self.t12)
        b2 = Booking("b2", "TestRoom", "u1", self.t9, self.t10)
        b3 = Booking("b3", "TestRoom", "u1", self.t10 + datetime.timedelta(minutes=30),
                     self.t11 + datetime.timedelta(minutes=30))

        room.add_booking(b1)
        room.add_booking(b2)  # Should be inserted before b1
        room.add_booking(b3)  # Should be inserted between b2 and b1

        bookings = room.get_all_bookings()
        self.assertEqual(len(bookings), 3)
        self.assertEqual(bookings[0].get_id(), "b2")  # 9:00-10:00
        self.assertEqual(bookings[1].get_id(), "b3")  # 10:30-11:30
        self.assertEqual(bookings[2].get_id(),
                         "b1")  # 11:00-12:00 (note: 10:30-11:30 and 11:00-12:00 overlap, but add_booking assumes no overlap)
        # The overlap check is done by the system, not directly by room.add_booking
        # The sorting key is only start_time, so b3 and b1 order depends on exact seconds,
        # but for this test, t11 is less than t10+30m. Let's fix times to ensure order.
        b1 = Booking("b1", "TestRoom", "u1", self.t11, self.t12)  # 11:00
        b2 = Booking("b2", "TestRoom", "u1", self.t9, self.t10)  # 9:00
        b3 = Booking("b3", "TestRoom", "u1", self.t10, self.t11)  # 10:00
        room = Room("TestRoom")
        room.add_booking(b1)
        room.add_booking(b2)
        room.add_booking(b3)
        bookings = room.get_all_bookings()
        self.assertEqual(bookings[0].get_id(), "b2")
        self.assertEqual(bookings[1].get_id(), "b3")
        self.assertEqual(bookings[2].get_id(), "b1")

    def test_room_remove_booking(self):
        room = Room("TestRoom")
        b1_id = "b1"
        b2_id = "b2"
        room.add_booking(Booking(b1_id, "TestRoom", "u1", self.t10, self.t11))
        room.add_booking(Booking(b2_id, "TestRoom", "u1", self.t12, self.t13))

        self.assertEqual(len(room.get_all_bookings()), 2)
        room.remove_booking(b1_id)
        self.assertEqual(len(room.get_all_bookings()), 1)
        self.assertEqual(room.get_all_bookings()[0].get_id(), b2_id)

    def test_room_remove_non_existent_booking(self):
        room = Room("TestRoom")
        room.add_booking(Booking("b1", "TestRoom", "u1", self.t10, self.t11))
        with self.assertRaises(BookingNotFoundException):
            room.remove_booking("non_existent_id")

    # --- System-level Tests ---
    def test_register_rooms_success(self):
        system = MeetingRoomBookingSystem()
        system.register_rooms(["RoomX", "RoomY"])
        self.assertIn("RoomX", system._rooms)
        self.assertIn("RoomY", system._rooms)
        self.assertIsInstance(system._rooms["RoomX"], Room)

    def test_register_rooms_invalid_input(self):
        system = MeetingRoomBookingSystem()
        with self.assertRaises(InvalidInputException):
            system.register_rooms("not_a_list")

        # Test warning for invalid string IDs
        with self.assertLogs(level='WARNING') as cm:  # This will check print statements
            system.register_rooms(["valid", "", "   ", "valid2"])
        self.assertIn("Warning: Skipping invalid room ID ''", cm.output[0])
        self.assertIn("Warning: Skipping invalid room ID '   '", cm.output[1])
        self.assertIn("valid", system._rooms)
        self.assertIn("valid2", system._rooms)
        self.assertNotIn("", system._rooms)

    def test_book_room_success(self):
        booking_id = self.system.book_room("RoomA", "user1", self.t10, self.t11)
        self.assertIsNotNone(booking_id)
        self.assertIn(booking_id, self.system._all_bookings_index)
        self.assertEqual(len(self.system._rooms["RoomA"].get_all_bookings()), 1)

    def test_book_room_not_found(self):
        with self.assertRaises(RoomNotFoundException):
            self.system.book_room("NonExistentRoom", "user1", self.t10, self.t11)

    def test_book_room_overlap_existing(self):
        self.system.book_room("RoomA", "user1", self.t10, self.t12)
        with self.assertRaises(BookingOverLapException):
            self.system.book_room("RoomA", "user2", self.t11, self.t13)  # Overlaps end of first
        with self.assertRaises(BookingOverLapException):
            self.system.book_room("RoomA", "user3", self.t9, self.t11)  # Overlaps start of first
        with self.assertRaises(BookingOverLapException):
            self.system.book_room("RoomA", "user4", self.t10, self.t12)  # Exact overlap

    def test_book_room_abutting_no_overlap(self):
        self.system.book_room("RoomA", "user1", self.t10, self.t11)
        booking_id2 = self.system.book_room("RoomA", "user2", self.t11, self.t12)  # Abutting, no overlap
        self.assertIsNotNone(booking_id2)
        self.assertEqual(len(self.system._rooms["RoomA"].get_all_bookings()), 2)

    def test_cancel_booking_success(self):
        booking_id = self.system.book_room("RoomA", "user1", self.t10, self.t11)
        self.system.cancel_booking(booking_id)
        self.assertNotIn(booking_id, self.system._all_bookings_index)
        self.assertEqual(len(self.system._rooms["RoomA"].get_all_bookings()), 0)

        # Ensure it's now available
        self.assertTrue(self.system.check_room_availability_for_slot("RoomA", self.t10, self.t11))

    def test_cancel_booking_not_found(self):
        with self.assertRaises(BookingNotFoundException):
            self.system.cancel_booking("NonExistentBooking")

    def test_check_room_availability_for_slot(self):
        self.system.book_room("RoomA", "user1", self.t10, self.t11)
        self.assertFalse(self.system.check_room_availability_for_slot("RoomA", self.t10, self.t11))  # Exact match
        self.assertFalse(self.system.check_room_availability_for_slot("RoomA", self.t9, self.t10 + datetime.timedelta(
            minutes=30)))  # Overlap
        self.assertTrue(self.system.check_room_availability_for_slot("RoomA", self.t9, self.t10))  # Abutting start
        self.assertTrue(self.system.check_room_availability_for_slot("RoomA", self.t11, self.t12))  # Abutting end
        self.assertTrue(
            self.system.check_room_availability_for_slot("RoomB", self.t10, self.t11))  # Other room available

    def test_get_room_bookings(self):
        b1_id = self.system.book_room("RoomA", "user1", self.t11, self.t12)
        b2_id = self.system.book_room("RoomA", "user2", self.t9, self.t10)

        bookings = self.system.get_room_bookings("RoomA")
        self.assertEqual(len(bookings), 2)
        # Should be sorted by start time
        self.assertEqual(bookings[0].get_id(), b2_id)
        self.assertEqual(bookings[1].get_id(), b1_id)

    def test_get_room_bookings_room_not_found(self):
        with self.assertRaises(RoomNotFoundException):
            self.system.get_room_bookings("NonExistentRoom")

    def test_list_user_bookings(self):
        self.system.book_room("RoomA", "userX", self.t10, self.t11)
        b2_id = self.system.book_room("RoomB", "userX", self.t12, self.t13)
        self.system.book_room("RoomA", "userY", self.t9, self.t10)  # Another user

        user_x_bookings = self.system.list_user_bookings("userX")
        self.assertEqual(len(user_x_bookings), 2)
        # Should be sorted by start time
        self.assertEqual(user_x_bookings[0].get_room_id(), "RoomA")
        self.assertEqual(user_x_bookings[1].get_room_id(), "RoomB")

        user_y_bookings = self.system.list_user_bookings("userY")
        self.assertEqual(len(user_y_bookings), 1)

    def test_list_user_bookings_no_bookings(self):
        self.assertEqual(len(self.system.list_user_bookings("non_existent_user")), 0)

    def test_book_invalid_time_range(self):
        with self.assertRaises(InvalidInputException):
            self.system.book_room("RoomA", "user1", self.t11, self.t10)
        with self.assertRaises(InvalidInputException):
            self.system.book_room("RoomA", "user1", self.t10, self.t10)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)