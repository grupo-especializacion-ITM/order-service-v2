from typing import Dict, List
from uuid import UUID
import json
import httpx
from httpx import AsyncClient, Timeout

from src.domain.ports.output.inventory_service_port import InventoryServicePort
from src.domain.entities.order_item import OrderItem
from src.domain.exceptions.domain_exceptions import InventoryValidationException
from src.infrastructure.config.settings import get_settings


class InventoryService(InventoryServicePort):
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.INVENTORY_SERVICE_URL
        self.timeout = Timeout(self.settings.INVENTORY_SERVICE_TIMEOUT)
    
    async def validate_items_availability(self, items: List[OrderItem]) -> Dict[UUID, bool]:
        """
        Validate the availability of items with the inventory service
        
        Returns a dictionary with item IDs as keys and boolean availability as values
        """
        # Prepare request data
        item_data = [
            {
                "product_id": str(item.product_id),
                "quantity": item.quantity
            }
            for item in items
        ]
        
        try:
            async with AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/inventory/validate",
                    json={"items": item_data}
                )
                
                if response.status_code != 200:
                    error_msg = "Error validating inventory"
                    try:
                        error_data = response.json()
                        if "message" in error_data:
                            error_msg = error_data["message"]
                    except json.JSONDecodeError:
                        pass
                    
                    raise InventoryValidationException(
                        error_msg,
                        {"status_code": response.status_code}
                    )
                
                # Process response
                result_data = response.json()
                availability = {}
                
                for item in items:
                    product_id_str = str(item.product_id)
                    # Default to False if not found in response
                    is_available = result_data.get("availability", {}).get(product_id_str, False)
                    availability[item.product_id] = is_available
                
                return availability
                
        except httpx.RequestError as e:
            # Handle network errors, timeouts, etc.
            raise InventoryValidationException(
                f"Error connecting to inventory service: {str(e)}",
                {"error_type": type(e).__name__}
            )