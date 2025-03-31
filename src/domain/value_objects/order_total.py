from dataclasses import dataclass


@dataclass(frozen=True)
class OrderTotal:
    subtotal: float
    tax: float
    total: float
    
    def __str__(self) -> str:
        return f"Total: ${self.total:.2f} (Subtotal: ${self.subtotal:.2f} + Tax: ${self.tax:.2f})"