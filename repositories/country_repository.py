"""
Repositorio de Países
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from models import Country
from repositories.base_repository import BaseRepository


class CountryRepository(BaseRepository[Country]):
    """Repositorio para operaciones con Países"""
    
    def __init__(self, db: Session):
        super().__init__(db, Country)
    
    def get_by_name(self, name: str) -> Optional[Country]:
        """Obtener país por nombre"""
        return self.db.query(Country).filter(
            Country.name.ilike(f"%{name}%")
        ).first()
    
    def get_all_ordered(self, skip: int = 0, limit: int = 100) -> List[Country]:
        """Obtener todos los países ordenados alfabéticamente"""
        return self.db.query(Country).order_by(Country.name).offset(skip).limit(limit).all()
    
    def search(self, query: str) -> List[Country]:
        """Buscar países por nombre"""
        return self.db.query(Country).filter(
            Country.name.ilike(f"%{query}%")
        ).all()
