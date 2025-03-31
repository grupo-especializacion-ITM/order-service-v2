from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


class OrderStatusEnum(str, Enum):
    CREATED = "CREATED"
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    READY = "READY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class DeliveryAddressSchema(BaseModel):
    street: str
    city: str
    state: str
    postal_code: str
    country: str
    apartment: Optional[str] = None
    instructions: Optional[str] = None


class OrderTotalSchema(BaseModel):
    subtotal: float
    tax: float
    total: float


class OrderItemCreateSchema(BaseModel):
    product_id: UUID
    name: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    notes: Optional[str] = None


class OrderItemSchema(OrderItemCreateSchema):
    id: UUID
    total_price: float
    created_at: datetime


class CustomerSchema(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    phone: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class OrderCreateSchema(BaseModel):
    customer_id: UUID
    items: List[OrderItemCreateSchema]
    delivery_address: DeliveryAddressSchema
    notes: Optional[str] = None


class OrderSchema(BaseModel):
    id: UUID
    customer_id: UUID
    items: List[Dict[str, Any]]
    status: OrderStatusEnum
    delivery_address: Optional[DeliveryAddressSchema] = None
    total: OrderTotalSchema
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class OrderStatusUpdateSchema(BaseModel):
    status: OrderStatusEnum


class ErrorResponse(BaseModel):
    message: str
    details: Optional[Dict[str, Any]] = None


class OrderListResponse(BaseModel):
    items: List[OrderSchema]
    total: int