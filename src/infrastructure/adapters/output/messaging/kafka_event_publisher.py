import json
import logging
from typing import Any, Dict, Optional
from aiokafka import AIOKafkaProducer
import asyncio

from src.domain.ports.output.event_publisher_port import EventPublisherPort
from src.domain.entities.order import Order
from src.application.events.order_events import (
    OrderCreatedEvent,
    OrderConfirmedEvent,
    OrderCancelledEvent,
    OrderStatusUpdatedEvent
)
from src.infrastructure.config.settings import get_settings


logger = logging.getLogger(__name__)


class KafkaEventPublisher(EventPublisherPort):
    def __init__(self):
        self.settings = get_settings()
        self.producer = None
        self.default_topic = self.settings.KAFKA_ORDER_TOPIC
    
    async def start(self):
        """Start the Kafka producer"""
        if self.producer is None:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS,
                client_id=self.settings.KAFKA_CLIENT_ID,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8') if k else None
            )
            
            await self.producer.start()
            logger.info("Kafka producer started")
    
    async def stop(self):
        """Stop the Kafka producer"""
        if self.producer is not None:
            await self.producer.stop()
            self.producer = None
            logger.info("Kafka producer stopped")
    
    async def publish_order_created(self, order: Order) -> None:
        """Publish an order created event"""
        # Create event
        event = OrderCreatedEvent.create(
            order_id=order.id,
            customer_id=order.customer_id,
            items=[{
                "id": str(item.id),
                "product_id": str(item.product_id),
                "name": item.name,
                "quantity": item.quantity,
                "price": item.unit_price
            } for item in order.items],
            total_amount=order.total.total,
            status=order.status.value
        )
        
        # Publish event
        await self.publish_event(
            event_type=event.event_type,
            payload=event.__dict__,
            key=str(order.id)
        )
    
    async def publish_order_confirmed(self, order: Order) -> None:
        """Publish an order confirmed event"""
        # Create event
        event = OrderConfirmedEvent.create(
            order_id=order.id,
            customer_id=order.customer_id,
            total_amount=order.total.total
        )
        
        # Publish event
        await self.publish_event(
            event_type=event.event_type,
            payload=event.__dict__,
            key=str(order.id)
        )
    
    async def publish_order_cancelled(self, order: Order) -> None:
        """Publish an order cancelled event"""
        # Create event
        event = OrderCancelledEvent.create(
            order_id=order.id,
            customer_id=order.customer_id
        )
        
        # Publish event
        await self.publish_event(
            event_type=event.event_type,
            payload=event.__dict__,
            key=str(order.id)
        )
    
    async def publish_order_status_updated(self, order: Order, previous_status: str) -> None:
        """Publish an order status updated event"""
        # Create event
        event = OrderStatusUpdatedEvent.create(
            order_id=order.id,
            customer_id=order.customer_id,
            previous_status=previous_status,
            new_status=order.status.value
        )
        
        # Publish event
        await self.publish_event(
            event_type=event.event_type,
            payload=event.__dict__,
            key=str(order.id)
        )
    
    async def publish_event(self, event_type: str, payload: Dict[str, Any], 
                           topic: Optional[str] = None, key: Optional[str] = None) -> None:
        """Publish a generic event to Kafka"""
        if self.producer is None:
            await self.start()
        
        try:
            # Use the provided topic or default to the configured topic
            kafka_topic = topic or self.default_topic
            
            # Publish the message
            await self.producer.send_and_wait(
                topic=kafka_topic,
                value=payload,
                key=key
            )
            
            logger.info(f"Event {event_type} published to topic {kafka_topic}")
            
        except Exception as e:
            logger.error(f"Error publishing event {event_type}: {str(e)}")
            # In a production system, we might want to implement a retry mechanism,
            # or store failed events for later reprocessing
            raise