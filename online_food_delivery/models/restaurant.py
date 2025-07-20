import uuid
from typing import Optional, Dict, List

from online_food_delivery.exceptions import DuplicateEntryError, DishNotFoundError
from online_food_delivery.models.dish import Dish


class Restaurant:

    def __init__(self, name: str, menu_items: list[Dish], location: str, restaurant_id: Optional[str]=None):

        if not name.strip():
            raise ValueError("Restaurant name cannot be empty.")
        if not location.strip():
            raise ValueError("Restaurant location cannot be empty.")
        if not menu_items:
            raise ValueError("Restaurant must have at least one menu item.")

        self._restaurant_id = restaurant_id if restaurant_id else str(uuid.uuid4())
        self._name = name
        self._location = location
        self._menu: Dict[str, Dish] = {}

        for item in menu_items:
            if item.get_name() in self._menu:
                raise DuplicateEntryError(
                    f"Duplicate dish name '{item.get_name()}' found in restaurant '{name}'s menu.")
            self._menu[item.get_name()] = item

    def get_id(self) -> str:
        return self._restaurant_id

    def get_name(self) -> str:
        return self._name

    def get_location(self) -> str:
        return self._location

    def get_menu(self) -> Dict[str, Dish]:
        """Returns the internal menu dictionary."""
        return self._menu  # For internal use, consider returning a copy if external modification is concern

    def get_menu_items(self) -> List[Dish]:
        """Returns a list of all dishes on the menu."""
        return list(self._menu.values())

    def get_dish(self, dish_name: str) -> Dish:
        """Retrieves a dish from the menu by its name."""
        dish = self._menu.get(dish_name)
        if dish is None:
            raise DishNotFoundError(f"Dish '{dish_name}' not found on menu for restaurant '{self._name}'.")
        return dish

    def __repr__(self):
        return f"Restaurant(id='{self._restaurant_id[:8]}...', name='{self._name}', location='{self._location}', menu_items={len(self._menu)})"


