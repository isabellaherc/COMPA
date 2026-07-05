"""
Generador de oportunidades de compra realistas al estilo COMPRASAL.

Produce datos sintéticos de licitaciones públicas salvadoreñas para
alimentar los workflows de n8n y las demostraciones del agente Compa.

Uso:
    from generador_oportunidades import generate_oportunidades
    ops = generate_oportunidades(25)
    print(json.dumps(ops, indent=2, ensure_ascii=False))
"""

import random
import json
from datetime import datetime, timedelta

# ── 1. Las 20 instituciones gubernamentales reales de El Salvador ─────────────

INSTITUCIONES = [
    {"siglas": "MINSAL",       "nombre": "Ministerio de Salud"},
    {"siglas": "MINEDUCYT",    "nombre": "Ministerio de Educación, Ciencia y Tecnología"},
    {"siglas": "MOPT",         "nombre": "Ministerio de Obras Públicas y Transporte"},
    {"siglas": "MAG",          "nombre": "Ministerio de Agricultura y Ganadería"},
    {"siglas": "MH",           "nombre": "Ministerio de Hacienda"},
    {"siglas": "MSP",          "nombre": "Ministerio de Seguridad Pública"},
    {"siglas": "MJ",           "nombre": "Ministerio de Justicia"},
    {"siglas": "MITUR",        "nombre": "Ministerio de Turismo"},
    {"siglas": "MTPS",         "nombre": "Ministerio de Trabajo y Previsión Social"},
    {"siglas": "MDN",          "nombre": "Ministerio de la Defensa Nacional"},
    {"siglas": "MICULTURA",    "nombre": "Ministerio de Cultura"},
    {"siglas": "MV",           "nombre": "Ministerio de Vivienda"},
    {"siglas": "MINEC",        "nombre": "Ministerio de Economía"},
    {"siglas": "ISSS",         "nombre": "Instituto Salvadoreño del Seguro Social"},
    {"siglas": "ANDA",         "nombre": "Administración Nacional de Acueductos y Alcantarillados"},
    {"siglas": "CEPA",         "nombre": "Comisión Ejecutiva Portuaria Autónoma"},
    {"siglas": "FINET",        "nombre": "Fondo de Inversión en Electricidad y Telefonía"},
    {"siglas": "AMSS",         "nombre": "Alcaldía Municipal de San Salvador"},
    {"siglas": "PNC",          "nombre": "Policía Nacional Civil"},
    {"siglas": "CSJ",          "nombre": "Corte Suprema de Justicia"},
]

# ── 2. Rubros con sus códigos UNSPSC ─────────────────────────────────────────

RUBROS_CON_UNSPSC = [
    ("Servicios de Limpieza y Fumigación",         "76100000"),
    ("Servicios de Vigilancia y Seguridad",        "92120000"),
    ("Alimentos y Bebidas",                        "50000000"),
    ("Material Médico y Farmacéutico",             "51000000"),
    ("Servicios de Construcción y Mantenimiento",  "72000000"),
    ("Servicios de Consultoría y Asesoría",        "80100000"),
    ("Suministro de Combustibles",                 "15100000"),
    ("Servicios de Tecnología Informática",        "43230000"),
    ("Materiales de Construcción",                 "30120000"),
    ("Servicios de Transporte",                    "78000000"),
    ("Servicios de Publicidad y Marketing",        "82120000"),
    ("Uniformes y Prendas de Vestir",              "53000000"),
    ("Servicios de Capacitación y Formación",      "86100000"),
    ("Suministro de Agua Potable",                 "22000000"),
    ("Equipo Agrícola y Ganadero",                 "24000000"),
    ("Servicios de Mantenimiento Vehicular",       "25170000"),
    ("Mobiliario y Equipo de Oficina",             "56000000"),
    ("Servicios de Alquiler de Equipo",            "72100000"),
    ("Material Didáctico y Educativo",             "60000000"),
    ("Servicios de Seguros",                       "95000000"),
]

# Diccionario de acceso rápido
RUBRO_MAP = dict(RUBROS_CON_UNSPSC)

# ── 3. Tipos de contratación con su distribución ─────────────────────────────

TIPOS_CONTRATACION = ["Licitacion Publica", "Libre Gestion", "Contratacion Directa"]
PESOS_CONTRATACION = [0.30, 0.50, 0.20]  # LP 30%, LG 50%, CD 20%

# ── 4. Distribución de montos (USD) ─────────────────────────────────────────

