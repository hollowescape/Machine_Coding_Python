from enum import Enum

class DriverStatus(Enum):
    AVAILABLE = "AVAILABLE"
    EN_ROUTE_TO_PICKUP = "EN_ROUTE_TO_PICKUP"
    IN_RIDE = "IN_RIDE"
    OFFLINE = "OFFLINE"


class RideStatus(Enum):
    REQUESTED = "REQUESTED"
    MATCHED = "MATCHED"
    ARRIVED_AT_PICKUP = "ARRIVED_AT_PICKUP"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


