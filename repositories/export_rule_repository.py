"""
Repositorio de Reglas de Exportación
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from models import ExportRule
from repositories.base_repository import BaseRepository


class ExportRuleRepository(BaseRepository[ExportRule]):
    """Repositorio para operaciones con Reglas de Exportación"""
    
    def __init__(self, db: Session):
        super().__init__(db, ExportRule)
    
    def get_rules_by_country(self, country_id: int) -> List[ExportRule]:
        """Obtener todas las reglas de un país"""
        return self.db.query(ExportRule).filter(
            ExportRule.country_id == country_id
        ).all()
    
    def get_rule_by_country_and_attribute(
        self, 
        country_id: int, 
        attribute_name: str
    ) -> Optional[ExportRule]:
        """Obtener una regla específica de un país"""
        return self.db.query(ExportRule).filter(
            ExportRule.country_id == country_id,
            ExportRule.attribute_name == attribute_name
        ).first()
    
    def get_rules_by_attribute(self, attribute_name: str) -> List[ExportRule]:
        """Obtener todas las reglas para un atributo específico"""
        return self.db.query(ExportRule).filter(
            ExportRule.attribute_name == attribute_name
        ).all()
    
    def get_rules_by_operator(self, operator: str) -> List[ExportRule]:
        """Obtener reglas por operador"""
        return self.db.query(ExportRule).filter(
            ExportRule.operator == operator
        ).all()
    
    def count_by_country(self, country_id: int) -> int:
        """Contar reglas de un país"""
        return self.db.query(ExportRule).filter(
            ExportRule.country_id == country_id
        ).count()
