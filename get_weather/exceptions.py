class CantGetCoordinates(Exception):
    '''Невозможно получить координаты'''

class ApiServiceError(Exception):
    '''Программа не может получить текущую погоду через внешний сервис API'''