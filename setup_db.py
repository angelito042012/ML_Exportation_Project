"""
Script de inicialización de la base de datos
Crear base de datos, tablas e insertar datos de prueba
"""

import os
import sys
import subprocess
import mysql.connector
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'export_validation')


def get_connection(use_db=False):
    """Crear conexión a MySQL sin/con base de datos específica"""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD if DB_PASSWORD else None,
            database=DB_NAME if use_db else None
        )
        return conn
    except mysql.connector.Error as err:
        if err.errno == 2003:
            print("❌ Error: No se puede conectar a MySQL. ¿Está ejecutándose?")
        else:
            print(f"❌ Error MySQL: {err}")
        return None


def execute_sql_file(filename, use_db=True):
    """Ejecutar un archivo SQL"""
    try:
        conn = get_connection(use_db=use_db)
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        with open(filename, 'r', encoding='utf-8') as f:
            sql = f.read()
            statements = sql.split(';')
            
            for statement in statements:
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error ejecutando {filename}: {e}")
        return False


def install_dependencies():
    """Instalar dependencias de Python"""
    print("\n📦 Instalando dependencias Python...")
    try:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        print("✓ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False


def create_schema():
    """Crear esquema de base de datos"""
    print("\n🗄️ Creando esquema de base de datos...")
    
    # Primero crear la base de datos
    try:
        conn = get_connection(use_db=False)
        if not conn:
            return False
        
        cursor = conn.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.close()
        conn.commit()
        conn.close()
        print(f"✓ Base de datos '{DB_NAME}' creada")
    except Exception as e:
        print(f"❌ Error creando base de datos: {e}")
        return False
    
    # Luego ejecutar el schema
    schema_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'database',
        'schema.sql'
    )
    
    if execute_sql_file(schema_file, use_db=True):
        print("✓ Tablas creadas correctamente")
        return True
    else:
        return False


def load_seed_data():
    """Cargar datos de prueba"""
    print("\n🌱 Cargando datos de prueba...")
    
    seed_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'database',
        'seed.sql'
    )
    
    if execute_sql_file(seed_file, use_db=True):
        print("✓ Datos de prueba cargados correctamente")
        return True
    else:
        return False


def create_folders():
    """Crear carpetas necesarias"""
    print("\n📁 Creando carpetas necesarias...")
    
    folders = [
        'uploads',
        'reports',
        'logs'
    ]
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for folder in folders:
        folder_path = os.path.join(base_dir, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"✓ Carpeta '{folder}' creada")
        else:
            print(f"→ Carpeta '{folder}' ya existe")


def verify_connection():
    """Verificar conexión a la base de datos"""
    print("\n🔗 Verificando conexión...")
    
    conn = get_connection(use_db=True)
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM countries")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"✓ Conexión OK. {count} países en base de datos")
        return True
    else:
        return False


def main():
    """Función principal de instalación"""
    print("=" * 60)
    print("🚀 INICIALIZADOR DE BASE DE DATOS - VALIDADOR DE EXPORTACIÓN")
    print("=" * 60)
    
    print("\n📋 Pasos de instalación:")
    print("1. Instalar dependencias Python")
    print("2. Crear esquema de base de datos MySQL")
    print("3. Cargar datos de prueba")
    print("4. Crear carpetas necesarias")
    print("5. Verificar conexión")
    
    print("\n" + "=" * 60)
    
    # Step 1: Instalar dependencias
    if not install_dependencies():
        print("\n⚠️ Se encontraron problemas con las dependencias. Continuando...")
    
    # Step 2: Crear schema
    if not create_schema():
        print("\n❌ Error: No se pudo crear el esquema de BD")
        print("Verifica tu conexión MySQL y credenciales en .env")
        return False
    
    # Step 3: Cargar datos
    if not load_seed_data():
        print("\n❌ Error: No se pudieron cargar los datos de prueba")
        return False
    
    # Step 4: Crear carpetas
    create_folders()
    
    # Step 5: Verificar conexión
    if not verify_connection():
        print("\n❌ Error: No se pudo verificar la conexión final")
        return False
    
    print("\n" + "=" * 60)
    print("✅ INSTALACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print("\nPróximos pasos:")
    print("1. Verifica el archivo .env con tus credenciales MySQL")
    print("2. Ejecuta: python app.py")
    print("3. Abre: http://localhost:5000")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
