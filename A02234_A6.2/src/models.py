from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class Hotel:
    hotel_id: str
    name: str
    city: str
    total_rooms: int

    def validate(self) -> None:
        if self.total_rooms <= 0:
            raise ValueError("total_rooms must be > 0")


@dataclass(frozen=True)
class Customer:
    customer_id: str
    full_name: str
    email: str


@dataclass(frozen=True)
class Reservation:
    reservation_id: str
    hotel_id: str
    customer_id: str
    check_in: str  # ISO date "YYYY-MM-DD"
    nights: int
    room_number: int

    def validate(self) -> None:
        if self.nights <= 0:
            raise ValueError("nights must be > 0")
        # date format validation
        date.fromisoformat(self.check_in)
        if self.room_number <= 0:
            raise ValueError("room_number must be > 0")
