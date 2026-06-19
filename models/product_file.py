"""
Modelo SQLAlchemy para Archivo de Producto (Historial de Evaluaciones)
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Numeric, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base
import enum as py_enum


class ComplianceStatus(py_enum.Enum):
    """Estados posibles de cumplimiento"""
    COMPLIES = "Cumple"  # 90-100%
    PARTIALLY_COMPLIES = "Cumple parcialmente"  # 60-89%
    NOT_COMPLIES = "No cumple"  # 0-59%


class ProductFile(Base):
    __tablename__ = 'product_files'
    
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    country_id = Column(Integer, ForeignKey('countries.id', ondelete='CASCADE'), nullable=False)
    extracted_attributes = Column(JSON)  # Almacenar atributos extraídos como JSON
    compliance_percentage = Column(Numeric(5, 2))  # Porcentaje de cumplimiento
    final_status = Column(
        Enum(ComplianceStatus),
        default=None,
        nullable=True
    )
    upload_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Índices compuestos
    __table_args__ = (
        Index('idx_country_date', 'country_id', 'upload_date'),
        Index('idx_status', 'final_status'),
    )
    
    # Relaciones
    country = relationship('Country', back_populates='product_files')
    validation_results = relationship('ValidationResult', back_populates='product_file', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<ProductFile(id={self.id}, file='{self.file_name}', status='{self.final_status}', compliance={self.compliance_percentage}%)>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'file_name': self.file_name,
            'country_id': self.country_id,
            'extracted_attributes': self.extracted_attributes,
            'compliance_percentage': float(self.compliance_percentage) if self.compliance_percentage else None,
            'final_status': self.final_status.value if self.final_status else None,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None
        }
    
    def classify_status(self) -> ComplianceStatus:
        """
        Clasificar el estado basado en el porcentaje de cumplimiento
        
        90-100% → Cumple
        60-89% → Cumple parcialmente
        0-59% → No cumple
        """
        if self.compliance_percentage is None:
            return None
        
        percentage = float(self.compliance_percentage)
        
        if percentage >= 90:
            return ComplianceStatus.COMPLIES
        elif percentage >= 60:
            return ComplianceStatus.PARTIALLY_COMPLIES
        else:
            return ComplianceStatus.NOT_COMPLIES
