import uuid
from datetime import datetime
from typing import List, Tuple, Optional, Dict

from online_food_delivery.enums.enums import OrderStatus, is_valid_transition
from online_food_delivery.exceptions import InvalidStatusTransitionError
from online_food_delivery.models.dish import Dish


class Order:

    def __init__(self, user_id: str,
                 restaurant_id: str, items: List[Tuple[Dish, int]],
                 total_amount: float,
                 order_id : Optional[str]= None):

        if not user_id or not restaurant_id:
            raise ValueError("Order must be associated with a user and a restaurant.")
        if not items:
            raise ValueError("Order must contain at least one item.")
        if total_amount <= 0:
            raise ValueError("Total amount must be positive.")

        self._order_id = order_id if order_id else str(uuid.uuid4())
        self._user_id = user_id
        self._restaurant_id = restaurant_id
        self._items = items
        self._total_amount = total_amount

        self._status = OrderStatus.PENDING
        self._timestamps: Dict[OrderStatus, datetime] = {OrderStatus.PENDING: datetime.now()}

    def get_id(self) -> str:
        return self._order_id

    def get_user_id(self) -> str:
        return self._user_id

    def get_restaurant_id(self) -> str:
        return self._restaurant_id

    def get_items(self) -> List[Tuple[Dish, int]]:
        return self._items

    def get_total_amount(self) -> float:
        return self._total_amount

    def get_status(self) -> OrderStatus:
        return self._status

    def get_timestamps(self) -> Dict[OrderStatus, datetime]:
        return self._timestamps

    def update_status(self, new_status):
        if not is_valid_transition(self._status, new_status):
            raise InvalidStatusTransitionError("Invalid Status Transistion")

        self._status = new_status
        self._timestamps[new_status] =  datetime.now()
        print(f"Order {self._order_id[:8]}... status updated to: {new_status}")

    def __repr__(self):
        return (f"Order(id='{self._order_id[:8]}...', user='{self._user_id[:8]}...', "
                f"restaurant='{self._restaurant_id[:8]}...', status={self._status.name}, "
                f"total=${self._total_amount:.2f}, items={len(self._items)})")



