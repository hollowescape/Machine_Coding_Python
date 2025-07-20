# tests/test_food_delivery_system.py
import unittest
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to allow importing modules from root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from online_food_delivery.food_delivery_system import FoodDeliverySystem
from online_food_delivery.models.dish import Dish
from online_food_delivery.models.restaurant import Restaurant
from online_food_delivery.models.user import User
from online_food_delivery.models.order import Order
from online_food_delivery.enums.enums import OrderStatus, VALID_ORDER_TRANSITIONS, is_valid_transition
from online_food_delivery.exceptions import (
    FoodDeliverySystemError, RestaurantNotFoundError, UserNotFoundError,
    OrderNotFoundError, DishNotFoundError, InvalidOrderError,
    InvalidStatusTransitionError, DuplicateEntryError
)


class TestFoodDeliverySystem(unittest.TestCase):

    def setUp(self):
        self.system = FoodDeliverySystem()

        # Register sample restaurant
        self.burger_menu_data = [
            {'name': 'Classic Burger', 'description': 'Beef patty', 'price': 12.50},
            {'name': 'Fries', 'description': 'Crispy fries', 'price': 3.00}
        ]
        self.res1 = self.system.register_restaurant("Burger Joint", self.burger_menu_data, "Downtown")
        self.res1_id = self.res1.get_id()

        # Register sample user
        self.user1 = self.system.register_user("Alice", "123 Main St")
        self.user1_id = self.user1.get_id()

        # Register another user and restaurant for specific tests
        self.pizza_menu_data = [
            {'name': 'Pepperoni', 'price': 15.00},
            {'name': 'Margherita Pizza', 'description': 'Classic cheese pizza', 'price': 14.00},  # ADD THIS DISH
            {'name': 'Garlic Bread', 'description': 'Side order', 'price': 4.50}
            # Add if your test uses it later, matching main.py
        ]
        self.res2 = self.system.register_restaurant("Pizza Place", self.pizza_menu_data, "Uptown")
        self.res2_id = self.res2.get_id()
        self.user2 = self.system.register_user("Bob", "456 Side Ave")
        self.user2_id = self.user2.get_id()

        self.initial_res1_order_for_alice = self.system.place_order(self.user1_id, self.res1_id, {'Classic Burger': 1})

    # --- Test Restaurant Registration ---
    def test_register_restaurant_success(self):
        new_res = self.system.register_restaurant("Sushi Spot", [{'name': 'Nigiri', 'price': 2.50}], "West Side")
        self.assertIsInstance(new_res, Restaurant)
        self.assertIn(new_res.get_id(), self.system._restaurants)
        self.assertEqual(new_res.get_name(), "Sushi Spot")
        self.assertEqual(len(new_res.get_menu_items()), 1)

    def test_register_restaurant_duplicate_name(self):
        with self.assertRaises(DuplicateEntryError):
            self.system.register_restaurant("Burger Joint", self.burger_menu_data, "Another Spot")

    def test_register_restaurant_invalid_data(self):
        with self.assertRaises(ValueError):  # No name
            self.system.register_restaurant("", self.burger_menu_data, "Downtown")
        with self.assertRaises(ValueError):  # Empty menu
            self.system.register_restaurant("Empty Cafe", [], "Downtown")

    # --- Test User Registration ---
    def test_register_user_success(self):
        new_user = self.system.register_user("Charlie", "789 Elm St")
        self.assertIsInstance(new_user, User)
        self.assertIn(new_user.get_id(), self.system._users)
        self.assertEqual(new_user.get_name(), "Charlie")

    def test_register_user_duplicate(self):
        with self.assertRaises(DuplicateEntryError):
            self.system.register_user("Alice", "123 Main St")

    def test_register_user_invalid_data(self):
        with self.assertRaises(ValueError):  # No name
            self.system.register_user("", "Anywhere")
        with self.assertRaises(ValueError):  # No address
            self.system.register_user("Dave", "")

    # --- Test Search Restaurants ---
    def test_search_restaurants_by_name(self):
        results = self.system.search_restaurants("Burger")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get_name(), "Burger Joint")

        results = self.system.search_restaurants("Pizza")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get_name(), "Pizza Place")

    def test_search_restaurants_case_insensitive(self):
        results = self.system.search_restaurants("burger")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get_name(), "Burger Joint")

    def test_search_restaurants_no_match(self):
        results = self.system.search_restaurants("Sushi")
        self.assertEqual(len(results), 0)

    # --- Test Place Order ---
    def test_place_order_success(self):
        dish_qty = {'Classic Burger': 1, 'Fries': 2}
        order = self.system.place_order(self.user1_id, self.res1_id, dish_qty)

        self.assertIsInstance(order, Order)
        self.assertEqual(order.get_user_id(), self.user1_id)
        self.assertEqual(order.get_restaurant_id(), self.res1_id)
        self.assertEqual(order.get_status(), OrderStatus.PENDING)
        self.assertEqual(order.get_total_amount(), 12.50 * 1 + 3.00 * 2)  # 12.50 + 6.00 = 18.50
        self.assertEqual(len(order.get_items()), 2)
        self.assertIn(order.get_id(), self.system._orders)
        self.assertIn(order, self.system._user_orders_index[self.user1_id])
        self.assertIn(order, self.system._restaurant_orders_index[self.res1_id])

    def test_place_order_invalid_user(self):
        dish_qty = {'Classic Burger': 1}
        with self.assertRaises(UserNotFoundError):
            self.system.place_order("non_existent_user_id", self.res1_id, dish_qty)

    def test_place_order_invalid_restaurant(self):
        dish_qty = {'Classic Burger': 1}
        with self.assertRaises(RestaurantNotFoundError):
            self.system.place_order(self.user1_id, "non_existent_res_id", dish_qty)

    def test_place_order_dish_not_found(self):
        dish_qty = {'NonExistentDish': 1}
        with self.assertRaises(DishNotFoundError):
            self.system.place_order(self.user1_id, self.res1_id, dish_qty)

    def test_place_order_empty_items(self):
        dish_qty = {}
        with self.assertRaises(InvalidOrderError):
            self.system.place_order(self.user1_id, self.res1_id, dish_qty)

    def test_place_order_zero_quantity(self):
        dish_qty = {'Classic Burger': 0}
        with self.assertRaises(InvalidOrderError):
            self.system.place_order(self.user1_id, self.res1_id, dish_qty)

    # --- Test Update Order Status ---
    def test_update_order_status_valid_transition(self):
        dish_qty = {'Classic Burger': 1}
        order = self.system.place_order(self.user1_id, self.res1_id, dish_qty)
        order_id = order.get_id()

        self.assertEqual(order.get_status(), OrderStatus.PENDING)

        self.system.update_order_status(order_id, OrderStatus.ACCEPTED)
        self.assertEqual(order.get_status(), OrderStatus.ACCEPTED)
        self.assertIn(OrderStatus.ACCEPTED, order.get_timestamps())

        self.system.update_order_status(order_id, OrderStatus.PREPARING)
        self.assertEqual(order.get_status(), OrderStatus.PREPARING)

    def test_update_order_status_invalid_transition(self):
        dish_qty = {'Classic Burger': 1}
        order = self.system.place_order(self.user1_id, self.res1_id, dish_qty)
        order_id = order.get_id()

        self.assertEqual(order.get_status(), OrderStatus.PENDING)

        # PENDING directly to DELIVERED is invalid
        with self.assertRaises(InvalidStatusTransitionError):
            self.system.update_order_status(order_id, OrderStatus.DELIVERED)

        # After DELIVERED, no more transitions
        self.system.update_order_status(order_id, OrderStatus.ACCEPTED)
        self.system.update_order_status(order_id, OrderStatus.PREPARING)
        self.system.update_order_status(order_id, OrderStatus.READY_FOR_PICKUP)
        self.system.update_order_status(order_id, OrderStatus.OUT_FOR_DELIVERY)
        self.system.update_order_status(order_id, OrderStatus.DELIVERED)
        self.assertEqual(order.get_status(), OrderStatus.DELIVERED)

        with self.assertRaises(InvalidStatusTransitionError):
            self.system.update_order_status(order_id, OrderStatus.CANCELLED)

    def test_update_order_status_order_not_found(self):
        with self.assertRaises(OrderNotFoundError):
            self.system.update_order_status("non_existent_order_id", OrderStatus.ACCEPTED)

    def test_update_order_status_cancel_from_pending(self):
        dish_qty = {'Classic Burger': 1}
        order = self.system.place_order(self.user1_id, self.res1_id, dish_qty)
        self.system.update_order_status(order.get_id(), OrderStatus.CANCELLED)
        self.assertEqual(order.get_status(), OrderStatus.CANCELLED)

    def test_update_order_status_cancel_from_accepted(self):
        dish_qty = {'Classic Burger': 1}
        order = self.system.place_order(self.user1_id, self.res1_id, dish_qty)
        self.system.update_order_status(order.get_id(), OrderStatus.ACCEPTED)
        self.system.update_order_status(order.get_id(), OrderStatus.CANCELLED)
        self.assertEqual(order.get_status(), OrderStatus.CANCELLED)

    def test_update_order_status_cancel_after_preparing_invalid(self):
        dish_qty = {'Classic Burger': 1}
        order = self.system.place_order(self.user1_id, self.res1_id, dish_qty)
        self.system.update_order_status(order.get_id(), OrderStatus.ACCEPTED)
        self.system.update_order_status(order.get_id(), OrderStatus.PREPARING)
        with self.assertRaises(InvalidStatusTransitionError):
            self.system.update_order_status(order.get_id(), OrderStatus.CANCELLED)

    # --- Test Get Order Details ---
    def test_get_order_details_success(self):
        dish_qty = {'Classic Burger': 1}
        order = self.system.place_order(self.user1_id, self.res1_id, dish_qty)
        retrieved_order = self.system.get_order_details(order.get_id())
        self.assertEqual(order.get_id(), retrieved_order.get_id())
        self.assertEqual(order.get_total_amount(), retrieved_order.get_total_amount())

    def test_get_order_details_not_found(self):
        with self.assertRaises(OrderNotFoundError):
            self.system.get_order_details("non_existent_id")

    # --- Test Get User Order History ---
    def test_get_user_order_history_success(self):
        # Alice has one order from setUp
        history = self.system.get_user_order_history(self.user1_id)
        self.assertEqual(len(history), 1)  # Order from setUp

        # Place another order for Alice
        dish_qty_alice2 = {'Fries': 1}
        order_alice2 = self.system.place_order(self.user1_id, self.res1_id, dish_qty_alice2)
        history_updated = self.system.get_user_order_history(self.user1_id)
        self.assertEqual(len(history_updated), 2)
        self.assertIn(order_alice2, history_updated)

    def test_get_user_order_history_no_orders(self):
        # User Bob has no orders yet
        history = self.system.get_user_order_history(self.user2_id)
        self.assertEqual(len(history), 0)

    def test_get_user_order_history_user_not_found(self):
        with self.assertRaises(UserNotFoundError):
            self.system.get_user_order_history("non_existent_user_id")

    # --- Test Get Restaurant Orders ---
    def test_get_restaurant_orders_no_filter(self):
        # Place order from res1 for user2
        order_res1_user2 = self.system.place_order(self.user2_id, self.res1_id, {'Fries': 3})

        orders = self.system.get_restaurant_orders(self.res1_id)
        self.assertEqual(len(orders), 2)  # 1 from setUp, 1 just placed
        self.assertIn(order_res1_user2, orders)

    def test_get_restaurant_orders_with_filter(self):
        # Place an order for res2
        order_res2_1 = self.system.place_order(self.user1_id, self.res2_id, {'Pepperoni': 1})
        self.system.update_order_status(order_res2_1.get_id(), OrderStatus.ACCEPTED)

        # Place another order for res2, keep pending
        order_res2_2 = self.system.place_order(self.user2_id, self.res2_id, {'Margherita Pizza': 1})

        # Filter for ACCEPTED orders from res2
        accepted_orders = self.system.get_restaurant_orders(self.res2_id, OrderStatus.ACCEPTED)
        self.assertEqual(len(accepted_orders), 1)
        self.assertEqual(accepted_orders[0].get_id(), order_res2_1.get_id())
        self.assertEqual(accepted_orders[0].get_status(), OrderStatus.ACCEPTED)

        # Filter for PENDING orders from res2
        pending_orders = self.system.get_restaurant_orders(self.res2_id, OrderStatus.PENDING)
        self.assertEqual(len(pending_orders), 1)
        self.assertEqual(pending_orders[0].get_id(), order_res2_2.get_id())
        self.assertEqual(pending_orders[0].get_status(), OrderStatus.PENDING)

    def test_get_restaurant_orders_no_orders(self):
        # Use a new restaurant that hasn't had orders
        new_res = self.system.register_restaurant("Cafe Fresh", [{'name': 'Coffee', 'price': 5.0}], "Midtown")
        orders = self.system.get_restaurant_orders(new_res.get_id())
        self.assertEqual(len(orders), 0)

    def test_get_restaurant_orders_restaurant_not_found(self):
        with self.assertRaises(RestaurantNotFoundError):
            self.system.get_restaurant_orders("non_existent_res_id")


# This block allows you to run tests directly from the file
if __name__ == '__main__':
    # Use argv=[] to prevent unittest from trying to parse command-line args for itself
    unittest.main(argv=['first-arg-is-ignored'], exit=False)