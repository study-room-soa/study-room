from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from .database import get_db
from .models import Booking
from .schemas import BookingCreate, BookingResponse
from .clients import check_user_exists, send_notification
from .auth import current_user, get_current_user_id

router = APIRouter(
    dependencies=[Depends(current_user)]
)

def validate_booking(
    db: Session,
    room_id: int,
    start_time: datetime,
    end_time: datetime,
    exclude_id: int | None = None
):
    if start_time >= end_time:
        raise HTTPException(
            status_code=400,
            detail="End time must be after start time"
        )

    query = db.query(Booking).filter(
        Booking.room_id == room_id,
        Booking.status != "cancelled",
        Booking.start_time < end_time,
        Booking.end_time > start_time
    )

    if exclude_id is not None:
        query = query.filter(Booking.id != exclude_id)

    if query.first() is not None:
        raise HTTPException(
            status_code=409,
            detail="Room is already booked for this time period"
        )

def check_booking_owner(booking: Booking, user_id: int):
    if booking.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot access another user's booking"
        )

# GET endpoints
@router.get("/bookings", response_model=list[BookingResponse])
def get_bookings(
    room_id: int | None = Query(default=None, alias="roomId"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    query = db.query(Booking).filter(
        Booking.user_id == current_user_id
    )

    if room_id is not None:
        query = query.filter(Booking.room_id == room_id)

    return query.all()

@router.get("/bookings/{id}", response_model=BookingResponse)
def get_booking(
    id: int, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    booking = db.get(Booking, id)
    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )
    
    check_booking_owner(booking, user_id)
    return booking

# POST endpoints
@router.post(
    "/bookings",
    response_model=BookingResponse,
    status_code=201
)
def create_booking(
    data: BookingCreate,
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    if data.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot create booking for another user"
        )

    check_user_exists(data.user_id, request.headers["Authorization"])
    validate_booking(
        db,
        data.room_id,
        data.start_time,
        data.end_time
    )

    booking = Booking(
        **data.model_dump(),
        status="confirmed"
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)
    send_notification(
        booking.user_id,
        f"Your booking #{booking.id} has been confirmed.",
        request.headers["Authorization"]
    )
    return booking

@router.post(
    "/bookings/{id}/checkin",
    response_model=BookingResponse
)
def checkin_booking(
    id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    booking = db.get(Booking, id)
    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    check_booking_owner(booking, user_id)

    if booking.status != "confirmed":
        raise HTTPException(
            status_code=409,
            detail="Booking must be confirmed"
        )

    booking.status = "checked_in"

    db.commit()
    db.refresh(booking)
    return booking

# PUT endpoints
@router.put(
    "/bookings/{id}",
    response_model=BookingResponse
)
def update_booking(
    id: int,
    data: BookingCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    booking = db.get(Booking, id)
    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    check_booking_owner(booking, user_id)
    if data.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot change booking owner"
        )
    
    if booking.status != "confirmed":
        raise HTTPException(
            status_code=409,
            detail="Only confirmed bookings can be updated"
        )

    validate_booking(
        db,
        data.room_id,
        data.start_time,
        data.end_time,
        exclude_id=id
    )

    booking.room_id = data.room_id
    booking.start_time = data.start_time
    booking.end_time = data.end_time
    db.commit()
    db.refresh(booking)
    return booking

@router.put(
    "/bookings/{id}/cancel",
    response_model=BookingResponse
)
def cancel_booking(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    booking = db.get(Booking, id)
    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    check_booking_owner(booking, user_id)

    if booking.status == "cancelled":
        return booking

    if booking.status != "confirmed":
        raise HTTPException(
            status_code=409,
            detail="Only confirmed bookings can be cancelled"
        )

    booking.status = "cancelled"
    db.commit()
    db.refresh(booking)
    send_notification(
        booking.user_id,
        f"Your booking #{booking.id} has been cancelled.",
        request.headers["Authorization"]
    )
    return booking

# DELETE endpoints
@router.delete("/bookings/{id}", status_code=204)
def delete_booking(
    id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    booking = db.get(Booking, id)
    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )
    
    check_booking_owner(booking, user_id)
    db.delete(booking)
    db.commit()


@router.delete("/bookings/user/{userId}", status_code=204)
def delete_user_bookings(
    userId: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    if userId != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot delete another user's bookings"
        )

    db.query(Booking).filter(
        Booking.user_id == userId
    ).delete()
    db.commit()