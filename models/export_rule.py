"""
Modelo SQLAlchemy para Regla de Exportación (Knowledge Base)
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base


class ExportRule(Base):
    __tablename__ = 'export_rules'
    
    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey('countries.id', ondelete='CASCADE'), nullable=False)
    attribute_name = Column(String(100), nullable=False, index=True)
    operator = Column(String(10), nullable=False, index=True)
    expected_value = Column(String(500), nullable=False)
    recommendation = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Índice compuesto
    __table_args__ = (
        Index('idx_country_attribute', 'country_id', 'attribute_name'),
    )
    
    # Relaciones
    country = relationship('Country', back_populates='export_rules')
    validation_results = relationship('ValidationResult', back_populates='rule', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<ExportRule(id={self.id}, country_id={self.country_id}, attribute='{self.attribute_name}', operator='{self.operator}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'country_id': self.country_id,
            'attribute_name': self.attribute_name,
            'operator': self.operator,
            'expected_value': self.expected_value,
            'recommendation': self.recommendation,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
