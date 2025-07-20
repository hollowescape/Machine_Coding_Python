from typing import Dict, List, Optional, Tuple

from online_food_delivery.enums.enums import OrderStatus
from online_food_delivery.exceptions import OrderNotFoundError, UserNotFoundError, RestaurantNotFoundError, \
    DishNotFoundError, DuplicateEntryError, FoodDeliverySystemError, InvalidOrderError
from online_food_delivery.models.dish import Dish
from online_food_delivery.models.order import Order
from online_food_delivery.models.restaurant import Restaurant
from online_food_delivery.models.user import User


class FoodDeliverySystem:

    def __init__(self):

        self._restaurants: Dict[str, Restaurant] = {}
        self._users : Dict[str, User] = {}
        self._orders : Dict[str, Order] = {}

        self._user_orders_index : Dict[str, List[Order]] = {}
        self._restaurant_orders_index: Dict[str, List[Order]] = {}

    # --- Helper Methods for Internal Lookup ---
    def _get_restaurant(self, restaurant_id: str) -> Restaurant:
        """Helper to retrieve a restaurant or raise an error."""
        restaurant = self._restaurants.get(restaurant_id)
        if not restaurant:
            raise RestaurantNotFoundError(f"Restaurant with ID '{restaurant_id}' not found.")
        return restaurant

    def _get_user(self, user_id: str) -> User:
        """Helper to retrieve a user or raise an error."""
        user = self._users.get(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID '{user_id}' not found.")
        return user

    def _get_order(self, order_id: str) -> Order:
        """Helper to retrieve an order or raise an error."""
        order = self._orders.get(order_id)
        if not order:
            raise OrderNotFoundError(f"Order with ID '{order_id}' not found.")
        return order

    def register_restaurant(self, name: str, menu_items: List[Dict], location: str) -> Restaurant:
        """
                Registers a new restaurant in the system.
                menu_items is a list of dicts: [{'name': 'Burger', 'description': '...', 'price': 10.0}]
                """
        try:
            # Check for duplicate restaurant name (simple unique check for this system)
            for existing_res in self._restaurants.values():
                if existing_res.get_name().lower() == name.lower():
                    raise DuplicateEntryError(f"Restaurant with name '{name}' already exists.")

            # Create Dish objects from menu_items dicts
            dishes = []
            for item_data in menu_items:
                dish = Dish(
                    name=item_data['name'],
                    description=item_data.get('description', ''),
                    price=item_data['price']
                )
                dishes.append(dish)

            restaurant = Restaurant(name=name, menu_items=dishes, location=location)
            self._restaurants[restaurant.get_id()] = restaurant
            print(f"Registered restaurant: {restaurant.get_name()} (ID: {restaurant.get_id()[:8]}...)")
            return restaurant
        except (ValueError, DuplicateEntryError) as e:
            print(f"Error registering restaurant: {e}")
            raise

    def register_user(self, name: str, address: str):
        """
                Registers a new user in the system.
                """
        try:
            # Check for duplicate user (simple unique check by name + address for this system)
            for existing_user in self._users.values():
                if existing_user.get_name().lower() == name.lower() and \
                        existing_user.get_address().lower() == address.lower():
                    raise DuplicateEntryError(f"User '{name}' at '{address}' already exists.")

            user = User(name=name, address=address)
            self._users[user.get_id()] = user
            # Initialize user's order history list
            self._user_orders_index[user.get_id()] = []
            print(f"Registered user: {user.get_name()} (ID: {user.get_id()[:8]}...)")
            return user
        except (ValueError, DuplicateEntryError) as e:
            print(f"Error registering user: {e}")
            raise

    def search_restaurants(self, query: str, user_location: Optional[str] = None) -> List[Restaurant]:
        """
        Searches for restaurants based on a query string (case-insensitive substring match on name).
        User location is ignored for now per assumption.
        """
        matching_restaurants: List[Restaurant] = []
        lower_query = query.lower()
        for restaurant in self._restaurants.values():
            if lower_query in restaurant.get_name().lower():
                matching_restaurants.append(restaurant)

        print(f"Found {len(matching_restaurants)} restaurants matching '{query}'.")
        return matching_restaurants

    # --- Order Operations ---
    def place_order(self, user_id: str, restaurant_id: str, dish_quantities: Dict[str, int]) -> Order:
        """
        Allows a user to place an order from a specific restaurant.
        dish_quantities: {'Dish Name': quantity, ...}
        """
        try:
            user = self._get_user(user_id)
            restaurant = self._get_restaurant(restaurant_id)

            if not dish_quantities:
                raise InvalidOrderError("Order must contain at least one dish.")

            order_items: List[Tuple[Dish, int]] = []
            total_amount = 0.0

            for dish_name, quantity in dish_quantities.items():
                if quantity <= 0:
                    raise InvalidOrderError(
                        f"Invalid quantity {quantity} for dish '{dish_name}'. Quantity must be positive.")

                dish = restaurant.get_dish(dish_name)  # This will raise DishNotFoundError if not found
                order_items.append((dish, quantity))
                total_amount += dish.get_price() * quantity

            # Create the order
            order = Order(
                user_id=user.get_id(),
                restaurant_id=restaurant.get_id(),
                items=order_items,
                total_amount=total_amount
            )

            self._orders[order.get_id()] = order
            self._user_orders_index.setdefault(user.get_id(), []).append(order)
            self._restaurant_orders_index.setdefault(restaurant.get_id(), []).append(order)

            print(
                f"Order {order.get_id()[:8]}... placed successfully for user {user.get_name()} at {restaurant.get_name()}. Total: ${total_amount:.2f}")
            return order
        except FoodDeliverySystemError as e:
            print(f"Error placing order: {e}")
            raise
        except ValueError as e:
            print(f"Error placing order (input validation): {e}")
            raise

    def update_order_status(self, order_id: str, new_status: OrderStatus) -> Order:
        """
        Updates the status of an existing order, validating the transition.
        """
        try:
            order = self._get_order(order_id)
            order.update_status(new_status)  # Order class handles transition validation
            return order
        except FoodDeliverySystemError as e:
            print(f"Error updating status for order '{order_id}': {e}")
            raise

    def get_order_details(self, order_id: str) -> Order:
        """
        Retrieves full details of a specific order.
        """
        try:
            order = self._get_order(order_id)
            return order
        except FoodDeliverySystemError as e:
            print(f"Error getting details for order '{order_id}': {e}")
            raise

    def get_user_order_history(self, user_id: str) -> List[Order]:
        """
        Returns a list of all orders placed by a specific user.
        """
        try:
            user = self._get_user(user_id)  # Ensures user exists
            # Return a copy to prevent external modification of the internal list
            return list(self._user_orders_index.get(user.get_id(), []))
        except FoodDeliverySystemError as e:
            print(f"Error getting order history for user '{user_id}': {e}")
            raise

    def get_restaurant_orders(self, restaurant_id: str, status_filter: Optional[OrderStatus] = None) -> List[Order]:
        """
        Returns orders for a specific restaurant, optionally filtered by status.
        """
        try:
            restaurant = self._get_restaurant(restaurant_id)  # Ensures restaurant exists
            orders = self._restaurant_orders_index.get(restaurant.get_id(), [])

            if status_filter:
                filtered_orders = [order for order in orders if order.get_status() == status_filter]
                return filtered_orders

            # Return a copy to prevent external modification of the internal list
            return list(orders)
        except FoodDeliverySystemError as e:
            print(f"Error getting restaurant orders for '{restaurant_id}': {e}")
            raise
