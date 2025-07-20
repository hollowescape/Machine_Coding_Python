You are tasked with designing and implementing a simplified in-memory system for an online food ordering and delivery service.

Core Requirements:

Entities:

Restaurant: Has a name, menu (list of Dishes), and location (e.g., coordinates or a simple address string).

Dish: Has a name, description, price.

User: Has a user_id, name, address (delivery location).

Order: Represents a customer's order. It should contain:

order_id (unique identifier).

user_id of the customer who placed the order.

restaurant_id from which the order was placed.

items (list of Dishes and their quantities).

total_amount.

order_status (e.g., PENDING, ACCEPTED, PREPARING, READY_FOR_PICKUP, OUT_FOR_DELIVERY, DELIVERED, CANCELLED).

timestamps for different status changes (e.g., placed_time, accepted_time, delivered_time).

System Operations (within a main FoodDeliverySystem class):

register_restaurant(name, menu, location) -> Restaurant: Registers a new restaurant.

register_user(name, address) -> User: Registers a new user.

search_restaurants(query: str, user_location: str) -> List[Restaurant]: Searches for restaurants based on a query (e.g., name, cuisine type - simple string match for now) and ideally proximity to the user (can be simplified to just a query match).

place_order(user_id: str, restaurant_id: str, dish_quantities: Dict[str, int]) -> Order:

Allows a user to place an order from a specific restaurant with specified dishes and quantities.

Validates if dishes exist on the restaurant's menu.

Calculates the total_amount.

Initializes the order_status to PENDING.

Generates a Ticket or Order object.

update_order_status(order_id: str, new_status: OrderStatus) -> Order:

Allows updating the status of an existing order.

Should ensure valid state transitions (e.g., PENDING -> ACCEPTED is valid, but DELIVERED -> PENDING is not).

Updates relevant timestamps.

get_order_details(order_id: str) -> Order: Retrieves full details of an order.

get_user_order_history(user_id: str) -> List[Order]: Returns a list of all orders placed by a specific user.

get_restaurant_orders(restaurant_id: str, status_filter: Optional[OrderStatus] = None) -> List[Order]: Returns orders for a specific restaurant, optionally filtered by status.

Assumptions & Further Details:

In-memory: All data will be stored in memory.

IDs: Use simple string UUIDs or sequential integers for user_id, restaurant_id, order_id.

Dish Quantity: dish_quantities will be a dictionary where keys are dish_name and values are quantity (e.g., {"Burger": 2, "Fries": 1}).

Location/Search: For search_restaurants, a simple string contains check on restaurant name or a dummy proximity check is sufficient.

Status Transitions: Define a clear state machine for order statuses. For example:
PENDING -> ACCEPTED -> PREPARING -> READY_FOR_PICKUP -> OUT_FOR_DELIVERY -> DELIVERED
PENDING -> CANCELLED
ACCEPTED -> CANCELLED
Other transitions are invalid.

Concurrency: Assume single-threaded for now, unless you explicitly want to discuss basic thread safety.