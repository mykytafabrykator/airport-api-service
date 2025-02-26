from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse

from airport.models import Crew
from airport.serializers import CrewSerializer
from airport.tests.base_functions import sample_crew, sample_user

CREW_URL = reverse("airport:crew-list")


class UnauthenticatedCrewTests(TestCase):
    """Test unauthenticated crew API access"""

    def setUp(self):
        self.client = APIClient()

    def test_list_crew_forbidden(self):
        """Test that unauthenticated users cannot access crew list"""
        sample_crew()

        res = self.client.get(CREW_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_crew_unauthorized(self):
        """Test that unauthenticated users cannot create a crew member"""
        payload = {
            "first_name": "John",
            "last_name": "Doe",
        }

        res = self.client.post(CREW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewTests(TestCase):
    """Test authenticated user crew API"""

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(user=self.user)

    def test_list_crew(self):
        """Test retrieving a list of crew members as an authenticated user"""
        sample_crew()

        res = self.client.get(CREW_URL)
        crew = Crew.objects.all()
        serializer = CrewSerializer(crew, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_crew_forbidden(self):
        """Test that regular users cannot create a crew member"""
        payload = {
            "first_name": "Alice",
            "last_name": "Smith",
        }

        res = self.client.post(CREW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewTests(TestCase):
    """Test admin user crew API"""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@admin.admin",
            password="adminpassword",
        )
        self.client.force_authenticate(self.admin_user)

    def test_create_crew(self):
        """Test creating a crew member as an admin"""
        payload = {
            "first_name": "Alice",
            "last_name": "Smith",
        }

        res = self.client.post(CREW_URL, payload)

        crew_member = Crew.objects.get(id=res.data["id"])
        serializer = CrewSerializer(crew_member)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, serializer.data)
