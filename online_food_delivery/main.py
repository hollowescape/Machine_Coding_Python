# main.py
from food_delivery_system import FoodDeliverySystem
from models.dish import Dish
from models.restaurant import Restaurant
from models.user import User
from models.order import Order
from enums.enums import OrderStatus
from exceptions import FoodDeliverySystemError


# Helper function to print order details nicely
def print_order_details(order: Order, system: FoodDeliverySystem):
    print(f"\n--- Order Details (ID: {order.get_id()[:8]}...) ---")
    try:
        user_name = system._get_user(order.get_user_id()).get_name()
        restaurant_name = system._get_restaurant(order.get_restaurant_id()).get_name()
        print(f"  User: {user_name}")
        print(f"  Restaurant: {restaurant_name}")
        print(f"  Status: {order.get_status().value}. {order.get_status()}")  # Shows enum value and string rep
        print(f"  Total Amount: ${order.get_total_amount():.2f}")
        print("  Items:")
        for dish, quantity in order.get_items():
            print(f"    - {dish.get_name()} (x{quantity}) @ ${dish.get_price():.2f} each")
        print("  Timestamps:")
        for status, ts in order.get_timestamps().items():
            print(f"    - {status}: {ts.strftime('%Y-%m-%d %H:%M:%S')}")
    except FoodDeliverySystemError as e:
        print(f"  Error retrieving associated details: {e}")
    print("-----------------------------------")


