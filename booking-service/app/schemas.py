from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, AwareDatetime

class BookingCreate(BaseModel):
    user_id: int = Field(alias="userId", gt=0)
    room_id: int = Field(alias="roomId", gt=0)
    start_time: AwareDatetime = Field(alias="startTime")
    end_time: AwareDatetime = Field(alias="endTime")

class BookingResponse(BookingCreate):
    id: int
    status: Literal["confirmed", "checked_in", "cancelled"]
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )