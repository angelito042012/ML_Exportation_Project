"""
Modelo SQLAlchemy para Resultados de Validación (Detalles)
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base


class ValidationResult(Base):
    __tablename__ = 'validation_results'
    
    id = Column(Integer, primary_key=True, index=True)
    product_file_id = Column(Integer, ForeignKey('product_files.id', ondelete='CASCADE'), nullable=False)
    export_rule_id = Column(Integer, ForeignKey('export_rules.id', ondelete='CASCADE'), nullable=False)
    attribute_name = Column(String(100), nullable=False, index=True)
    expected_value = Column(String(500), nullable=False)
    found_value = Column(String(500))
    operator = Column(String(10), nullable=False)
    is_valid = Column(Boolean, default=False, index=True)
    suggestion = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Índices compuestos
    __table_args__ = (
        Index('idx_product_file', 'product_file_id'),
        Index('idx_product_attribute', 'product_file_id', 'attribute_name'),
    )
    
    # Relaciones
    product_file = relationship('ProductFile', back_populates='validation_results')
    rule = relationship('ExportRule', back_populates='validation_results')
    
    def __repr__(self):
        return f"<ValidationResult(id={self.id}, product_file_id={self.product_file_id}, attribute='{self.attribute_name}', valid={self.is_valid})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_file_id': self.product_file_id,
            'export_rule_id': self.export_rule_id,
            'attribute_name': self.attribute_name,
            'expected_value': self.expected_value,
            'found_value': self.found_value,
            'operator': self.operator,
            'is_valid': self.is_valid,
            'suggestion': self.suggestion,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
