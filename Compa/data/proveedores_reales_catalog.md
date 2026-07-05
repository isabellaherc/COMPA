# =============================================================================
# Compa — Proveedores & Productores Reales (3 fuentes del registro público)
# Buildathon 4 Julio 2026
# Fuentes:
#   1. UNIDAD DE COMPRAS PUBLICAS - Registro de Contratistas jul-sep 2025 (51)
#   2. UNIDAD DE COMPRAS PUBLICAS - Registro de Contratistas ene-mar 2026 (~45)
#   3. MINISTERIO DE HACIENDA - Clasificación de Ofertantes Aprobados 2019 (~43)
# =============================================================================

# NUEVOS RUBROS DESCUBIERTOS (se suman a los 14 anteriores):
# - Transporte y Logística (TRANSPORTES ARGUETA, LINEA ROSA, URBANO EXPRESS, etc.)
# - Servicios de Publicidad (LEMUSIMUN PUBLICIDAD)
# - Servicios Educativos (CORPORACIÓN HERMANOS MARISTAS)
# - Medios y Suscripciones (DIARIO EL SALVADOR, EDITORA EL MUNDO)
# - Servicios de Mensajería (SERVICIO SALVADOREÑO DE PROTECCIÓN)
# - Artículos Deportivos (NETO SPORT)
# - Servicios de Viajes/Turismo (INTERTOURS)
# - Seguridad Documental (SCREENCHECK - carnés de identificación)
# - Equipos de Refrigeración (TECNOLOGÍAS Y SISTEMAS FRÍOS)

# =============================================================================
# NUEVOS PRODUCTORES (micro/pequeña empresa + personas naturales)
# Estos son candidatos IDEALES para ser usuarios de Compa:
# ya vendieron al Estado, son pequeños, y se beneficiarían de detección de oportunidades
# =============================================================================

