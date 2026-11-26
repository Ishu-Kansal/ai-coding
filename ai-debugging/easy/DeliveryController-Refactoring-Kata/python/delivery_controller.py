import datetime
from dataclasses import dataclass

from email_gateway import EmailGateway
from map_service import MapService, Location


# Architecture: this file is the application orchestration layer. DeliveryController
# coordinates the delivery schedule, EmailGateway notifications, and MapService
# route calculations. DeliveryEvent is the inbound status data; Delivery is the
# mutable state that combines schedule information with delivery progress.

@dataclass(frozen=True)
class DeliveryEvent:
    id: str
    time_of_delivery: datetime.datetime
    location: Location

@dataclass
class Delivery:
    id: str
    contact_email: str
    location: Location
    time_of_delivery: datetime.datetime
    arrived: bool
    on_time: bool


class DeliveryController:

    def __init__(self, delivery_schedule : list, email_gateway=None, map_service=None):
        # Business logic: stores the shared schedule and uses injected email/map
        # services when supplied, otherwise constructing their default services.
        self.delivery_schedule = delivery_schedule
        self.email_gateway = email_gateway if email_gateway is not None else EmailGateway()
        self.map_service = map_service if map_service is not None else MapService()

    def update_delivery(self, delivery_event : DeliveryEvent):
        # Business logic: finds the delivery matching the event ID, marks it as
        # arrived, determines timeliness, updates ETA-related state, and sends
        # notifications. The operation is a no-op if the event ID is not in the
        # schedule.
        #
        # Truth table for an on-time result:
        # | event matched | time difference <= 10 minutes | on_time |
        # |---------------|-------------------------------|---------|
        # | No            | Not evaluated                 | Unchanged |
        # | Yes           | True                          | True |
        # | Yes           | False                         | False |
        #
        # Truth table for recalculating average speed:
        # | delivery is late | schedule has >1 item | delivery has previous item | update speed |
        # |------------------|----------------------|----------------------------|--------------|
        # | No               | X                    | X                          | No |
        # | Yes              | No                   | X                          | No |
        # | Yes              | Yes                  | No                         | No |
        # | Yes              | Yes                  | Yes                        | Yes |
        #
        # Truth table for notifying the next delivery:
        # | event matched | next delivery exists | ETA notification |
        # |---------------|----------------------|------------------|
        # | No            | X                    | No |
        # | Yes           | No                   | No |
        # | Yes           | Yes                  | Yes |
        next_delivery = None
        for i, delivery in enumerate(self.delivery_schedule):
            if delivery_event.id == delivery.id and delivery.arrived is False:
                delivery.arrived = True
                time_difference = delivery_event.time_of_delivery - delivery.time_of_delivery
                if time_difference <= datetime.timedelta(minutes=10):
                    delivery.on_time = True
                else:
                    delivery.on_time = False
                delivery.time_of_delivery = delivery_event.time_of_delivery
                message = f"""Regarding your delivery today at {delivery.time_of_delivery}. How likely would you be to recommend this delivery service to a friend? Click <a href="url">here</a>"""
                self.email_gateway.send(delivery.contact_email, "Your feedback is important to us", message)
                next_delivery = next(
                    (
                        scheduled_delivery
                        for scheduled_delivery in self.delivery_schedule[i + 1:]
                        if not scheduled_delivery.arrived
                    ),
                    None,
                )
                if not delivery.on_time and len(self.delivery_schedule) > 1 and i > 0:
                    previous_delivery = self.delivery_schedule[i-1]
                    elapsed_time = delivery.time_of_delivery - previous_delivery.time_of_delivery
                    self.map_service.update_average_speed(previous_delivery.location, delivery.location, elapsed_time)
        if next_delivery:
            next_eta = self.map_service.calculate_eta(delivery_event.location, next_delivery.location)
            message = f"Your delivery to {next_delivery.location} is next, estimated time of arrival is in {next_eta:.0f} minutes. Be ready!"
            self.email_gateway.send(next_delivery.contact_email, "Your delivery will arrive soon", message)



