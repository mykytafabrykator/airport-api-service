from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse

from airport.models import Route
from airport.serializers import (
    RouteListSerializer,
    RouteRetrieveSerializer,
    RouteSerializer
)
from airport.tests.base_functions import (
    sample_route,
    sample_user,
    sample_airport
)

ROUTE_URL = reverse("airport:route-list")


def route_detail_url(route_id):
    """Return the route detail URL"""
    return reverse("airport:route-detail", args=[route_id])


class UnauthenticatedRouteTests(TestCase):
    """Test unauthenticated route API access"""

    def setUp(self):
        self.client = APIClient()

    def test_list_routes_unauthorized(self):
        """Test that unauthenticated users cannot retrieve a list of routes"""
        sample_route()

        res = self.client.get(ROUTE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_route_unauthorized(self):
        """Test that unauthenticated users cannot retrieve a specific route"""
        route = sample_route()
        url = route_detail_url(route.id)

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_route_unauthorized(self):
        """Test that unauthenticated users cannot create a route"""
        payload = {
            "source": sample_airport().id,
            "destination": sample_airport(name="Los Angeles").id,
            "distance": 800,
        }
        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteTests(TestCase):
    """Test authenticated user route API"""

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(user=self.user)

    def test_list_routes(self):
        """Test retrieving a list of routes as an authenticated user"""
        sample_route()

        res = self.client.get(ROUTE_URL)
        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_route(self):
        """Test retrieving a specific route as an authenticated user"""
        route = sample_route()
        url = route_detail_url(route.id)

        res = self.client.get(url)
        serializer = RouteRetrieveSerializer(route)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_route_forbidden(self):
        """Test that regular users cannot create a route"""
        payload = {
            "source": sample_airport().id,
            "destination": sample_airport(name="Los Angeles").id,
            "distance": 900,
        }
        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteTests(TestCase):
    """Test admin user route API"""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@admin.admin",
            password="adminpassword",
        )
        self.client.force_authenticate(self.admin_user)

    def test_create_route(self):
        """Test creating a route as an admin"""
        source_airport = sample_airport()
        destination_airport = sample_airport(name="Los Angeles")

        payload = {
            "source": source_airport.id,
            "destination": destination_airport.id,
            "distance": 1200,
        }

        res = self.client.post(ROUTE_URL, payload)

        route = Route.objects.get(id=res.data["id"])
        serializer = RouteSerializer(route)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, serializer.data)