NUEVOS_PRODUCTORES = """
# Personas naturales microempresarias (emprendedores reales que ya vendieron al Estado):
- CESAR ROLANDO CONTRERAS OBISPO (CROBISPO) | Micro | Construcción | Mantenimiento infraestructura MH
- MILTON ERNESTO CEA PANAMEÑO | Micro | Tecnología | Consultoría PowerBuilder/Oracle para MH
- OSCAR ARMANDO OCÓN DÍAZ | Micro | Tecnología | Soporte SONARQUBE Enterprise
- KAREN YAMILETH HERNÁNDEZ DE MÉNDEZ | Micro | Alimentos | Refrigerios para juegos deportivos MH
- Baltazar Gómez Romero | Micro | Servicios Deportivos | Arbitrajes juegos deportivos MH
- Bryan Otoniel Fuentes Renderos | Micro | Servicios Deportivos | Arbitrajes juegos deportivos MH
- NORMA ELOISA ROMERO MEDRANO (Medical Systems) | Pequeña | Suministros Médicos | Botiquines DGA
- MARÍA ZOILA AGUILAR PINEDA (IMPRESOS UNIDOS SALVADOREÑOS) | Pequeña | Imprenta | Formularios MH
- Sandra Patricia Vásquez Hernández (BIT OFFICE) | Micro | Tecnología | Reloj marcador
- CARLOS ORLANDO ROMERO CALLES | Mediana | Suministros de Laboratorio | Consumibles y cristalería DGA
- DORA ENELSA CASTRO BORJA (DIVERSUS HOME) | Micro | Mobiliario y Equipo | Electrodomésticos DGA
- JOSÉ CECILIO TOBAR VALLE (IMPRESOS DILEFRAN) | Micro | Imprenta | Impresos
- MARIA SUSANA MEJIA ARGUETA (DISTRIBUIDORA SALVADOREÑA-TU SURTIDORA) | Micro | Comercio | Distribución
- RONALD ONIL SERRANO TEXIN (TRANS ARGENTINA) | Micro | Transporte | Transporte empleados MH

# Micro y pequeñas empresas (ya son formales, podrían crecer con Compa):
- INGENIERIA BIO PRO S.A.S DE C.V. | Micro | Servicios de Mantenimiento | Equipos médicos
- PRINT RUNNING, S.A. DE C.V. | Micro | Imprenta | Formularios MH
- IMPRESOS DOBLE G, S.A. DE C.V. | Micro | Imprenta | Formularios MH
- EDITORIAL E IMPRESORA PANAMERICANA, S.A. DE C.V. | Micro | Imprenta | Formularios MH
- LANDOS, S.A. DE C.V. | Micro | Imprenta | Formularios, especies, encuadernado
- AIR AND ELECTRIC SERVICE, S.A. DE C.V. | Micro | Servicios de Mantenimiento | Extractores DGA
- CONSULTORIA, MEDIO AMBIENTE Y SOLUCIONES, S.A. DE C.V. | Micro | Servicios Ambientales | Filtración agua
- LINEA ROSA, S.A. DE CV. | Micro | Transporte | Transporte nocturno MH
- GRUPO ASINET EL SALVADOR, S.A. DE C.V. | Micro | Tecnología | Kerio Connect
- NETO SPORT, S.A DE C.V. | Pequeña | Artículos Deportivos | Trofeos y artículos deportivos MH
- SCREENCHECK EL SALVADOR, S.A. DE C.V. | Pequeña | Seguridad Documental | Carnés de identificación
- DOCUMENTOS INTELIGENTES, S.A. DE C.V. | Pequeña | Tecnología | Laptops y accesorios
- INSTRUQUIMICA, S.A. DE C.V. | Pequeña | Suministros de Laboratorio | Consumibles laboratorio DGA
- SOLUTECNO, S.A. DE CV. | Pequeña | Tecnología | Centrales telefónicas MH
- GEOSIS, S.A. DE C.V. | Pequeña | Tecnología | Licencias ARCGIS
- NEXT GENESIS TECHNOLOGIES, S.A. DE C.V. | Pequeña | Tecnología | Licencias Quest
- COMPONENTES EL ORBE, S.A. DE CV. | Pequeña | Tecnología | Soporte VMWARE MH
- FERRETERIA GUARDADO, S.A. DE C.V. | (sin clasif.) | Construcción | Ferretería
- PLANTA DE TORREFACCIÓN DE CAFÉ | (sin clasif.) | Alimentos | Café
- PARCELADORA SALVADOREÑA / RESTAURANTE CASA DE PIEDRA | (sin clasif.) | Alimentos | Restaurante
"""

