import pytest
import datetime
from unittest.mock import Mock

from delivery_controller import DeliveryController, Delivery, DeliveryEvent
from email_gateway import EmailGateway
from map_service import MapService, Location

location1 = Location(52.2296756, 21.0122287)
location2 = Location(52.406374, 16.9251681)

def test_map_service():
    map_service = MapService()
    assert map_service.calculate_distance(location1, location2) == pytest.approx(278.546, rel=1e-2)


@pytest.mark.parametrize(
    ("elapsed_seconds", "expected_average_speed"),
    [(3600, 500), (25 * 3600, 20)],
)
def test_map_service_updates_average_speed(
    monkeypatch, elapsed_seconds, expected_average_speed
):
    map_service = MapService()
    monkeypatch.setattr(map_service, "calculate_distance", lambda *_: 500)

    map_service.update_average_speed(
        location1,
        location2,
        datetime.timedelta(seconds=elapsed_seconds),
    )

    assert map_service.average_speed == pytest.approx(expected_average_speed)


@pytest.mark.parametrize("elapsed_seconds", [0, -1])
def test_map_service_rejects_non_positive_elapsed_time(elapsed_seconds):
    map_service = MapService()

    with pytest.raises(ValueError, match="elapsed_time must be greater than zero"):
        map_service.update_average_speed(
            location1,
            location2,
            datetime.timedelta(seconds=elapsed_seconds),
        )


def test_delivery_controller_accepts_injected_services():
    email_gateway = EmailGateway()
    map_service = MapService()

    controller = DeliveryController([], email_gateway, map_service)

    assert controller.email_gateway is email_gateway
    assert controller.map_service is map_service


def test_delivery_controller_defaults_services_for_existing_callers():
    controller = DeliveryController([])

    assert isinstance(controller.email_gateway, EmailGateway)
    assert isinstance(controller.map_service, MapService)


def test_email_gateway_uses_configured_smtp_settings(monkeypatch):
    class FakeSMTP:
        def __init__(self, server):
            self.server = server
            self.sent_message = None

        def sendmail(self, from_address, recipients, message):
            self.sent_message = (from_address, recipients, message)

        def quit(self):
            pass

    smtp_connections = []

    def create_smtp(server):
        connection = FakeSMTP(server)
        smtp_connections.append(connection)
        return connection

    monkeypatch.setattr("email_gateway.smtplib.SMTP", create_smtp)
    gateway = EmailGateway("smtp.example.test", "dispatch@example.test")

    gateway.send("customer@example.test", "Subject", "Message")

    assert smtp_connections[0].server == "smtp.example.test"
    assert smtp_connections[0].sent_message[0] == "dispatch@example.test"
    assert smtp_connections[0].sent_message[1] == ["customer@example.test"]


@pytest.mark.parametrize(
    ("minutes_late", "expected_on_time"),
    [(9, True), (10, True), (11, False)],
)
def test_delivery_on_time_boundary(minutes_late, expected_on_time):
    scheduled_time = datetime.datetime(2025, 1, 1, 12, 0)
    delivery = Delivery(
        id="delivery-1",
        contact_email="customer@example.test",
        location=location1,
        time_of_delivery=scheduled_time,
        arrived=False,
        on_time=not expected_on_time,
    )
    controller = DeliveryController([delivery], email_gateway=Mock())
    event = DeliveryEvent(
        id=delivery.id,
        time_of_delivery=scheduled_time + datetime.timedelta(minutes=minutes_late),
        location=location1,
    )

    controller.update_delivery(event)

    assert delivery.on_time is expected_on_time


def test_duplicate_late_delivery_event_is_ignored():
    scheduled_time = datetime.datetime(2025, 1, 1, 12, 0)
    delivery = Delivery(
        id="delivery-1",
        contact_email="customer@example.test",
        location=location1,
        time_of_delivery=scheduled_time,
        arrived=False,
        on_time=False,
    )
    email_gateway = Mock()
    controller = DeliveryController([delivery], email_gateway=email_gateway)
    event = DeliveryEvent(
        id=delivery.id,
        time_of_delivery=scheduled_time + datetime.timedelta(minutes=11),
        location=location1,
    )

    controller.update_delivery(event)
    first_arrival_time = delivery.time_of_delivery
    controller.update_delivery(event)

    assert delivery.arrived is True
    assert delivery.on_time is False
    assert delivery.time_of_delivery == first_arrival_time
    assert email_gateway.send.call_count == 1


def test_out_of_order_arrivals_refresh_eta_for_next_unarrived_stop():
    scheduled_time = datetime.datetime(2025, 1, 1, 12, 0)
    next_location = Location(53.0, 22.0)
    deliveries = [
        Delivery("first", "first@example.test", location1, scheduled_time, False, False),
        Delivery("middle", "middle@example.test", location2, scheduled_time, False, False),
        Delivery("next", "next@example.test", next_location, scheduled_time, False, False),
    ]
    map_service = Mock()
    map_service.calculate_eta.return_value = 15
    controller = DeliveryController(
        deliveries,
        email_gateway=Mock(),
        map_service=map_service,
    )

    controller.update_delivery(
        DeliveryEvent(
            "middle",
            scheduled_time + datetime.timedelta(minutes=1),
            location2,
        )
    )
    controller.update_delivery(
        DeliveryEvent(
            "first",
            scheduled_time + datetime.timedelta(minutes=1),
            location1,
        )
    )

    assert map_service.calculate_eta.call_count == 2
    assert map_service.calculate_eta.call_args_list[0].args == (location2, next_location)
    assert map_service.calculate_eta.call_args_list[1].args == (location1, next_location)

# TODO: test delivery_controller