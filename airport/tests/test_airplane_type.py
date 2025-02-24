from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse

from airport.models import AirplaneType
from airport.serializers import AirplaneTypeSerializer
from airport.tests.base_functions import sample_airplane_type, sample_user

AIRPLANE_TYPE_URL = reverse("airport:airplanetype-list")


class UnauthenticatedAirplaneTypeTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required
        for retrieving airplane types"""
        result = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneTypeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(user=self.user)

    def test_airplane_type_list(self):
        """Test retrieving a list of airplane types"""
        sample_airplane_type(name="Commercial Jet")
        sample_airplane_type(name="Private Jet")

        result = self.client.get(AIRPLANE_TYPE_URL)
        airplane_types = AirplaneType.objects.all().order_by("name")
        serializer = AirplaneTypeSerializer(airplane_types, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_create_airplane_type_forbidden(self):
        """Test that creating an airplane type
        is forbidden for regular users"""
        payload = {"name": "Helicopter"}

        result = self.client.post(AIRPLANE_TYPE_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTypeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.com",
            password="adminpassword",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_airplane_type(self):
        """Test creating a new airplane type"""
        payload = {"name": "Cargo Aircraft"}

        result = self.client.post(AIRPLANE_TYPE_URL, payload)
        airplane_type = AirplaneType.objects.get(id=result.data["id"])
        serializer = AirplaneTypeSerializer(airplane_type)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertEqual(serializer.data["name"], payload["name"])
