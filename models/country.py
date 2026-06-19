"""
Modelo SQLAlchemy para País
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base


class Country(Base):
    __tablename__ = 'countries'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    export_rules = relationship('ExportRule', back_populates='country', cascade='all, delete-orphan')
    product_files = relationship('ProductFile', back_populates='country', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Country(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
