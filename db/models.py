from sqlalchemy import Column, String, Float, DateTime, Integer, Text, Date
import datetime
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

class DBAlertaMercado(Base):
    """Almacena alertas de anomalías de mercado generadas por la IA."""
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    tipo_alerta = Column(String, index=True)
    titulo = Column(String(80))
    mensaje = Column(Text)
    nivel_severidad = Column(String)

class DBResumenDiario(Base):
    """Almacena el resumen pedagógico diario del mercado."""
    __tablename__ = "resumenes_diarios"

    id = Column(Integer, primary_key=True, index=True)
    fecha_resumen = Column(Date, unique=True, index=True)
    titulo_jornada = Column(String)
    resumen_oro = Column(Text)
    resumen_petroleo = Column(Text)
    leccion_concepto = Column(String)
    leccion_explicacion = Column(Text)