# 60% menores a $50K, 30% entre $50K y $200K, 10% entre $200K y $500K
def _monto_aleatorio():
    r = random.random()
    if r < 0.60:
        # $800 — $48,000  (pequeños productores)
        return round(random.uniform(800, 48_000), 2)
    elif r < 0.90:
        # $50,000 — $195,000
        return round(random.uniform(50_000, 195_000), 2)
    else:
        # $200,000 — $495,000
        return round(random.uniform(200_000, 495_000), 2)


# ── 5. Plantillas de título (10+) ────────────────────────────────────────────

PLANTILLAS_TITULO = [
    # Plantilla 0: Servicio de [rubro] en [ubicacion] - [institucion]
    lambda r, u, i, s: f"Servicio de {_rubro_para_titulo(r)} en {u} - {s}",
    # Plantilla 1: Contratacion de Servicios de [rubro] para [institucion] - [lote/ubicacion]
    lambda r, u, i, s: f"Contratacion de Servicios de {_rubro_para_titulo(r)} para {s} - {u}",
    # Plantilla 2: Adquisicion de [insumos] para [dependencia] de [institucion], [ubicacion]
    lambda r, u, i, s: f"Adquisicion de {_insumos_del_rubro(r)} para la {_dependencia()} de {s}, {u}",
    # Plantilla 3: Suministro de [producto] para el [proyecto] de [institucion]
    lambda r, u, i, s: f"Suministro de {_producto_del_rubro(r)} para el {_proyecto()} de {s}",
    # Plantilla 4: Servicio de [actividad] en [ubicacion] - Lote No. [lote] - [institucion]
    lambda r, u, i, s: f"Servicio de {_actividad_del_rubro(r)} en {u} - Lote No. {_lote()} - {s}",
    # Plantilla 5: Contratacion de [servicio] por [periodo] para [institucion] en [ubicacion]
    lambda r, u, i, s: f"Contratacion de {_servicio_generico(r)} por {_periodo()} para {s} en {u}",
    # Plantilla 6: Adquisicion de [materiales/equipo] para [proyecto] - [institucion], [ubicacion]
    lambda r, u, i, s: f"Adquisicion de {_materiales_del_rubro(r)} para {_proyecto()} - {s}, {u}",
    # Plantilla 7: Servicios de [cosa] para las instalaciones de [institucion] en [ubicacion]
    lambda r, u, i, s: f"Servicios de {_rubro_para_titulo(r)} para las Instalaciones de {s} en {u}",
    # Plantilla 8: Suministro e Instalacion de [equipo] en [ubicacion] - [institucion]
    lambda r, u, i, s: f"Suministro e Instalacion de {_equipo_del_rubro(r)} en {u} - {s}",
    # Plantilla 9: [rubro] para [dependencia] - [institucion], Departamento de [ubicacion]
    lambda r, u, i, s: f"{_rubro_para_titulo(r)} para {_dependencia()} - {s}, Departamento de {_departamento(u)}",
    # Plantilla 10: Contratacion de [servicio] a nivel nacional para [institucion]
    lambda r, u, i, s: f"Contratacion de {_servicio_generico(r)} a Nivel Nacional para {s}",
    # Plantilla 11: [tipo_obra] en [ubicacion] - [institucion]
    lambda r, u, i, s: f"{_obra_del_rubro(r)} en {u} - {s}",
    # Plantilla 12: Renovacion de [servicio] para [institucion] - Ejercicio [year]
    lambda r, u, i, s: f"Renovacion de {_servicio_generico(r)} para {s} - Ejercicio {_year()}",
    # Plantilla 13: Provision de [insumos] para [programa] - [institucion], [ubicacion]
    lambda r, u, i, s: f"Provision de {_insumos_del_rubro(r)} para el {_programa_social()} - {s}, {u}",
]

# ── 6. Descripciones formales de contratación pública ───────────────────────

