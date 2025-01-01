from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette import status

from get_weather.config import USE_ROUNDED_COORDS
from get_weather.exceptions import CantGetCoordinates, ApiServiceError
from get_weather.weather_api_service import get_weather
from get_weather.weather_formatter import format_weather

from typing import NamedTuple
from geopy.geocoders import Nominatim
from redis import Redis
import logging
import time
import asyncio


router = APIRouter()

templates = Jinja2Templates(directory='templates')

r = Redis(host='127.0.0.1', port=6379, db=0)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Coordinates(NamedTuple):
    latitude: float
    longitude: float


async def get_coords(location: str):
    try:
        loc = Nominatim(user_agent="GetLoc")
        getLoc = await asyncio.to_thread(loc.geocode, location)
        if getLoc is None:
            raise CantGetCoordinates("Локация не найдена.")
        
        latitude = getLoc.latitude
        longitude = getLoc.longitude
        if USE_ROUNDED_COORDS:
            latitude, longitude = map(lambda c: round(c, 1), [latitude, longitude])
        return Coordinates(latitude=latitude, longitude=longitude)
    except CantGetCoordinates:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Не удалось получить координаты.')



@router.get('/', response_class=HTMLResponse)
async def get_weather_page(request: Request):
    return templates.TemplateResponse(request, 'index.html', {'title': 'Главная'})

@router.get('/get_weather', response_class=HTMLResponse)
async def get_weather_end(request: Request, location: str):
    try:
        weather_from_redis = r.get(f'weather:{location}')
        if weather_from_redis:
            formatted_weather = weather_from_redis.decode('utf-8')
            return templates.TemplateResponse(request, 'index.html', {
                'location': location,
                'weather': formatted_weather,
                'title': 'Главная'
            })
        
        coordinates = await get_coords(location)
        r.set(f'location:{location}', location)  
        weather = await get_weather(coordinates)
        formatted_weather = format_weather(weather)
        r.set(f'weather:{location}', formatted_weather)  
        
        return templates.TemplateResponse(request, 'index.html', {
            'location': location,
            'weather': formatted_weather,
            'title': 'Главная'
        })
    except CantGetCoordinates as e:
        logger.error(str(e))
        return templates.TemplateResponse(request, 'index.html', {
            'location': location,
            'error': 'Невозможно получить координаты.',
            'title': 'Главная'
        })
    except ApiServiceError as e:
        logger.error(str(e))
        return templates.TemplateResponse(request, 'index.html', {
            'location': location,
            'error': 'Ошибка сервиса погоды.',
            'title': 'Главная'
        })
    except Exception as e:
        logger.error(str(e))
        return templates.TemplateResponse(request, 'index.html', {
            'location': location,
            'error': 'Произошла неизвестная ошибка.',
            'title': 'Главная'
        })


@router.get('/authenticated/get_weather', response_class=HTMLResponse)
async def get_auth_weather_end(request: Request, location: str):
    try:
        weather_from_redis = r.get(f'weather:{location}')
        if weather_from_redis:
            formatted_weather = weather_from_redis.decode('utf-8')
        else:
            coordinates = await get_coords(location)
            r.set(f'location:{location}', location)  
            weather = await get_weather(coordinates)
            formatted_weather = format_weather(weather)
            r.set(f'weather:{location}', formatted_weather)  
            r.expire(f'weather:{location}', 1800)  #TTL на 30 минут
            r.expire(f'location:{location}', 1800)  

        current_time = int(time.time())  
        request_key = f"weather_request:{current_time}:{location}"
        r.set(request_key, location)  
        r.expire(request_key, 1800)  

        return templates.TemplateResponse(request, 'auth_index.html', {
            'location': location,
            'weather': formatted_weather,
            'recent_locations': [],
            'title': 'Главная'
        })
    
    except CantGetCoordinates as e:
        logger.error(str(e))
        return templates.TemplateResponse(request, 'auth_index.html', {
            'location': location,
            'error': str(e),
            'recent_locations': [],
            'title': 'Главная'
        })
    except ApiServiceError as e:
        logger.error(str(e))
        return templates.TemplateResponse(request, 'auth_index.html', {
            'location': location,
            'error': 'Ошибка сервиса погоды.',
            'recent_locations': [],
            'title': 'Главная'  
        })
    except Exception as e:
        logger.error(str(e))
        return templates.TemplateResponse(request, 'auth_index.html', {
            'location': location,
            'error': 'Произошла неизвестная ошибка.',
            'recent_locations': [],
            'title': 'Главная'  
        })



@router.get('/about_us', response_class=HTMLResponse)
async def get_about_us_page(request: Request):
    return templates.TemplateResponse(request, 'about_us.html', {'title': 'О нас'})


@router.get('/jwt/login/', response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse(request, 'login.html', {'title': 'Логин'})


@router.get('/register', response_class=HTMLResponse)
async def get_register_page(request: Request):
    return templates.TemplateResponse(request, 'register.html', {'title': 'Регистрация'})


@router.get('/authenticated/', response_class=HTMLResponse)
async def get_authenticated_page(request: Request):
    try:
        cursor, recent_requests = r.scan(match="weather_request:*", count=100)

        recent_locations = []
        seen = set()

        for req in recent_requests:
            decoded_loc = r.get(req).decode('utf-8')  
            if decoded_loc not in seen:
                seen.add(decoded_loc)
                recent_locations.append(decoded_loc)

        weather_data = []
        for location in recent_locations:
            weather_from_redis = r.get(f'weather:{location}')
            if weather_from_redis:
                formatted_weather = weather_from_redis.decode('utf-8')
            else:
                coordinates = await get_coords(location)
                weather = await get_weather(coordinates)
                formatted_weather = format_weather(weather)
                r.set(f'weather:{location}', formatted_weather)
                r.expire(f'weather:{location}', 1800)  
            weather_data.append({'location': location, 'weather': formatted_weather})

        return templates.TemplateResponse(request, 'auth_index.html', {
            'recent_locations': weather_data ,
            'title': 'Главная'
        })
    except Exception as e:
        logger.error(str(e))
        return templates.TemplateResponse(request, 'auth_index.html', {
            'error': 'Произошла ошибка при получении данных.',
            'title': 'Главная'
        })