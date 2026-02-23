
from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List, Optional

from src.models import Customer, Hotel, Reservation
from src.storage import JsonStorage


class HotelService:
    def __init__(self, hotels_path: str, reservations_path: str) -> None:
        self.hotels_store = JsonStorage(hotels_path)
        self.res_store = JsonStorage(reservations_path)

    def _load_hotels(self) -> List[Hotel]:
        raw = self.hotels_store.load_list()
        return self.hotels_store.from_dict_list(raw, Hotel)

    def _save_hotels(self, hotels: List[Hotel]) -> None:
        self.hotels_store.save_list([asdict(h) for h in hotels])

    def create_hotel(self, hotel: Hotel) -> None:
        hotel.validate()
        hotels = self._load_hotels()
        if any(h.hotel_id == hotel.hotel_id for h in hotels):
            raise ValueError("Hotel already exists")
        hotels.append(hotel)
        self._save_hotels(hotels)

    def delete_hotel(self, hotel_id: str) -> None:
        hotels = self._load_hotels()
        new_hotels = [h for h in hotels if h.hotel_id != hotel_id]
        if len(new_hotels) == len(hotels):
            raise ValueError("Hotel not found")
        self._save_hotels(new_hotels)

    def get_hotel(self, hotel_id: str) -> Hotel:
        for h in self._load_hotels():
            if h.hotel_id == hotel_id:
                return h
        raise ValueError("Hotel not found")

    def modify_hotel(
        self,
        hotel_id: str,
        name: Optional[str] = None,
        city: Optional[str] = None,
        total_rooms: Optional[int] = None,
    ) -> None:
        hotels = self._load_hotels()
        updated: List[Hotel] = []
        found = False
        for h in hotels:
            if h.hotel_id != hotel_id:
                updated.append(h)
                continue
            found = True
            new_hotel = Hotel(
                hotel_id=h.hotel_id,
                name=name if name is not None else h.name,
                city=city if city is not None else h.city,
                total_rooms=total_rooms if total_rooms is not None else h.total_rooms,
            )
            new_hotel.validate()
            updated.append(new_hotel)

        if not found:
            raise ValueError("Hotel not found")
        self._save_hotels(updated)

    def list_hotels(self) -> List[Hotel]:
        return self._load_hotels()

    def reserve_room_capacity_check(self, hotel_id: str) -> int:
        hotel = self.get_hotel(hotel_id)
        reservations = self.res_store.from_dict_list(
            self.res_store.load_list(), Reservation
        )
        reserved_rooms = {r.room_number for r in reservations if r.hotel_id == hotel_id}
        # simplistic: next available room number in 1..total_rooms
        for room in range(1, hotel.total_rooms + 1):
            if room not in reserved_rooms:
                return room
        raise ValueError("No rooms available")


class CustomerService:
    def __init__(self, customers_path: str) -> None:
        self.customers_store = JsonStorage(customers_path)

    def _load_customers(self) -> List[Customer]:
        return self.customers_store.from_dict_list(
            self.customers_store.load_list(), Customer
        )

    def _save_customers(self, customers: List[Customer]) -> None:
        self.customers_store.save_list([asdict(c) for c in customers])

    def create_customer(self, customer: Customer) -> None:
        customers = self._load_customers()
        if any(c.customer_id == customer.customer_id for c in customers):
            raise ValueError("Customer already exists")
        customers.append(customer)
        self._save_customers(customers)

    def delete_customer(self, customer_id: str) -> None:
        customers = self._load_customers()
        new_customers = [c for c in customers if c.customer_id != customer_id]
        if len(new_customers) == len(customers):
            raise ValueError("Customer not found")
        self._save_customers(new_customers)

    def get_customer(self, customer_id: str) -> Customer:
        for c in self._load_customers():
            if c.customer_id == customer_id:
                return c
        raise ValueError("Customer not found")

    def modify_customer(
        self,
        customer_id: str,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        customers = self._load_customers()
        updated: List[Customer] = []
        found = False
        for c in customers:
            if c.customer_id != customer_id:
                updated.append(c)
                continue
            found = True
            updated.append(
                Customer(
                    customer_id=c.customer_id,
                    full_name=full_name if full_name is not None else c.full_name,
                    email=email if email is not None else c.email,
                )
            )
        if not found:
            raise ValueError("Customer not found")
        self._save_customers(updated)

    def list_customers(self) -> List[Customer]:
        return self._load_customers()


class ReservationService:
    def __init__(
        self,
        reservations_path: str,
        hotel_service: HotelService,
        customer_service: CustomerService,
    ) -> None:
        self.res_store = JsonStorage(reservations_path)
        self.hotel_service = hotel_service
        self.customer_service = customer_service

    def _load_reservations(self) -> List[Reservation]:
        return self.res_store.from_dict_list(self.res_store.load_list(), Reservation)

    def _save_reservations(self, reservations: List[Reservation]) -> None:
        self.res_store.save_list([asdict(r) for r in reservations])

    def create_reservation(
        self, reservation_id: str, hotel_id: str, customer_id: str, check_in: str, nights: int
    ) -> Reservation:
        _ = self.hotel_service.get_hotel(hotel_id)
        _ = self.customer_service.get_customer(customer_id)

        reservations = self._load_reservations()
        if any(r.reservation_id == reservation_id for r in reservations):
            raise ValueError("Reservation already exists")

        room = self.hotel_service.reserve_room_capacity_check(hotel_id)
        reservation = Reservation(
            reservation_id=reservation_id,
            hotel_id=hotel_id,
            customer_id=customer_id,
            check_in=check_in,
            nights=nights,
            room_number=room,
        )
        reservation.validate()
        reservations.append(reservation)
        self._save_reservations(reservations)
        return reservation

    def cancel_reservation(self, reservation_id: str) -> None:
        reservations = self._load_reservations()
        new_list = [r for r in reservations if r.reservation_id != reservation_id]
        if len(new_list) == len(reservations):
            raise ValueError("Reservation not found")
        self._save_reservations(new_list)

    def list_reservations(self) -> List[Reservation]:
        return self._load_reservations()