DESCRIPCIONES = {
    "Servicios de Limpieza y Fumigacion": [
        "La presente contratacion tiene por objeto la prestacion de servicios integrales de limpieza, desinfeccion y fumigacion en las instalaciones administrativas y operativas de la institucion, incluyendo la provision de insumos, equipos y personal especializado para garantizar condiciones optimas de salubridad e higiene durante el periodo contratado.",
        "Se requiere la contratacion de servicios generales de aseo, desinfeccion y control de plagas para las oficinas centrales y sedes departamentales, con personal capacitado, equipo adecuado y productos biodegradables que cumplan con las normativas ambientales vigentes en El Salvador.",
    ],
    "Servicios de Vigilancia y Seguridad": [
        "La institucion requiere los servicios de empresas especializadas en seguridad privada para la proteccion perimetral, control de acceso y vigilancia de sus instalaciones a nivel nacional, con personal debidamente acreditado por la Division de Armas y Explosivos de la PNC, armamento reglamentario y sistemas de monitoreo en tiempo real.",
        "Contratacion de servicios de guardiania y seguridad para la proteccion de bienes institucionales, control de entrada y salida de personal y visitantes, y prevencion de riesgos en las instalaciones, debiendo el contratista proveer el recurso humano calificado y los equipos de radiocomunicacion necesarios.",
    ],
    "Alimentos y Bebidas": [
        "Adquisicion de canasta basica de alimentos no perecederos para la suplementacion alimenticia de familias en situacion de vulnerabilidad, incluyendo granos basicos, leche en polvo, aceite vegetal, harina de maiz, frijol, arroz, azucar y pastas alimenticias, en cumplimiento del Programa de Alimentacion Solidaria.",
        "Suministro de raciones alimenticias para pacientes hospitalizados y personal de guardia en los centros de salud de la red publica, elaboradas con estrictos controles de calidad nutricional e inocuidad, de conformidad con los estandares del Ministerio de Salud.",
    ],
    "Material Medico y Farmaceutico": [
        "Adquisicion de medicamentos esenciales e insumos medico-quirurgicos para el abastecimiento de farmacias institucionales y unidades de salud del primer nivel de atencion, incluyendo analgesicos, antiinflamatorios, antibioticos de amplio espectro, material de curacion y dispositivos medicos desechables.",
        "Compra de equipo medico e instrumental quirurgico para la modernizacion de salas de operaciones en hospitales nacionales, incluyendo mesas quirurgicas, lamparas cialiticas, monitores de signos vitales, desfibriladores y equipos de succion, con garantia minima de dos anos y servicio de mantenimiento correctivo.",
    ],
    "Servicios de Construccion y Mantenimiento": [
        "Ejecucion de obras de remodelacion, ampliacion y mantenimiento preventivo y correctivo de infraestructura institucional, incluyendo reparacion de cubiertas, instalaciones electricas, sistema hidrosanitario, acabados de pisos y paredes, y obras complementarias de drenaje y aceras perimetrales.",
        "Contratacion de servicios de construccion para la edificacion de aulas modulares en centros educativos publicos del area rural, conforme a especificaciones tecnicas del MOP, planos estructurales aprobados y cronograma de obra no mayor a 120 dias calendario.",
    ],
    "Servicios de Consultoria y Asesoria": [
        "Contratacion de servicios de consultoria especializada para la elaboracion de estudios de prefactibilidad, factibilidad y diseno final del proyecto de modernizacion institucional, incluyendo analisis de procesos, diagnostico organizacional y propuesta de rediseno de la estructura funcional.",
        "Servicios de asesoria legal y tecnica para la revision y actualizacion del marco normativo interno de la institucion, con enfasis en la armonizacion con la Ley de Adquisiciones y Contrataciones de la Administracion Publica (LACAP) y las directrices de la Corte de Cuentas de la Republica.",
    ],
    "Suministro de Combustibles": [
        "Suministro de combustible tipo diesel y gasolina especial para el parque vehicular de la institucion, incluyendo vehiculos livianos, pesados, motocicletas, equipo pesado y generadores electricos, mediante el sistema de vales o tarjetas electronicas en estaciones de servicio a nivel nacional.",
        "Adquisicion de gas licuado de petroleo (GLP) para el funcionamiento de cocinas industriales en centros penitenciarios, hogares de proteccion y centros de alimentacion administrados por la institucion, con entregas programadas semanalmente segun requerimiento de cada sede.",
    ],
    "Servicios de Tecnologia Informatica": [
        "Contratacion de servicios de desarrollo e implementacion de un sistema integrado de gestion administrativa y financiera sobre plataforma web, con modulos de presupuesto, tesoreria, contabilidad, adquisiciones, almacen y recursos humanos, integrable con el Sistema de Administracion Financiera Integrada (SAFI).",
        "Adquisicion de equipo informatico incluyendo computadoras de escritorio, portatiles, servidores, impresoras y equipo de redes para la actualizacion del parque tecnologico institucional, con especificaciones tecnicas minimas, licencias de software original y garantia de tres anos.",
    ],
    "Materiales de Construccion": [
        "Adquisicion de materiales de construccion para la ejecucion de proyectos de infraestructura social basica en comunidades rurales, incluyendo cemento, varilla de hierro, block, arena, piedrin, tuberia PVC, conductores electricos, lamina galvanizada y accesorios de ferreteria en general.",
        "Suministro de agregados petricos, mezcla asfaltica, emulsiones y materiales de senalizacion para el mantenimiento de la red vial secundaria y terciaria del pais, conforme a las especificaciones tecnicas del Ministerio de Obras Publicas y Transporte.",
    ],
    "Servicios de Transporte": [
        "Contratacion de servicios de transporte de personal para el traslado de empleados hacia las diferentes sedes y centros de trabajo a nivel nacional, con unidades en buen estado, seguro de pasajeros, conductores con licencia vigente y cumplimiento de las rutas y horarios establecidos.",
        "Servicios de flete y transporte de carga para el traslado de mobiliario, equipo, alimentos y materiales entre la bodega central y las sedes departamentales de la institucion, incluyendo carga, descarga, estiba y desestiba de los productos.",
    ],
    "Servicios de Publicidad y Marketing": [
        "Contratacion de servicios de publicidad institucional para la difusion de campanas de bien publico en medios de comunicacion nacionales escritos, radiales, televisivos y digitales, incluyendo la produccion de material grafico, edicion de piezas audiovisuales y pauta publicitaria.",
        "Servicios de diseno grafico, impresion y distribucion de material promocional, senaletica institucional, vallas publicitarias y piezas de comunicacion visual para las distintas dependencias de la institucion a nivel nacional.",
    ],
    "Uniformes y Prendas de Vestir": [
        "Adquisicion de uniformes institucionales para el personal administrativo y operativo de la institucion, incluyendo camisas, pantalones, calzado, gorras, chalecos y prendas de proteccion personal con logos bordados y conforme a las especificaciones tecnicas de color y diseno institucional.",
        "Suministro de vestuario y equipo de proteccion personal (EPP) para el personal de campo y talleres, incluyendo overoles, guantes, mascarillas, cascos de seguridad, botas industriales, lentes de proteccion y arneses de seguridad certificados bajo norma ASTM.",
    ],
    "Servicios de Capacitacion y Formacion": [
        "Contratacion de servicios de capacitacion y formacion profesional para el fortalecimiento de capacidades del recurso humano institucional en areas de administracion publica, gestion de proyectos, contrataciones estatales, atencion al usuario, seguridad ocupacional y liderazgo organizacional.",
        "Implementacion de programa de formacion continua en modalidad virtual y presencial para docentes del sistema publico de educacion, abarcando metodologias activas de ensenanza, evaluacion por competencias, inclusion educativa y uso de tecnologias digitales en el aula.",
    ],
    "Suministro de Agua Potable": [
        "Suministro de agua potable mediante camiones cisterna para comunidades rurales afectadas por la sequia y desabastecimiento del vital liquido, con frecuencias de entrega establecidas, control de calidad del agua mediante pruebas bacteriologicas y supervision de la Direccion General de Proteccion Civil.",
        "Contratacion del servicio de distribucion de agua purificada en garrafones para consumo humano en las diferentes dependencias administrativas, incluyendo la instalacion y mantenimiento de dispensadores y la reposicion semanal de envases segun el consumo de cada sede.",
    ],
    "Equipo Agricola y Ganadero": [
        "Adquisicion de equipo agricola, maquinaria e implementos para el fortalecimiento de la produccion agropecuaria de pequenos y medianos productores del sector reformado, incluyendo tractores, motocultores, sistemas de riego por goteo, aspersores, bombas de fumigacion y herramientas manuales.",
        "Suministro de insumos agropecuarios incluyendo semillas mejoradas de maiz y frijol, fertilizantes granulados, abono organico, insecticidas biologicos, herbicidas selectivos, concentrados para alimentacion animal y kits veterinarios basicos para atencion primaria del hato ganadero.",
    ],
    "Servicios de Mantenimiento Vehicular": [
        "Contratacion de servicios de mantenimiento preventivo y correctivo para el parque vehicular de la institucion, incluyendo cambio de aceite y filtros, reparacion de motores, sistemas de frenos, transmision, suspension, electricidad automotriz, aire acondicionado y vulcanizacion.",
        "Servicios de reparacion mayor y menor de la flota institucional de vehiculos pesados, incluyendo camiones, pickups, microbuses y ambulancias, con talleres autorizados, uso de repuestos originales o equivalentes certificados y garantia de mano de obra por seis meses.",
    ],
    "Mobiliario y Equipo de Oficina": [
        "Adquisicion de mobiliario de oficina para la renovacion de las areas administrativas de la institucion, incluyendo escritorios ejecutivos, sillas ergonomicas, archiveros metalicos, estanterias, mesas de reuniones, pizarrones, lockers y accesorios de oficina en general.",
        "Suministro de equipo de oficina y papelerio para el funcionamiento de las dependencias a nivel nacional, incluyendo fotocopiadoras multifuncionales, destructoras de papel, enmicadoras, suministros de papel bond, folders, toners, tintas y utiles de oficina en general.",
    ],
    "Servicios de Alquiler de Equipo": [
        "Contratacion del servicio de alquiler de maquinaria pesada para la ejecucion de proyectos de desarrollo local, incluyendo retroexcavadoras, motoniveladoras, compactadores de rodillo, vibroapisonadores, generadores electricos y plantas de luz, con operador calificado y combustible incluido.",
        "Servicio de alquiler de equipo de sonido, iluminacion, pantallas led y tarimas para la realizacion de eventos institucionales, actos protocolarios, ferias de salud y actividades culturales programadas por la institucion durante el presente ejercicio fiscal.",
    ],
    "Material Didactico y Educativo": [
        "Adquisicion de material didactico y recursos educativos para bibliotecas escolares y centros de recursos de aprendizaje del sistema publico, incluyendo libros de texto, guias metodologicas, mapas, kits de ciencias, material manipulativo, juegos educativos y recursos multimedia.",
        "Suministro de kits escolares para ninos y ninas de educacion basica del sector publico, incluyendo mochilas, cuadernos, lapices, borradores, sacapuntas, colores, tijeras, pegamento, reglas y cartucheras, en el marco del programa de apoyo a la permanencia escolar.",
    ],
    "Servicios de Seguros": [
        "Contratacion de polizas de seguros multiriesgo para la proteccion de los bienes muebles e inmuebles de la institucion, incluyendo cobertura contra incendio, terremoto, hurto, robo, danos por agua, responsabilidad civil y equipo electronico, con deducibles preferenciales y cobertura a nivel nacional.",
        "Adquisicion de seguros de vida colectivo y accidentes personales para los empleados de la institucion, con cobertura de muerte accidental, invalidez total y permanente, gastos medicos por accidente y una suma asegurada no menor a veinte salarios minimos del sector comercio.",
    ],
}

