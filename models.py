from sqlalchemy import Column, Integer, String, ForeignKey, Table, Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d


class Product(Base):
    __tablename__ = "product"
    title = Column(String)
    price = Column(Float)
    img = Column(String)
    id = Column(String, primary_key=True, index=True)
    item_class = Column(String)


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    href = Column(String)


class Price(Base):
    __tablename__ = "price"
    price = Column(Float)
    ts = Column(Float, primary_key=True)
    product_id = Column("proudct_id", String, ForeignKey("product.id"), primary_key=True, index=True)
