from .weather_api_service import Weather

def format_weather(weather: Weather) -> str:
    '''Форматирует данные о погоде в строку'''
    return (f"Температура {weather.temperature}°C, "
            f"{weather.weather_type}, скорость ветра {weather.wind} м/с")