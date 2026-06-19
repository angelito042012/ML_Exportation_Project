/* JavaScript para interactividad del dashboard */

const API_BASE = '/';

// Estado global
let currentReport = null;
let countries = [];
let historyPage = 1;
let historyTotal = 0;
let historyPageSize = 15;

// Inicialización
document.addEventListener('DOMContentLoaded', function () {
    loadCountries();
    loadHistory();
    setupEventListeners();
    setupDropZone();
});

// ========================================
// CARGAR PAÍSES
// ========================================
function loadCountries() {
    fetch(`${API_BASE}countries`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                countries = data.countries;
                // Ya están en el dropdown (se cargan desde Flask)
            }
        })
        .catch(error => console.error('Error cargando países:', error));
}

// ========================================
// CARGAR HISTORIAL
// ========================================
function loadHistory(page = 1) {
    historyPage = page;
    fetch(`${API_BASE}history?page=${page}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                historyTotal = data.total;
                historyPageSize = data.page_size;
                displayHistory(data.history, data.page, data.total, data.page_size);
            }
        })
        .catch(error => console.error('Error cargando historial:', error));
}

function displayHistory(history, page, total, pageSize) {
    const historyTable = document.getElementById('historyTable');
    historyTable.innerHTML = '';

    if (history.length === 0) {
        historyTable.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted py-4">
                    No hay evaluaciones aún
                </td>
            </tr>
        `;
        updateHistoryPagination(0, 0, 0, 0);
        return;
    }

    history.forEach(item => {
        const row = document.createElement('tr');
        const statusBadge = getStatusBadge(item.final_status);

        row.innerHTML = `
            <td><small>${cleanFileName(item.file_name)}</small></td>
            <td>${item.country}</td>
            <td><small>${formatDate(item.upload_date)}</small></td>
            <td><strong>${item.compliance_percentage.toFixed(2)}%</strong></td>
            <td>${statusBadge}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="viewReport(${item.id})">
                    <i class="bi bi-eye"></i>
                </button>
            </td>
        `;
        historyTable.appendChild(row);
    });

    const from = (page - 1) * pageSize + 1;
    const to = Math.min(page * pageSize, total);
    updateHistoryPagination(from, to, total, page, pageSize);
}

function updateHistoryPagination(from, to, total, page, pageSize) {
    const info = document.getElementById('historyInfo');
    const prev = document.getElementById('historyPrev');
    const next = document.getElementById('historyNext');

    if (total === 0) {
        info.textContent = '0 registros';
        prev.disabled = true;
        next.disabled = true;
        return;
    }

    const totalPages = Math.ceil(total / pageSize);
    info.textContent = `${from}–${to} de ${total} registros`;
    prev.disabled = page <= 1;
    next.disabled = page >= totalPages;

    prev.onclick = () => loadHistory(page - 1);
    next.onclick = () => loadHistory(page + 1);
}

function formatDate(isoString) {
    if (!isoString) return '—';
    return new Date(isoString).toLocaleString('es-PE', {
        timeZone: 'America/Lima',
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ========================================
// VISTA DE CONFIGURACIÓN DE EVENTOS
// ========================================
function setupEventListeners() {
    // Formulario de carga
    document.getElementById('uploadForm').addEventListener('submit', handleFormSubmit);

    // Botones
    document.getElementById('downloadPdfBtn').addEventListener('click', downloadPDF);
    document.getElementById('newValidationBtn').addEventListener('click', resetForm);
}

// ========================================
// MANEJAR ENVÍO DE FORMULARIO
// ========================================
function handleFormSubmit(e) {
    e.preventDefault();

    const countryId = document.getElementById('countrySelect').value;
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!countryId) {
        showAlert('Por favor selecciona un país', 'danger');
        return;
    }

    if (!file) {
        showAlert('Por favor selecciona un archivo', 'danger');
        return;
    }

    // Validar tipo de archivo
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type)) {
        showAlert('Tipo de archivo no permitido. Usa PDF o DOCX', 'danger');
        return;
    }

    // Validar tamaño
    if (file.size > 16 * 1024 * 1024) {
        showAlert('Archivo demasiado grande (máximo 16MB)', 'danger');
        return;
    }

    validateDocument(countryId, file);
}

