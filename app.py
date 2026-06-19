"""
Aplicación Flask Principal
Clasificador Inteligente de Productos para Exportación
"""

import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from flask_cors import CORS

from config import SessionLocal, health_check, init_db
from models import ProductFile, ComplianceStatus
from repositories import (
    CountryRepository,
    ExportRuleRepository,
    ProductFileRepository,
    ValidationResultRepository
)
from services import (
    ValidationService,
    DocumentExtractionService,
    ReportService
)

# Configuración de Flask
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Cargar configuración desde .env
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# Crear carpetas si no existen
for folder in [app.config['UPLOAD_FOLDER'], 'reports', 'logs']:
    os.makedirs(folder, exist_ok=True)


def allowed_file(filename: str) -> bool:
    """Verificar si el archivo tiene extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db():
    """Obtener sesión de base de datos"""
    return SessionLocal()


# =====================================================
# RUTAS - INTERFAZ WEB
# =====================================================

@app.route('/', methods=['GET'])
def index():
    """Página principal - Dashboard"""
    db = get_db()
    try:
        country_repo = CountryRepository(db)
        countries = country_repo.get_all_ordered()
        
        product_repo = ProductFileRepository(db)
        stats = product_repo.get_statistics()
        
        return render_template('dashboard.html', 
                             countries=countries,
                             stats=stats)
    finally:
        db.close()


@app.route('/validate', methods=['POST'])
def validate():
    """
    Endpoint para validar un producto
    Recibe: archivo, país
    Retorna: resultados de validación
    """
    db = get_db()
    try:
        # Verificar que se enviaron los datos requeridos
        if 'file' not in request.files:
            return jsonify({'error': 'No se envió archivo'}), 400
        
        if 'country_id' not in request.form:
            return jsonify({'error': 'No se seleccionó país'}), 400
        
        file = request.files['file']
        country_id = int(request.form['country_id'])
        
        # Validar archivo
        if file.filename == '':
            return jsonify({'error': 'Archivo vacío'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Tipo de archivo no permitido. Use PDF o DOCX'}), 400
        
        # Guardar archivo
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extraer atributos del documento
        extraction_service = DocumentExtractionService()
        extracted_attributes, extraction_source = extraction_service.extract_attributes(file_path)
        
        # Crear registro de archivo en BD
        product_file = ProductFile(
            file_name=filename,
            country_id=country_id,
            extracted_attributes=extracted_attributes
        )
        db.add(product_file)
        db.flush()
        product_id = product_file.id
        
        # Validar producto contra reglas del país
        validation_service = ValidationService(db)
        validation_results, compliance_percentage, final_status = validation_service.validate_product(
            product_id,
            country_id,
            extracted_attributes
        )
        
        # Actualizar registro con resultados
        product_file.compliance_percentage = compliance_percentage
        product_file.final_status = final_status
        db.commit()
        
        # Generar reporte
        report_service = ReportService(db)
        report = report_service.generate_evaluation_report(product_id)
        
        return jsonify({
            'success': True,
            'product_id': product_id,
            'extraction_source': extraction_source,
            'report': report
        }), 200
    
    except ValueError:
        return jsonify({'error': 'ID de país inválido'}), 400
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Error procesando archivo: {str(e)}'}), 500
    finally:
        db.close()


@app.route('/history', methods=['GET'])
def history():
    """Obtener historial de evaluaciones"""
    db = get_db()
    try:
        PAGE_SIZE = 15
        page = request.args.get('page', 1, type=int)
        country_id = request.args.get('country_id', type=int)
        skip = (page - 1) * PAGE_SIZE

        product_repo = ProductFileRepository(db)
        total = product_repo.count_by_country(country_id) if country_id else product_repo.count()

        report_service = ReportService(db)
        history_data = report_service.get_history(country_id=country_id, skip=skip, limit=PAGE_SIZE)

        return jsonify({
            'success': True,
            'history': history_data,
            'page': page,
            'page_size': PAGE_SIZE,
            'total': total
        }), 200

    except Exception as e:
        return jsonify({'error': f'Error obteniendo historial: {str(e)}'}), 500
    finally:
        db.close()


@app.route('/report/<int:product_id>', methods=['GET'])
def get_report(product_id: int):
    """Obtener reporte de una evaluación específica"""
    db = get_db()
    try:
        report_service = ReportService(db)
        report = report_service.generate_evaluation_report(product_id)
        
        if not report:
            return jsonify({'error': 'Reporte no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'report': report
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error obteniendo reporte: {str(e)}'}), 500
    finally:
        db.close()


@app.route('/statistics', methods=['GET'])
def statistics():
    """Obtener estadísticas generales"""
    db = get_db()
    try:
        country_id = request.args.get('country_id', type=int)
        
        report_service = ReportService(db)
        
        if country_id:
            stats = report_service.generate_country_statistics(country_id)
        else:
            stats = report_service.generate_global_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error obteniendo estadísticas: {str(e)}'}), 500
    finally:
        db.close()


@app.route('/countries', methods=['GET'])
def get_countries():
    """Obtener lista de países"""
    db = get_db()
    try:
        country_repo = CountryRepository(db)
        countries = country_repo.get_all_ordered()
        
        countries_data = [c.to_dict() for c in countries]
        
        return jsonify({
            'success': True,
            'countries': countries_data
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error obteniendo países: {str(e)}'}), 500
    finally:
        db.close()


@app.route('/rules/<int:country_id>', methods=['GET'])
def get_rules(country_id: int):
    """Obtener reglas de un país"""
    db = get_db()
    try:
        rule_repo = ExportRuleRepository(db)
        rules = rule_repo.get_rules_by_country(country_id)
        
        rules_data = [r.to_dict() for r in rules]
        
        return jsonify({
            'success': True,
            'rules': rules_data,
            'rule_count': len(rules_data)
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error obteniendo reglas: {str(e)}'}), 500
    finally:
        db.close()


# =====================================================
# MANEJO DE ERRORES
# =====================================================

@app.errorhandler(404)
def not_found(error):
    """Error 404 - Página no encontrada"""
    return jsonify({'error': 'Recurso no encontrado'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Error 500 - Error interno del servidor"""
    return jsonify({'error': 'Error interno del servidor'}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Error 413 - Archivo demasiado grande"""
    return jsonify({'error': 'Archivo demasiado grande (máximo 16MB)'}), 413


# =====================================================
# VERIFICACIÓN Y INICIALIZACIÓN
# =====================================================

@app.before_request
def before_request():
    """Acciones antes de cada request"""
    pass


@app.teardown_appcontext
def shutdown_session(exception=None):
    """Limpiar sesión después de request"""
    pass


def initialize_app():
    """Inicializar aplicación"""
    print("\n" + "="*60)
    print("🚀 INICIALIZANDO APLICACIÓN")
    print("="*60)
    
    # Verificar conexión a BD
    print("\n📊 Verificando base de datos...")
    if health_check():
        print("✓ Base de datos conectada")
    else:
        print("✗ Error: No se pudo conectar a la base de datos")
        print("Ejecuta: python setup_db.py")
        return False
    
    print("\n✓ Aplicación inicializada correctamente")
    print("="*60)
    return True


# =====================================================
# PUNTO DE ENTRADA
# =====================================================

if __name__ == '__main__':
    if initialize_app():
        print("\n🌐 Iniciando servidor Flask...")
        print("📍 Accede a: http://localhost:5000")
        print("\n(Presiona Ctrl+C para detener)")
        print("="*60 + "\n")
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
