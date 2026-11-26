from pydantic import BaseModel, ConfigDict, Field

class BuildingCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    address: str = Field(min_length=1, max_length=255)

class BuildingResponse(BuildingCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class RoomCreate(BaseModel):
    building_id: int = Field(alias="buildingId", gt=0)
    name: str = Field(min_length=1, max_length=100)
    capacity: int = Field(gt=0)
    floor: int
    description: str | None = None

class RoomResponse(RoomCreate):
    id: int
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class RoomDetailResponse(RoomResponse):
    average_rating: float | None = Field(
        default=None,
        alias="averageRating"
    )