# ── Funciones auxiliares para las plantillas ─────────────────────────────────

RUBRO_PALABRAS = {
    "Servicios de Limpieza y Fumigacion":        "Limpieza y Fumigacion",
    "Servicios de Vigilancia y Seguridad":       "Vigilancia y Seguridad",
    "Alimentos y Bebidas":                       "Alimentacion",
    "Material Medico y Farmaceutico":            "Insumos Medicos y Farmaceuticos",
    "Servicios de Construccion y Mantenimiento": "Construccion y Mantenimiento",
    "Servicios de Consultoria y Asesoria":        "Consultoria y Asesoria",
    "Suministro de Combustibles":                 "Combustibles",
    "Servicios de Tecnologia Informatica":        "Informatica",
    "Materiales de Construccion":                 "Materiales de Construccion",
    "Servicios de Transporte":                    "Transporte",
    "Servicios de Publicidad y Marketing":        "Publicidad",
    "Uniformes y Prendas de Vestir":              "Uniformes",
    "Servicios de Capacitacion y Formacion":      "Capacitacion",
    "Suministro de Agua Potable":                 "Agua Potable",
    "Equipo Agricola y Ganadero":                 "Equipo Agricola",
    "Servicios de Mantenimiento Vehicular":       "Mantenimiento Vehicular",
    "Mobiliario y Equipo de Oficina":             "Mobiliario y Equipo de Oficina",
    "Servicios de Alquiler de Equipo":            "Alquiler de Equipo",
    "Material Didactico y Educativo":             "Material Didactico",
    "Servicios de Seguros":                       "Seguros",
}

