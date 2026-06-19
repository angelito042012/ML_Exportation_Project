"""
Repositorio Base - Clase base con operaciones CRUD comunes
"""

from typing import TypeVar, Generic, List, Optional, Type
from sqlalchemy.orm import Session
from sqlalchemy import desc

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Repositorio genérico con operaciones CRUD comunes.
    Hereda de esta clase para crear repositorios específicos.
    """
    
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model
    
    def create(self, obj_in: dict) -> T:
        """Crear nuevo registro"""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Obtener registro por ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Obtener todos los registros con paginación"""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def update(self, id: int, obj_in: dict) -> Optional[T]:
        """Actualizar registro"""
        db_obj = self.get_by_id(id)
        if db_obj:
            for key, value in obj_in.items():
                setattr(db_obj, key, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> Optional[T]:
        """Eliminar registro"""
        db_obj = self.get_by_id(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
        return db_obj
    
    def count(self) -> int:
        """Contar total de registros"""
        return self.db.query(self.model).count()
    
    def exists(self, id: int) -> bool:
        """Verificar si existe un registro"""
        return self.db.query(self.model).filter(self.model.id == id).first() is not None
