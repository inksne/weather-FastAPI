import pytest
from typing import AsyncGenerator
from sqlalchemy.future import select
from database.models import User
from database.database import async_session_maker
from .test_config import MODE
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text


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