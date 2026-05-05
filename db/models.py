from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class MarketTick(Base):
    """
    Modelo optimizado para TimescaleDB.
    Almacena cada tick de mercado recibido a través de WebSockets.
    """
    __tablename__ = "market_ticks"

    # En TimescaleDB, la columna de partición (timestamp) debe ser parte de cualquier Primary Key.
    timestamp = Column(DateTime(timezone=True), primary_key=True, index=True)
    symbol = Column(String, primary_key=True, index=True)
    price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
