"""
Repositorio de Archivos de Productos
"""

from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models import ProductFile, ComplianceStatus
from repositories.base_repository import BaseRepository


class ProductFileRepository(BaseRepository[ProductFile]):
    """Repositorio para operaciones con Archivos de Productos"""
    
    def __init__(self, db: Session):
        super().__init__(db, ProductFile)
    
    def get_by_country(self, country_id: int, skip: int = 0, limit: int = 100) -> List[ProductFile]:
        """Obtener archivos por país"""
        return self.db.query(ProductFile).filter(
            ProductFile.country_id == country_id
        ).order_by(desc(ProductFile.upload_date)).offset(skip).limit(limit).all()
    
    def get_by_status(self, status: ComplianceStatus, skip: int = 0, limit: int = 100) -> List[ProductFile]:
        """Obtener archivos por estado de cumplimiento"""
        return self.db.query(ProductFile).filter(
            ProductFile.final_status == status
        ).order_by(desc(ProductFile.upload_date)).offset(skip).limit(limit).all()
    
    def get_recent(self, days: int = 7, skip: int = 0, limit: int = 100) -> List[ProductFile]:
        """Obtener evaluaciones de los últimos N días"""
        from_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(ProductFile).filter(
            ProductFile.upload_date >= from_date
        ).order_by(desc(ProductFile.upload_date)).offset(skip).limit(limit).all()
    
    def count_by_country(self, country_id: int) -> int:
        """Contar evaluaciones de un país"""
        return self.db.query(ProductFile).filter(
            ProductFile.country_id == country_id
        ).count()
    
    def count_by_status(self, status: ComplianceStatus) -> int:
        """Contar evaluaciones por estado"""
        return self.db.query(ProductFile).filter(
            ProductFile.final_status == status
        ).count()
    
    def get_average_compliance(self, country_id: Optional[int] = None) -> Optional[float]:
        """Obtener porcentaje promedio de cumplimiento"""
        query = self.db.query(ProductFile)
        if country_id:
            query = query.filter(ProductFile.country_id == country_id)
        
        result = query.with_entities(
            (lambda: __import__('sqlalchemy').func.avg(ProductFile.compliance_percentage))()
        ).scalar()
        return float(result) if result else None
    
    def get_statistics(self, country_id: Optional[int] = None) -> dict:
        """Obtener estadísticas de evaluaciones"""
        query = self.db.query(ProductFile)
        if country_id:
            query = query.filter(ProductFile.country_id == country_id)
        
        total = query.count()
        complies = query.filter(ProductFile.final_status == ComplianceStatus.COMPLIES).count()
        partially = query.filter(ProductFile.final_status == ComplianceStatus.PARTIALLY_COMPLIES).count()
        not_complies = query.filter(ProductFile.final_status == ComplianceStatus.NOT_COMPLIES).count()
        
        return {
            'total': total,
            'complies': complies,
            'partially_complies': partially,
            'not_complies': not_complies,
            'complies_percentage': (complies / total * 100) if total > 0 else 0,
            'partially_percentage': (partially / total * 100) if total > 0 else 0,
            'not_complies_percentage': (not_complies / total * 100) if total > 0 else 0
        }
