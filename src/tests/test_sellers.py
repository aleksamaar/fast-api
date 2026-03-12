import pytest
from fastapi import status
from sqlalchemy import select

from src.models.books import Book
from src.models.sellers import Seller

API_V1_URL_PREFIX = "/api/v1/seller"


# Тест на ручку создающую продавца
@pytest.mark.asyncio()
async def test_create_seller(async_client):
    data = {
        "first_name": "Aleksandra",
        "last_name": "Sevostianova",
        "e_mail": "aleksandra@example.com",
        "password": "12345678",
    }

    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    resp_seller_id = result_data.pop("id", None)
    assert resp_seller_id is not None, "Seller id not returned from endpoint"

    # password не должен возвращаться наружу
    assert result_data == {
        "first_name": "Aleksandra",
        "last_name": "Sevostianova",
        "e_mail": "aleksandra@example.com",
    }


# Тест на ручку получения списка продавцов
@pytest.mark.asyncio()
async def test_get_sellers(db_session, async_client):
    seller = Seller(
        first_name="Aleksandra",
        last_name="Sevostianova",
        e_mail="aleksandra_get@example.com",
        password="12345678",
    )
    seller_2 = Seller(
        first_name="Anna",
        last_name="Sidorova",
        e_mail="anna_get@example.com",
        password="87654321",
    )

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["sellers"]) == 2

    # password не должен возвращаться
    assert response.json() == {
        "sellers": [
            {
                "id": seller.id,
                "first_name": "Aleksandra",
                "last_name": "Sevostianova",
                "e_mail": "aleksandra_get@example.com",
            },
            {
                "id": seller_2.id,
                "first_name": "Anna",
                "last_name": "Sidorova",
                "e_mail": "anna_get@example.com",
            },
        ]
    }


# Тест на ручку получения одного продавца вместе с книгами
@pytest.mark.asyncio()
async def test_get_single_seller(db_session, async_client):
    seller = Seller(
        first_name="Aleksandra",
        last_name="Sevostianova",
        e_mail="aleksandra_single@example.com",
        password="12345678",
    )
    db_session.add(seller)
    await db_session.flush()

    book = Book(
        title="Call of Cthulhu",
        author="Howard P. Lovecraft",
        year=2021,
        pages=104,
        seller_id=seller.id,
    )
    book_2 = Book(
        title="1984",
        author="George Orwell",
        year=2024,
        pages=108,
        seller_id=seller.id,
    )

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    # password не должен возвращаться
    assert response.json() == {
        "id": seller.id,
        "first_name": "Aleksandra",
        "last_name": "Sevostianova",
        "e_mail": "aleksandra_single@example.com",
        "books": [
            {
                "id": book.id,
                "title": "Call of Cthulhu",
                "author": "Howard P. Lovecraft",
                "year": 2021,
                "pages": 104,
                "seller_id": seller.id,
            },
            {
                "id": book_2.id,
                "title": "1984",
                "author": "George Orwell",
                "year": 2024,
                "pages": 108,
                "seller_id": seller.id,
            },
        ],
    }


@pytest.mark.asyncio()
async def test_get_single_seller_with_wrong_id(db_session, async_client):
    seller = Seller(
        first_name="Aleksandra",
        last_name="Sevostianova",
        e_mail="aleksandra_wrong_id@example.com",
        password="12345678",
    )
    db_session.add(seller)
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/426548")

    assert response.status_code == status.HTTP_404_NOT_FOUND


# Тест на ручку обновления продавца
@pytest.mark.asyncio()
async def test_update_seller(db_session, async_client):
    seller = Seller(
        first_name="Aleksandra",
        last_name="Sevostianova",
        e_mail="aleksandra_update@example.com",
        password="12345678",
    )
    db_session.add(seller)
    await db_session.flush()

    data = {
        "id": seller.id,
        "first_name": "Anna",
        "last_name": "Sidorova",
        "e_mail": "annasidorova@example.com",
    }

    response = await async_client.put(
        f"{API_V1_URL_PREFIX}/{seller.id}",
        json=data,
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    res = await db_session.get(Seller, seller.id)
    assert res.id == seller.id
    assert res.first_name == "Anna"
    assert res.last_name == "Sidorova"
    assert res.e_mail == "annasidorova@example.com"
    assert res.password == "12345678" 


# Тест на частичное обновление продавца
@pytest.mark.asyncio()
async def test_patch_seller(db_session, async_client):
    seller = Seller(
        first_name="Aleksandra",
        last_name="Sevostianova",
        e_mail="aleksandra_patch@example.com",
        password="12345678",
    )
    db_session.add(seller)
    await db_session.flush()

    data = {
        "first_name": "New Aleksandra",
    }

    response = await async_client.patch(
        f"{API_V1_URL_PREFIX}/{seller.id}",
        json=data,
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    res = await db_session.get(Seller, seller.id)
    assert res.first_name == "New Aleksandra"
    assert res.last_name == "Sevostianova"
    assert res.e_mail == "aleksandra_patch@example.com"
    assert res.password == "12345678"


# Тест на удаление продавца
@pytest.mark.asyncio()
async def test_delete_seller(db_session, async_client):
    seller = Seller(
        first_name="Aleksandra",
        last_name="Sevostianova",
        e_mail="aleksandra_delete@example.com",
        password="12345678",
    )
    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.flush()
    all_sellers = await db_session.execute(select(Seller))
    res = all_sellers.scalars().all()

    assert len(res) == 0


@pytest.mark.asyncio()
async def test_delete_seller_with_invalid_seller_id(db_session, async_client):
    seller = Seller(
        first_name="Aleksandra",
        last_name="Sevostianova",
        e_mail="aleksandra_invalid_delete@example.com",
        password="12345678",
    )
    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller.id + 1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


# Тест на каскадное удаление книг продавца
@pytest.mark.asyncio()
async def test_delete_seller_with_books_cascade(db_session, async_client):
    seller = Seller(
        first_name="Aleksandra",
        last_name="Sevostianova",
        e_mail="aleksandra_cascade@example.com",
        password="12345678",
    )
    db_session.add(seller)
    await db_session.flush()

    book = Book(
        title="Call of Cthulhu",
        author="Howard P. Lovecraft",
        year=2024,
        pages=300,
        seller_id=seller.id,
    )
    book_2 = Book(
        title="1984",
        author="George Orwell",
        year=2025,
        pages=350,
        seller_id=seller.id,
    )

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.flush()

    all_sellers = await db_session.execute(select(Seller))
    sellers_res = all_sellers.scalars().all()
    assert len(sellers_res) == 0

    all_books = await db_session.execute(select(Book))
    books_res = all_books.scalars().all()
    assert len(books_res) == 0