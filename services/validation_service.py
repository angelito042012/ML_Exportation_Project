"""
Servicio de Validación - Valida atributos de productos contra reglas de exportación
"""

from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
from models import ValidationResult, ProductFile, ComplianceStatus
from repositories import ExportRuleRepository, ValidationResultRepository, ProductFileRepository


class ValidationService:
    """Servicio para validación de productos contra reglas de exportación"""
    
    def __init__(self, db: Session):
        self.db = db
        self.rule_repo = ExportRuleRepository(db)
        self.validation_repo = ValidationResultRepository(db)
        self.product_repo = ProductFileRepository(db)
    
    def compare_values(self, actual: any, operator: str, expected: str) -> bool:
        """
        Comparar valor actual contra valor esperado usando un operador
        
        Operadores soportados:
        - '=' : Igualdad exacta
        - '<=' : Menor o igual (para números)
        - '>=' : Mayor o igual (para números)
        - 'contains' : Contiene (para strings)
        - 'in' : Está en lista (para múltiples valores)
        """
        try:
            # Normalizar valores
            if isinstance(actual, str):
                actual = actual.strip().lower()
            if isinstance(expected, str):
                expected = expected.strip().lower()
            
            # Operador: igualdad exacta
            if operator == '=':
                return actual == expected
            
            # Operadores: menor o igual / mayor o igual (para números)
            if operator in ('<=', '>='):
                try:
                    # Intentar con números (peso)
                    actual_num = float(str(actual).replace('kg', '').strip())
                    expected_num = float(str(expected).replace('kg', '').strip())
                    
                    if operator == '<=':
                        return actual_num <= expected_num
                    else:  # >=
                        return actual_num >= expected_num
                except (ValueError, AttributeError):
                    # Si no es número, intentar con fechas
                    try:
                        actual_date = datetime.fromisoformat(str(actual))
                        expected_date = datetime.fromisoformat(str(expected))
                        
                        if operator == '<=':
                            return actual_date <= expected_date
                        else:  # >=
                            return actual_date >= expected_date
                    except:
                        return False
            
            # Operador: contiene
            if operator == 'contains':
                if isinstance(actual, list):
                    return any(exp in str(item).lower() for item in actual for exp in [expected])
                return expected in str(actual).lower()
            
            # Operador: está en
            if operator == 'in':
                actual_items = [item.strip().lower() for item in str(actual).split(',')]
                expected_items = [item.strip().lower() for item in str(expected).split(',')]
                return all(item in actual_items for item in expected_items)
            
            return False
        
        except Exception as e:
            print(f"Error en comparación: {e}")
            return False
    
    def validate_product(
        self,
        product_file_id: int,
        country_id: int,
        extracted_attributes: Dict[str, any]
    ) -> Tuple[List[ValidationResult], float, ComplianceStatus]:
        """
        Validar un producto contra las reglas de un país
        
        Retorna:
        - Lista de resultados de validación
        - Porcentaje de cumplimiento (0-100)
        - Estado final (Cumple/Parcialmente/No cumple)
        """
        # Obtener reglas del país
        rules = self.rule_repo.get_rules_by_country(country_id)
        
        if not rules:
            return [], 100.0, ComplianceStatus.COMPLIES
        
        validation_results = []
        valid_count = 0
        
        # Validar cada regla
        for rule in rules:
            found_value = extracted_attributes.get(rule.attribute_name)
            is_valid = self.compare_values(found_value, rule.operator, rule.expected_value)
            
            if is_valid:
                valid_count += 1
            
            # Crear resultado de validación
            result = ValidationResult(
                product_file_id=product_file_id,
                export_rule_id=rule.id,
                attribute_name=rule.attribute_name,
                expected_value=rule.expected_value,
                found_value=str(found_value) if found_value else None,
                operator=rule.operator,
                is_valid=is_valid,
                suggestion=rule.recommendation if not is_valid else None
            )
            
            self.db.add(result)
            validation_results.append(result)
        
        self.db.commit()
        
        # Calcular porcentaje y estado final
        total_rules = len(rules)
        compliance_percentage = (valid_count / total_rules * 100) if total_rules > 0 else 100.0
        final_status = self.classify_compliance(compliance_percentage)
        
        return validation_results, compliance_percentage, final_status
    
    def classify_compliance(self, percentage: float) -> ComplianceStatus:
        """
        Clasificar nivel de cumplimiento basado en porcentaje
        
        90-100% → Cumple
        60-89% → Cumple parcialmente
        0-59% → No cumple
        """
        if percentage >= 90:
            return ComplianceStatus.COMPLIES
        elif percentage >= 60:
            return ComplianceStatus.PARTIALLY_COMPLIES
        else:
            return ComplianceStatus.NOT_COMPLIES
    
    def get_validation_summary(self, product_file_id: int) -> Dict:
        """Obtener resumen de validación para un archivo"""
        results = self.validation_repo.get_by_product_file(product_file_id)
        errors = self.validation_repo.get_errors_by_product_file(product_file_id)
        
        total = len(results)
        valid = total - len(errors)
        
        return {
            'total_validations': total,
            'valid_count': valid,
            'error_count': len(errors),
            'compliance_percentage': (valid / total * 100) if total > 0 else 0,
            'errors': [e.to_dict() for e in errors],
            'suggestions': [e.suggestion for e in errors if e.suggestion]
        }
