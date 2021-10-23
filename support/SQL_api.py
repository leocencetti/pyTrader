import numpy as np
import pandas as pd
import sqlalchemy as db
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta
from enum import Enum

Base: DeclarativeMeta = declarative_base()


class TransactionType(db.Enum):
    buy = 1
    sell = 2


class Exchange(Base):
    __tablename__ = "exchange"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    currency = db.Column(db.String)
    code = db.Column(db.String, nullable=False, unique=True)
    opening_time = db.Column("opening_time", db.Time)
    closing_time = db.Column("closing_time", db.Time)
    platform_id = db.Column("platform_id", db.ForeignKey("platform.id"))
    platform = db.orm.relationship("Platform")


class Platform(Base):
    __tablename__ = "platform"

    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String)


class Security(Base):
    __tablename__ = "security"

    id = db.Column("id", db.Integer, primary_key=True)
    ticker = db.Column("ticker", db.String, nullable=False, unique=True)
    name = db.Column("name", db.String, nullable=False)
    company_id = db.Column("company_id", db.ForeignKey("company.id"))
    exchange_id = db.Column("exchange_id", db.ForeignKey("exchange.id"))
    company = db.orm.relationship("Company")
    exchange = db.orm.relationship("Exchange")


class Company(Base):
    __tablename__ = "company"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    industry = db.Column(db.String)
    sector = db.Column(db.String)
    hq_location = db.Column(db.String)
    security_id = db.Column(db.Integer, db.ForeignKey("security.id"))
    security = db.orm.relationship("Security")


class SecurityPrice(Base):
    __tablename__ = "security_price"

    id = db.Column("id", db.Integer, primary_key=True)
    date = db.Column("date", db.DateTime, nullable=False)
    open = db.Column("open", db.Float)
    high = db.Column("high", db.Float)
    low = db.Column("low", db.Float)
    close = db.Column("close", db.Float)
    volume = db.Column("volume", db.Integer)
    adj_close = db.Column("adj_close", db.Float)
    security_id = db.Column("security_id", db.ForeignKey("security.id"))
    security = db.orm.relationship("Security")


class Portfolio(Base):
    __tablename__ = "portfolio"

    id = db.Column("id", db.Integer, primary_key=True)
    timestamp = db.Column("timestamp", db.DateTime)
    security_id = db.Column("security_id", db.ForeignKey("security.id"))
    name = db.Column("name", db.String)
    quantity = db.Column("quantity", db.Float)
    investment = db.Column("investment", db.Float)
    value = db.Column("value", db.Float)
    security = db.orm.relationship("Security")


class Transaction(Base):
    __tablename__ = "transaction"

    id = db.Column("id", db.Integer, primary_key=True)
    timestamp = db.Column("timestamp", db.DateTime, nullable=False)
    price = db.Column("price", db.Float)
    quantity = db.Column("quantity", db.Float)
    action = db.Column("action", TransactionType)
    security_id = db.Column("security_id", db.ForeignKey("security.id"))
    security = db.orm.relationship("Security")


class Database:
    def __init__(self, database: str) -> None:
        """
        Create a database connection to the SQLite database
            specified by database
        :param database: database file
        """

        self.engine = db.create_engine(f"sqlite:///{database}")
        self.connection = self.engine.connect()
        self._metadata = db.MetaData()
        Base.metadata.create_all(self.engine)

    def insert(self, df: pd.DataFrame, table: str, mode: str = "update"):
        if not self._has_table(table):
            return

        if mode == "replace":
            # insert (df)
            df.to_sql(table, self.engine, if_exists="replace", index=False)
            return

        content = pd.read_sql_table(table, self.engine)
        if content.empty:
            df.to_sql(table, self.engine, if_exists="append", index=False)
            return

        # replace None with numpy.nan
        content.replace([None], np.nan, inplace=True)
        if mode == "append":
            # insert only (df - content)
            content = df[(df != content)].dropna(how="all")
            content.to_sql(table, self.engine, if_exists="append", index=False)

        if mode == "update":
            # insert (df U content)
            content = pd.merge(content, df, "outer")
            content.to_sql(table, self.engine, if_exists="replace", index=False)

    def _has_table(self, table: str):
        insp = db.inspect(self.engine)
        return insp.has_table(table)