// ========================================
// VALIDAR DOCUMENTO
// ========================================
function validateDocument(countryId, file) {
    const formData = new FormData();
    formData.append('country_id', countryId);
    formData.append('file', file);

    showProgress(true);

    fetch(`${API_BASE}validate`, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentReport = data.report;
                currentReport.extraction_source = data.extraction_source;
                displayResults(data.report);
                showAlert('Documento validado correctamente', 'success');
                loadHistory();
            } else {
                showAlert(data.error || 'Error en la validación', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error al procesar el archivo: ' + error, 'danger');
        })
        .finally(() => {
            showProgress(false);
        });
}

// ========================================
// MOSTRAR RESULTADOS
// ========================================
function displayResults(report) {
    document.getElementById('initialMessage').style.display = 'none';
    document.getElementById('resultContainer').style.display = 'block';

    const compliance = report.summary.compliance_percentage;
    const status = report.summary.final_status;

    // Actualizar semáforo
    updateTraffic(compliance, status);

    // Porcentaje y estado
    document.getElementById('fileInfo').textContent = `${cleanFileName(report.product_info.file_name)} • ${report.product_info.country}`;
    document.getElementById('compliancePercentage').textContent = `${compliance.toFixed(2)}%`;
    document.getElementById('statusText').innerHTML = getStatusBadge(status);

    // Atributos extraídos
    displayAttributes(report.extracted_attributes);
    updateExtractionSourceBadge(report.extraction_source);

    // Errores
    if (report.validation_details.failed.length > 0) {
        displayErrors(report.validation_details.failed);
    } else {
        document.getElementById('errorsCard').style.display = 'none';
    }

    // Recomendaciones
    if (report.recommendations.length > 0) {
        displayRecommendations(report.recommendations);
    } else {
        document.getElementById('recommendationsCard').style.display = 'none';
    }

    // Animar entrada
    document.getElementById('resultContainer').classList.add('fade-in');
}

// ========================================
// ACTUALIZAR SEMÁFORO
// ========================================
function updateTraffic(compliance, status) {
    const light = document.getElementById('statusLight');
    light.style.display = 'block';

    light.className = 'status-light';

    if (compliance >= 90) {
        light.classList.add('green');
    } else if (compliance >= 60) {
        light.classList.add('yellow');
    } else {
        light.classList.add('red');
    }
}

// ========================================
// MOSTRAR ATRIBUTOS
// ========================================
function displayAttributes(attributes) {
    const list = document.getElementById('attributesList');
    list.innerHTML = '';

    for (const [key, value] of Object.entries(attributes)) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <strong>${formatAttributeName(key)}</strong>
            </td>
            <td>
                <code>${value || 'No detectado'}</code>
            </td>
        `;
        list.appendChild(row);
    }
}

// ========================================
// MOSTRAR ERRORES
// ========================================
function displayErrors(errors) {
    const card = document.getElementById('errorsCard');
    const list = document.getElementById('errorsList');

    card.style.display = 'block';
    list.innerHTML = '';

    errors.forEach(error => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="text-danger fw-bold">${formatAttributeName(error.attribute_name)}</td>
            <td><code>${error.expected_value}</code></td>
            <td><code>${error.found_value || 'No detectado'}</code></td>
        `;
        list.appendChild(row);
    });
}

// ========================================
// MOSTRAR RECOMENDACIONES
// ========================================
function displayRecommendations(recommendations) {
    const card = document.getElementById('recommendationsCard');
    const list = document.getElementById('recommendationsList');

    card.style.display = 'block';
    list.innerHTML = '';

    recommendations.forEach(rec => {
        const item = document.createElement('li');
        item.innerHTML = `<i class="bi bi-check-circle-fill text-warning flex-shrink-0 mt-1"></i><span>${rec}</span>`;
        list.appendChild(item);
    });
}

// ========================================
// OBTENER BADGE DE ESTADO
// ========================================
function getStatusBadge(status) {
    const badges = {
        'Cumple':              '<span class="badge-complies"><i class="bi bi-check-circle-fill"></i> Cumple</span>',
        'Cumple parcialmente': '<span class="badge-partially"><i class="bi bi-exclamation-circle-fill"></i> Cumple Parcialmente</span>',
        'No cumple':           '<span class="badge-not-complies"><i class="bi bi-x-circle-fill"></i> No Cumple</span>'
    };
    return badges[status] || '<span class="badge bg-secondary">Desconocido</span>';
}

