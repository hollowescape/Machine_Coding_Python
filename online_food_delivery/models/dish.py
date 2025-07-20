
class Dish:

    def __init__(self, name: str, price: int, description: str):

        if not name.strip():
            raise ValueError("Dish name cannot be empty.")
        if price <= 0:
            raise ValueError("Dish price must be positive.")

        self._name = name
        self._price = price
        self._description = description


    def get_name(self):
        return self._name

    def get_price(self):
        return self._price

    def get_description(self) -> str:
        return self._description

    def __repr__(self):
        return f"Dish(name='{self._name}', price=${self._price:.2f})"

    def __eq__(self, other):
        if not isinstance(other, Dish):
            return NotImplemented
        return self._name == other._name and self._price == other._price

    def __hash__(self):
        return hash((self._name, self._price))