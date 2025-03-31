import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from src.infrastructure.db.base import Base
from src.domain.entities.order import OrderStatus


class CustomerModel(Base):
    __tablename__ = "customers"
    __table_args__ = {'schema': 'order_service'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    
    # Relationships
    orders = relationship("OrderModel", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer {self.name}>"


class OrderModel(Base):
    __tablename__ = "orders"
    __table_args__ = {'schema': 'order_service'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("order_service.customers.id"), nullable=False)
    status = Column(String(50), default=OrderStatus.CREATED.value, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    
    # JSON columns
    delivery_address = Column(JSON, nullable=True)
    total = Column(JSON, nullable=False)
    
    # Relationships
    customer = relationship("CustomerModel", back_populates="orders")
    items = relationship("OrderItemModel", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order {self.id}>"


class OrderItemModel(Base):
    __tablename__ = "order_items"
    __table_args__ = {'schema': 'order_service'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("order_service.orders.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    
    # Relationships
    order = relationship("OrderModel", back_populates="items")
    
    def __repr__(self):
        return f"<OrderItem {self.name} x{self.quantity}>"