// ========================================
// VER REPORTE
// ========================================
function viewReport(productId) {
    fetch(`${API_BASE}report/${productId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentReport = data.report;
                displayResults(data.report);
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        })
        .catch(error => console.error('Error:', error));
}

// ========================================
// DESCARGAR PDF
// ========================================
function downloadPDF() {
    if (!currentReport) {
        showAlert('No hay reporte para descargar', 'danger');
        return;
    }

    showAlert('La funcionalidad de PDF estará disponible pronto', 'info');
    // Se implementará con reportlab en versión mejorada
}

// ========================================
// REINICIAR FORMULARIO
// ========================================
function resetForm() {
    document.getElementById('uploadForm').reset();
    document.getElementById('countrySelect').value = '';
    document.getElementById('fileInput').value = '';
    document.getElementById('resultContainer').style.display = 'none';
    document.getElementById('initialMessage').style.display = 'flex';
    document.getElementById('alertContainer').innerHTML = '';
    currentReport = null;

    const dropZone = document.getElementById('dropZone');
    const fileName = document.getElementById('fileName');
    if (dropZone) dropZone.classList.remove('has-file', 'drag-over');
    if (fileName) {
        fileName.textContent = 'PDF · DOCX · máx. 16 MB';
        fileName.className = 'badge bg-light text-muted';
    }

    const header = document.getElementById('attributesCardHeader');
    if (header) header.innerHTML = '<i class="bi bi-list-check me-2"></i>Atributos Extraídos';
}

// ========================================
// MOSTRAR PROGRESO
// ========================================
function showProgress(show) {
    const container = document.getElementById('progressContainer');
    const submitBtn = document.getElementById('submitBtn');

    if (show) {
        container.style.display = 'block';
        submitBtn.disabled = true;
    } else {
        container.style.display = 'none';
        submitBtn.disabled = false;
    }
}

// ========================================
// MOSTRAR ALERTA
// ========================================
function showAlert(message, type) {
    const container = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    container.innerHTML = '';
    container.appendChild(alert);

    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// ========================================
// DROP ZONE
// ========================================
function setupDropZone() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    if (!dropZone || !fileInput) return;

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            markDropZoneWithFile(e.dataTransfer.files[0].name);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            markDropZoneWithFile(fileInput.files[0].name);
        }
    });
}

function markDropZoneWithFile(name) {
    const dropZone = document.getElementById('dropZone');
    const fileName = document.getElementById('fileName');
    if (dropZone) dropZone.classList.add('has-file');
    if (fileName) {
        fileName.textContent = name;
        fileName.className = 'badge bg-success text-white';
    }
}

// ========================================
// BADGE DE FUENTE DE EXTRACCIÓN
// ========================================
function updateExtractionSourceBadge(source) {
    const header = document.getElementById('attributesCardHeader');
    if (!header) return;

    let badge = '';
    if (source === 'llm') {
        badge = '<span class="badge bg-success ms-2"><i class="bi bi-robot"></i> IA (OpenAI)</span>';
    } else if (source === 'regex') {
        badge = '<span class="badge bg-secondary ms-2"><i class="bi bi-code-slash"></i> Regex (Fallback)</span>';
    }

    header.innerHTML = `<i class="bi bi-list-check"></i> Atributos Extraídos ${badge}`;
}

// ========================================
// UTILIDADES
// ========================================
function cleanFileName(name) {
    return name.replace(/^\d{8}_\d{6}_/, '');
}

function formatAttributeName(name) {
    const names = {
        'empaquetado': 'Empaquetado',
        'ingredientes': 'Ingredientes',
        'peso': 'Peso',
        'fecha_vencimiento': 'Fecha de Vencimiento',
        'registro_fda': 'Registro FDA',
        'etiquetado_ingles': 'Etiquetado en Inglés',
        'pais_origen': 'País de Origen',
        'certificaciones': 'Certificaciones'
    };
    return names[name] || name;
}
