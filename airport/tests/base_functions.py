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


def sample_airport(**params) -> Airport:
    """Create a sample airport"""
    defaults = {
        "name": "Amsterdam Schiphol Airport",
        "closest_big_city": "Amsterdam"
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)


def sample_route(**params) -> Route:
    """Create a sample route"""
    defaults = {
        "source": sample_airport(),
        "destination": sample_airport(
            name="Boryspil International Airport",
            closest_big_city="Kyiv"
        ),
        "distance": 1111
    }
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


def sample_flight(**params) -> Flight:
    """Create a sample flight"""
    defaults = {
        "route": sample_route(),
        "airplane": sample_airplane(),
        "departure_time": datetime.strptime("24-02-2025", "%d-%m-%Y"),
        "arrival_time": datetime.strptime("25-02-2025", "%d-%m-%Y"),
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
