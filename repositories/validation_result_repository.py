"""
Repositorio de Resultados de Validación
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from models import ValidationResult
from repositories.base_repository import BaseRepository


class ValidationResultRepository(BaseRepository[ValidationResult]):
    """Repositorio para operaciones con Resultados de Validación"""
    
    def __init__(self, db: Session):
        super().__init__(db, ValidationResult)
    
    def get_by_product_file(self, product_file_id: int) -> List[ValidationResult]:
        """Obtener todos los resultados de validación de un archivo"""
        return self.db.query(ValidationResult).filter(
            ValidationResult.product_file_id == product_file_id
        ).all()
    
    def get_errors_by_product_file(self, product_file_id: int) -> List[ValidationResult]:
        """Obtener solo los errores (validaciones fallidas) de un archivo"""
        return self.db.query(ValidationResult).filter(
            ValidationResult.product_file_id == product_file_id,
            ValidationResult.is_valid == False
        ).all()
    
    def get_successes_by_product_file(self, product_file_id: int) -> List[ValidationResult]:
        """Obtener solo los aciertos (validaciones exitosas) de un archivo"""
        return self.db.query(ValidationResult).filter(
            ValidationResult.product_file_id == product_file_id,
            ValidationResult.is_valid == True
        ).all()
    
    def get_by_attribute(self, attribute_name: str, product_file_id: Optional[int] = None) -> List[ValidationResult]:
        """Obtener resultados por atributo"""
        query = self.db.query(ValidationResult).filter(
            ValidationResult.attribute_name == attribute_name
        )
        if product_file_id:
            query = query.filter(ValidationResult.product_file_id == product_file_id)
        return query.all()
    
    def count_errors(self, product_file_id: int) -> int:
        """Contar errores en un archivo"""
        return self.db.query(ValidationResult).filter(
            ValidationResult.product_file_id == product_file_id,
            ValidationResult.is_valid == False
        ).count()
    
    def count_successes(self, product_file_id: int) -> int:
        """Contar aciertos en un archivo"""
        return self.db.query(ValidationResult).filter(
            ValidationResult.product_file_id == product_file_id,
            ValidationResult.is_valid == True
        ).count()
    
    def get_total_evaluations(self, product_file_id: int) -> int:
        """Obtener total de evaluaciones para un archivo"""
        return self.db.query(ValidationResult).filter(
            ValidationResult.product_file_id == product_file_id
        ).count()
