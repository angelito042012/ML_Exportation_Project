-- Schema MySQL para Clasificador de Exportación

CREATE DATABASE IF NOT EXISTS export_validation;
USE export_validation;

-- Tabla de Países
CREATE TABLE IF NOT EXISTS countries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Reglas de Exportación (Knowledge Base)
CREATE TABLE IF NOT EXISTS export_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    country_id INT NOT NULL,
    attribute_name VARCHAR(100) NOT NULL,
    operator VARCHAR(10) NOT NULL,
    expected_value VARCHAR(500) NOT NULL,
    recommendation VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (country_id) REFERENCES countries(id) ON DELETE CASCADE,
    INDEX idx_country_attribute (country_id, attribute_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Archivos de Productos (Historial)
CREATE TABLE IF NOT EXISTS product_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    country_id INT NOT NULL,
    extracted_attributes JSON,
    compliance_percentage DECIMAL(5, 2),
    final_status ENUM('COMPLIES', 'PARTIALLY_COMPLIES', 'NOT_COMPLIES') DEFAULT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_id) REFERENCES countries(id) ON DELETE CASCADE,
    INDEX idx_country_date (country_id, upload_date),
    INDEX idx_status (final_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Validaciones Detalladas (Errores y Observaciones)
CREATE TABLE IF NOT EXISTS validation_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_file_id INT NOT NULL,
    export_rule_id INT NOT NULL,
    attribute_name VARCHAR(100) NOT NULL,
    expected_value VARCHAR(500) NOT NULL,
    found_value VARCHAR(500),
    operator VARCHAR(10) NOT NULL,
    is_valid BOOLEAN DEFAULT FALSE,
    suggestion VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_file_id) REFERENCES product_files(id) ON DELETE CASCADE,
    FOREIGN KEY (export_rule_id) REFERENCES export_rules(id) ON DELETE CASCADE,
    INDEX idx_product_file (product_file_id),
    INDEX idx_export_rule (export_rule_id),
    INDEX idx_attribute (attribute_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Crear índices adicionales para optimización
CREATE INDEX idx_countries_name ON countries(name);
CREATE INDEX idx_rules_operator ON export_rules(operator);
