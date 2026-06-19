# FASE 2: Estructura y Modelos SQLAlchemy

## ✅ Completada

Este documento resume la **Fase 2** de refactorización del clasificador de exportación.

---

## 📊 MODELOS SQLALCHEMY (`models/`)

### 1. **Country** (`country.py`)
```python
- id (PK)
- name (Unique)
- created_at
- Relaciones: export_rules, product_files
- Métodos: to_dict()
```

### 2. **ExportRule** (`export_rule.py`) - Base de Conocimiento
```python
- id (PK)
- country_id (FK)
- attribute_name (índice)
- operator (índice)
- expected_value
- recommendation
- created_at, updated_at
- Índice compuesto: (country_id, attribute_name)
```

### 3. **ProductFile** (`product_file.py`) - Historial
```python
- id (PK)
- file_name
- country_id (FK)
- extracted_attributes (JSON)
- compliance_percentage
- final_status (Enum: Cumple/Parcialmente/No cumple)
- upload_date (índice)
- Métodos: classify_status()
```

### 4. **ValidationResult** (`validation_result.py`) - Detalles
```python
- id (PK)
- product_file_id (FK)
- export_rule_id (FK)
- attribute_name (índice)
- expected_value
- found_value
- operator
- is_valid (índice)
- suggestion
- created_at
```

### 5. **ComplianceStatus** (Enum)
```python
- COMPLIES = "Cumple" (90-100%)
- PARTIALLY_COMPLIES = "Cumple parcialmente" (60-89%)
- NOT_COMPLIES = "No cumple" (0-59%)
```

---

## 🗄️ REPOSITORIOS (`repositories/`)

Capa de acceso a datos con patrón **Repository** para separar lógica de persistencia.

### 1. **BaseRepository**
Clase genérica base con CRUD común:
- `create(obj_in)` - Crear registro
- `get_by_id(id)` - Obtener por ID
- `get_all(skip, limit)` - Listar con paginación
- `update(id, obj_in)` - Actualizar
- `delete(id)` - Eliminar
- `count()` - Contar registros
- `exists(id)` - Verificar existencia

### 2. **CountryRepository**
Métodos específicos:
- `get_by_name(name)` - Buscar por nombre
- `get_all_ordered()` - Ordenado alfabéticamente
- `search(query)` - Búsqueda

### 3. **ExportRuleRepository**
Métodos específicos:
- `get_rules_by_country(country_id)` - Reglas de un país
- `get_rule_by_country_and_attribute(country_id, attribute_name)` - Regla específica
- `get_rules_by_attribute(attribute_name)` - Por atributo
- `get_rules_by_operator(operator)` - Por operador
- `count_by_country(country_id)` - Contar por país

### 4. **ProductFileRepository**
Métodos específicos:
- `get_by_country(country_id)` - Por país
- `get_by_status(status)` - Por estado
- `get_recent(days)` - Últimos N días
- `count_by_country(country_id)` - Contar por país
- `count_by_status(status)` - Contar por estado
- `get_average_compliance(country_id)` - Promedio cumplimiento
- `get_statistics(country_id)` - Estadísticas completas

### 5. **ValidationResultRepository**
Métodos específicos:
- `get_by_product_file(product_file_id)` - Resultados de archivo
- `get_errors_by_product_file(product_file_id)` - Solo errores
- `get_successes_by_product_file(product_file_id)` - Solo aciertos
- `get_by_attribute(attribute_name)` - Por atributo
- `count_errors(product_file_id)` - Contar errores
- `count_successes(product_file_id)` - Contar aciertos
- `get_total_evaluations(product_file_id)` - Total evaluaciones

---

## 🔧 SERVICIOS (`services/`)

Capa de lógica de negocio con reglas de validación y procesamiento.

### 1. **ValidationService** (`validation_service.py`)
Validación de productos contra reglas:
- `compare_values(actual, operator, expected)` - Comparar valores
  - Operadores: `=`, `<=`, `>=`, `contains`, `in`
- `validate_product(product_file_id, country_id, attributes)` - Validar producto
  - Retorna: (resultados, porcentaje, estado)
