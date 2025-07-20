from cache.lru_cache import LRUCache
from exceptions import InvalidCapacityException


def run_lru_cache_cli():
    cache = None
    print("Welcome to the LRU Cache Simulator!")

    while True:
        try:
            if cache is None:
                print("\n--- Cache Not Initialized ---")
                capacity_input = input("Enter cache capacity to initialize: ").strip()
                if capacity_input.lower() == "exit":
                    break
                try:
                    capacity = int(capacity_input)
                    cache = LRUCache(capacity)
                    print(f"LRU Cache initialized with capacity {capacity}.")
                except (ValueError, InvalidCapacityException) as e:
                    print(f"Initialization Error: {e}. Please enter a positive integer.")
                    continue

            print(f"\n--- Current Cache State (Size: {cache.get_size()}/{cache.get_capacity()}) ---")
            cache.print_cache()

            print("Commands:")
            print("  get <key>")
            print("  put <key> <value>")
            print("  exit")

            command_line = input("Enter command: ").strip().lower()
            parts = command_line.split(maxsplit=2)  # maxsplit for put command

            cmd = parts[0]

            if cmd == "get":
                if len(parts) == 2:
                    key = parts[1]
                    # Attempt to convert key to int if possible, common for test cases
                    try:
                        key = int(key)
                    except ValueError:
                        pass  # Keep as string if not int

                    value = cache.get(key)
                    if value is not None:
                        print(f"GET '{key}': Found value '{value}'")
                    else:
                        print(f"GET '{key}': Key not found in cache.")
                else:
                    print("Usage: get <key>")

            elif cmd == "put":
                if len(parts) == 3:
                    key = parts[1]
                    value_str = parts[2]

                    # Attempt to convert key/value to int if possible
                    try:
                        key = int(key)
                    except ValueError:
                        pass  # Keep as string
                    try:
                        value = int(value_str)
                    except ValueError:
                        value = value_str  # Keep as string

                    cache.put(key, value)
                    print(f"PUT '{key}': Set value '{value}'")
                else:
                    print("Usage: put <key> <value>")

            elif cmd == "exit":
                print("Exiting LRU Cache Simulator. Goodbye!")
                break

            else:
                print("Unknown command.")

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    run_lru_cache_cli()