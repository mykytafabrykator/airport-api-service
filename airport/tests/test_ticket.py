from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse

from airport.models import Ticket
from airport.serializers import (
    TicketListSerializer,
    TicketRetrieveSerializer,
)
from airport.tests.base_functions import (
    sample_ticket,
    sample_user,
    sample_order,
)

TICKET_URL = reverse("airport:ticket-list")


def ticket_detail_url(ticket_id):
    """Return the ticket detail URL"""
    return reverse("airport:ticket-detail", args=[ticket_id])


class UnauthenticatedTicketTests(TestCase):
    """Test unauthenticated ticket API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required for accessing ticket API"""
        res = self.client.get(TICKET_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTicketTests(TestCase):
    """Test authenticated user ticket API"""

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(user=self.user)

    def test_list_tickets(self):
        """Test retrieving a list of tickets for the authenticated user"""
        order = sample_order(user=self.user)
        sample_ticket(order=order)

        res = self.client.get(TICKET_URL)
        tickets = Ticket.objects.filter(order__user=self.user)
        serializer = TicketListSerializer(tickets, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_ticket(self):
        """Test retrieving a specific ticket as an authenticated user"""
        order = sample_order(user=self.user)
        ticket = sample_ticket(order=order)
        url = ticket_detail_url(ticket.id)

        res = self.client.get(url)
        serializer = TicketRetrieveSerializer(ticket)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_access_other_user_ticket_forbidden(self):
        """Test that a user cannot retrieve another user's ticket"""
        other_user = sample_user(email="other@example.com")
        order = sample_order(user=other_user)
        ticket = sample_ticket(order=order)
        url = ticket_detail_url(ticket.id)

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
