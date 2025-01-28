import enum
from typing import Type, Optional, Any, Iterable

from passlib.context import CryptContext
from tortoise import Model, fields, BaseDBAsyncClient
from tortoise.models import MODEL

from config import pwd_context


class OrderStatusChoices(enum.IntEnum):
    PENDING = 0
    CANCELLED = 1
    COMPLETED = 2





class User(Model):
    id = fields.IntField(pk=True)
    billz_id = fields.CharField(null=True, unique=True, max_length=64)
    full_name = fields.CharField(max_length=64)
    phone_number = fields.CharField(max_length=15)
    is_wholesale_user = fields.BooleanField(default=False)
    discount_percentage = fields.FloatField(default=0.0)
    password_hash = fields.TextField()

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)

    async def create(
            cls: Type[MODEL], using_db: Optional[BaseDBAsyncClient] = None, **kwargs: Any
    ) -> MODEL:
        kwargs['password_hash'] = pwd_context.hash(kwargs['password_hash'])
        return await super().create(using_db, **kwargs)

    async def save(
            self,
            using_db: Optional[BaseDBAsyncClient] = None,
            update_fields: Optional[Iterable[str]] = None,
            force_create: bool = False,
            force_update: bool = False,
    ) -> None:
        self.password_hash = pwd_context.hash(self.password_hash)
        return await super().save(using_db, update_fields, force_create, force_update)


class Order(Model):
    user = fields.ForeignKeyField("models.User", related_name="orders")
    status = fields.IntEnumField(OrderStatusChoices, 'Order status', default=OrderStatusChoices.PENDING)
    data = fields.TextField()
