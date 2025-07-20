import math


class FareCalculator:
    # Constants for fare calculation (simplified)
    BASE_FARE = 2.0  # Base fare per ride
    RATE_PER_KM = 1.5  # Rate per kilometer
    RATE_PER_MINUTE = 0.2  # Rate per minute

    @staticmethod
    def calculate_fare(distance_km: float, duration_minutes: float) -> float:
        """
        Calculates the ride fare based on distance and duration.
        """
        if distance_km < 0 or duration_minutes < 0:
            raise ValueError("Distance and duration must be non-negative.")

        # Ensure minimums for calculation if values are very small but positive
        distance_km = max(0.0, distance_km)
        duration_minutes = max(0.0, duration_minutes)

        fare = FareCalculator.BASE_FARE + \
               (distance_km * FareCalculator.RATE_PER_KM) + \
               (duration_minutes * FareCalculator.RATE_PER_MINUTE)

        # Round to 2 decimal places for currency
        return round(fare, 2)