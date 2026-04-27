from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import List, Optional, Literal
from datetime import date


class AddressCreateSchema(BaseModel):
    formatted: Optional[str] = None
    streetAddress: Optional[str] = None
    locality: Optional[str] = None
    region: Optional[str] = None
    postalCode: Optional[str] = None
    country: Optional[str] = None


class ProfileCreateSchema(BaseModel):
    familyName: Optional[str] = None
    givenName: Optional[str] = None
    middleName: Optional[str] = None
    nickname: Optional[str] = None
    preferredUsername: Optional[str] = None
    profile: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None
    gender: Optional[Literal["male", "female", "other"]] = None
    birthdate: Optional[date] = None
    zoneinfo: Optional[str] = None
    locale: Optional[str] = None
    address: Optional[AddressCreateSchema] = None


class CustomDataCreateSchema(BaseModel):
    user_id_odoo: Optional[int] = None
    partner_id_odoo: Optional[int] = None
    user_id_gontv: Optional[str] = None
    user_id_service: Optional[List[int]] = None

class UserLogtoCreateSchema(BaseModel):
    username: str
    password: str
    primaryEmail: Optional[EmailStr] = None
    primaryPhone: Optional[str] = None
    name: Optional[str] = None
    avatar: Optional[HttpUrl] = None
    passwordAlgorithm: Optional[str] = None
    customData: Optional[CustomDataCreateSchema] = None
    profile: Optional[ProfileCreateSchema] = None


class UserLogtoUpdateSchema(BaseModel):
    username: Optional[str] = None
    primaryEmail: Optional[EmailStr] = None
    primaryPhone: Optional[str] = None
    name: Optional[str] = None
    avatar: Optional[HttpUrl] = None
    passwordAlgorithm: Optional[str] = None
    customData: Optional[CustomDataCreateSchema] = None
    profile: Optional[ProfileCreateSchema] = None


class UserLogtoSchema(BaseModel):
    id: str
    username: str
    primaryEmail: Optional[EmailStr] = None
    primaryPhone: Optional[str] = None
    name: Optional[str] = None
    avatar: Optional[HttpUrl] = None
    customData: Optional[CustomDataCreateSchema] = None
    profile: Optional[ProfileCreateSchema] = None
