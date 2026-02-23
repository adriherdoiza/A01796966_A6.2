import json
import tempfile
import unittest
from pathlib import Path

from src.models import Customer, Hotel
from src.services import CustomerService, HotelService, ReservationService


class TestReservations(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        base = Path(self.tmpdir.name)
        self.hotels = str(base / "hotels.json")
        self.customers = str(base / "customers.json")
        self.reservations = str(base / "reservations.json")

        Path(self.hotels).write_text("[]", encoding="utf-8")
        Path(self.customers).write_text("[]", encoding="utf-8")
        Path(self.reservations).write_text("[]", encoding="utf-8")

        self.hotel_service = HotelService(self.hotels, self.reservations)
        self.customer_service = CustomerService(self.customers)
        self.res_service = ReservationService(
            self.reservations, self.hotel_service, self.customer_service
        )

        self.hotel_service.create_hotel(Hotel("H1", "Hotel 1", "MTY", 2))
        self.customer_service.create_customer(Customer("C1", "User One", "u1@test.com"))

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_create_reservation_assigns_room(self) -> None:
        r1 = self.res_service.create_reservation("R1", "H1", "C1", "2026-01-01", 2)
        self.assertEqual(r1.room_number, 1)

        r2 = self.res_service.create_reservation("R2", "H1", "C1", "2026-01-02", 1)
        self.assertEqual(r2.room_number, 2)

    def test_no_rooms_available(self) -> None:
        self.res_service.create_reservation("R1", "H1", "C1", "2026-01-01", 1)
        self.res_service.create_reservation("R2", "H1", "C1", "2026-01-02", 1)
        with self.assertRaises(ValueError):
            self.res_service.create_reservation("R3", "H1", "C1", "2026-01-03", 1)

    def test_cancel_reservation(self) -> None:
        self.res_service.create_reservation("R1", "H1", "C1", "2026-01-01", 1)
        self.res_service.cancel_reservation("R1")
        self.assertEqual(len(self.res_service.list_reservations()), 0)
