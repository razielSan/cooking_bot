from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from sqlalchemy import (
    BigInteger,
    DECIMAL,
    ForeignKey,
    String,
    Integer,
    UniqueConstraint,
)

from database import Base
from database.db_helper import db_helper


class Users(Base):
    """База пользователя"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    telegram: Mapped[int] = mapped_column(BigInteger, unique=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=True)

    carts: Mapped["Carts"] = relationship(back_populates="user_cart")

    def __str__(self):
        return self.name


class Carts(Base):
    """Временная корзина покупателя, используется до кассы"""

    __tablename__ = "carts"
    id: Mapped[int] = mapped_column(primary_key=True)
    total_price: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2), default=0)
    total_products: Mapped[int] = mapped_column(default=0)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user_cart: Mapped["Users"] = relationship(back_populates="carts")

    finally_id: Mapped["Finally_carts"] = relationship(back_populates="user_cart")
    # finally_id: Mapped[int] = relationship("FInally_carts", back_populates="user_cart")

    def __str__(self):
        return str(self.id)


class Finally_carts(Base):
    """Окончательная корзина пользователя, возле кассы"""

    __tablename__ = "finally_carts"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(50))
    final_price: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2))
    quantity: Mapped[int]

    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"))
    user_cart: Mapped["Carts"] = relationship(back_populates="finally_id")

    __table_args__ = (
        UniqueConstraint("cart_id", "product_name"),
    )  # в одном cart_id может быть только один продукт


class Categories(Base):
    """Категории товаров"""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_name: Mapped[str] = mapped_column(String(50), unique=True)

    products: Mapped["Products"] = relationship(back_populates="product_category")

    def read_model(self):
        return {
            "id": self.id,
            "category_name": self.category_name,
        }

    def __str__(self):
        return self.category_name


class Products(Base):
    """Продукты"""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(50), unique=True)
    price: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2))
    description: Mapped[str]
    image: Mapped[str] = mapped_column(String(100))

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    product_category: Mapped["Categories"] = relationship(back_populates="products")


def main():
    caregories = ("Лаваши", "Донары", "Хот-Доги", "Десерты", "Соусы")
    products = (
        (
            1,
            "Мини Лаваш",
            20000,
            "Мясо, тесто, помидоры",
            "media/lavash/lavash_1.jpg",
        ),
        (
            1,
            "Мини Говяжий",
            22000,
            "Мясо, тесто, помидоры",
            "media/lavash/lavash_2.jpg",
        ),
        (
            1,
            "Мини с сыром",
            24000,
            "Мясо, тесто, помидоры",
            "media/lavash/lavash_3.jpg",
        ),
        (
            2,
            "Дамбургер",
            14000,
            "Мясо, тесто, помидоры",
            "media/donar/donar_1.jpg",
        ),
        (
            2,
            "Чисбургер",
            64000,
            "Мясо, тесто, помидоры",
            "media/donar/donar_2.jpg",
        ),
        (
            2,
            "Бургер",
            14060,
            "Мясо, тесто, помидоры",
            "media/donar/donar_3.jpg",
        ),
    )

    with db_helper.get_session() as session:
        Base.metadata.create_all()
        for category in caregories:
            print(category)
            cat = Categories(category_name=category)
            session.add(cat)
            session.commit()

        for product in products:
            pr = Products(
                category_id=product[0],
                product_name=product[1],
                price=product[2],
                description=product[3],
                image=product[4],
            )

            session.add(pr)
            session.commit()