RUBRO_TITULO = {
    "Servicios de Limpieza y Fumigacion":        "Limpieza, Desinfeccion y Fumigacion",
    "Servicios de Vigilancia y Seguridad":       "Vigilancia y Seguridad Privada",
    "Alimentos y Bebidas":                       "Alimentos y Bebidas",
    "Material Medico y Farmaceutico":            "Insumos Medico-Quirurgicos",
    "Servicios de Construccion y Mantenimiento": "Construccion",
    "Servicios de Consultoria y Asesoria":        "Consultoria Especializada",
    "Suministro de Combustibles":                 "Suministro de Combustibles",
    "Servicios de Tecnologia Informatica":        "Desarrollo y Soporte Informatico",
    "Materiales de Construccion":                 "Materiales de Construccion",
    "Servicios de Transporte":                    "Transporte Terrestre",
    "Servicios de Publicidad y Marketing":        "Publicidad y Comunicaciones",
    "Uniformes y Prendas de Vestir":              "Uniformes y Vestuario",
    "Servicios de Capacitacion y Formacion":      "Capacitacion Profesional",
    "Suministro de Agua Potable":                 "Suministro de Agua",
    "Equipo Agricola y Ganadero":                 "Equipamiento Agricola",
    "Servicios de Mantenimiento Vehicular":       "Mantenimiento Automotriz",
    "Mobiliario y Equipo de Oficina":             "Mobiliario de Oficina",
    "Servicios de Alquiler de Equipo":            "Alquiler de Maquinaria",
    "Material Didactico y Educativo":             "Material Educativo",
    "Servicios de Seguros":                       "Polizas de Seguros",
}


