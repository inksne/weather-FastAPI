import json
import ssl
import httpx
from typing import NamedTuple
from .config import GISMETEO_URL
from .exceptions import ApiServiceError
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("TOKEN")

Celsius = int
type_weather = str
speed = int

class Weather(NamedTuple):
    temperature: Celsius
    weather_type: type_weather
    wind: speed

class Coordinates(NamedTuple):
    latitude: float
    longitude: float

async def get_weather(coordinates: Coordinates) -> Weather:
    gismeteo_response = await _get_gismeteo_response(
        longitude=coordinates.longitude, latitude=coordinates.latitude)
    weather = _parse_gismeteo_response(gismeteo_response)
    return weather

async def _get_gismeteo_response(latitude: float, longitude: float) -> str:
    ssl._create_default_https_context = ssl._create_unverified_context
    url = GISMETEO_URL.format(
        latitude=latitude, longitude=longitude, TOKEN=TOKEN)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()  
            gismeteo_response = response.text
            return gismeteo_response
    except httpx.RequestError as e:
        print(f"Ошибка запроса: {e}")
        raise ApiServiceError

def _parse_gismeteo_response(gismeteo_response: str) -> Weather:
    try:
        gismeteo_dict = json.loads(gismeteo_response)
    except json.JSONDecodeError:
        print('Невозможно считать файл JSON')
        raise ApiServiceError
    return Weather(
        temperature=_parse_temperature(gismeteo_dict),
        weather_type=_parse_weather_type(gismeteo_dict),
        wind=_parse_wind(gismeteo_dict)
    )

def _parse_temperature(gismeteo_dict: dict) -> Celsius:
    return round(gismeteo_dict["response"]["temperature"]["air"]["C"])

def _parse_weather_type(gismeteo_dict: dict) -> type_weather:
    try:
        return gismeteo_dict["response"]["description"]["full"]
    except KeyError:
        print('Ошибка ключа')
        raise ApiServiceError

def _parse_wind(gismeteo_dict: dict) -> speed:
    return gismeteo_dict["response"]["wind"]["speed"]["m_s"]

