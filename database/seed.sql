-- Datos de Prueba para Clasificador de Exportación
USE export_validation;

-- Insertar Países
INSERT INTO countries (name) VALUES 
('Honduras'),
('México'),
('Colombia'),
('Estados Unidos'),
('Unión Europea'),
('Canadá'),
('Japón'),
('Australia'),
('China'),
('Brasil');

-- Reglas para Honduras (id=1)
INSERT INTO export_rules (country_id, attribute_name, operator, expected_value, recommendation) VALUES
(1, 'empaquetado', '=', 'plástico', 'Utilizar empaque de plástico resistente'),
(1, 'ingredientes', 'contains', 'pectina', 'Asegurar que contiene pectina de calidad'),
(1, 'ingredientes', 'contains', 'azúcar', 'Verificar contenido de azúcar'),
(1, 'peso', '<=', '5kg', 'El peso total no debe exceder 5 kg'),
(1, 'fecha_vencimiento', '>=', '2026-08-01', 'La fecha de vencimiento debe ser posterior a agosto 2026');

-- Reglas para México (id=2)
INSERT INTO export_rules (country_id, attribute_name, operator, expected_value, recommendation) VALUES
(2, 'empaquetado', '=', 'vidrio', 'Utilizar envases de vidrio de calidad'),
(2, 'ingredientes', 'contains', 'preservantes', 'Debe contener preservantes permitidos'),
(2, 'peso', '<=', '10kg', 'Peso máximo permitido: 10 kg'),
(2, 'fecha_vencimiento', '>=', '2026-08-05', 'Fecha de vencimiento mínima: agosto 2026');

-- Reglas para Colombia (id=3)
INSERT INTO export_rules (country_id, attribute_name, operator, expected_value, recommendation) VALUES
(3, 'empaquetado', '=', 'cartón', 'Empaque de cartón reciclable'),
(3, 'ingredientes', 'contains', 'colorantes artificiales', 'Los colorantes deben ser permitidos en Colombia'),
(3, 'peso', '<=', '8kg', 'Peso máximo: 8 kg'),
(3, 'fecha_vencimiento', '>=', '2026-09-15', 'Vencimiento mínimo: 15 de septiembre 2026');

-- Reglas para Estados Unidos (id=4)
INSERT INTO export_rules (country_id, attribute_name, operator, expected_value, recommendation) VALUES
(4, 'empaquetado', '=', 'plástico', 'Empaque que cumpla con normativas FDA'),
(4, 'registro_fda', '=', 'sí', 'Debe tener registro FDA'),
(4, 'etiquetado_ingles', '=', 'sí', 'Etiquetado obligatorio en inglés'),
(4, 'fecha_vencimiento', '>=', '2026-08-01', 'Vencimiento posterior a agosto 2026');

-- Reglas para Unión Europea (id=5)
INSERT INTO export_rules (country_id, attribute_name, operator, expected_value, recommendation) VALUES
(5, 'empaquetado', '=', 'vidrio', 'Empaque de vidrio reciclable'),
(5, 'ingredientes', 'contains', 'organismos modificados', 'Debe cumplir regulaciones GMO'),
(5, 'fecha_vencimiento', '>=', '2026-09-01', 'Vencimiento europeo mínimo');

-- Reglas para Canadá (id=6)
INSERT INTO export_rules (country_id, attribute_name, operator, expected_value, recommendation) VALUES
(6, 'empaquetado', '=', 'plástico', 'Empaque biodegradable preferido'),
(6, 'etiquetado_ingles', '=', 'sí', 'Etiquetas en inglés requeridas'),
(6, 'peso', '<=', '12kg', 'Peso máximo permitido'),
(6, 'fecha_vencimiento', '>=', '2026-10-01', 'Vencimiento mínimo canadiense');

-- Reglas para Japón (id=7)
INSERT INTO export_rules (country_id, attribute_name, operator, expected_value, recommendation) VALUES
(7, 'empaquetado', '=', 'vidrio', 'Empaque de vidrio de alta calidad'),
(7, 'peso', '<=', '3kg', 'Peso máximo muy restrictivo'),
(7, 'fecha_vencimiento', '>=', '2026-11-01', 'Vencimiento muy exigente para Japón');

-- Reglas para Australia (id=8)
INSERT INTO export_rules (country_id, attribute_name, operator, expected_value, recommendation) VALUES
(8, 'empaquetado', '=', 'cartón', 'Empaque de cartón certificado'),
(8, 'ingredientes', 'contains', 'pesticidas', 'Verificar límites de residuos de pesticidas'),
(8, 'peso', '<=', '6kg', 'Peso máximo permitido');

-- Reglas para China (id=9)
INSERT INTO export_rules (country_id, attribute_name, operator, expected_value, recommendation) VALUES
(9, 'empaquetado', '=', 'plástico', 'Empaque plástico resistente'),
(9, 'ingredientes', 'contains', 'aditivos', 'Aditivos deben estar registrados'),
(9, 'peso', '<=', '15kg', 'Peso máximo permitido');

-- Reglas para Brasil (id=10)
INSERT INTO export_rules (country_id, attribute_name, operator, expected_value, recommendation) VALUES
(10, 'empaquetado', '=', 'vidrio', 'Empaque de vidrio preferido'),
(10, 'ingredientes', 'contains', 'azúcar', 'Azúcar local certificada'),
(10, 'peso', '<=', '7kg', 'Peso máximo permitido'),
(10, 'fecha_vencimiento', '>=', '2026-12-01', 'Vencimiento mínimo brasileño');
