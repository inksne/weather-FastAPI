from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette import status

from weather.config import USE_ROUNDED_COORDS
from weather.exceptions import CantGetCoordinates, ApiServiceError
from weather.weather_api_service import get_weather
from weather.weather_formatter import format_weather

from typing import NamedTuple
from geopy.geocoders import Nominatim
import asyncio

router = APIRouter()

templates = Jinja2Templates(directory='templates')


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
    return templates.TemplateResponse('index.html', {'request': request, 'title': 'Главная'})

@router.get('/get_weather', response_class=HTMLResponse)
async def get_weather_end(request: Request, location: str):
    try:
        coordinates = await get_coords(location)
        weather = await get_weather(coordinates)
        formatted_weather = format_weather(weather)
        return templates.TemplateResponse('index.html', {
            'request': request,
            'location': location,
            'weather': formatted_weather
        })
    except CantGetCoordinates as e:
        return templates.TemplateResponse('index.html', {
            'request': request,
            'location': location,
            'error': str(e)
        })
    except ApiServiceError as e:
        return templates.TemplateResponse('index.html', {
            'request': request,
            'location': location,
            'error': 'Ошибка сервиса погоды.'
        })
    except Exception as e:
        return templates.TemplateResponse('index.html', {
            'request': request,
            'location': location,
            'error': 'Произошла неизвестная ошибка.'
        })
    

@router.get('/authenticated/get_weather', response_class=HTMLResponse)
async def get_weather_end(request: Request, location: str):
    try:
        coordinates = await get_coords(location)
        weather = await get_weather(coordinates)
        formatted_weather = format_weather(weather)
        return templates.TemplateResponse('auth_index.html', {
            'request': request,
            'location': location,
            'weather': formatted_weather
        })
    except CantGetCoordinates as e:
        return templates.TemplateResponse('auth_index.html', {
            'request': request,
            'location': location,
            'error': str(e)
        })
    except ApiServiceError as e:
        return templates.TemplateResponse('auth_index.html', {
            'request': request,
            'location': location,
            'error': 'Ошибка сервиса погоды.'
        })
    except Exception as e:
        return templates.TemplateResponse('auth_index.html', {
            'request': request,
            'location': location,
            'error': 'Произошла неизвестная ошибка.'
        })
    

@router.get('/about_us', response_class=HTMLResponse)
async def get_about_us_page(request: Request):
    return templates.TemplateResponse('about_us.html', {'request': request, 'title': 'О нас'})


@router.get('/jwt/login/', response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse('login.html', {'request': request, 'title': 'Логин'})


@router.get('/register', response_class=HTMLResponse)
async def get_register_page(request: Request):
    return templates.TemplateResponse('register.html', {'request': request, 'title': 'Регистрация'})


@router.get('/authenticated/', response_class=HTMLResponse)
async def get_authenticated_page(request: Request):
    return templates.TemplateResponse('auth_index.html', {'request': request, 'title': 'Главная'})