NUEVOS_PROVEEDORES = """
# Medianas y grandes empresas (proveedores establecidos, no usuarios de Compa):
- ETS CONSULTING, S.A. DE C.V. | Mediana | Tecnología | Soporte balanceo ADC MH
- LEMUSIMUN PUBLICIDAD, S.A. DE C.V. | Mediana | Servicios de Publicidad | Imagen y publicidad MH
- TRANSPORTES ARGUETA, S.A. DE C.V. | Micro | Transporte | Transporte colectivo MH
- TRANSPORTES ALAS S.A. DE C.V. | Mediana | Transporte | Transporte empleados MH
- INTRACON, S.A. DE C.V. | Pequeña | Transporte | Transporte MH
- SERCOMCA, S.A. DE C.V. | Mediana | Servicios de Mantenimiento | Contadoras de billetes Tesorería
- MAPFRE SEGUROS EL SALVADOR, S.A. DE CV | Gran | Servicios Financieros | Pólizas de seguro
- LA CENTRAL DE SEGUROS Y FIANZAS, S.A. DE CV. | Gran | Servicios Financieros | Seguros y fianzas
- MAPRECO, S.A. DE C.V. | Mediana | Servicios de Limpieza | Limpieza fosas sépticas DGA
- CORPORACIÓN HERMANOS MARISTAS DE EL SALVADOR | Mediana | Servicios Educativos | Educación hijos empleados
- UDP ASOCIO GRUPO PLUS-CONFICO | Pequeña | Tecnología | Soporte BPM AuraQuantic
- DATAGUARDS, S.A. DE C.V. | Mediana | Tecnología | Colocation centro de datos
- AMAZON WEB SERVICES, INC | Gran | Tecnología | Almacenamiento en nube
- GBM DE EL SALVADOR, S.A. DE C.V. | Gran | Tecnología | Soporte UPS, CISCO, IBM Cognos
- TELEMOVIL EL SALVADOR, S.A. DE CV. | Gran | Tecnología | Internet satelital, CloudFlare WAF
- LISETH MARGARITA GARCÍA DE HIDALGO | Micro | Servicios Profesionales | Consultoría financiera UGP-CAF
- DIARIO EL SALVADOR (El Diario Nacional, S.A. de C.V.) | Mediana | Medios | Suscripción periódicos
- PRODUCTIVE BUSINESS SOLUTIONS (PBS EL SALVADOR) | Gran | Tecnología | Adobe Creative Cloud
- SERVICIO SALVADOREÑO DE PROTECCIÓN, S.A. DE C.V. | Gran | Servicios de Mensajería | Recolección y traslado paquetería
- GOOGLE LLC | Gran | Tecnología | Google Cloud, Workspace, CrowdStrike
- HOTELES, S.A. DE C.V. | Gran | Servicios de Catering | Celebración actos MH
- ASECOMER, S.A. DE C.V. | Micro | Alimentos | Café y azúcar MH
- JOSÉ EDGARDO HERNÁNDEZ PINEDA | Mediana | Alimentos | Café y azúcar MH
- AENOR CENTROAMERICA, S.A. DE C.V. | (sin clasif.) | Servicios Profesionales | Certificación
- ANALI (ANALITICA SALVADOREÑA, S.A. DE C.V.) | (sin clasif.) | Suministros de Laboratorio | Analítica
- BASCULAS Y BALANZAS, S.A. DE C.V. | (sin clasif.) | Mobiliario y Equipo | Equipos medición
- BATERIAS SUPERIOR DE C.A. (BATERSUPERCA) | (sin clasif.) | Tecnología | Baterías
- CENTRO DE SERVICIO DOÑO, S.A. DE C.V. | (sin clasif.) | Servicios Generales | Servicios
- DATUM, S.A. DE C.V. | (sin clasif.) | Tecnología | Sistemas
- EDITORA EL MUNDO, S.A. | (sin clasif.) | Medios | Publicaciones
- IMPORTACIONES Y SERVICIOS DIVERSOS, S.A. DE C.V. | (sin clasif.) | Comercio | Importaciones
- INTERTOURS, S.A. DE C.V. | (sin clasif.) | Servicios de Viajes | Turismo
- JMTELCOM (JESUS MARTINEZ Y ASOCIADOS, S.A. DE C.V.) | (sin clasif.) | Tecnología | Telecom
- O & M MANTENIMIENTO Y SERVICIOS, S.A. DE C.V. | (sin clasif.) | Servicios de Mantenimiento | Mantenimiento
- RYASA (R.Y.A. SERVICIOS PROFESIONALES, S.A. DE C.V.) | (sin clasif.) | Servicios Profesionales | Servicios profesionales
- SISTEMAS C&C, S.A. DE C.V. | (sin clasif.) | Tecnología | Sistemas
- TECNOLOGIAS INDUSTRIALES, S.A. DE C.V. | (sin clasif.) | Tecnología | Industrial
- TECNOLOGÍAS Y SISTEMAS FRIOS, S.A. DE C.V | (sin clasif.) | Tecnología | Refrigeración
- URBANO EXPRESS, S.A. DE C.V. | (sin clasif.) | Transporte | Mensajería
"""

# =============================================================================
# RESUMEN FINAL DE DATOS REALES
# =============================================================================
# Total proveedores únicos: ~120+ (51 + 45 + 43, menos duplicados)
# Total rubros: 22 (14 originales + 8 nuevos)
# Productores candidatos (micro/pequeña): ~35
# Oportunidades generadas: 31 (cubriendo los 14 rubros principales)
# Períodos cubiertos: 2019, jul-sep 2025, ene-mar 2026
# Fuente: UNIDAD DE COMPRAS PUBLICAS + MINISTERIO DE HACIENDA, Gobierno de El Salvador
