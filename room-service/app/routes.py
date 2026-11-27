from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from .database import get_db
from .models import Building, Room
from .schemas import (
    BuildingCreate,
    BuildingResponse,
    RoomCreate,
    RoomResponse,
    RoomDetailResponse
)
from .clients import get_average_rating
from .auth import current_user

router = APIRouter(
    dependencies=[Depends(current_user)]
)

# GET endpoints
@router.get("/buildings", response_model=list[BuildingResponse])
def get_buildings(db: Session = Depends(get_db)):
    return db.query(Building).all()

@router.get("/rooms", response_model=list[RoomResponse])
def get_rooms(db: Session = Depends(get_db)):
    return db.query(Room).all()

@router.get("/rooms/{id}", response_model=RoomDetailResponse)
def get_room(
    id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    room = db.get(Room, id)
    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found"
        )

    result = RoomDetailResponse.model_validate(room)
    result.average_rating = get_average_rating(
        id,
        request.headers["Authorization"]
    )

# POST endpoints
@router.post(
    "/buildings",
    response_model=BuildingResponse,
    status_code=201
)
def create_building(
    data: BuildingCreate,
    db: Session = Depends(get_db)
):
    building = Building(**data.model_dump())
    db.add(building)
    db.commit()
    db.refresh(building)
    return building


@router.post(
    "/rooms",
    response_model=RoomResponse,
    status_code=201
)
def create_room(
    data: RoomCreate,
    db: Session = Depends(get_db)
):
    building = db.get(Building, data.building_id)
    if building is None:
        raise HTTPException(
            status_code=404,
            detail="Building not found"
        )
    room = Room(**data.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

# PUT endpoints
@router.put(
    "/buildings/{id}",
    response_model=BuildingResponse
)
def update_building(
    id: int,
    data: BuildingCreate,
    db: Session = Depends(get_db)
):
    building = db.get(Building, id)
    if building is None:
        raise HTTPException(
            status_code=404,
            detail="Building not found"
        )

    building.name = data.name
    building.address = data.address
    db.commit()
    db.refresh(building)
    return building


@router.put(
    "/rooms/{id}",
    response_model=RoomResponse
)
def update_room(
    id: int,
    data: RoomCreate,
    db: Session = Depends(get_db)
):
    room = db.get(Room, id)
    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found"
        )

    building = db.get(Building, data.building_id)
    if building is None:
        raise HTTPException(
            status_code=404,
            detail="Building not found"
        )
    
    room.building_id = data.building_id
    room.name = data.name
    room.capacity = data.capacity
    room.floor = data.floor
    room.description = data.description
    db.commit()
    db.refresh(room)
    return room

# DELETE endpoints
@router.delete("/buildings/{id}", status_code=204)
def delete_building(
    id: int,
    db: Session = Depends(get_db)
):
    building = db.get(Building, id)
    if building is None:
        raise HTTPException(
            status_code=404,
            detail="Building not found"
        )

    if building.rooms:
        raise HTTPException(
            status_code=409,
            detail="Building contains rooms"
        )

    db.delete(building)
    db.commit()


@router.delete("/rooms/{id}", status_code=204)
def delete_room(
    id: int,
    db: Session = Depends(get_db)
):
    room = db.get(Room, id)
    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found"
        )

    db.delete(room)
    db.commit()