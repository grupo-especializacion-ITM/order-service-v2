from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DeliveryAddress:
    street: str
    city: str
    state: str
    postal_code: str
    country: str
    apartment: Optional[str] = None
    instructions: Optional[str] = None
    
    def __str__(self) -> str:
        base_address = f"{self.street}, {self.city}, {self.state} {self.postal_code}, {self.country}"
        if self.apartment:
            base_address = f"{base_address}, Apt/Suite: {self.apartment}"
        return base_address