from abc import abstractmethod, ABC
from typing import Dict, Any


class BaseStrategy(ABC):

    def __init__(self, config: Dict[str, Any]):
        """
        Abstract Base Class for all Rate Limiter strategies.
        Defines the common interface that all concrete strategies must implement.
        """
        self._config = config
        self._validate_config()

    @abstractmethod
    def allow_request(self, user_id: str) -> bool:
        pass

    @abstractmethod
    def _validate_config(self):
        pass
