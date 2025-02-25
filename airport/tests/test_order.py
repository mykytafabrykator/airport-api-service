from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse

from airport.models import Order
from airport.serializers import (
    OrderListSerializer,
    OrderRetrieveSerializer,
    OrderSerializer
)
from airport.tests.base_functions import (
    sample_order,
    sample_user,
    sample_ticket
)

ORDER_URL = reverse("airport:order-list")


def order_detail_url(order_id):
    """Return the order detail URL"""
    return reverse("airport:order-detail", args=[order_id])


class UnauthenticatedOrderTests(TestCase):
    """Test unauthenticated order API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required for accessing orders"""
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderTests(TestCase):
    """Test authenticated user order API"""

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(user=self.user)
        self.user2 = sample_user(email="hello_world@email.com")

    def test_list_orders(self):
        """Test retrieving a list of orders for the authenticated user"""
        sample_order(user=self.user)

        res = self.client.get(ORDER_URL)
        orders = Order.objects.filter(user=self.user)
        serializer = OrderListSerializer(orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_create_order(self):
        """Test creating an order as an authenticated user"""
        flight = sample_ticket().flight
        payload = {
            "tickets": [
                {
                    "row": 3,
                    "seat": 3,
                    "flight": flight.id,
                }
            ]
        }

        res = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        order = Order.objects.get(id=res.data["id"])
        serializer = OrderSerializer(order)

        self.assertEqual(res.data, serializer.data)


class RetrieveOrderTest(TestCase):
    """Test retrieving a specific order"""

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(user=self.user)
        self.order = sample_order(user=self.user)

    def test_retrieve_order(self):
        """Test retrieving order details"""
        url = order_detail_url(self.order.id)
        res = self.client.get(url)
        serializer = OrderRetrieveSerializer(self.order)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
