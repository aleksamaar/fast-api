from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

from .books import ReturnedBook

__all__ = [
    "PatchSeller",
    "IncomingSeller",
    "ReturnedSeller",
    "ReturnedSellerWithBooks",
    "ReturnedAllSellers",
]


# Базовый класс "Sellers", содержащий поля, которые есть во всех классах-наследниках.
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: str


# Класс для обработки входных данных для частичного обновления данных о книге
class PatchSeller(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    e_mail: int | None = None

# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingSeller(BaseSeller):
    password: str

class ReturnedSeller(BaseSeller):  # {"id": 1, "title": "Clean Code", ....}
    id: int

class ReturnedSellerWithBooks(ReturnedSeller):
    books: list[ReturnedBook]

# Класс для возврата массива объектов "Seller"
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
