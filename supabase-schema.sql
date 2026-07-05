-- =============================================================================
-- Compa — Supabase SQL Schema (con 51 proveedores REALES del registro público)
-- Buildathon 4 Julio 2026 | Fuente: UNIDAD DE COMPRAS PUBLICAS, jul-sep 2025
-- =============================================================================

-- =============================================================================
-- 1. TABLA: productores (sintéticos de Nemotron + fallback)
-- =============================================================================
CREATE TABLE IF NOT EXISTS productores (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre      TEXT NOT NULL,
    rubro       TEXT NOT NULL,
    ubicacion   TEXT,
    capacidad   TEXT,
    telefono    TEXT,
    dui         TEXT,
    nit         TEXT,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_productores_rubro     ON productores(rubro);
CREATE INDEX IF NOT EXISTS idx_productores_ubicacion ON productores(ubicacion);

-- =============================================================================
-- 2. TABLA: oportunidades (sintéticas estilo COMPRASAL, generadas de rubros reales)
-- =============================================================================
CREATE TABLE IF NOT EXISTS oportunidades (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo            TEXT NOT NULL,
    institucion       TEXT NOT NULL,
    monto             DECIMAL(12,2) NOT NULL,
    fecha_cierre      DATE NOT NULL,
    rubro_requerido   TEXT NOT NULL,
    unspsc_code       TEXT,
    url_fuente        TEXT,
    tipo_contratacion TEXT,
    created_at        TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_oportunidades_rubro ON oportunidades(rubro_requerido);
CREATE INDEX IF NOT EXISTS idx_oportunidades_fecha ON oportunidades(fecha_cierre);

-- =============================================================================
-- 3. TABLA: proveedores — 51 PROVEEDORES REALES del registro público
--    Fuente: UNIDAD DE COMPRAS PUBLICAS, Registro de Contratistas jul-sep 2025
-- =============================================================================
CREATE TABLE IF NOT EXISTS proveedores (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre            TEXT NOT NULL,
    clasificacion     TEXT,
    rubro             TEXT NOT NULL,
    descripcion       TEXT,
    ubicacion         TEXT,
    telefono          TEXT,
    created_at        TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_proveedores_rubro ON proveedores(rubro);

-- =============================================================================
-- 4. TABLA: decisiones
-- =============================================================================
CREATE TABLE IF NOT EXISTS decisiones (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    productor_id      UUID REFERENCES productores(id) ON DELETE CASCADE,
    decision_descrita TEXT NOT NULL,
    preguntas_json    JSONB,
    reasoning_trace   TEXT,
    created_at        TIMESTAMPTZ DEFAULT now()
);

-- =============================================================================
-- 5. RLS permisivo (demo, sin autenticación)
-- =============================================================================
ALTER TABLE productores   ENABLE ROW LEVEL SECURITY;
ALTER TABLE oportunidades ENABLE ROW LEVEL SECURITY;
ALTER TABLE proveedores   ENABLE ROW LEVEL SECURITY;
ALTER TABLE decisiones    ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "all_access" ON productores   FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "all_access" ON oportunidades FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "all_access" ON proveedores   FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "all_access" ON decisiones    FOR ALL USING (true) WITH CHECK (true);

-- =============================================================================
-- 6. SEED: productores (5 sintéticos para demo)
-- =============================================================================
INSERT INTO productores (nombre, rubro, ubicacion, capacidad, telefono, dui, nit) VALUES
('Vilma Jeanneth Guardado de Ayala', 'Alimentos y Bebidas', 'Cantón El Zapote, San Juan Opico, La Libertad', '500 almuerzos/día', '+50377234567', '02734457-8', '0614-270479-105-7'),
('Carlos Alberto Mejía López', 'Textiles y Uniformes', 'Colonia Escalón, San Salvador', '2000 uniformes/mes', '+50378901234', '04567891-2', '0614-150389-101-3'),
('María Elena Rivas de Hernández', 'Mobiliario y Equipo', 'Ciudad Arce, La Libertad', '100 pupitres/semana', '+50370123456', '03124567-8', '0614-220592-109-1'),
('Pedro Antonio Sorto García', 'Construcción y Materiales', 'Soyapango, San Salvador', '50 m³ concreto/semana', '+50375678901', '05678901-2', '0614-100183-101-5'),
('Ana Beatriz Cruz de Lemus', 'Servicios Generales', 'Santa Tecla, La Libertad', '30 instalaciones/mes', '+50372345678', '03456789-0', '0614-051290-103-9'),
-- Nuevos productores: micro/pequeñas empresas REALES del registro público (ya vendieron al Estado)
('César Rolando Contreras Obispo', 'Construcción y Materiales', 'San Salvador, San Salvador', 'Mantenimiento de infraestructura gubernamental', '+50372561478', '04256987-3', '0614-150881-102-6'),
('Milton Ernesto Cea Panameño', 'Tecnología', 'San Salvador, San Salvador', 'Desarrollo PowerBuilder/Oracle', '+50379854123', '05123456-7', '0614-201192-105-2'),
('Óscar Armando Ocón Díaz', 'Tecnología', 'Santa Tecla, La Libertad', 'Soporte SONARQUBE Enterprise', '+50371239876', '04789123-5', '0614-180690-103-4'),
('Karen Yamileth Hernández de Méndez', 'Alimentos y Bebidas', 'Soyapango, San Salvador', 'Refrigerios y catering para eventos', '+50374561230', '05214789-6', '0614-110588-104-8'),
('Norma Eloisa Romero Medrano', 'Suministros Médicos', 'San Miguel, San Miguel', 'Botiquines y equipos médicos', '+50376894512', '03874561-2', '0614-220384-101-9'),
('María Zoila Aguilar Pineda', 'Imprenta y Papelería', 'San Salvador, San Salvador', 'Impresos Unidos Salvadoreños - Formularios oficiales', '+50372369874', '03698741-0', '0614-080479-103-5'),
('José Cecilio Tobar Valle', 'Imprenta y Papelería', 'Santa Ana, Santa Ana', 'IMPRESOS DILEFRAN - Impresos comerciales', '+50378965412', '04512369-8', '0614-140286-105-1'),
('Dora Enelsa Castro Borja', 'Mobiliario y Equipo', 'San Salvador, San Salvador', 'DIVERSUS HOME - Electrodomésticos para oficina', '+50375632148', '04123789-5', '0614-250691-104-3'),
('María Susana Mejía Argueta', 'Comercio y Distribución', 'San Salvador, San Salvador', 'DISTRIBUIDORA SALVADOREÑA - Insumos para negocios', '+50378963214', '05369874-1', '0614-200889-106-2'),
('Ronald Onil Serrano Texin', 'Transporte y Logística', 'San Salvador, San Salvador', 'TRANS ARGENTINA - Transporte de personal', '+50370123698', '04789632-5', '0614-170492-102-7');

-- =============================================================================
-- 7. SEED: oportunidades (25 — generadas de los rubros reales de los 51 proveedores)
-- =============================================================================
INSERT INTO oportunidades (titulo, institucion, monto, fecha_cierre, rubro_requerido, unspsc_code, url_fuente, tipo_contratacion) VALUES
-- Alimentos y Bebidas (match Vilma)
('Servicio de Alimentación Escolar - Distrito 04-25', 'MINEDUCYT', 48750.00, '2026-07-18', 'Alimentos y Bebidas', '50200000', 'https://www.comprasal.gob.sv/licitaciones/lp-07-2026-mined', 'LP'),
('Servicio de Cafetería - Edificio Central ANDA', 'ANDA', 28400.00, '2026-07-22', 'Alimentos y Bebidas', '50200000', 'https://www.comprasal.gob.sv/libre-gestion/lg-12-2026-anda', 'LG'),
('Suministro de Botellas de Agua para SEDE', 'Ministerio de Hacienda', 8750.00, '2026-07-10', 'Alimentos y Bebidas', '50202301', 'https://www.comprasal.gob.sv/libre-gestion/lg-08-2026-mh', 'LG'),
(' Servicio de Catering para Eventos Institucionales', 'Ministerio de Hacienda', 4200.00, '2026-07-05', 'Alimentos y Bebidas', '90101601', 'https://www.comprasal.gob.sv/contrataciones/cd-03-2026-mh', 'CD'),

-- Imprenta y Papelería (rubro #1 del registro — 16 proveedores reales)
('Adquisición de Formularios, Viñetas y Sobres Impresos', 'Ministerio de Hacienda', 45200.00, '2026-07-15', 'Imprenta y Papelería', '82121501', 'https://www.comprasal.gob.sv/licitaciones/lp-11-2026-mh', 'LP'),
('Suministro de Especies Municipales Forma Plana', 'Ministerio de Hacienda', 38500.00, '2026-07-20', 'Imprenta y Papelería', '82121502', 'https://www.comprasal.gob.sv/libre-gestion/lg-15-2026-mh', 'LG'),
('Suministro de Papelería y Útiles de Oficina', 'Ministerio de Hacienda', 22100.00, '2026-07-08', 'Imprenta y Papelería', '14111500', 'https://www.comprasal.gob.sv/libre-gestion/lg-09-2026-mh', 'LG'),
('Servicio de Encuadernado y Empastado de Diarios Oficiales', 'Ministerio de Hacienda', 5600.00, '2026-07-25', 'Imprenta y Papelería', '82121503', 'https://www.comprasal.gob.sv/contrataciones/cd-07-2026-mh', 'CD'),

-- Tecnología (8 proveedores reales)
('Adquisición de ACCESS POINTS para Red Inalámbrica', 'Ministerio de Hacienda', 67200.00, '2026-07-28', 'Tecnología', '43222600', 'https://www.comprasal.gob.sv/licitaciones/lp-14-2026-mh', 'LP'),
('Adquisición de UPS para Dirección General de Aduanas', 'Ministerio de Hacienda (DGA)', 18900.00, '2026-07-12', 'Tecnología', '39121000', 'https://www.comprasal.gob.sv/libre-gestion/lg-10-2026-dga', 'LG'),
('Suscripción de Software AUTODESK AEC COLLECTION 2025', 'Ministerio de Hacienda', 24500.00, '2026-07-05', 'Tecnología', '43230000', 'https://www.comprasal.gob.sv/libre-gestion/lg-06-2026-mh', 'LG'),
('Suscripción Licencia ADOBE CREATIVE CLOUD', 'Ministerio de Hacienda', 12300.00, '2026-07-03', 'Tecnología', '43232100', 'https://www.comprasal.gob.sv/contrataciones/cd-04-2026-mh', 'CD'),
('Servicios de Desarrollo de Sistemas', 'Ministerio de Hacienda', 115000.00, '2026-08-01', 'Tecnología', '81111500', 'https://www.comprasal.gob.sv/licitaciones/lp-16-2026-mh', 'LP'),

-- Servicios de Mantenimiento (6 proveedores reales)
('Mantenimiento Preventivo y Correctivo de Equipos Médicos', 'Ministerio de Hacienda', 32600.00, '2026-07-22', 'Servicios de Mantenimiento', '81101500', 'https://www.comprasal.gob.sv/libre-gestion/lg-16-2026-mh', 'LG'),
('Mantenimiento de Sistema de Detención de Incendios', 'Ministerio de Hacienda (DGA)', 15300.00, '2026-07-11', 'Servicios de Mantenimiento', '72101500', 'https://www.comprasal.gob.sv/contrataciones/cd-08-2026-dga', 'CD'),
('Mantenimiento de Extractores de Aire - Laboratorio DGA', 'Ministerio de Hacienda (DGA)', 8700.00, '2026-07-06', 'Servicios de Mantenimiento', '72151200', 'https://www.comprasal.gob.sv/contrataciones/cd-06-2026-dga', 'CD'),
('Recarga de Gases y Mantenimiento de Red de Gases - Laboratorio DGA', 'Ministerio de Hacienda (DGA)', 12400.00, '2026-07-14', 'Servicios de Mantenimiento', '72120000', 'https://www.comprasal.gob.sv/libre-gestion/lg-11-2026-dga', 'LG'),

-- Construcción y Mantenimiento (4 proveedores)
('Readecuación de Espacios Físicos y Reparación de Techos', 'Ministerio de Hacienda', 98500.00, '2026-07-30', 'Construcción y Materiales', '72101500', 'https://www.comprasal.gob.sv/licitaciones/lp-15-2026-mh', 'LP'),
('Mantenimiento de Infraestructura - Edificio Central', 'Ministerio de Hacienda', 28700.00, '2026-07-18', 'Construcción y Materiales', '72120000', 'https://www.comprasal.gob.sv/libre-gestion/lg-14-2026-mh', 'LG'),

-- Suministros de Laboratorio (4 proveedores)
('Suministro de Consumibles para Laboratorio DGA', 'Ministerio de Hacienda (DGA)', 23400.00, '2026-07-09', 'Suministros de Laboratorio', '41100000', 'https://www.comprasal.gob.sv/libre-gestion/lg-07-2026-dga', 'LG'),
('Suministro de Consumibles y Cristalería para Laboratorio', 'Ministerio de Hacienda (DGA)', 15100.00, '2026-07-16', 'Suministros de Laboratorio', '41103000', 'https://www.comprasal.gob.sv/libre-gestion/lg-13-2026-dga', 'LG'),

-- Textiles y Uniformes (match Carlos Mejía)
('Adquisición de Chumpas, Gorras, Chalecos y Calzado de Seguridad', 'Ministerio de Hacienda', 34200.00, '2026-07-21', 'Textiles y Uniformes', '53102500', 'https://www.comprasal.gob.sv/libre-gestion/lg-17-2026-mh', 'LG'),
('Confección de Uniformes - Personal Operativo DGA', 'Ministerio de Hacienda (DGA)', 18900.00, '2026-07-13', 'Textiles y Uniformes', '53102700', 'https://www.comprasal.gob.sv/contrataciones/cd-09-2026-dga', 'CD'),

-- Mobiliario y Equipo (3 proveedores)
('Suministro de Mobiliario para Dirección General', 'Ministerio de Hacienda', 45600.00, '2026-07-19', 'Mobiliario y Equipo', '56101500', 'https://www.comprasal.gob.sv/licitaciones/lp-13-2026-mh', 'LP'),
('Adquisición de Electrodomésticos para DGA', 'Ministerio de Hacienda (DGA)', 14300.00, '2026-07-07', 'Mobiliario y Equipo', '52141500', 'https://www.comprasal.gob.sv/contrataciones/cd-05-2026-dga', 'CD'),

-- Suministros Médicos (2 proveedores)
('Suministro de Insumos Médicos para Clínicas Empresariales', 'Ministerio de Hacienda', 28700.00, '2026-07-17', 'Suministros Médicos', '42140000', 'https://www.comprasal.gob.sv/libre-gestion/lg-18-2026-mh', 'LG'),
('Adquisición de Botiquines para DGA', 'Ministerio de Hacienda (DGA)', 3200.00, '2026-07-04', 'Suministros Médicos', '42140000', 'https://www.comprasal.gob.sv/contrataciones/cd-02-2026-dga', 'CD'),

-- Servicios Profesionales
('Auditoría Externa del Programa de Transformación del Clima de Negocios', 'Ministerio de Hacienda', 78000.00, '2026-07-29', 'Servicios Profesionales', '84111500', 'https://www.comprasal.gob.sv/licitaciones/lp-12-2026-mh', 'LP'),

-- Servicios Financieros
('Adquisición de Póliza de Seguro de Responsabilidad Civil', 'Ministerio de Hacienda', 42000.00, '2026-07-24', 'Servicios Financieros', '84131600', 'https://www.comprasal.gob.sv/libre-gestion/lg-19-2026-mh', 'LG'),

-- Suministros de Limpieza
('Adquisición de Papel Higiénico Jumbo y Dispensadores para DGA', 'Ministerio de Hacienda (DGA)', 8700.00, '2026-07-02', 'Suministros de Limpieza', '14111700', 'https://www.comprasal.gob.sv/contrataciones/cd-01-2026-dga', 'CD'),

-- Servicios Ambientales
('Mantenimiento de Sistema de Filtración de Agua - Aduana El Poy', 'Ministerio de Hacienda (DGA)', 11400.00, '2026-07-23', 'Servicios Ambientales', '70170000', 'https://www.comprasal.gob.sv/libre-gestion/lg-20-2026-dga', 'LG'),
-- NUEVAS OPORTUNIDADES (rubros descubiertos en ene-mar 2026 y clasificación 2019)
('Servicio de Transporte Colectivo para Empleados', 'Ministerio de Hacienda', 52300.00, '2026-07-25', 'Transporte y Logística', '78110000', 'https://www.comprasal.gob.sv/licitaciones/lp-18-2026-mh', 'LP'),
('Servicio de Imagen y Agencia de Publicidad Institucional', 'Ministerio de Hacienda', 36700.00, '2026-07-19', 'Servicios de Publicidad', '82140000', 'https://www.comprasal.gob.sv/libre-gestion/lg-22-2026-mh', 'LG'),
('Servicio de Recolección y Traslado de Paquetería y Correspondencia', 'Ministerio de Hacienda', 18900.00, '2026-07-11', 'Servicios de Mensajería', '78110000', 'https://www.comprasal.gob.sv/contrataciones/cd-11-2026-mh', 'CD'),
('Adquisición de Trofeos y Artículos Deportivos para Juegos Institucionales', 'Ministerio de Hacienda', 12400.00, '2026-07-06', 'Artículos Deportivos', '49120000', 'https://www.comprasal.gob.sv/contrataciones/cd-10-2026-mh', 'CD'),
('Servicio de Suscripción de Periódicos para Oficinas de Gobierno', 'Ministerio de Hacienda', 8700.00, '2026-07-26', 'Medios y Suscripciones', '55101500', 'https://www.comprasal.gob.sv/libre-gestion/lg-23-2026-mh', 'LG'),
('Suministro de Café y Azúcar para Dependencias Gubernamentales', 'Ministerio de Hacienda', 15200.00, '2026-07-08', 'Alimentos y Bebidas', '50200000', 'https://www.comprasal.gob.sv/comparacion-precios/cp-03-2026-mh', 'CP'),
('Solución de Google Cloud para Modernización de Entidades del Estado', 'Gobierno de El Salvador', 485000.00, '2026-08-15', 'Tecnología', '81110000', 'https://www.comprasal.gob.sv/alianza-estrategica/afa-01-2026-google', 'AFA'),
('Servicio de Almacenamiento en la Nube para Aplicativos Gubernamentales', 'Gobierno de El Salvador', 235000.00, '2026-08-01', 'Tecnología', '81110000', 'https://www.comprasal.gob.sv/contrataciones/cd-12-2026-mh', 'CD'),
('Servicio de Educación para Hijos de Empleados del Ministerio', 'Ministerio de Hacienda', 98000.00, '2026-07-30', 'Servicios Educativos', '86130000', 'https://www.comprasal.gob.sv/convenios/cv-01-2026-mh', 'CV'),
('Servicio de Limpieza de Fosas Sépticas para DGA', 'Ministerio de Hacienda (DGA)', 17800.00, '2026-07-09', 'Servicios de Limpieza', '76120000', 'https://www.comprasal.gob.sv/libre-gestion/lg-21-2026-dga', 'LG');

-- =============================================================================
-- 8. SEED: proveedores — 51 REALES del Registro de Contratistas jul-sep 2025
--     Fuente: UNIDAD DE COMPRAS PUBLICAS, Gobierno de El Salvador
-- =============================================================================
INSERT INTO proveedores (nombre, clasificacion, rubro, descripcion) VALUES
-- Imprenta y Papelería (16)
('PRINT RUNNING, S.A. DE C.V.', 'Micro Empresa', 'Imprenta y Papelería', 'Formularios, viñetas, sobres impresos y talonarios para el Ministerio de Hacienda'),
('UH INTERNACIONAL', 'Pequeña Empresa', 'Imprenta y Papelería', 'Formularios, viñetas, sobres impresos y talonarios para el Ministerio de Hacienda'),
('IMPRESOS DOBLE G, S.A. DE C.V.', 'Micro Empresa', 'Imprenta y Papelería', 'Formularios, viñetas, sobres impresos y talonarios para el Ministerio de Hacienda'),
('EDITORIAL E IMPRESORA PANAMERICANA, S.A. DE C.V.', 'Micro Empresa', 'Imprenta y Papelería', 'Formularios, viñetas, sobres impresos y talonarios para el Ministerio de Hacienda'),
('LANDOS, S.A. DE C.V.', 'Micro Empresa', 'Imprenta y Papelería', 'Formularios, especies municipales forma plana, encuadernado y empastado de diarios oficiales'),
('MARÍA ZOILA AGUILAR PINEDA (IMPRESOS UNIDOS SALVADOREÑOS)', 'Pequeña Empresa', 'Imprenta y Papelería', 'Formularios, viñetas, sobres impresos y talonarios para el Ministerio de Hacienda'),
('FORMULARIOS STANDARD, S.A. DE C.V.', 'Mediana Empresa', 'Imprenta y Papelería', 'Especies municipales forma plana'),
('RR DONNELEY DE EL SALVADOR, S.A. DE C.V.', 'Gran Empresa', 'Imprenta y Papelería', 'Especies municipales forma plana'),
('RZ, S.A. DE C.V.', 'Pequeña Empresa', 'Imprenta y Papelería', 'Papelería y útiles de oficina para la Dirección General de Aduanas'),
('OLG SERVICE, S.A. DE C.V.', 'Pequeña Empresa', 'Imprenta y Papelería', 'Papelería y útiles de oficina para la Dirección General de Aduanas'),
('PAPELERA SAN REY, S.A. DE C.V.', 'Mediana Empresa', 'Imprenta y Papelería', 'Papelería y útiles de oficina para la Secretaría de Estado'),
('NOE ALBERTO GUILLEN (LIBRERÍA Y PAPELERÍA LA NUEVA SAN SALVADOR)', 'Mediana Empresa', 'Imprenta y Papelería', 'Papelería y útiles de oficina para la Secretaría de Estado'),
('DPG, S.A. DE C.V.', 'Mediana Empresa', 'Imprenta y Papelería', 'Papelería y útiles de oficina para la Secretaría de Estado'),
('BUSINESS CENTER, S.A. DE C.V.', 'Mediana Empresa', 'Imprenta y Papelería', 'Papelería y útiles de oficina para la Dirección General de Tesorería'),
('LIBRERÍA CERVANTES, S.A. DE C.V.', 'Mediana Empresa', 'Imprenta y Papelería', 'Papelería y útiles de oficina para la Dirección General de Tesorería'),
('LANDOS, S.A. DE C.V. (Encuadernados)', 'Micro Empresa', 'Imprenta y Papelería', 'Servicio de encuadernado y empastado de diarios oficiales, registros de entrada y salida de documentos'),

-- Tecnología (8)
('COMUNICACIONES IBW EL SALVADOR, S.A. DE C.V.', 'Gran Empresa', 'Tecnología', 'ACCESS POINTS para la Red Inalámbrica del Ministerio de Hacienda'),
('CRM SOLUTIONS, S.A. DE C.V.', 'Pequeña Empresa', 'Tecnología', 'UPS para la Dirección General de Aduanas'),
('BIT OFFICE EL SALVADOR (Sandra Patricia Vásquez Hernández)', 'Micro Empresa', 'Tecnología', 'Reloj Marcador para el registro de correspondencia'),
('MT2005, S.A. DE C.V.', 'Pequeña Empresa', 'Tecnología', 'Reforzamiento de memoria principal RAM para solución VMWARE HCI del Ministerio de Hacienda'),
('GRUPO OCTO, S.A. DE C.V.', 'Pequeña Empresa', 'Tecnología', 'Suscripción del software AUTODESK AEC COLLECTION versión 2025 o superior'),
('PBS EL SALVADOR, S.A. DE C.V.', 'Gran Empresa', 'Tecnología', 'Servicios de desarrollo de sistemas y suscripción SONARQUBE ENTERPRISE'),
('SPC INTERNACIONAL, S.A. DE C.V.', 'Pequeña Empresa', 'Tecnología', 'Soporte de Equipos CISCO MDS del Ministerio de Hacienda'),
('STB COMPUTER, S.A. DE C.V.', 'Mediana Empresa', 'Tecnología', 'Suscripción de Licencia ADOBE CREATIVE CLOUD para el departamento de formación'),

-- Servicios de Mantenimiento (6)
('INGENIERIA BIO PRO S.A.S DE C.V.', 'Micro Empresa', 'Servicios de Mantenimiento', 'Mantenimiento preventivo y correctivo para equipos médicos de clínicas empresariales del Ministerio de Hacienda'),
('ISERTEC DE EL SALVADOR, S.A. DE C.V.', 'Mediana Empresa', 'Servicios de Mantenimiento', 'Mantenimiento preventivo y correctivo, desmontaje y traslado para sistema de detención'),
('AIR AND ELECTRIC SERVICE, S.A. DE C.V.', 'Micro Empresa', 'Servicios de Mantenimiento', 'Mantenimiento Preventivo y Correctivo para Extractores de Aire en Laboratorio de Merceología DGA'),
('INFRA DE EL SALVADOR, S.A. DE C.V.', 'Gran Empresa', 'Servicios de Mantenimiento', 'Recarga de Gases y Mantenimiento Preventivo y Correctivo a Red de Gases del Laboratorio DGA'),
('ABJ INVERSORES, S.A. DE C.V.', 'Pequeña Empresa', 'Servicios de Mantenimiento', 'Mantenimiento preventivo y correctivo del sistema de detención de incendios en Laboratorio DGA'),
('SUPLIDORES DIVERSOS, S.A. DE C.V.', 'Mediana Empresa', 'Servicios de Mantenimiento', 'Insumos Médicos para las 4 clínicas empresariales del Ministerio de Hacienda'),

-- Construcción y Mantenimiento (4)
('CESAR ROLANDO CONTRERAS OBISPO (CROBISPO)', 'Micro Empresa', 'Construcción y Materiales', 'Mantenimiento preventivo y correctivo en infraestructura y readecuación de espacios físicos del Ministerio de Hacienda'),
('INGEREZ, S.A. DE C.V.', 'Pequeña Empresa', 'Construcción y Materiales', 'Mantenimiento preventivo y correctivo en la infraestructura del Ministerio de Hacienda'),
('INESERMA, S.A. DE C.V.', 'Pequeña Empresa', 'Construcción y Materiales', 'Readecuación de espacios físicos y reparación de techos en oficinas, bodegas y salones del Ministerio de Hacienda'),
('CONSULTORIA, MEDIO AMBIENTE Y SOLUCIONES, S.A. DE C.V.', 'Micro Empresa', 'Construcción y Materiales', 'Mantenimiento preventivo y correctivo al sistema de filtración para remoción de hierro y manganeso - Aduana El Poy'),

-- Suministros de Laboratorio (4)
('INSTRUQUIMICA, S.A. DE C.V.', 'Pequeña Empresa', 'Suministros de Laboratorio', 'Consumibles para el departamento de laboratorio de la Dirección General de Aduanas'),
('COMERCIO Y REPRESENTACIONES, S.A. DE C.V.', 'Mediana Empresa', 'Suministros de Laboratorio', 'Consumibles para el departamento de laboratorio de la Dirección General de Aduanas'),
('RGH DE EL SALVADOR', 'Mediana Empresa', 'Suministros de Laboratorio', 'Consumibles para el departamento de laboratorio de la Dirección General de Aduanas'),
('CARLOS ORLANDO ROMERO CALLES', 'Mediana Empresa', 'Suministros de Laboratorio', 'Consumibles y Cristalería para el Laboratorio de Merceología de la Dirección General de Aduanas'),

-- Alimentos y Bebidas (1 + 1 del registro)
('INVERSIONES VIDA, S.A. DE C.V.', 'Gran Empresa', 'Alimentos y Bebidas', 'Botellas de agua para SEDE del Ministerio de Hacienda'),
('FUNDACION EMPRESARIAL PARA EL DESARROLLO EDUCATIVO (FEPADE)', 'Mediana Empresa', 'Alimentos y Bebidas', 'Servicios de Auditorio y Refrigerio para Coloquio del Ministerio de Hacienda'),

-- Textiles y Uniformes (1)
('MULTIPROMOCIONES, S.A. DE C.V.', 'Pequeña Empresa', 'Textiles y Uniformes', 'Chumpas, Gorras, Chalecos, Capas Impermeables, Mochilas y Calzado de seguridad para personal operativo de la DGA'),

-- Mobiliario y Equipo (3)
('PROBIGE, S.A. DE C.V.', 'Pequeña Empresa', 'Mobiliario y Equipo', 'Mobiliario para la Dirección General del Presupuesto del Ministerio de Hacienda'),
('DORA ENELSA CASTRO BORJA (DIVERSUS HOME)', 'Micro Empresa', 'Mobiliario y Equipo', 'Electrodomésticos para la Dirección General de Aduanas'),
('BTECH SOLUCIONES INTEGRALES, S.A. DE C.V.', 'Pequeña Empresa', 'Mobiliario y Equipo', 'Electrodomésticos para la Dirección General de Aduanas'),

-- Servicios Profesionales (1)
('MURCIA Y MURCIA, S.A. DE C.V.', 'Pequeña Empresa', 'Servicios Profesionales', 'Auditoría externa del programa para la transformación del clima de negocios de El Salvador CFA-12031'),

-- Servicios Financieros (1)
('SEGUROS FEDECREDITO, S.A.', 'Mediana Empresa', 'Servicios Financieros', 'Póliza de seguro de Responsabilidad Civil para el Ministerio de Hacienda'),

-- Suministros Médicos (2)
('NORMA ELOISA ROMERO MEDRANO (Medical Systems El Salvador)', 'Pequeña Empresa', 'Suministros Médicos', 'Botiquines para la Dirección General de Aduanas'),
('SUPLIDORES DIVERSOS, S.A. DE C.V. (Médico)', 'Mediana Empresa', 'Suministros Médicos', 'Insumos Médicos para las 4 clínicas empresariales del Ministerio de Hacienda'),

-- Suministros de Limpieza (1)
('D''QUISA, S.A. DE C.V.', 'Mediana Empresa', 'Suministros de Limpieza', 'Papel Higiénico Jumbo y dispensadores para la Dirección General de Aduanas'),

-- Servicios Ambientales (1)
('CONSULTORIA, MEDIO AMBIENTE Y SOLUCIONES, S.A. DE C.V. (Ambiental)', 'Micro Empresa', 'Servicios Ambientales', 'Mantenimiento a sistema de filtración para Remoción de Hierro y Manganeso y Suministro de Hipoclorito de sodio para Aduana El Poy'),

-- =============================================================================
-- 8.2 NUEVOS PROVEEDORES (ene-mar 2026 + clasificación 2019)
-- =============================================================================
-- Transporte y Logística (nuevo rubro)
('TRANSPORTES ARGUETA, S.A. DE C.V.', 'Micro Empresa', 'Transporte y Logística', 'Servicio de transporte colectivo y jornada extraordinaria para empleados del Ministerio de Hacienda'),
('TRANSPORTES ALAS S.A. DE C.V.', 'Mediana Empresa', 'Transporte y Logística', 'Servicio de transporte colectivo para empleados del Ministerio de Hacienda'),
('URBANO EXPRESS, S.A. DE C.V.', 'Sin clasificar', 'Transporte y Logística', 'Servicios de mensajería y paquetería'),

-- Tecnología (nuevos)
('ETS CONSULTING, S.A. DE C.V.', 'Mediana Empresa', 'Tecnología', 'Servicio de soporte técnico para infraestructura de balanceo de aplicaciones ADC del Ministerio de Hacienda'),
('GBM DE EL SALVADOR, S.A. DE C.V.', 'Gran Empresa', 'Tecnología', 'Soporte UPS, CISCO, IBM Cognos Analytics e Infosphere Information Server para Ministerio de Hacienda'),
('TELEMOVIL EL SALVADOR, S.A. DE CV.', 'Gran Empresa', 'Tecnología', 'Enlace de internet satelital para respaldo DGA y CloudFlare Application Security Advanced WAF'),
('AMAZON WEB SERVICES, INC', 'Gran Empresa', 'Tecnología', 'Servicios de almacenamiento en la nube para despliegue de aplicativos gubernamentales'),
('GOOGLE LLC', 'Gran Empresa', 'Tecnología', 'Google Cloud, Workspace, CrowdStrike Falcon Cloud Security para Gobierno de El Salvador'),
('DATAGUARDS, S.A. DE C.V.', 'Mediana Empresa', 'Tecnología', 'Servicio de alojamiento físico para equipos TIC del centro de datos MH (colocation)'),
('UDP ASOCIO GRUPO PLUS-CONFICO', 'Pequeña Empresa', 'Tecnología', 'Servicio de soporte técnico especializado para plataforma BPM AuraQuantic del MH'),
('COMPONENTES EL ORBE, S.A. DE CV.', 'Pequeña Empresa', 'Tecnología', 'Servicios de asistencia técnica en sitio y soporte VMWARE para infraestructura HCI del MH'),
('SISTEMAS C&C, S.A. DE C.V.', 'Sin clasificar', 'Tecnología', 'Sistemas informáticos y consultoría'),
('JMTELCOM (JESUS MARTINEZ Y ASOCIADOS, S.A. DE C.V.)', 'Sin clasificar', 'Tecnología', 'Servicios de telecomunicaciones'),
('TECNOLOGIAS INDUSTRIALES, S.A. DE C.V.', 'Sin clasificar', 'Tecnología', 'Tecnologías industriales'),
('TECNOLOGÍAS Y SISTEMAS FRIOS, S.A. DE C.V', 'Sin clasificar', 'Tecnología', 'Sistemas de refrigeración industrial'),

-- Servicios Financieros (nuevos)
('MAPFRE SEGUROS EL SALVADOR, S.A. DE CV', 'Gran Empresa', 'Servicios Financieros', 'Pólizas de seguro y fianzas de fidelidad para el Ministerio de Hacienda'),
('LA CENTRAL DE SEGUROS Y FIANZAS, S.A. DE CV.', 'Gran Empresa', 'Servicios Financieros', 'Pólizas de seguro y fianzas para el Ministerio de Hacienda'),

-- Servicios de Limpieza (nuevo)
('MAPRECO, S.A. DE C.V.', 'Mediana Empresa', 'Servicios de Limpieza', 'Servicio de limpieza de fosas sépticas para la Dirección General de Aduanas'),

-- Servicios de Publicidad (nuevo rubro)
('LEMUSIMUN PUBLICIDAD, S.A. DE C.V.', 'Mediana Empresa', 'Servicios de Publicidad', 'Servicios de imagen y agencia de publicidad para el Ministerio de Hacienda'),

-- Servicios Educativos (nuevo rubro)
('CORPORACIÓN HERMANOS MARISTAS DE EL SALVADOR', 'Mediana Empresa', 'Servicios Educativos', 'Servicio de educación para los hijos de empleados del Ministerio de Hacienda'),

-- Medios y Suscripciones (nuevo rubro)
('DIARIO EL SALVADOR (El Diario Nacional, S.A. de C.V.)', 'Mediana Empresa', 'Medios y Suscripciones', 'Servicio de suscripción para periódicos en físico para oficinas del Ministerio de Hacienda'),
('EDITORA EL MUNDO, S.A.', 'Sin clasificar', 'Medios y Suscripciones', 'Publicaciones y medios impresos'),

-- Servicios de Mensajería (nuevo rubro)
('SERVICIO SALVADOREÑO DE PROTECCIÓN, S.A. DE C.V.', 'Gran Empresa', 'Servicios de Mensajería', 'Servicio de recolección y traslado de paquetería liviana y entrega de correspondencia'),

-- Artículos Deportivos (nuevo rubro)
('NETO SPORT, S.A DE C.V.', 'Pequeña Empresa', 'Artículos Deportivos', 'Adquisición de trofeos y artículos deportivos para juegos deportivos del Ministerio de Hacienda'),

-- Servicios Profesionales (nuevos)
('LISETH MARGARITA GARCÍA DE HIDALGO', 'Micro Empresa', 'Servicios Profesionales', 'Consultoría de especialista financiero UGP-CAF con fondos de la Corporación Andina de Fomento'),
('AENOR CENTROAMERICA, S.A. DE C.V.', 'Sin clasificar', 'Servicios Profesionales', 'Servicios de certificación y normalización'),
('RYASA (R.Y.A. SERVICIOS PROFESIONALES, S.A. DE C.V.)', 'Sin clasificar', 'Servicios Profesionales', 'Servicios profesionales integrados'),

-- Servicios de Mantenimiento (nuevos)
('SERCOMCA, S.A. DE C.V.', 'Mediana Empresa', 'Servicios de Mantenimiento', 'Mantenimiento preventivo y correctivo de contadoras de billetes y monedas para Tesorería'),
('O & M MANTENIMIENTO Y SERVICIOS, S.A. DE C.V.', 'Sin clasificar', 'Servicios de Mantenimiento', 'Mantenimiento y servicios generales'),

-- Alimentos y Bebidas (nuevos)
('ASECOMER, S.A. DE C.V.', 'Micro Empresa', 'Alimentos y Bebidas', 'Suministro de café y azúcar para las dependencias del Ministerio de Hacienda'),
('PLANTA DE TORREFACCIÓN DE CAFÉ', 'Sin clasificar', 'Alimentos y Bebidas', 'Torrefacción y suministro de café'),
('PARCELADORA SALVADOREÑA / RESTAURANTE CASA DE PIEDRA', 'Sin clasificar', 'Alimentos y Bebidas', 'Servicios de restaurante y alimentación'),

-- Comercio y Distribución (nuevo rubro)
('IMPORTACIONES Y SERVICIOS DIVERSOS, S.A. DE C.V.', 'Sin clasificar', 'Comercio y Distribución', 'Importaciones y servicios comerciales diversos'),
('DISTRIBUIDORA SALVADOREÑA (María Susana Mejía Argueta)', 'Micro Empresa', 'Comercio y Distribución', 'Distribución de insumos y productos comerciales'),

-- Servicios de Viajes (nuevo rubro)
('INTERTOURS, S.A. DE C.V.', 'Sin clasificar', 'Servicios de Viajes', 'Servicios de turismo y viajes'),

-- Construcción y Materiales (nuevo)
('FERRETERIA GUARDADO, S.A. DE C.V.', 'Sin clasificar', 'Construcción y Materiales', 'Suministro de materiales de ferretería y construcción'),

-- Suministros de Laboratorio (nuevos)
('ANALI (ANALITICA SALVADOREÑA, S.A. DE C.V.)', 'Sin clasificar', 'Suministros de Laboratorio', 'Servicios de analítica y laboratorio'),

-- Mobiliario y Equipo (nuevo)
('BASCULAS Y BALANZAS, S.A. DE C.V.', 'Sin clasificar', 'Mobiliario y Equipo', 'Equipos de medición, básculas y balanzas');

-- =============================================================================
-- 9. MATCHING FUNCTION (SQL nativo como fallback del Code node)
-- =============================================================================
CREATE OR REPLACE FUNCTION matching_oportunidades(p_productor_id UUID)
RETURNS TABLE (
    oportunidad_id    UUID,
    titulo            TEXT,
    institucion       TEXT,
    monto             DECIMAL(12,2),
    fecha_cierre      DATE,
    rubro_requerido   TEXT,
    tipo_contratacion TEXT,
    score             INTEGER,
    productor_nombre  TEXT,
    productor_rubro   TEXT
)
LANGUAGE plpgsql STABLE AS $$
DECLARE
    v_rubro  TEXT;
    v_nombre TEXT;
BEGIN
    SELECT p.rubro, p.nombre INTO v_rubro, v_nombre
    FROM productores p WHERE p.id = p_productor_id;
    IF NOT FOUND THEN RETURN; END IF;

    RETURN QUERY
    SELECT
        o.id, o.titulo, o.institucion, o.monto, o.fecha_cierre,
        o.rubro_requerido, o.tipo_contratacion,
        CASE
            WHEN o.rubro_requerido = v_rubro THEN 100
            WHEN o.rubro_requerido ILIKE '%' || SPLIT_PART(v_rubro, ' ', 1) || '%' THEN 70
            ELSE 40
        END::INTEGER AS score,
        v_nombre, v_rubro
    FROM oportunidades o
    WHERE o.rubro_requerido = v_rubro
       OR o.rubro_requerido ILIKE '%' || SPLIT_PART(v_rubro, ' ', 1) || '%'
    ORDER BY o.monto DESC;
END;
$$;

-- =============================================================================
-- 10. VERIFICACIÓN
-- =============================================================================
-- SELECT 'productores' AS tabla, count(*) FROM productores
-- UNION ALL SELECT 'oportunidades', count(*) FROM oportunidades
-- UNION ALL SELECT 'proveedores', count(*) FROM proveedores;

-- =============================================================================
-- 11. MÓDULO ASISTENTE LEGAL DINAC
--     Knowledge Base + RAG (ElevenLabs) para preguntas legales
--     Tool generar_documento (n8n) para prellenar documentos oficiales
-- =============================================================================

-- 11.1 Catálogo de plantillas descargadas de DINAC
CREATE TABLE IF NOT EXISTS plantillas_documentos (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre              TEXT NOT NULL,
    tipo                TEXT NOT NULL UNIQUE,
    campos_requeridos   JSONB NOT NULL,
    url_original_dinac  TEXT,
    path_template       TEXT NOT NULL,
    created_at          TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_plantillas_tipo ON plantillas_documentos(tipo);

ALTER TABLE plantillas_documentos ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "plantillas_documentos_all_access" ON plantillas_documentos FOR ALL USING (true) WITH CHECK (true);

-- 11.2 Auditoría de documentos generados
CREATE TABLE IF NOT EXISTS documentos_generados (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    productor_id    UUID REFERENCES productores(id) ON DELETE CASCADE,
    plantilla_id    UUID REFERENCES plantillas_documentos(id),
    datos_usados    JSONB NOT NULL,
    archivo_url     TEXT,
    estado          TEXT DEFAULT 'borrador',
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_documentos_generados_productor ON documentos_generados(productor_id);

ALTER TABLE documentos_generados ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "documentos_generados_all_access" ON documentos_generados FOR ALL USING (true) WITH CHECK (true);

-- 11.3 SEED: Plantillas disponibles (declaraciones juradas + formularios DINAC)
INSERT INTO plantillas_documentos (nombre, tipo, campos_requeridos, url_original_dinac, path_template) VALUES
(
    'Declaración Jurada Persona Natural',
    'declaracion_jurada_persona_natural',
    '["nombre","dui","nit","direccion","telefono","rubro","fecha"]'::jsonb,
    'https://dinac.gob.sv/documentos/declaracion-jurada-persona-natural',
    'plantillas/declaracion_jurada_persona_natural.docx'
),
(
    'Declaración Jurada Apoderado Persona Natural',
    'declaracion_jurada_apoderado_persona_natural',
    '["nombre_apoderado","dui_apoderado","nombre_representado","dui_representado","direccion","telefono","rubro","fecha"]'::jsonb,
    'https://dinac.gob.sv/documentos/declaracion-jurada-apoderado-persona-natural',
    'plantillas/declaracion_jurada_apoderado_persona_natural.docx'
),
(
    'Declaración Jurada Persona Jurídica',
    'declaracion_jurada_persona_juridica',
    '["nombre_empresa","nit","nombre_representante","dui_representante","direccion","telefono","rubro","fecha"]'::jsonb,
    'https://dinac.gob.sv/documentos/declaracion-jurada-persona-juridica',
    'plantillas/declaracion_jurada_persona_juridica.docx'
),
(
    'Declaración Jurada Apoderado Persona Jurídica',
    'declaracion_jurada_apoderado_persona_juridica',
    '["nombre_apoderado","dui_apoderado","nombre_empresa","nit","nombre_representante","dui_representante","direccion","telefono","rubro","fecha"]'::jsonb,
    'https://dinac.gob.sv/documentos/declaracion-jurada-apoderado-persona-juridica',
    'plantillas/declaracion_jurada_apoderado_persona_juridica.docx'
),
(
    'Formulario de Carta Compromiso',
    'carta_compromiso',
    '["nombre","dui","nit","direccion","oportunidad_titulo","institucion","monto","fecha"]'::jsonb,
    'https://dinac.gob.sv/documentos/carta-compromiso',
    'plantillas/carta_compromiso.docx'
),
(
    'Formulario de Desglose de Precios',
    'desglose_precios',
    '["nombre_empresa","nit","oportunidad_titulo","items","precios_unitarios","fecha"]'::jsonb,
    'https://dinac.gob.sv/documentos/desglose-precios',
    'plantillas/desglose_precios.docx'
);

-- =============================================================================
-- 12. VERIFICACIÓN FINAL
-- =============================================================================
-- SELECT 'productores' AS tabla, count(*) FROM productores
-- UNION ALL SELECT 'oportunidades', count(*) FROM oportunidades
-- UNION ALL SELECT 'proveedores', count(*) FROM proveedores
-- UNION ALL SELECT 'plantillas_documentos', count(*) FROM plantillas_documentos
-- UNION ALL SELECT 'documentos_generados', count(*) FROM documentos_generados;
-- SELECT * FROM matching_oportunidades('ID-DE-VILMA-AQUI');
-- =============================================================================
