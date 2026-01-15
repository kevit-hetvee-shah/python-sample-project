from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

# Database file in current directory
DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    website_url = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    landmark = Column(String(255), nullable=True)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    # New fields
    detail_description = Column(Text, nullable=True)
    discount = Column(Float, nullable=True, default=0.0)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    color = Column(String(100), nullable=True)
    extra_images = Column(JSON, nullable=True)  # Stores list of image URLs

    # Relationships
    category = relationship("Category", backref="products")
    company = relationship("Company", backref="products")


class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)

    # Relationships
    user = relationship("User", backref="cart_items")
    product = relationship("Product", backref="cart_items")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
