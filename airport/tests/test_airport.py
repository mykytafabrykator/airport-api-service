from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse

from airport.models import Airport
from airport.serializers import AirportSerializer
from airport.tests.base_functions import sample_airport, sample_user

AIRPORT_URL = reverse("airport:airport-list")


def airport_detail_url(airport_id):
    """Return the airport detail URL"""
    return reverse("airport:airport-detail", args=[airport_id])


class UnauthenticatedAirportTests(TestCase):
    """Test unauthenticated airport API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required for accessing airport API"""
        res = self.client.get(AIRPORT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_airport_unauthorized(self):
        """Test that unauthenticated users cannot create an airport"""
        payload = {
            "name": "John F. Kennedy International Airport",
            "closest_big_city": "New York"
        }
        res = self.client.post(AIRPORT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirportTests(TestCase):
    """Test authenticated user airport API"""

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(user=self.user)

    def test_airport_list(self):
        """Test retrieving a list of airports"""
        sample_airport()

        res = self.client.get(AIRPORT_URL)
        airports = Airport.objects.all()
        serializer = AirportSerializer(airports, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airport_forbidden(self):
        """Test that regular users cannot create an airport"""
        payload = {
            "name": "Los Angeles International Airport",
            "closest_big_city": "Los Angeles"
        }

        res = self.client.post(AIRPORT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportTests(TestCase):
    """Test admin user airport API"""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@admin.admin",
            password="adminpassword",
        )
        self.client.force_authenticate(self.admin_user)

    def test_create_airport(self):
        """Test creating an airport as admin"""
        payload = {
            "name": "San Francisco International Airport",
            "closest_big_city": "San Francisco"
        }

        res = self.client.post(AIRPORT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Airport.objects.count(), 1)
        self.assertEqual(Airport.objects.get().name, payload["name"])
