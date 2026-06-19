🚀 CÓMO USAR EL PROYECTO
═════════════════════════════════════════════════════════════════════════════════

PASO 0: CONFIGURAR ENTORNO VIRTUAL
────────────────────────────────────
Desde la carpeta raíz del proyecto:

$ cd "..............\ML_Exportation_Project"

Crear el entorno virtual:
$ python -3.12 -m venv venv

Activar el entorno virtual:

  Windows:
  $ venv\Scripts\activate

  Mac / Linux:
  $ source venv/bin/activate

Deberías ver (venv) al inicio de tu terminal:
  (venv) D:\PROYECTOS\...\ML_Exportation_Project>

Instalar dependencias:
$ pip install -r requirements.txt


PASO 1: CONFIGURAR VARIABLES DE ENTORNO
─────────────────────────────────────────
Copia el archivo de ejemplo y edítalo:

$ copy .env.example .env        (Windows)
$ cp .env.example .env          (Mac / Linux)

Abre .env y completa los valores:

  DB_HOST=localhost
  DB_PORT=3306
  DB_USER=root
  DB_PASSWORD=tu_contraseña
  DB_NAME=export_validation

  OPENAI_API_KEY=sk-...         ← tu clave de OpenAI


PASO 2: INICIALIZAR BASE DE DATOS
─────────────────────────────────
Con el entorno virtual activado:

$ python setup_db.py

Esto:
  • Crea la BD MySQL
  • Crea las 4 tablas
  • Inserta 10 países + 45 reglas de exportación
  • Crea carpetas necesarias (uploads/, reports/, logs/)
  • Verifica conexión


PASO 3: EJECUTAR APLICACIÓN FLASK
──────────────────────────────────
$ python app.py

Resultado esperado:
  🚀 INICIALIZANDO APLICACIÓN
  📊 Verificando base de datos...
  ✓ Base de datos conectada
  ✓ Aplicación inicializada correctamente

  🌐 Iniciando servidor Flask...
  📍 Accede a: http://localhost:5000


PASO 4: ABRIR EN NAVEGADOR
───────────────────────────
http://localhost:5000

¡Listo! Dashboard en vivo.


FLUJO DE USO
────────────
1. Selecciona el país destino en el dropdown
2. Arrastra o selecciona un archivo PDF o DOCX
3. Haz clic en "Validar Documento"
4. El sistema extrae atributos vía OpenAI (o regex si la API falla)
5. Ve los resultados:
   - Semáforo (Verde / Amarillo / Rojo)
   - Porcentaje de cumplimiento
   - Atributos extraídos + fuente (IA o Regex)
   - Observaciones (reglas que no se cumplieron)
   - Recomendaciones automáticas
6. El historial se actualiza automáticamente (paginado, hora Perú)


DETENER LA APLICACIÓN
──────────────────────
Presiona Ctrl + C en la terminal.

Para desactivar el entorno virtual:
$ deactivate


NOTAS
──────
- El entorno virtual (venv/) no se sube al repositorio (.gitignore)
- La clave OPENAI_API_KEY nunca se sube (.env está en .gitignore)
- Si cambias dependencias: pip install -r requirements.txt con el venv activo
