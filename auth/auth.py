from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from auth.helpers import create_access_token, create_refresh_token
from auth.validation import (
    get_current_access_token_payload,
    get_current_auth_user_for_refresh,
    get_current_auth_user,
    validate_auth_user_db
)
from database.models import User

from pydantic import BaseModel
from datetime import timedelta

http_bearer = HTTPBearer(auto_error=False)

class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


router = APIRouter(prefix='/jwt', tags=["JWT"], dependencies=[Depends(http_bearer)])


@router.post('/login/', response_model=TokenInfo)
async def auth_user_issue_jwt(response: Response, user: User = Depends(validate_auth_user_db)):
    '''вход: создание access и refresh токена и добавление их в куки'''
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    response.set_cookie(
        key="access_token",
          value=access_token,
            httponly=False,
              secure=False,
                samesite="Lax",
                 max_age=int(timedelta(minutes=5).total_seconds()))
    
    response.set_cookie(
        key="refresh_token",
          value=refresh_token,
            httponly=False,
              secure=False,
                samesite="Lax",
                  max_age=int(timedelta(days=30).total_seconds()))
    
    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh/")
async def refresh_jwt(current_user: User = Depends(get_current_auth_user_for_refresh)):
    '''обновление access токена с помощью refresh и обновление его в куки'''
    new_access_token = create_access_token(current_user)
    response = JSONResponse(content={"access_token": new_access_token})
    response.set_cookie(
        key="access_token",
          value=new_access_token,
            httponly=False,  
              secure=False,    
                samesite="Lax",  
                  max_age=int(timedelta(minutes=1).total_seconds())) 
    
    return response


@router.get('/users/me/')
async def auth_user_check_self_info(
    payload: dict = Depends(get_current_access_token_payload), 
    user: User = Depends(get_current_auth_user),
):
    '''получение своего пользователя (для отладки)'''
    iat = payload.get("iat")
    return {
        "username": user.username,
        "email": user.email,
        "logged_in_at": iat,
    }

@router.post('/logout')
async def logout(response: Response):
    '''удаление токена из куки и перенаправление на главную страницу'''
    
    response.delete_cookie(key="access_token", httponly=False, secure=False, samesite="Lax")
    response.delete_cookie(key="refresh_token", httponly=False, secure=False, samesite="Lax")

    return {'detail': 'Успешный выход'}