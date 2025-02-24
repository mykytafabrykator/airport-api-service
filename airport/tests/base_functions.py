import uuid
from datetime import datetime
from django.contrib.auth import get_user_model
from airport.models import (
    Airport,
    Airplane,
    AirplaneType,
    Flight,
    Route,
    Crew,
    Order,
    Ticket
)


def sample_user(**params):
    """Create a sample user"""
    defaults = {
        "email": "test@test.test",
        "password": "testpassword",
    }
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


def sample_airplane_type(**params) -> AirplaneType:
    """Create a sample airplane type"""
    defaults = {"name": "Civil aircraft"}
    defaults.update(params)

    return AirplaneType.objects.create(**defaults)


def sample_airplane(**params) -> Airplane:
    """Create a sample airplane"""
    defaults = {
        "name": "Airbus A320neo",
        "airplane_type": sample_airplane_type(),
        "rows": 30,
        "seats_in_row": 6,
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)


def sample_airport(name=None, closest_big_city=None, **params) -> Airport:
    """Create and return an airport with unique parameters"""
    defaults = {
        "name": name if name else f"Airport {uuid.uuid4()}",
        "closest_big_city": closest_big_city
        if closest_big_city else f"City {uuid.uuid4()}",
    }
    defaults.update(params)
    return Airport.objects.create(**defaults)


def sample_route(source=None, destination=None, **params) -> Route:
    """Create and return a route"""
    if not source:
        source = sample_airport(
            name="JFK Airport",
            closest_big_city="New York"
        )
    if not destination:
        destination = sample_airport(
            name="LAX Airport",
            closest_big_city="Los Angeles"
        )

    defaults = {"source": source, "destination": destination, "distance": 1000}
    defaults.update(params)
    return Route.objects.create(**defaults)


def sample_crew(**params) -> Crew:
    """Create a sample crew member"""
    defaults = {
        "first_name": "Laura",
        "last_name": "Anderson",
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)


def sample_flight(route=None, airplane=None, **params) -> Flight:
    """Create and return a flight"""
    if not route:
        route = sample_route(
            source=sample_airport(
                name="DXB Airport",
                closest_big_city="Dubai"
            ),
            destination=sample_airport(
                name="CDG Airport",
                closest_big_city="Paris"
            ),
        )
    if not airplane:
        airplane = sample_airplane(name="Boeing 777X")

    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": datetime.strptime(
            "2025-02-24 14:30:00",
            "%Y-%m-%d %H:%M:%S"
        ),
        "arrival_time": datetime.strptime(
            "2025-02-25 06:45:00",
            "%Y-%m-%d %H:%M:%S"
        ),
    }
    defaults.update(params)
    return Flight.objects.create(**defaults)


def sample_order(**params) -> Order:
    """Create a sample order"""
    defaults = {
        "created_at": datetime.now(),
        "user": sample_user(email="test2@test.test"),
    }
    defaults.update(params)

    return Order.objects.create(**defaults)


def sample_ticket(**params) -> Ticket:
    """Create a sample ticket"""
    defaults = {
        "row": 1,
        "seat": 1,
        "flight": sample_flight(),
        "order": sample_order(),
    }
    defaults.update(params)

    return Ticket.objects.create(**defaults)
