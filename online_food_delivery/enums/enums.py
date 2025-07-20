from enum import Enum, auto

class OrderStatus(Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    PREPARING = "PREPARING"
    READY_FOR_PICKUP = "READY_FOR_PICKUP"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


VALID_ORDER_TRANSITIONS = {
    OrderStatus.PENDING : {
        OrderStatus.ACCEPTED,
        OrderStatus.CANCELLED
    },
    OrderStatus.ACCEPTED: {
        OrderStatus.PREPARING,
        OrderStatus.CANCELLED
    },
    OrderStatus.PREPARING: {
        OrderStatus.READY_FOR_PICKUP
    },
    OrderStatus.READY_FOR_PICKUP:{
        OrderStatus.OUT_FOR_DELIVERY
    },
    OrderStatus.OUT_FOR_DELIVERY:{
        OrderStatus.DELIVERED
    },
    OrderStatus.DELIVERED: set(),
    OrderStatus.CANCELLED: set()
}

def is_valid_transition(current_status: OrderStatus, new_status: OrderStatus) -> bool:
    return new_status in VALID_ORDER_TRANSITIONS.get(current_status, set())

