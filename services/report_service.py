"""
Servicio de Reportes - Genera reportes PDF y resúmenes de evaluaciones
"""

from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models import ProductFile, ComplianceStatus
from repositories import ProductFileRepository, ValidationResultRepository


class ReportService:
    """Servicio para generación de reportes"""
    
    def __init__(self, db: Session):
        self.db = db
        self.product_repo = ProductFileRepository(db)
        self.validation_repo = ValidationResultRepository(db)
    
    def generate_evaluation_report(self, product_file_id: int) -> Dict:
        """Generar reporte completo de una evaluación"""
        product = self.product_repo.get_by_id(product_file_id)
        
        if not product:
            return None
        
        validation_results = self.validation_repo.get_by_product_file(product_file_id)
        errors = self.validation_repo.get_errors_by_product_file(product_file_id)
        
        report = {
            'product_info': {
                'file_name': product.file_name,
                'country': product.country.name if product.country else 'N/A',
                'upload_date': product.upload_date.isoformat() if product.upload_date else None,
            },
            'summary': {
                'total_validations': len(validation_results),
                'passed': len(validation_results) - len(errors),
                'failed': len(errors),
                'compliance_percentage': float(product.compliance_percentage) if product.compliance_percentage else 0,
                'final_status': product.final_status.value if product.final_status else None,
            },
            'extracted_attributes': product.extracted_attributes or {},
            'validation_details': {
                'passed': [v.to_dict() for v in validation_results if v.is_valid],
                'failed': [v.to_dict() for v in errors]
            },
            'recommendations': [v.suggestion for v in errors if v.suggestion]
        }
        
        return report
    
    def generate_country_statistics(self, country_id: int) -> Dict:
        """Generar estadísticas de evaluaciones para un país"""
        stats = self.product_repo.get_statistics(country_id)
        
        return {
            'country_id': country_id,
            'timestamp': datetime.utcnow().isoformat(),
            'statistics': stats,
            'average_compliance': self.product_repo.get_average_compliance(country_id)
        }
    
    def generate_global_statistics(self) -> Dict:
        """Generar estadísticas globales de todas las evaluaciones"""
        stats = self.product_repo.get_statistics()
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'global_statistics': stats,
            'average_compliance': self.product_repo.get_average_compliance()
        }
    
    def format_pdf_content(self, product_file_id: int) -> Dict:
        """
        Preparar contenido para generación de PDF
        (se implementará con reportlab en fases posteriores)
        """
        report = self.generate_evaluation_report(product_file_id)
        
        if not report:
            return None
        
        pdf_content = {
            'title': 'Reporte de Evaluación de Exportación',
            'date': datetime.utcnow().strftime('%d/%m/%Y %H:%M'),
            'product_name': report['product_info']['file_name'],
            'country': report['product_info']['country'],
            'compliance_percentage': f"{report['summary']['compliance_percentage']:.2f}%",
            'final_status': report['summary']['final_status'],
            'status_color': self._get_status_color(report['summary']['final_status']),
            'summary_table': [
                ['Validaciones Totales', str(report['summary']['total_validations'])],
                ['Cumplidas', str(report['summary']['passed'])],
                ['No Cumplidas', str(report['summary']['failed'])],
                ['Porcentaje', f"{report['summary']['compliance_percentage']:.2f}%"]
            ],
            'attributes': report['extracted_attributes'],
            'errors': report['validation_details']['failed'],
            'recommendations': report['recommendations']
        }
        
        return pdf_content
    
    @staticmethod
    def _get_status_color(status: str) -> str:
        """Obtener color según estado de cumplimiento"""
        if status == 'Cumple':
            return '#2ecc71'  # Verde
        elif status == 'Cumple parcialmente':
            return '#f1c40f'  # Amarillo
        else:
            return '#e74c3c'  # Rojo
    
    def get_history(self, country_id: Optional[int] = None, skip: int = 0, limit: int = 15) -> list:
        """Obtener historial de evaluaciones ordenado por fecha descendente"""
        from sqlalchemy import desc

        query = self.db.query(ProductFile).order_by(desc(ProductFile.upload_date))
        if country_id:
            query = query.filter(ProductFile.country_id == country_id)
        files = query.offset(skip).limit(limit).all()

        history = []
        for f in files:
            history.append({
                'id': f.id,
                'file_name': f.file_name,
                'country': f.country.name if f.country else 'N/A',
                'compliance_percentage': float(f.compliance_percentage) if f.compliance_percentage else 0,
                'final_status': f.final_status.value if f.final_status else None,
                'upload_date': f.upload_date.strftime('%Y-%m-%dT%H:%M:%SZ') if f.upload_date else None
            })

        return history