def _rubro_para_titulo(rubro):
    """Retorna una version corta del rubro para insertar en el titulo."""
    return RUBRO_TITULO.get(rubro, rubro)


def _insumos_del_rubro(rubro):
    mapa = {
        "Servicios de Limpieza y Fumigacion": "Productos de Limpieza e Insumos de Fumigacion",
        "Alimentos y Bebidas": "Alimentos No Perecederos",
        "Material Medico y Farmaceutico": "Medicamentos e Insumos Medicos",
        "Materiales de Construccion": "Materiales de Construccion",
        "Uniformes y Prendas de Vestir": "Prendas y Uniformes Institucionales",
        "Mobiliario y Equipo de Oficina": "Equipamiento y Mobiliario",
        "Equipo Agricola y Ganadero": "Insumos Agropecuarios",
        "Material Didactico y Educativo": "Material Didactico y Libros",
    }
    return mapa.get(rubro, "Insumos Diversos")


def _producto_del_rubro(rubro):
    mapa = {
        "Suministro de Combustibles": "Combustible y Lubricantes",
        "Alimentos y Bebidas": "Productos Alimenticios",
        "Material Medico y Farmaceutico": "Equipo Medico",
        "Materiales de Construccion": "Materiales de Ferreteria",
        "Uniformes y Prendas de Vestir": "Vestuario y Calzado",
        "Mobiliario y Equipo de Oficina": "Muebles de Oficina",
        "Equipo Agricola y Ganadero": "Implementos Agricolas",
    }
    return mapa.get(rubro, "Productos y Suministros")


def _materiales_del_rubro(rubro):
    mapa = {
        "Servicios de Construccion y Mantenimiento": "Materiales de Construccion",
        "Materiales de Construccion": "Agregados y Materiales",
        "Mobiliario y Equipo de Oficina": "Equipo y Mobiliario",
        "Material Didactico y Educativo": "Recursos Pedagogicos",
        "Material Medico y Farmaceutico": "Insumos Hospitalarios",
    }
    return mapa.get(rubro, "Materiales Diversos")


def _equipo_del_rubro(rubro):
    mapa = {
        "Servicios de Tecnologia Informatica": "Equipo Informatico",
        "Equipo Agricola y Ganadero": "Maquinaria Agricola",
        "Material Medico y Farmaceutico": "Equipo Medico",
        "Servicios de Alquiler de Equipo": "Maquinaria Pesada",
        "Mobiliario y Equipo de Oficina": "Equipo de Oficina",
    }
    return mapa.get(rubro, "Equipo Especializado")


def _servicio_generico(rubro):
    return rubro.replace("Servicios de ", "").replace("Suministro de ", "Suministro de ").replace("Adquisicion de ", "")


def _actividad_del_rubro(rubro):
    mapa = {
        "Servicios de Limpieza y Fumigacion": "Saneamiento Ambiental",
        "Servicios de Construccion y Mantenimiento": "Mejoramiento de Infraestructura",
        "Servicios de Consultoria y Asesoria": "Acompanamiento Tecnico",
        "Servicios de Capacitacion y Formacion": "Formacion y Desarrollo",
        "Servicios de Publicidad y Marketing": "Difusion y Comunicacion",
    }
    return mapa.get(rubro, "Asistencia Tecnica")


