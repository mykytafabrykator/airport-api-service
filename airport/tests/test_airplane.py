from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse

from airport.models import Airplane
from airport.serializers import (
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
    AirplaneSerializer,
)
from airport.tests.base_functions import (
    sample_airplane,
    sample_airplane_type,
    sample_user
)

AIRPLANE_URL = reverse("airport:airplane-list")


def airplane_detail_url(airplane_id):
    """Return the airplane detail URL"""
    return reverse("airport:airplane-detail", args=[airplane_id])


class UnauthenticatedAirplaneTests(TestCase):
    """Test unauthenticated airplane API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required for accessing airplane API"""
        result = self.client.get(AIRPLANE_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneTests(TestCase):
    """Test authenticated user airplane API"""

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(user=self.user)

    def test_airplane_list(self):
        """Test retrieving a list of airplanes"""
        sample_airplane()

        result = self.client.get(AIRPLANE_URL)
        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_airplane_retrieve(self):
        """Test retrieving a single airplane"""
        airplane = sample_airplane()
        url = airplane_detail_url(airplane.id)

        result = self.client.get(url)
        serializer = AirplaneRetrieveSerializer(airplane)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_create_airplane_forbidden(self):
        """Test that non-admin users cannot create an airplane"""
        payload = {
            "name": "Airbus A321XLR",
            "rows": 35,
            "seats_in_row": 6,
            "airplane_type": sample_airplane_type().id,
        }

        result = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTests(TestCase):
    """Test admin user airplane API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@admin.admin",
            password="adminpassword",
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane(self):
        """Test creating an airplane as admin"""
        airplane_type = sample_airplane_type()
        payload = {
            "name": "Airbus A321XLR",
            "rows": 35,
            "seats_in_row": 6,
            "airplane_type": airplane_type.id,
        }

        res = self.client.post(AIRPLANE_URL, payload)

        airplane = Airplane.objects.get(id=res.data["id"])
        serializer = AirplaneSerializer(airplane)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, serializer.data)
