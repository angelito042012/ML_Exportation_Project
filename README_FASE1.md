# 🚀 Clasificador Inteligente de Productos Exportables

## Fase 1: Base de Datos MySQL ✅

Este proyecto ha sido refactorizado para implementar una arquitectura basada en **Sistemas del Conocimiento** y **Procesamiento de Lenguaje Natural** para la validación automática de documentos de exportación.

---

## 📋 Requisitos Previos

Asegúrate de tener instalado:

- **Python 3.9+**
- **MySQL Server 8.0+**
- **pip** (gestor de paquetes de Python)

---

## 🔧 Instalación (Pasos para Fase 1)

### 1. **Clonar/Descargar el Proyecto**
```bash
# Ya lo tienes en:
# d:\PROYECTOS\Machine Learning Rogelio\ML_Exportation_Project
```

### 2. **Crear Archivo .env**

El archivo `.env` ya fue creado con configuración por defecto. **Verifica y ajusta si es necesario:**

```bash
# .env (por defecto)
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=export_validation
```

⚠️ **Si tu MySQL requiere contraseña**, actualiza:
```
DB_PASSWORD=tu_contraseña_aqui
```

### 3. **Instalar Dependencias**

Abre una terminal en el directorio del proyecto:

```bash
pip install -r requirements.txt
```

### 4. **Ejecutar Setup de Base de Datos**

Este script crea automáticamente todo:

```bash
python setup_db.py
```

**Qué hace:**
- ✅ Crea la base de datos `export_validation`
- ✅ Crea todas las tablas necesarias
- ✅ Inserta 10 países con sus reglas de exportación
- ✅ Crea las carpetas necesarias (uploads, reports, logs)
- ✅ Verifica la conexión

---

## 🗄️ Estructura de Base de Datos

### Tablas Principales:

#### 1. **countries**
```sql
id | name | created_at
```
Almacena los países de exportación.

#### 2. **export_rules** (Base de Conocimiento)
```sql
id | country_id | attribute_name | operator | expected_value | recommendation
```
Define las reglas de validación para cada país.

#### 3. **product_files** (Historial)
```sql
id | file_name | country_id | extracted_attributes | compliance_percentage | final_status
```
Registro de evaluaciones realizadas.

#### 4. **validation_results** (Detalles de Validación)
```sql
id | product_file_id | attribute_name | expected_value | found_value | is_valid | suggestion
```
Resultados detallados de cada validación.

---

## 📊 Datos de Prueba

Se incluyen 10 países con reglas específicas:

| País | Reglas | Ejemplos |
|------|--------|----------|
| 🇭🇳 Honduras | 5 | Plástico, ≤5kg, pectina |
| 🇲🇽 México | 4 | Vidrio, ≤10kg, preservantes |
| 🇨🇴 Colombia | 4 | Cartón, ≤8kg, colorantes |
| 🇺🇸 Estados Unidos | 4 | Registro FDA, etiquetado inglés |
| 🇪🇺 Unión Europea | 3 | Vidrio, regulaciones GMO |
| 🇨🇦 Canadá | 4 | Plástico biodegradable |
| 🇯🇵 Japón | 3 | Vidrio, ≤3kg (muy restrictivo) |
| 🇦🇺 Australia | 3 | Cartón, límites de pesticidas |
| 🇨🇳 China | 3 | Plástico, aditivos registrados |
| 🇧🇷 Brasil | 4 | Vidrio, azúcar local |

---

## ✅ Verificar Instalación

```bash
python -c "from config import health_check; health_check()"
```

Debería mostrar:
```
✓ Conexión a base de datos OK
```

---

## 🔍 Próxima Fase (Fase 2)

Una vez completada esta fase:

- [ ] Crear modelos SQLAlchemy (Country, ExportRule, ProductFile)
- [ ] Implementar repositories (acceso a datos)
- [ ] Crear servicios base
- [ ] Refactorizar código anterior

**Continuar con Fase 2 cuando confirmes que la BD está lista.**

---

## 📝 Notas

- La base de datos se crea automáticamente con `setup_db.py`
- Los datos de prueba se cargan desde `database/seed.sql`
- El esquema está optimizado con índices para performance
- Se usa `pymysql` para compatibilidad con SQLAlchemy

---

## 🆘 Troubleshooting

### Error: "Cannot connect to MySQL"
```bash
# Verifica que MySQL está ejecutándose
# Windows: Services > MySQL
# Linux: sudo systemctl status mysql
```

### Error: "Access Denied (using password: YES)"
```bash
# Actualiza .env con contraseña correcta
# o actualiza usuario/host correcto
```

### Error: "Database already exists"
```bash
# El script automáticamente lo elimina y recrea
# Si necesitas preservar datos, hacer backup antes
```

---

## 📄 Licencia

Este proyecto es parte de un trabajo académico.

---

**Fase 1: ✅ Completada**

Próximo paso: Ejecutar `python setup_db.py` y pasar a **Fase 2: Estructura del Proyecto**
