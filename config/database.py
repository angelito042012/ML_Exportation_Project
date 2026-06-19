"""
Configuración de conexión a base de datos MySQL
Utiliza SQLAlchemy para abstracción de datos
"""

import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de conexión
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '123456789')
DB_NAME = os.getenv('DB_NAME', 'export_validation')

# URL de conexión
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Crear motor de base de datos
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verificar conexión antes de usar
    echo=False  # Cambiar a True para debug SQL
)

# Factory para crear sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_session() -> Session:
    """
    Obtener una nueva sesión de base de datos.
    Usar con context manager:
    
    with get_session() as session:
        # Usar session aquí
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializar la base de datos.
    Crear todas las tablas definidas en los modelos.
    """
    from models.base import Base
    Base.metadata.create_all(bind=engine)
    print("✓ Base de datos inicializada")


def health_check():
    """
    Verificar conexión a la base de datos.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("✓ Conexión a base de datos OK")
        return True
    except Exception as e:
        print(f"✗ Error de conexión: {e}")
        return False
