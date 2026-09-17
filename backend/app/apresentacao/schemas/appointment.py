from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AppointmentBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1)
    start_datetime: datetime
    end_datetime: datetime
    url_maps: str | None = None
    location_name: str | None = Field(default=None, max_length=500)
    location_lat: float | None = None
    location_lng: float | None = None

    @model_validator(mode="after")
    def validate_interval(self) -> "AppointmentBase":
        if self.end_datetime <= self.start_datetime:
            raise ValueError("A data final deve ser posterior a data inicial")
        return self


class AppointmentCreate(AppointmentBase):
    user_ids: list[int] = Field(default_factory=list)


class AppointmentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    body: str | None = Field(default=None, min_length=1)
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    url_maps: str | None = None
    location_name: str | None = Field(default=None, max_length=500)
    location_lat: float | None = None
    location_lng: float | None = None

    @model_validator(mode="after")
    def validate_interval(self) -> "AppointmentUpdate":
        if self.start_datetime and self.end_datetime and self.end_datetime <= self.start_datetime:
            raise ValueError("A data final deve ser posterior a data inicial")
        return self


class AppointmentUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    appointment_id: int
    is_confirmed: bool


class AppointmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    start_datetime: datetime
    end_datetime: datetime
    url_maps: str | None
    location_name: str | None
    location_lat: float | None
    location_lng: float | None
    participants: list[AppointmentUserRead] = []


class LinkUserRequest(BaseModel):
    user_id: int
