import pathlib
import uuid
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError


class AirplaneType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Airplane(models.Model):
    name = models.CharField(max_length=100, unique=True)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name='airplanes'
    )

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return f"Airplane: {self.name} (id: {self.id})"

    class Meta:
        ordering = ["name"]


def airport_image_path(instance: "Airport", filename: str) -> pathlib.Path:
    filename = (f"{slugify(instance.closest_big_city)}-{uuid.uuid4()}"
                + pathlib.Path(filename).suffix)
    return pathlib.Path(f"upload/airports/") / pathlib.Path(filename)


class Airport(models.Model):
    name = models.CharField(max_length=100, unique=True)
    closest_big_city = models.CharField(max_length=100, unique=True)
    image = models.ImageField(null=True, upload_to=airport_image_path)

    @property
    def full_name(self) -> str:
        return f"{self.name} ({self.closest_big_city})"

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ["name"]


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="departing_routes"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="arriving_routes"
    )
    distance = models.PositiveIntegerField()

    @property
    def full_route(self) -> str:
        return f"{self.source.name} -> {self.destination.name}"

    def __str__(self):
        return self.full_route

    class Meta:
        unique_together = ("source", "destination")
        ordering = ["source__name", "destination__name"]


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ["last_name", "first_name"]


class Flight(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(
        Crew,
        related_name="flights"
    )

    @staticmethod
    def validate_flight(departure_time, arrival_time, error_to_raise):
        if not departure_time or not arrival_time:
            raise error_to_raise(
                "Both departure_time and arrival_time must be set."
            )

        if arrival_time <= departure_time:
            raise error_to_raise(
                "Arrival time must be later than departure time."
            )

    def clean(self):
        Flight.validate_flight(
            self.departure_time,
            self.arrival_time,
            ValidationError,
        )

    def __str__(self):
        return (f"Flight {self.id}: {self.route.full_route} "
                f"({self.departure_time} - {self.arrival_time})")

    class Meta:
        ordering = ["departure_time", "arrival_time"]


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    def __str__(self):
        return f"Order {self.id} - {self.user.username} ({self.created_at})"

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets",
    )

    @staticmethod
    def validate_ticket(row, seat, airplane, error_to_raise):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name.capitalize()} "
                        f"number must be in the range (1, {count_attrs}), "
                        f"but got {ticket_attr_value}."
                    }
                )

    def clean(self):
        if not self.flight or not self.flight.airplane:
            raise ValidationError(
                "Flight and Airplane must be set before validation."
            )

        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.flight.airplane,
            ValidationError,
        )

    def __str__(self):
        return (f"Ticket {self.id}: Flight {self.flight.route.full_route}, "
                f"Row {self.row}, Seat {self.seat}")

    class Meta:
        ordering = ["flight", "row", "seat"]
        unique_together = ("flight", "row", "seat")
