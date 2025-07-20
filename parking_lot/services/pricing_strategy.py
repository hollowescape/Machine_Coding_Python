from abc import ABC, abstractmethod
from parking_lot.models.ticket import Ticket

class PricingStrategy(ABC):
    @abstractmethod
    def calculate_fee(self, ticket: Ticket) -> float:
        pass

class HourlyPricingStrategy(PricingStrategy):
    def __init__(self, hourly_rate: float):
        self.hourly_rate = hourly_rate

    def calculate_fee(self, ticket: Ticket) -> float:
        if not ticket.exit_time:
            raise ValueError("Exit time not set for ticket.")
        time_parked_seconds = (ticket.exit_time - ticket.entry_time).total_seconds()
        hours = max(1, (time_parked_seconds / 3600)) # Minimum 1 hour
        return hours * self.hourly_rate