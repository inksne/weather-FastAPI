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


# class Coordinates(NamedTuple):
#     latitude: float
#     longitude: float

class UserResponse(BaseModel):
    id: int
    email: Optional[str] = None
    username: str


# async def get_coords(location: str):
#     try:
#         loc = Nominatim(user_agent="GetLoc")
#         getLoc = await asyncio.to_thread(loc.geocode, location)
#         if getLoc is None:
#             raise CantGetCoordinates("Локация не найдена.")
        
#         latitude = getLoc.latitude
#         longitude = getLoc.longitude
#         if USE_ROUNDED_COORDS:
#             latitude, longitude = map(lambda c: round(c, 1), [latitude, longitude])
#         return Coordinates(latitude=latitude, longitude=longitude)
#     except CantGetCoordinates:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Не удалось получить координаты.')

# @app.get('/api/v1/get_weather')
# async def get_weather_end(location: str):
#     try:
#         coordinates = await get_coords(location)
#         logger.debug(f'Координаты: {coordinates}')
        
#         weather = await get_weather(coordinates)
#         return {'location': location, 'weather': format_weather(weather)}
#     except CantGetCoordinates as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
#     except ApiServiceError as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
#     except AttributeError as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

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