def run_cli():
    system = FoodDeliverySystem()

    # --- Setup Some Initial Data ---
    print("\n--- Initializing Sample Data ---")

    # Dishes for Restaurant 1
    burger_menu = [
        {'name': 'Classic Burger', 'description': 'Beef patty, lettuce, tomato', 'price': 12.50},
        {'name': 'Veggie Burger', 'description': 'Plant-based patty, avocado', 'price': 11.00},
        {'name': 'Fries', 'description': 'Crispy golden fries', 'price': 3.00},
        {'name': 'Coca-Cola', 'description': 'Refreshing soda', 'price': 2.00}
    ]
    # Dishes for Restaurant 2
    pizza_menu = [
        {'name': 'Margherita Pizza', 'description': 'Tomato, mozzarella, basil', 'price': 15.00},
        {'name': 'Pepperoni Pizza', 'description': 'Pepperoni, mozzarella', 'price': 16.50},
        {'name': 'Garlic Bread', 'description': 'Toasted bread with garlic butter', 'price': 4.50}
    ]

    try:
        res1 = system.register_restaurant("Burger Heaven", burger_menu, "123 Main St")
        res2 = system.register_restaurant("Pizza Planet", pizza_menu, "456 Oak Ave")

        user1 = system.register_user("Alice", "789 Pine Ln")
        user2 = system.register_user("Bob", "101 Maple Rd")
        user3 = system.register_user("Charlie", "202 Elm St")

        # Place some orders
        print("\n--- Placing Sample Orders ---")
        order1_items = {'Classic Burger': 1, 'Fries': 1, 'Coca-Cola': 2}
        order1 = system.place_order(user1.get_id(), res1.get_id(), order1_items)

        order2_items = {'Pepperoni Pizza': 1, 'Margherita Pizza': 1, 'Garlic Bread': 1}
        order2 = system.place_order(user2.get_id(), res2.get_id(), order2_items)

        order3_items = {'Veggie Burger': 1, 'Fries': 2}
        order3 = system.place_order(user1.get_id(), res1.get_id(), order3_items)

    except FoodDeliverySystemError as e:
        print(f"Initial data setup failed: {e}")
        return  # Exit if initial setup fails

    print("\n--- Food Delivery System CLI ---")
    print("Commands:")
    print("  search <query>                             - Search restaurants by name")
    print("  place <user_id> <restaurant_id> <dish:qty,...> - Place a new order")
    print("  update_status <order_id> <new_status>    - Update order status (e.g., ACCEPTED, PREPARING)")
    print("  details <order_id>                       - Get full order details")
    print("  user_history <user_id>                   - Get all orders for a user")
    print("  restaurant_orders <restaurant_id> [status] - Get orders for a restaurant (optional filter)")
    print("  list_users                               - List all registered users")
    print("  list_restaurants                         - List all registered restaurants")
    print("  exit                                     - Exit the CLI")
    print("\nNote: Use first 8 characters of UUIDs for commands.")

    # Store IDs for easy access in CLI
    user_ids = {user1.get_name().lower(): user1.get_id(), user2.get_name().lower(): user2.get_id(),
                user3.get_name().lower(): user3.get_id()}
    restaurant_ids = {res1.get_name().lower(): res1.get_id(), res2.get_name().lower(): res2.get_id()}
    order_map = {
        order1.get_id()[:8]: order1.get_id(),
        order2.get_id()[:8]: order2.get_id(),
        order3.get_id()[:8]: order3.get_id()
    }

    # Helper to resolve partial IDs
    def resolve_id(id_type: str, partial_id: str) -> str:
        if id_type == "user":
            for name, uid in user_ids.items():
                if uid.startswith(partial_id):
                    return uid
            for full_id in system._users.keys():  # Fallback check
                if full_id.startswith(partial_id):
                    return full_id
        elif id_type == "restaurant":
            for name, rid in restaurant_ids.items():
                if rid.startswith(partial_id):
                    return rid
            for full_id in system._restaurants.keys():  # Fallback check
                if full_id.startswith(partial_id):
                    return full_id
        elif id_type == "order":
            for full_id in system._orders.keys():
                if full_id.startswith(partial_id):
                    return full_id
        raise ValueError(f"Could not resolve {id_type} ID for '{partial_id}'.")

    while True:
        try:
            command_line = input("\n> ").strip()
            if not command_line:
                continue

            parts = command_line.split(maxsplit=3)  # Adjust maxsplit based on command
            cmd = parts[0].lower()

            if cmd == "search":
                if len(parts) >= 2:
                    query = parts[1]
                    results = system.search_restaurants(query)
                    if results:
                        print("Matching Restaurants:")
                        for res in results:
                            print(f"  - {res.get_name()} (ID: {res.get_id()[:8]}..., Location: {res.get_location()})")
                    else:
                        print("No matching restaurants found.")
                else:
                    print("Usage: search <query>")

            elif cmd == "place":
                if len(parts) == 4:
                    user_p_id = parts[1]
                    restaurant_p_id = parts[2]
                    dish_qty_str = parts[3]

                    try:
                        resolved_user_id = resolve_id("user", user_p_id)
                        resolved_restaurant_id = resolve_id("restaurant", restaurant_p_id)
                    except ValueError as e:
                        print(e)
                        continue

                    dish_quantities = {}
                    for item_pair in dish_qty_str.split(','):
                        try:
                            dish_name, qty_str = item_pair.split(':')
                            dish_quantities[dish_name.strip()] = int(qty_str.strip())
                        except ValueError:
                            print(f"Invalid dish:quantity format: {item_pair}. Expected 'Dish Name:Quantity'")
                            break
                    else:  # Only runs if loop completes without break
                        new_order = system.place_order(resolved_user_id, resolved_restaurant_id, dish_quantities)
                        order_map[new_order.get_id()[:8]] = new_order.get_id()  # Add to map for easy lookup
                else:
                    print("Usage: place <user_id_prefix> <restaurant_id_prefix> <dish1:qty1,dish2:qty2,...>")
                    print("Example: place alice burgerh classicburger:1,fries:1")

            elif cmd == "update_status":
                if len(parts) == 3:
                    order_p_id = parts[1]
                    new_status_str = parts[2].upper()

                    try:
                        resolved_order_id = resolve_id("order", order_p_id)
                        new_status = OrderStatus[new_status_str]
                    except KeyError:
                        print(f"Invalid status: {new_status_str}. Choose from: {[s.name for s in OrderStatus]}")
                        continue
                    except ValueError as e:
                        print(e)
                        continue

                    system.update_order_status(resolved_order_id, new_status)
                else:
                    print("Usage: update_status <order_id_prefix> <NEW_STATUS>")
                    print("Example: update_status e6c7 ACCEPTED")

            elif cmd == "details":
                if len(parts) == 2:
                    order_p_id = parts[1]
                    try:
                        resolved_order_id = resolve_id("order", order_p_id)
                        order = system.get_order_details(resolved_order_id)
                        print_order_details(order, system)
                    except ValueError as e:
                        print(e)
                else:
                    print("Usage: details <order_id_prefix>")

            elif cmd == "user_history":
                if len(parts) == 2:
                    user_p_id = parts[1]
                    try:
                        resolved_user_id = resolve_id("user", user_p_id)
                        history = system.get_user_order_history(resolved_user_id)
                        if history:
                            print(f"\n--- Order History for User ID: {resolved_user_id[:8]}... ---")
                            for order in history:
                                print(
                                    f"  - Order {order.get_id()[:8]}... from {system._get_restaurant(order.get_restaurant_id()).get_name()} (Status: {order.get_status()})")
                            print("-----------------------------------")
                        else:
                            print(f"No orders found for user ID: {resolved_user_id[:8]}...")
                    except ValueError as e:
                        print(e)
                else:
                    print("Usage: user_history <user_id_prefix>")

            elif cmd == "restaurant_orders":
                if len(parts) >= 2:
                    restaurant_p_id = parts[1]
                    status_filter_str = parts[2].upper() if len(parts) == 3 else None

                    try:
                        resolved_restaurant_id = resolve_id("restaurant", restaurant_p_id)
                        status_filter = OrderStatus[status_filter_str] if status_filter_str else None
                    except KeyError:
                        print(f"Invalid status: {status_filter_str}. Choose from: {[s.name for s in OrderStatus]}")
                        continue
                    except ValueError as e:
                        print(e)
                        continue

                    orders = system.get_restaurant_orders(resolved_restaurant_id, status_filter)
                    if orders:
                        print(
                            f"\n--- Orders for Restaurant: {system._get_restaurant(resolved_restaurant_id).get_name()} (Filter: {status_filter if status_filter else 'None'}) ---")
                        for order in orders:
                            print(
                                f"  - Order {order.get_id()[:8]}... by {system._get_user(order.get_user_id()).get_name()} (Status: {order.get_status()})")
                        print("-----------------------------------")
                    else:
                        print(
                            f"No orders found for restaurant ID: {resolved_restaurant_id[:8]}... (Filter: {status_filter if status_filter else 'None'})")
                else:
                    print("Usage: restaurant_orders <restaurant_id_prefix> [status_filter]")

            elif cmd == "list_users":
                print("\n--- Registered Users ---")
                if not system._users:
                    print("No users registered.")
                for user_id, user in system._users.items():
                    print(f"  - {user.get_name()} (ID: {user.get_id()[:8]}..., Address: {user.get_address()})")
                print("------------------------")

            elif cmd == "list_restaurants":
                print("\n--- Registered Restaurants ---")
                if not system._restaurants:
                    print("No restaurants registered.")
                for res_id, res in system._restaurants.items():
                    print(f"  - {res.get_name()} (ID: {res.get_id()[:8]}..., Location: {res.get_location()})")
                    print(f"    Menu: {[d.get_name() for d in res.get_menu_items()]}")
                print("----------------------------")

            elif cmd == "exit":
                print("Exiting Food Delivery System. Goodbye!")
                break
            else:
                print("Unknown command. Type 'help' (if implemented) or refer to the command list.")

        except FoodDeliverySystemError as e:
            print(f"Operation failed: {e}")
        except ValueError as e:
            print(f"Input error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            import traceback
            traceback.print_exc()  # Print full stack trace for unexpected errors


if __name__ == "__main__":
    run_cli()