def _obra_del_rubro(rubro):
    if rubro == "Servicios de Construccion y Mantenimiento":
        return random.choice([
            "Construccion de Obra Civil",
            "Remodelacion de Instalaciones",
            "Ampliacion de Infraestructura",
            "Reparacion de Planta Fisica",
        ])
    return "Obra de Infraestructura"


def _dependencia():
    return random.choice([
        "Direccion Administrativa",
        "Unidad de Adquisiciones y Contrataciones",
        "Gerencia de Operaciones",
        "Departamento de Servicios Generales",
        "Direccion de Logistica",
        "Unidad de Mantenimiento",
        "Departamento de Informatica",
        "Direccion de Recursos Humanos",
        "Gerencia Financiera",
        "Departamento de Compras Publicas",
    ])


def _proyecto():
    return random.choice([
        "Programa de Modernizacion Institucional",
        "Proyecto de Fortalecimiento de Capacidades",
        "Plan de Mejoramiento de la Infraestructura",
        "Programa de Asistencia Tecnica y Capacitacion",
        "Proyecto de Transformacion Digital",
        "Programa Nacional de Desarrollo Local",
        "Plan de Sostenibilidad Ambiental",
        "Proyecto de Equipamiento Tecnologico",
    ])


def _programa_social():
    return random.choice([
        "Programa de Alimentacion Solidaria",
        "Plan de Atencion Integral a la Primera Infancia",
        "Programa de Apoyo al Emprendimiento Rural",
        "Plan de Seguridad Alimentaria y Nutricional",
        "Estrategia Nacional de Inclusion Productiva",
    ])


def _periodo():
    return random.choice([
        "12 Meses",
        "6 Meses",
        "24 Meses",
        "18 Meses",
        "Periodo Fiscal 2026",
        "Ejercicio 2026-2027",
    ])


def _lote():
    return str(random.randint(1, 15))


def _departamento(ubicacion):
    """Extrae el departamento de una ubicacion completa."""
    deptos = [
        "San Salvador", "La Libertad", "Santa Ana", "San Miguel",
        "Sonsonate", "Usulutan", "Ahuachapan", "La Paz",
        "Cuscatlan", "Chalatenango", "Morazan", "La Union",
        "Cabanas", "San Vicente",
    ]
    return random.choice(deptos)


def _year():
    return str(random.choice([2026, 2027]))


# ── Ubicaciones ─────────────────────────────────────────────────────────────

UBICACIONES = [
    "San Salvador",
    "San Salvador, Centro Historico",
    "Santa Ana",
    "San Miguel",
    "Sonsonate",
    "Usulutan",
    "Ahuachapan",
    "La Libertad, Puerto de La Libertad",
    "Zacatecoluca, La Paz",
    "Cojutepeque, Cuscatlan",
    "Chalatenango",
    "San Francisco Gotera, Morazan",
    "La Union",
    "Sensuntepeque, Cabanas",
    "San Vicente",
    "San Martin, San Salvador",
    "Antiguo Cuscatlan, La Libertad",
    "Mejicanos, San Salvador",
    "Apopa, San Salvador",
    "Soyapango, San Salvador",
    "Ilopango, San Salvador",
    "Ciudad Delgado, San Salvador",
    "Zona Metropolitana de San Salvador",
    "Colon, La Libertad",
    "Santa Tecla, La Libertad",
    "Nueva San Salvador",
    "Tonacatepeque, San Salvador",
    "Ayutuxtepeque, San Salvador",
    "Cuscatancingo, San Salvador",
    "San Marcos, San Salvador",
    "Panchimalco, San Salvador",
    "Rosario de Mora, San Salvador",
    "A nivel nacional",
    "A nivel nacional, 14 departamentos",
    "Zona Occidental (Santa Ana, Sonsonate, Ahuachapan)",
    "Zona Paracentral (San Vicente, La Paz, Cabanas, Cuscatlan)",
    "Zona Oriental (San Miguel, Usulutan, Morazan, La Union)",
    "Region Central de El Salvador",
]


# ── Generador principal ─────────────────────────────────────────────────────