- `classify_compliance(percentage)` - Clasificar cumplimiento
- `get_validation_summary(product_file_id)` - Resumen validación

**Operadores soportados:**
```python
'=' : Igualdad exacta
'<=' : Menor o igual (números/fechas)
'>=' : Mayor o igual (números/fechas)
'contains' : Contiene (strings/listas)
'in' : Está en lista
```

### 2. **DocumentExtractionService** (`document_service.py`)
Extrae atributos de documentos:
- `extract_from_pdf(file_path)` - Extraer texto PDF
- `extract_from_docx(file_path)` - Extraer texto DOCX
- `extract_attributes(file_path)` - Extraer atributos
- `extract_with_confidence(file_path)` - Extraer con metadatos

**Atributos extraídos:**
```python
- empaquetado
- ingredientes
- peso
- fecha_vencimiento
- registro_fda
- etiquetado_ingles
- pais_origen
- certificaciones
```

### 3. **ReportService** (`report_service.py`)
Genera reportes y estadísticas:
- `generate_evaluation_report(product_file_id)` - Reporte completo
- `generate_country_statistics(country_id)` - Estadísticas por país
- `generate_global_statistics()` - Estadísticas globales
- `format_pdf_content(product_file_id)` - Preparar contenido PDF
- `get_history(country_id, limit)` - Historial evaluaciones

---

## 📁 ESTRUCTURA COMPLETA

```
ML_Exportation_Project/
│
├── config/
│   ├── __init__.py
│   └── database.py (SQLAlchemy + MySQL)
│
├── models/
│   ├── __init__.py (exporta todos)
│   ├── base.py
│   ├── country.py
│   ├── export_rule.py
│   ├── product_file.py
│   └── validation_result.py
│
├── repositories/
│   ├── __init__.py (exporta todos)
│   ├── base_repository.py
│   ├── country_repository.py
│   ├── export_rule_repository.py
│   ├── product_file_repository.py
│   └── validation_result_repository.py
│
├── services/
│   ├── __init__.py (exporta todos)
│   ├── validation_service.py
│   ├── document_service.py
│   └── report_service.py
│
├── extractors/ (para Fase 3)
├── templates/ (para Fase 4)
├── static/ (para Fase 4)
├── database/
│   ├── schema.sql
│   └── seed.sql
├── .env
├── requirements.txt
└── setup_db.py
```

---

## 🔄 FLUJO DE DATOS

```
PDF/DOCX Upload
    ↓
DocumentExtractionService.extract_attributes()
    ↓ (atributos extraídos)
ValidationService.validate_product()
    ↓ (validaciones contra reglas)
ValidationResults (BD)
    ↓
ReportService.generate_evaluation_report()
    ↓ (reporte completo)
PDF / JSON / Web UI
```

---

## ✨ VENTAJAS DE LA ARQUITECTURA

✅ **Separación de responsabilidades**
- Models: estructura de datos
- Repositories: acceso a datos
- Services: lógica de negocio
- Controllers/Routes: manejo de requests (Fase 3)

✅ **Reutilizable**
- Servicios pueden usarse desde cualquier interfaz (web, API, CLI)
- Repositories abstraen la BD (cambiar MySQL a PostgreSQL sin afectar lógica)

✅ **Testeable**
- Cada componente es independiente
- Fácil crear mocks para testing

✅ **Escalable**
- Agregar nuevos atributos/reglas sin cambiar código
- Fácil agregar nuevos operadores de comparación

---

## 🚀 PRÓXIMA FASE (FASE 3)

**Refactorización de Extractores y Flask Integration**

Se implementará:
1. Aplicación Flask con rutas
2. Integración de servicios en endpoints
3. Manejo de uploads
4. Almacenamiento de evaluaciones
5. API REST

---

## 📝 NOTAS

- Toda la lógica está documentada con docstrings
- Métodos `to_dict()` en modelos para serialización JSON
- Enums para estados de cumplimiento
- Índices optimizados en BD para queries frecuentes
- Type hints en todos los métodos

---

**Fase 2 Status: ✅ COMPLETADA**

Próximo: Ejecutar Fase 3 o ir a Fase 4 según necesidad.
