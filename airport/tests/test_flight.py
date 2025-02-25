from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse

from airport.models import Flight
from airport.serializers import (
    FlightListSerializer,
    FlightRetrieveSerializer,
    FlightSerializer
)
from airport.tests.base_functions import (
    sample_flight,
    sample_airport,
    sample_route,
    sample_airplane,
    sample_user,
    sample_crew
)

FLIGHT_URL = reverse("airport:flight-list")


def flight_detail_url(flight_id):
    """Return the flight detail URL"""
    return reverse("airport:flight-detail", args=[flight_id])


class UnauthenticatedFlightTests(TestCase):
    """Test unauthenticated flight API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required to access flights"""
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightTests(TestCase):
    """Test authenticated user flight API"""

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(user=self.user)

    def test_list_flights(self):
        """Test retrieving a list of flights"""
        airport_1 = sample_airport(
            name="JFK Airport",
            closest_big_city="New York"
        )
        airport_2 = sample_airport(
            name="DXB Airport",
            closest_big_city="Dubai"
        )
        route = sample_route(source=airport_1, destination=airport_2)
        airplane = sample_airplane(name="Boeing 777X")

        sample_flight(route=route, airplane=airplane)

        res = self.client.get(FLIGHT_URL)
        flights = Flight.objects.all()
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_flight(self):
        """Test retrieving a specific flight"""
        airport_1 = sample_airport(
            name="LAX Airport",
            closest_big_city="Los Angeles"
        )
        airport_2 = sample_airport(
            name="HND Airport",
            closest_big_city="Tokyo"
        )
        route = sample_route(source=airport_1, destination=airport_2)
        airplane = sample_airplane(name="Airbus A380")

        flight = sample_flight(route=route, airplane=airplane)
        url = flight_detail_url(flight.id)

        res = self.client.get(url)
        serializer = FlightRetrieveSerializer(flight)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_flight_forbidden(self):
        """Test that regular users cannot create a flight"""
        airport_1 = sample_airport(
            name="Berlin Brandenburg",
            closest_big_city="Berlin"
        )
        airport_2 = sample_airport(
            name="Heathrow",
            closest_big_city="London"
        )
        route = sample_route(source=airport_1, destination=airport_2)
        airplane = sample_airplane(name="Boeing 737 MAX")

        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "25-06-2025",
            "arrival_time": "26-06-2025",
        }
        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightTests(TestCase):
    """Test admin user flight API"""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@admin.admin",
            password="adminpassword",
        )
        self.client.force_authenticate(self.admin_user)

    def test_create_flight(self):
        """Test creating a flight as an admin"""
        airport_1 = sample_airport(
            name="Changi Airport",
            closest_big_city="Singapore"
        )
        airport_2 = sample_airport(
            name="Sydney Airport",
            closest_big_city="Sydney"
        )
        route = sample_route(source=airport_1, destination=airport_2)
        airplane = sample_airplane(name="Boeing 787 Dreamliner")
        crew = sample_crew()

        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2025-02-24T14:30:00Z",
            "arrival_time": "2025-02-25T06:45:00Z",
            "crew": [crew.id]
        }

        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        flight = Flight.objects.get(id=res.data["id"])
        serializer = FlightSerializer(flight)

        self.assertEqual(res.data, serializer.data)