def generate_oportunidades(n=25):
    """
    Genera una lista de n oportunidades de compra realistas al estilo COMPRASAL.

    Parametros
    ----------
    n : int
        Cantidad de oportunidades a generar (default 25).

    Retorna
    -------
    list[dict]
        Lista de diccionarios con la estructura:
        - id, titulo, institucion, monto, fecha_cierre, rubro_requerido,
          unspsc_code, url_fuente, tipo_contratacion, descripcion
    """
    oportunidades = []
    base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    for i in range(n):
        # Seleccionar rubro
        rubro, unspsc = random.choice(RUBROS_CON_UNSPSC)

        # Seleccionar institucion
        inst = random.choice(INSTITUCIONES)
        institucion_nombre = f"{inst['siglas']} - {inst['nombre']}"

        # Seleccionar ubicacion
        ubicacion = random.choice(UBICACIONES)

        # Generar titulo usando una plantilla aleatoria
        plantilla = random.choice(PLANTILLAS_TITULO)
        titulo = plantilla(rubro, ubicacion, inst['nombre'], inst['siglas'])

        # Generar fecha de cierre (1 a 30 dias desde hoy)
        dias_cierre = random.randint(1, 30)
        fecha_cierre = (base_date + timedelta(days=dias_cierre)).strftime("%Y-%m-%d")

        # Monto
        monto = _monto_aleatorio()

        # Tipo de contratacion segun distribucion
        tipo_contratacion = random.choices(TIPOS_CONTRATACION, weights=PESOS_CONTRATACION, k=1)[0]

        # Descripcion
        desc_key = rubro  # Las descripciones estan indexadas por rubro exacto
        if desc_key in DESCRIPCIONES:
            descripcion = random.choice(DESCRIPCIONES[desc_key])
        else:
            descripcion = _descripcion_generica(rubro, ubicacion, institucion_nombre, tipo_contratacion)

        # URL fuente (COMPRASAL fake)
        opp_id = f"opp-{i+1:03d}"
        url_fuente = _generar_url(inst['siglas'], opp_id)

        oportunidad = {
            "id": opp_id,
            "titulo": titulo,
            "institucion": institucion_nombre,
            "monto": monto,
            "fecha_cierre": fecha_cierre,
            "rubro_requerido": rubro,
            "unspsc_code": unspsc,
            "url_fuente": url_fuente,
            "tipo_contratacion": tipo_contratacion,
            "descripcion": descripcion,
        }

        oportunidades.append(oportunidad)

    return oportunidades


# ── Funciones auxiliares ────────────────────────────────────────────────────

def _generar_url(siglas, opp_id):
    """Genera una URL realista del portal COMPRASAL."""
    numero_expediente = f"{siglas}-{random.randint(1,99):02d}-{random.randint(1000,9999)}-{random.randint(2025,2027)}"
    return (
        f"https://www.comprasal.gob.sv/Oportunidades/"
        f"DetalleOportunidad.aspx?"
        f"oppId={opp_id}&"
        f"exp={numero_expediente}"
    )


def _descripcion_generica(rubro, ubicacion, institucion, tipo_contratacion):
    """Genera una descripcion por defecto cuando no hay descripciones predefinidas."""
    # rubro names already start with "Servicios de" or similar; strip to avoid
    # double "servicios de servicios de" in the sentence.
    rubro_short = rubro[0].lower() + rubro[1:]  # lowercase first char
    verbo = random.choice(["contratar", "adquirir", "la contratacion de"])
    if verbo == "la contratacion de":
        return (
            f"La presente solicitud tiene por objeto {verbo} "
            f"{rubro_short} para las dependencias de {institucion} en {ubicacion}, "
            f"por un periodo de {random.choice(['doce meses', 'seis meses', 'el ejercicio fiscal vigente'])}, "
            f"de conformidad con lo establecido en la Ley de Adquisiciones y Contrataciones "
            f"de la Administracion Publica (LACAP) y sus reformas. Los interesados deberan "
            f"presentar su oferta tecnica y economica en sobre sellado en la Unidad de "
            f"Adquisiciones y Contrataciones Institucional (UACI)."
        )
    return (
        f"La presente solicitud tiene por objeto {verbo} los "
        f"{rubro_short} para las dependencias de {institucion} en {ubicacion}, "
        f"por un periodo de {random.choice(['doce meses', 'seis meses', 'el ejercicio fiscal vigente'])}, "
        f"de conformidad con lo establecido en la Ley de Adquisiciones y Contrataciones "
        f"de la Administracion Publica (LACAP) y sus reformas. Los interesados deberan "
        f"presentar su oferta tecnica y economica en sobre sellado en la Unidad de "
        f"Adquisiciones y Contrataciones Institucional (UACI)."
    )


# ── Punto de entrada para prueba ─────────────────────────────────────────────

if __name__ == "__main__":
    ops = generate_oportunidades(25)
    print(json.dumps(ops, indent=2, ensure_ascii=False))
