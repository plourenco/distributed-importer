from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = "events"

    id = sa.Column(sa.Integer, primary_key=True)
    start_dt = sa.Column(sa.DateTime, default=datetime.now, nullable=False)
    end_dt = sa.Column(sa.DateTime)
    count = sa.Column(sa.Integer)
