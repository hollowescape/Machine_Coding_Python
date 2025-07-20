High-Level Design & Core Entities
The system will revolve around several key classes, each with its own responsibilities.

Dish Class:

Attributes:

name: str

description: str

price: float

Methods:

__init__: To create a dish.

Getters for attributes.

Restaurant Class:

Attributes:

restaurant_id: str (UUID)

name: str

location: str

menu: Dict[str, Dish] (maps dish name to Dish object for quick lookup)

Methods:

__init__: To create a restaurant.

get_dish(dish_name: str) -> Optional[Dish]: To retrieve a dish from its menu.

get_menu_items() -> List[Dish]: To list all dishes.

User Class:

Attributes:

user_id: str (UUID)

name: str

address: str

Methods:

__init__: To create a user.

Order Class:

Attributes:

order_id: str (UUID)

user_id: str

restaurant_id: str

items: List[Tuple[Dish, int]] (list of (Dish object, quantity))

total_amount: float

status: OrderStatus (an Enum, see below)

timestamps: Dict[OrderStatus, datetime] (stores when each status was set)

Methods:

__init__: To initialize an order.

update_status(new_status: OrderStatus, current_time: datetime): Handles status transitions with validation and updates timestamps.

OrderStatus Enum:

A Python Enum to clearly define possible order states: PENDING, ACCEPTED, PREPARING, READY_FOR_PICKUP, OUT_FOR_DELIVERY, DELIVERED, CANCELLED.

Could also store valid transitions within the enum or a separate helper.

FoodDeliverySystem Class (The Orchestrator):

Attributes:

_restaurants: Dict[str, Restaurant] (maps restaurant_id to Restaurant object)

_users: Dict[str, User] (maps user_id to User object)

_orders: Dict[str, Order] (maps order_id to Order object)

_user_orders_index: Dict[str, List[Order]] (maps user_id to a list of their orders for quick history retrieval)

_restaurant_orders_index: Dict[str, List[Order]] (maps restaurant_id to a list of orders for that restaurant)

Methods:

__init__: Initializes the system with empty data structures.

All the public operations mentioned in the problem statement (register_restaurant, register_user, search_restaurants, place_order, update_order_status, get_order_details, get_user_order_history, get_restaurant_orders).

Helper Methods:

_validate_status_transition(current_status: OrderStatus, new_status: OrderStatus) -> bool: Checks if a transition is valid.

_get_restaurant(restaurant_id: str) -> Restaurant: Internal lookup.

_get_user(user_id: str) -> User: Internal lookup.

_get_order(order_id: str) -> Order: Internal lookup.

Data Structures
For efficient storage and retrieval, we'll primarily rely on dictionaries (hash maps):

FoodDeliverySystem._restaurants: Dict[str, Restaurant] - Allows O(1) average time lookup of a restaurant by its ID.

FoodDeliverySystem._users: Dict[str, User] - Allows O(1) average time lookup of a user by their ID.

FoodDeliverySystem._orders: Dict[str, Order] - Allows O(1) average time lookup of any order by its ID.

Restaurant.menu: Dict[str, Dish] - Allows O(1) average time lookup of a dish by its name within a restaurant's menu.

FoodDeliverySystem._user_orders_index: Dict[str, List[Order]] - This is crucial for get_user_order_history. When an order is placed, it's added to this list for the corresponding user. Retrieval is O(1) to get the list, then O(N) on list size if further filtering is needed.

FoodDeliverySystem._restaurant_orders_index: Dict[str, List[Order]] - Similar to the user index, for get_restaurant_orders.

Key Logic Flow
1. place_order(user_id: str, restaurant_id: str, dish_quantities: Dict[str, int]) -> Order
Validate Inputs:

Check if user_id exists in _users. If not, raise UserNotFoundError.

Check if restaurant_id exists in _restaurants. If not, raise RestaurantNotFoundError.

Ensure dish_quantities is not empty.

Retrieve Entities: Get the User and Restaurant objects.

Process Dishes and Calculate Total:

Initialize total_amount = 0.0 and order_items = [].

Iterate through dish_quantities:

For each dish_name and quantity:

Retrieve the Dish object from restaurant.menu. If not found, raise DishNotFoundError.

Validate quantity (must be > 0). If not, raise InvalidOrderError.

Add (Dish object, quantity) to order_items.

Add dish.price * quantity to total_amount.

Create Order:

Generate a unique order_id.

Create a new Order object with order_id, user_id, restaurant_id, order_items, total_amount, and initial status = OrderStatus.PENDING. Set placed_time.

Store Order & Update Indexes:

Add the new Order to _orders (main storage).

Add the Order to _user_orders_index[user_id].

Add the Order to _restaurant_orders_index[restaurant_id].

Return: The newly created Order object.

2. update_order_status(order_id: str, new_status: OrderStatus) -> Order
Validate Inputs:

Check if order_id exists in _orders. If not, raise OrderNotFoundError.

Ensure new_status is a valid OrderStatus enum member.

Retrieve Order: Get the Order object using order_id.

Validate Transition:

Get the current_status from the Order object.

Call a helper _validate_status_transition(current_status, new_status):

This helper would define valid transitions (e.g., using a dictionary or if-elif chain for rules).

If the transition is invalid, raise InvalidStatusTransitionError.

Update Order Status and Timestamp:

Set order.status = new_status.

Update order.timestamps[new_status] with the current time.

Return: The updated Order object.