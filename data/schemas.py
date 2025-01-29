from typing import Self, Optional

from fastapi import HTTPException
from pydantic import BaseModel, model_validator

from billz_config import ACCESS_URLS
from config import settings


class BillzRequestSchema(BaseModel):
    path: str | None = None

    @model_validator(mode='after')
    @classmethod
    def model_validate(cls, data) -> Self:
        if data.path not in ACCESS_URLS and not settings.DEBUG:
            raise HTTPException(404, "Not Found Billz Paths")

        return data

class UserPhoneValidateSchema(BaseModel):
    phone_number: str
    code: Optional[str] = None
    hash_data: str

class BaseUserSchema(BaseModel):
    full_name: str
    phone_number: str
    is_wholesale_user: Optional[bool] = False
    discounted_percentage: Optional[float] = None

    class Config:
        from_attributes = True

    @model_validator(mode='after')
    @classmethod
    def validate_phone(cls, data) -> Self:
        if len(data.phone_number) == 12:
            if data.phone_number.startswith('998'):
                return data
        elif len(data.phone_number) == 11:
            if data.phone_number.startswith('93'):
                return data
        raise HTTPException(404, "Wrong Phone Number")



class BearerTokenSchema(BaseModel):
    token: str
    token_type: str