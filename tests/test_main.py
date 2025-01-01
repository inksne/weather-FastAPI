from typing import AsyncGenerator
from fastapi.testclient import TestClient
import pytest

from database.models import User
from database.database import async_session_maker
from .test_config import MODE
from main import app

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy.future import select


client = TestClient(app)


def test_read_main_page():
    response = client.get('/')
    assert response.status_code == 200


def test_read_about_us_page():
    response = client.get('/about_us')
    assert response.status_code == 200


def test_read_register_page():
    response = client.get('/register')
    assert response.status_code == 200


def test_read_login_page():
    response = client.get('/jwt/login')
    assert response.status_code == 200


@pytest.fixture
async def setup_test_db(scope="function") -> AsyncGenerator[AsyncSession, None]:
    '''фикстура для создания базы данных и предоставления сессии для тестов'''
    assert MODE == 'TEST'
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))
            await session.commit()


@pytest.mark.skip(reason='для бд')
@pytest.mark.asyncio
async def test_delete_user(setup_test_db):
    '''тест для проверки удаления пользователя в бд'''
    assert MODE == 'TEST'
    async for session in setup_test_db:  
        new_user = User(username="testuser", email="testuser@example.com", password="password")
        session.add(new_user)
        await session.commit()

        result = await session.execute(select(User))
        user = result.scalars().first()
        await session.delete(user)
        await session.commit()

        result = await session.execute(select(User))
        users = result.scalars().all()

        assert len(users) == 0