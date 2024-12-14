from fastapi import FastAPI, HTTPException, APIRouter, Form, Depends
from starlette import status

from typing import NamedTuple, Optional
from pydantic import BaseModel
from geopy.geocoders import Nominatim
import logging
import asyncio

from weather.config import USE_ROUNDED_COORDS
from weather.exceptions import CantGetCoordinates, ApiServiceError
from weather.weather_api_service import get_weather
from weather.weather_formatter import format_weather
from templates.router import router as base_router
from auth.auth import router as jwt_router
from auth.utils import hash_password
from database.database import AsyncSession, get_async_session
from database.models import User

app = FastAPI(title='weather')


logger = logging.getLogger(__name__)

class UserResponse(BaseModel):
    id: int
    email: Optional[str] = None
    username: str
    

@app.post('/register', response_model=UserResponse)
async def register(
    username: str = Form(...),
    password: str = Form(...),
    email: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_async_session)
):
    if email in [None, '', 'null']:
        email = None
    hashed_password = hash_password(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password, email=email)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


router = APIRouter()

app.include_router(base_router)

app.include_router(jwt_router)