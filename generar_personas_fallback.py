#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_personas_fallback.py — Fallback Synthetic Persona Generator for Compa.

Generates realistic Salvadoran business personas WITHOUT accessing HuggingFace.
Outputs productores_demo.csv, proveedores_demo.csv, and personas_sinteticas.json
with Nemotron-style professional_persona texts.

Usage:
    python generar_personas_fallback.py

Output directory: data/  (created automatically)
"""

import csv
import json
import os
import random
import re
from datetime import datetime, timedelta

# =============================================================================
# CONSTANTS — Real Salvadoran data
# =============================================================================

# 14 Departamentos (with weighted distribution for realistic sampling)
DEPARTAMENTOS = [
    "Ahuachapan",
    "Santa Ana",
    "Sonsonate",
    "Chalatenango",
    "La Libertad",
    "San Salvador",
    "Cuscatlan",
    "La Paz",
    "Cabanas",
    "San Vicente",
    "Usulutan",
    "San Miguel",
    "Morazan",
    "La Union",
]

# 44 Municipios mapped to their departamentos (3-4 per department, 44 total)
MUNICIPIOS_POR_DEPARTAMENTO = {
    "Ahuachapan":    ["Ahuachapan", "Atiquizaya", "Tacuba"],
    "Santa Ana":     ["Santa Ana", "Chalchuapa", "Metapan"],
    "Sonsonate":     ["Sonsonate", "Acajutla", "Izalco", "Juayua"],
    "Chalatenango":  ["Chalatenango", "La Palma", "Tejutla", "Nueva Concepcion"],
    "La Libertad":   ["Santa Tecla", "Antiguo Cuscatlan", "Nuevo Cuscatlan",
                      "San Juan Opico", "Zaragoza"],
    "San Salvador":  ["San Salvador", "Soyapango", "Mejicanos", "Apopa",
                      "Ilopango", "San Martin"],
    "Cuscatlan":     ["Cojutepeque", "San Rafael Cedros", "Suchitoto"],
    "La Paz":        ["Zacatecoluca", "San Pedro Nonualco", "Santiago Nonualco",
                      "San Luis Talpa"],
    "Cabanas":       ["Sensuntepeque", "Ilobasco", "Victoria"],
    "San Vicente":   ["San Vicente", "San Sebastian", "Tecoluca", "Guadalupe"],
    "Usulutan":      ["Usulutan", "Jiquilisco", "Santiago de Maria", "Berlin"],
    "San Miguel":    ["San Miguel", "Chinameca", "El Transito", "Ciudad Barrios"],
    "Morazan":       ["San Francisco Gotera", "Jocoro", "Corinto"],
    "La Union":      ["La Union", "Santa Rosa de Lima", "Conchagua"],
}

# Flatten for lookup
ALL_MUNICIPIOS = []
for dept, municipios in MUNICIPIOS_POR_DEPARTAMENTO.items():
    for m in municipios:
        ALL_MUNICIPIOS.append((m, dept))

# 10 Standardized business rubros
RUBROS = [
    "Alimentos y Bebidas",
    "Textiles y Uniformes",
    "Construccion",
    "Servicios de Limpieza",
    "Transporte",
    "Tecnologia",
    "Mobiliario",
    "Suministros Agricolas",
    "Imprenta",
    "Reciclaje",
]

# Rubro descriptions (for the persona text)
RUBRO_DESCRIPCIONES = {
    "Alimentos y Bebidas": [
        "preparacion y venta de alimentos y bebidas",
        "cocina tradicional y catering para eventos",
        "produccion de alimentos artesanales y tipicos",
        "servicio de alimentacion colectiva",
    ],
    "Textiles y Uniformes": [
        "confeccion de uniformes y ropa de trabajo",
        "fabricacion de prendas textiles y bordados",
        "costura industrial y arreglos de vestuario",
        "produccion de uniformes escolares y corporativos",
    ],
    "Construccion": [
        "remodelacion y construccion de obras menores",
        "acabados de construccion y mantenimiento",
        "albanileria y trabajos de construccion general",
    ],
    "Servicios de Limpieza": [
        "servicios de limpieza general para empresas",
        "limpieza y desinfeccion de oficinas y comercios",
        "servicios de aseo industrial y mantenimiento",
    ],
    "Transporte": [
        "servicio de transporte de carga ligera",
        "transporte de personal y distribucion de mercaderia",
        "fletes y mudanzas locales",
    ],
    "Tecnologia": [
        "soporte tecnico y mantenimiento de equipos informaticos",
        "desarrollo de software y soluciones digitales",
        "instalacion de redes y sistemas de seguridad",
    ],
    "Mobiliario": [
        "fabricacion y venta de muebles de madera",
        "carpinteria metalica y mobiliario escolar",
        "diseno y produccion de mobiliario para oficinas",
    ],
    "Suministros Agricolas": [
        "venta de insumos agricolas y semillas mejoradas",
        "distribucion de fertilizantes y productos agroquimicos",
        "comercializacion de herramientas para el agro",
    ],
    "Imprenta": [
        "servicios de imprenta y reproduccion de documentos",
        "diseno grafico e impresion de material publicitario",
        "produccion de etiquetas y empaques personalizados",
    ],
    "Reciclaje": [
        "acopio y clasificacion de materiales reciclables",
        "gestion de residuos solidos y reciclaje industrial",
        "transformacion de plasticos y papel reciclado",
    ],
}

# Business name prefixes/suffixes for each rubro
BUSINESS_NAME_PATTERNS = {
    "Alimentos y Bebidas": [
        "Comedor {nombre}",
        "Sabor {apellido}",
        "{nombre} Catering",
        "Delicias de {municipio}",
        "Cocina {apellido}",
        "{inicial}. Alimentos",
    ],
    "Textiles y Uniformes": [
        "Textiles {apellido}",
        "Confecciones {municipio}",
        "{apellido} Uniformes",
        "Costura {nombre}",
        "Maquila {apellido}",
    ],
    "Construccion": [
        "Construcciones {apellido}",
        "{apellido} Ingenieria",
        "Obras {municipio}",
        "{inicial}. Construccion",
    ],
    "Servicios de Limpieza": [
        "Limpieza {apellido}",
        "{municipio} Clean",
        "Servicios {nombre}",
        "Clean {apellido}",
    ],
    "Transporte": [
        "Transportes {apellido}",
        "Carga {municipio}",
        "Fletes {nombre}",
        "{apellido} Distribuciones",
    ],
    "Tecnologia": [
        "{apellido} Tech",
        "Soluciones {nombre}",
        "Tecno {municipio}",
        "{inicial}. Sistemas",
    ],
    "Mobiliario": [
        "Muebles {apellido}",
        "{apellido} Diseno",
        "Carpinteria {municipio}",
        "Mobiliario {nombre}",
    ],
    "Suministros Agricolas": [
        "Agro {apellido}",
        "Semillas {municipio}",
        "Campo {nombre}",
        "{apellido} Suministros",
    ],
    "Imprenta": [
        "Imprenta {apellido}",
        "Grafica {municipio}",
        "Impresiones {nombre}",
        "Disenos {apellido}",
    ],
    "Reciclaje": [
        "Reciclaje {apellido}",
        "Eco {municipio}",
        "Verde {nombre}",
        "{apellido} Recuperacion",
    ],
}

# Salvadoran first names
NOMBRES_FEMENINOS = [
    "Maria", "Ana", "Sandra", "Rosa", "Carmen", "Gloria", "Norma", "Patricia",
    "Silvia", "Vilma", "Blanca", "Marta", "Irma", "Ruth", "Nancy", "Sonia",
    "Elena", "Yolanda", "Clara", "Dora", "Miriam", "Alma", "Ligia", "Leticia",
    "Dalila", "Marleni", "Xiomara", "Nelly", "Bertha", "Adela", "Alicia",
    "Margarita", "Angelica", "Esperanza", "Concepcion", "Reina", "Celia",
    "Marlene", "Julia", "Maritza", "Elsa", "Dinora", "Carolina", "Katherine",
    "Jennifer", "Marcela", "Gabriela", "Karla", "Yesenia", "Lourdes",
]

NOMBRES_MASCULINOS = [
    "Jose", "Carlos", "Juan", "Manuel", "Francisco", "Antonio", "Miguel",
    "Luis", "Rafael", "Roberto", "Mario", "Jorge", "David", "Oscar",
    "Hector", "Victor", "Eduardo", "William", "Diego", "Fernando", "Kevin",
    "Bryan", "Henry", "Marvin", "Rene", "Saul", "Julio", "Raul", "Santos",
    "Jaime", "Douglas", "Alexander", "Moises", "Isaac", "Joel", "Daniel",
    "Mauricio", "Ricardo", "Marco", "Edwin", "Marcos", "Wilfredo", "German",
    "Armando", "Andres", "Pablo", "Christian", "Adrian", "Salvador", "Rene",
]

NOMBRES = NOMBRES_FEMENINOS + NOMBRES_MASCULINOS

# Salvadoran last names (common in El Salvador)
APELLIDOS = [
    "Garcia", "Hernandez", "Martinez", "Lopez", "Gonzalez", "Rodriguez",
    "Perez", "Sanchez", "Ramirez", "Cruz", "Flores", "Rivera", "Castillo",
    "Reyes", "Morales", "Ortiz", "Aguilar", "Gutierrez", "Mendoza",
    "Vasquez", "Castro", "Romero", "Moreno", "Alvarez", "Herrera", "Medina",
    "Guzman", "Lara", "Pena", "Salazar", "Molina", "Soto", "Vargas", "Rivas",
    "Campos", "Delgado", "Pineda", "Alvarado", "Lemus", "Chacon", "Coreas",
    "Portillo", "Quintanilla", "Marroquin", "Orellana", "Escobar", "Melgar",
    "Ventura", "Lovo", "Contreras", "Barrera", "Carballo", "Larios",
    "Guardado", "Ayala", "Zuniga", "Menjivar", "Ochoa", "Henriquez",
    "Serrano", "Nunez", "Aragon", "Galdamez", "Alas", "Caceres",
    "Monterrosa", "Dubon", "Huezo", "Renderos", "Chavez", "Landaverde",
    "Penado", "Sibrian", "Palacios", "Navarrete", "Villalobos", "Argueta",
]

# Occupations mapped to rubros
OCUPACIONES_POR_RUBRO = {
    "Alimentos y Bebidas": [
        "Cocinero/a", "Chef", "Panadero/a", "Pastelero/a", "Catering",
        "Empresario/a de alimentos",
    ],
    "Textiles y Uniformes": [
        "Sastre", "Modista", "Confeccionista textil", "Costurero/a industrial",
        "Bordador/a", "Operario/a textil",
    ],
    "Construccion": [
        "Albanil", "Maestro de obras", "Contratista", "Carpintero/a",
        "Pintor/a", "Electricista",
    ],
    "Servicios de Limpieza": [
        "Supervisor/a de limpieza", "Servicios generales",
        "Empresario/a de limpieza", "Jefe/a de mantenimiento",
    ],
    "Transporte": [
        "Conductor/a", "Transportista", "Distribuidor/a",
        "Operador/a logistico/a",
    ],
    "Tecnologia": [
        "Tecnico/a en informatica", "Desarrollador/a de software",
        "Soporte tecnico", "Administrador/a de sistemas",
    ],
    "Mobiliario": [
        "Carpintero/a", "Ebanista", "Disenador/a de muebles",
        "Fabricante de muebles", "Tapicero/a",
    ],
    "Suministros Agricolas": [
        "Agricultor/a", "Vendedor/a de insumos", "Agropecuario/a",
        "Distribuidor/a agricola",
    ],
    "Imprenta": [
        "Disenador/a grafico", "Impresor/a", "Editor/a",
        "Operario/a de imprenta",
    ],
    "Reciclaje": [
        "Reciclador/a", "Gestor/a de residuos", "Clasificador/a de materiales",
        "Empresario/a de reciclaje",
    ],
}

# Marital statuses
ESTADOS_CIVILES_M = ["soltero", "casado", "divorciado", "viudo", "union libre"]
ESTADOS_CIVILES_F = ["soltera", "casada", "divorciada", "viuda", "union libre"]

# Education levels
NIVELES_EDUCATIVOS = [
    "educacion basica incompleta",
    "educacion basica completa",
    "bachillerato",
    "educacion superior incompleta",
    "educacion superior completa",
    "tecnico universitario",
    "universitario completo",
]

# Social economic strata in El Salvador
ESTRATOS = ["bajo", "medio-bajo", "medio", "medio-alto"]

# =============================================================================
# PERSONA TEXT TEMPLATES (Nemotron-style in Salvadoran Spanish)
# =============================================================================

PERSONA_TEMPLATES = [
    # Template 1: Standard personal introduction
    (
        "{nombre} es de {edad} anos, originario/a de {municipio}, "
        "{departamento}. Es {ocupacion} y dueno/a de {negocio}, un negocio "
        "dedicado a {rubro_desc}. Empezo su negocio hace {antiguedad} anos "
        "con ahorros propios y hoy atiende a aproximadamente {clientes} clientes "
        "por semana. {nombre} es {estado_civil} y vive con {hijos} hijos. "
        "Su ingreso mensual aproximado es de ${ingresos}. "
        "Le interesa venderle al Estado para hacer crecer su negocio."
    ),

    # Template 2: Growth and aspiration focused
    (
        "{nombre} tiene {edad} anos y es {ocupacion} de {municipio}, "
        "{departamento}. Comenzo {negocio} hace {antiguedad} anos "
        "como un proyecto familiar y hoy emplea a {empleados} personas. "
        "Su negocio se especializa en {rubro_desc}. "
        "Actualmente gana ${ingresos} mensuales y atiende "
        "a {clientes} clientes regulares. {nombre} es {estado_civil} "
        "con {hijos} hijos y ha invertido en mejorar su equipo de trabajo. "
        "Su meta es calificar como proveedor del Estado y asegurar contratos "
        "estables para su negocio."
    ),

    # Template 3: Formalization story
    (
        "{nombre} es {ocupacion} de {edad} anos, radicado/a en "
        "{municipio}, {departamento}. Durante {antiguedad} anos trabajo "
        "de manera informal hasta que decidio formalizar su negocio "
        "{negocio}, dedicado a {rubro_desc}. Ahora cuenta con matricula "
        "de comercio y registro en la alcaldia. Su negocio genera alrededor "
        "de ${ingresos} mensuales y atiende a {clientes} clientes por semana. "
        "{nombre} es {estado_civil} con {hijos} hijos y cree que el siguiente "
        "paso es registrarse en RUPES para poder contratar con el gobierno."
    ),

    # Template 4: Daily operations focus
    (
        "{nombre} tiene {edad} anos y vive en {municipio}, {departamento}. "
        "Es {ocupacion} y propietario/a de {negocio}, dedicado a "
        "{rubro_desc}. Su negocio opera de lunes a sabado y emplea "
        "a {empleados} personas de la comunidad. Prepara "
        "personalmente los pedidos y supervisa la calidad. "
        "Gana aproximadamente ${ingresos} al mes y tiene {hijos} hijos. "
        "{nombre} es {estado_civil} y le gustaria expandir su negocio "
        "participando en licitaciones publicas."
    ),

    # Template 5: Family business narrative
    (
        "{nombre} es de {edad} anos, de {municipio}, "
        "{departamento}. Su negocio {negocio}, dedicado a {rubro_desc}, "
        "empezo como un emprendimiento familiar hace {antiguedad} anos. "
        "Hoy emplea a {empleados} personas, incluyendo familiares. "
        "Atienden a {clientes} clientes por semana y generan ${ingresos} "
        "mensuales. Tiene {hijos} hijos y es {estado_civil}. "
        "Su experiencia en {rubro_desc} lo/la motiva a buscar "
        "oportunidades de negocio con instituciones del Estado."
    ),

    # Template 6: Equipment / capacity focused
    (
        "{nombre} es {ocupacion} de {edad} anos, originario/a de "
        "{municipio}, {departamento}. Su negocio {negocio} se dedica a "
        "{rubro_desc}. Ha invertido en maquinaria y equipo para aumentar "
        "su capacidad de produccion a {capacidad} unidades por semana. "
        "Actualmente tiene {empleados} empleados y genera ${ingresos} "
        "mensuales. {nombre} es {estado_civil} y tiene {hijos} hijos. "
        "Su objetivo es conseguir contratos con el gobierno para mantener "
        "su capacidad operativa al maximo."
    ),

    # Template 7: Entrepreneurial journey
    (
        "{nombre}, de {edad} anos, es {ocupacion} en {municipio}, "
        "{departamento}. Despues de trabajar varios anos como empleado/a, "
        "decidio emprender con {negocio}, un negocio de {rubro_desc}. "
        "Con {antiguedad} anos de operacion, hoy emplea a "
        "{empleados} personas y atiende a {clientes} clientes "
        "semanalmente. Su ingreso promedio es de ${ingresos} mensuales. "
        "{nombre} es {estado_civil}, tiene {hijos} hijos y actualmente "
        "esta explorando oportunidades de venta al sector publico "
        "para diversificar sus ingresos."
    ),

    # Template 8: Community impact
    (
        "{nombre} tiene {edad} anos y es {ocupacion} en {municipio}, "
        "{departamento}. Su negocio {negocio}, dedicado a {rubro_desc}, "
        "nacio para cubrir una necesidad en su comunidad. Hoy da trabajo "
        "a {empleados} personas locales y atiende a {clientes} clientes "
        "cada semana. Gana ${ingresos} mensuales y es "
        "{estado_civil} con {hijos} hijos. Apoya a otros emprendedores "
        "locales compartiendo experiencia y recursos. "
        "Quiere crecer para generar mas empleo en su comunidad."
    ),
]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generar_dui():
    """Generate a realistic Salvadoran DUI: XXXXXXXX-X"""
    return f"{random.randint(1000000, 99999999):08d}-{random.randint(0, 9)}"


def generar_nit():
    """Generate a realistic Salvadoran NIT: XXXX-XXXXXX-XXX-X"""
    part1 = random.randint(1000, 9999)
    part2 = random.randint(100000, 999999)
    part3 = random.randint(100, 999)
    part4 = random.randint(0, 9)
    return f"{part1:04d}-{part2:06d}-{part3:03d}-{part4}"


def generar_telefono():
    """Generate a realistic Salvadoran phone number: +503 XXXX XXXX"""
    # Common prefixes: 70, 72, 75, 76, 77, 78, 79, 61, 62, 63
    prefix = random.choice(["70", "72", "75", "76", "77", "78", "79", "61", "62", "63"])
    suffix = random.randint(1000, 9999)
    return f"+503{prefix}{suffix:04d}"


def generar_edad(min_age=22, max_age=68):
    """Generate a realistic business owner age."""
    # Weight toward 30-55 range
    weights = [1] * (min_age - 22) + [3] * 25 + [1] * (68 - 55) if min_age < 55 else [1] * (max_age - min_age)
    # Simpler approach: uniform with bias toward mid-range
    return random.choices(range(min_age, max_age + 1), k=1)[0]


def generar_ingresos(rubro):
    """Generate realistic monthly income based on rubro."""
    base_ranges = {
        "Alimentos y Bebidas":      (800, 5000),
        "Textiles y Uniformes":     (700, 4500),
        "Construccion":            (1000, 6000),
        "Servicios de Limpieza":   (600, 3500),
        "Transporte":              (800, 5500),
        "Tecnologia":              (1200, 7000),
        "Mobiliario":              (900, 5000),
        "Suministros Agricolas":   (700, 4000),
        "Imprenta":                (800, 4500),
        "Reciclaje":               (600, 3500),
    }
    low, high = base_ranges.get(rubro, (600, 4000))
    # Weight toward lower end (most MYPE earn less)
    return random.randint(low, high)


def generar_clientes():
    """Generate realistic client count per week."""
    return random.choice([20, 30, 40, 50, 60, 75, 80, 100, 120, 150, 200])


def generar_empleados():
    """Generate realistic employee count for micro/small business."""
    # 50% micro (1-3), 30% small (4-10), 20% tiny (0-1)
    r = random.random()
    if r < 0.2:
        return random.randint(0, 1)
    elif r < 0.7:
        return random.randint(2, 5)
    else:
        return random.randint(6, 15)


def generar_capacidad(rubro):
    """Generate capacity description based on rubro."""
    capacities = {
        "Alimentos y Bebidas":      lambda: f"{random.randint(100, 2000)} comidas/dia",
        "Textiles y Uniformes":     lambda: f"{random.randint(50, 1000)} prendas/semana",
        "Construccion":            lambda: f"{random.randint(1, 5)} obras simultaneas",
        "Servicios de Limpieza":   lambda: f"{random.randint(3, 20)} clientes/dia",
        "Transporte":              lambda: f"{random.randint(1, 10)} viajes/dia",
        "Tecnologia":              lambda: f"{random.randint(10, 200)} equipos/mes",
        "Mobiliario":              lambda: f"{random.randint(10, 200)} piezas/mes",
        "Suministros Agricolas":   lambda: f"{random.randint(50, 2000)} qq/mes",
        "Imprenta":                lambda: f"{random.randint(500, 10000)} impresiones/mes",
        "Reciclaje":               lambda: f"{random.randint(100, 5000)} kg/semana",
    }
    return capacities.get(rubro, lambda: "capacidad variable")()


def generar_ubicacion(municipio, departamento):
    """Generate a realistic location string."""
    cantones = [
        "Centro Urbano", "El Centro", "Barrio El Carmen", "Colonia Nueva",
        "Colonia San Jose", "Barrio San Miguel", "Colonia Las Flores",
        "Residencial El Valle", "Canton El Zapote", "Canton San Antonio",
        "Colonia Santa Marta", "Canton Los Naranjos", "Colonia La Union",
        "Canton Las Brisas", "Barrio San Juan", "Colonia Escalon",
        "Canton San Nicolas", "Residencial San Luis", "Colonia Milagro de la Paz",
        "Canton El Porvenir",
    ]
    canton = random.choice(cantones)
    return f"{canton}, {municipio}, {departamento}"


def generar_nombre_negocio(nombre, apellido, rubro, municipio):
    """Generate a business name from patterns."""
    patrones = BUSINESS_NAME_PATTERNS.get(rubro, ["{apellido} {rubro}"])
    patron = random.choice(patrones)
    inicial = nombre[0].upper()
    return patron.format(
        nombre=nombre,
        apellido=apellido,
        municipio=municipio,
        rubro=rubro.split()[0] if " " in rubro else rubro,
        inicial=inicial,
    )


def seleccionar_genero(nombre):
    """Determine gender from first name."""
    if nombre in NOMBRES_FEMENINOS:
        return "femenino"
    return "masculino"


def articulo_genero(genero):
    """Return appropriate Spanish articles based on gender."""
    if genero == "femenino":
        return "a", "duena", "la", "ella"
    return "o", "dueno", "el", "el"


def generar_persona_text(persona):
    """Generate a 3-5 sentence professional_persona text using templates."""
    template = random.choice(PERSONA_TEMPLATES)

    genero = persona["genero"]
    if genero == "femenino":
        estado_civil = random.choice(ESTADOS_CIVILES_F)
    else:
        estado_civil = random.choice(ESTADOS_CIVILES_M)

    # Pick a random rubro description
    rubro_desc = random.choice(RUBRO_DESCRIPCIONES.get(persona["rubro"], ["su especialidad"]))

    text = template.format(
        nombre=persona["nombre"],
        edad=persona["edad"],
        genero=genero,
        municipio=persona["municipio"],
        departamento=persona["departamento"],
        ocupacion=persona["ocupacion"],
        negocio=persona["nombre_negocio"],
        rubro_desc=rubro_desc,
        antiguedad=persona["antiguedad"],
        clientes=persona["clientes"],
        estado_civil=estado_civil,
        hijos=persona["hijos"],
        ingresos=persona["ingresos_mensuales"],
        empleados=persona["empleados"],
        capacidad=persona["capacidad"],
    )

    # Clean up double spaces and normalize
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def generar_persona(tipo="productor"):
    """Generate a single persona dictionary."""
    # Choose gender and name
    if random.random() < 0.52:  # Slightly more women (many MYPE owners are women)
        nombre = random.choice(NOMBRES_FEMENINOS)
        genero = "femenino"
    else:
        nombre = random.choice(NOMBRES_MASCULINOS)
        genero = "masculino"

    apellido = random.choice(APELLIDOS)
    nombre_completo = f"{nombre} {apellido}"

    # Choose location
    municipio, departamento = random.choice(ALL_MUNICIPIOS)

    # Choose rubro
    rubro = random.choice(RUBROS)

    # Choose occupation
    ocupacion = random.choice(OCUPACIONES_POR_RUBRO[rubro])

    # Generate business name
    nombre_negocio = generar_nombre_negocio(nombre, apellido, rubro, municipio)

    # Demographics
    edad = generar_edad()
    hijos = random.choices(range(0, 6), weights=[15, 20, 25, 20, 12, 8])[0]
    antiguedad = max(1, min(edad - 18 - random.randint(0, 5), random.randint(1, 30)))

    # Business metrics
    ingresos = generar_ingresos(rubro)
    empleados = generar_empleados()
    clientes = generar_clientes()
    capacidad = generar_capacidad(rubro)
    ubicacion = generar_ubicacion(municipio, departamento)

    # IDs
    telefono = generar_telefono()
    dui = generar_dui()
    nit = generar_nit()

    # Experience with the state (for productores)
    experiencia_estado = random.choice(["Ninguna", "1-2 contratos", "3-5 contratos", "Mas de 5 contratos"])

    # Persona text
    persona = {
        "nombre": nombre,
        "apellido": apellido,
        "nombre_completo": nombre_completo,
        "genero": genero,
        "edad": edad,
        "departamento": departamento,
        "municipio": municipio,
        "ubicacion": ubicacion,
        "rubro": rubro,
        "ocupacion": ocupacion,
        "nombre_negocio": nombre_negocio,
        "antiguedad": antiguedad,
        "clientes": clientes,
        "hijos": hijos,
        "ingresos_mensuales": ingresos,
        "empleados": empleados,
        "capacidad": capacidad,
        "telefono": telefono,
        "dui": dui,
        "nit": nit,
        "experiencia_estado": experiencia_estado if tipo == "productor" else "N/A",
    }

    # Generate the professional persona text (needs full dict)
    persona["professional_persona"] = generar_persona_text(persona)

    return persona


# =============================================================================
# MAIN GENERATION
# =============================================================================

def generate_all():
    """Generate all personas and write output files."""
    # Ensure data/ directory exists
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(output_dir, exist_ok=True)

    print("Generando 30 productores...")
    productores = []
    for i in range(30):
        p = generar_persona("productor")
        p["id"] = f"prod-{i+1:03d}"
        productores.append(p)

    print("Generando 20 proveedores...")
    proveedores = []
    for i in range(20):
        p = generar_persona("proveedor")
        p["id"] = f"prov-{i+1:03d}"
        proveedores.append(p)

    # ---- Write productores_demo.csv ----
    prod_csv_fields = [
        "id", "nombre_completo", "edad", "genero", "rubro", "ocupacion",
        "nombre_negocio", "departamento", "municipio", "ubicacion",
        "capacidad", "telefono", "dui", "nit", "experiencia_estado",
        "ingresos_mensuales", "antiguedad", "empleados", "professional_persona",
    ]
    prod_csv_path = os.path.join(output_dir, "productores_demo.csv")
    with open(prod_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=prod_csv_fields, extrasaction="ignore")
        writer.writeheader()
        for p in productores:
            row = {
                "id": p["id"],
                "nombre_completo": p["nombre_completo"],
                "edad": p["edad"],
                "genero": p["genero"],
                "rubro": p["rubro"],
                "ocupacion": p["ocupacion"],
                "nombre_negocio": p["nombre_negocio"],
                "departamento": p["departamento"],
                "municipio": p["municipio"],
                "ubicacion": p["ubicacion"],
                "capacidad": p["capacidad"],
                "telefono": p["telefono"],
                "dui": p["dui"],
                "nit": p["nit"],
                "experiencia_estado": p["experiencia_estado"],
                "ingresos_mensuales": p["ingresos_mensuales"],
                "antiguedad": p["antiguedad"],
                "empleados": p["empleados"],
                "professional_persona": p["professional_persona"],
            }
            writer.writerow(row)
    print(f"  -> {prod_csv_path} ({len(productores)} filas)")

    # ---- Write proveedores_demo.csv ----
    prov_csv_fields = [
        "id", "nombre_completo", "edad", "genero", "rubro", "ocupacion",
        "nombre_negocio", "departamento", "municipio", "ubicacion",
        "capacidad", "telefono", "dui", "nit",
        "ingresos_mensuales", "antiguedad", "empleados", "professional_persona",
    ]
    prov_csv_path = os.path.join(output_dir, "proveedores_demo.csv")
    with open(prov_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=prov_csv_fields, extrasaction="ignore")
        writer.writeheader()
        for p in proveedores:
            row = {
                "id": p["id"],
                "nombre_completo": p["nombre_completo"],
                "edad": p["edad"],
                "genero": p["genero"],
                "rubro": p["rubro"],
                "ocupacion": p["ocupacion"],
                "nombre_negocio": p["nombre_negocio"],
                "departamento": p["departamento"],
                "municipio": p["municipio"],
                "ubicacion": p["ubicacion"],
                "capacidad": p["capacidad"],
                "telefono": p["telefono"],
                "dui": p["dui"],
                "nit": p["nit"],
                "ingresos_mensuales": p["ingresos_mensuales"],
                "antiguedad": p["antiguedad"],
                "empleados": p["empleados"],
                "professional_persona": p["professional_persona"],
            }
            writer.writerow(row)
    print(f"  -> {prov_csv_path} ({len(proveedores)} filas)")

    # ---- Write personas_sinteticas.json ----
    json_output = {
        "metadata": {
            "generator": "generar_personas_fallback.py",
            "date_generated": datetime.now().isoformat(),
            "dataset": "Compa Synthetic Personas (Nemotron-style fallback)",
            "total_productores": len(productores),
            "total_proveedores": len(proveedores),
            "source": "Synthetic — generated from templates, no HuggingFace dependency",
        },
        "rubros_utilizados": RUBROS,
        "departamentos_utilizados": DEPARTAMENTOS,
        "productores": [],
        "proveedores": [],
    }

    for p in productores:
        json_output["productores"].append({
            "id": p["id"],
            "nombre_completo": p["nombre_completo"],
            "demograficos": {
                "edad": p["edad"],
                "genero": p["genero"],
                "estado_civil": "N/A",
                "hijos": p["hijos"],
                "educacion": "N/A",
            },
            "ubicacion": {
                "departamento": p["departamento"],
                "municipio": p["municipio"],
                "direccion": p["ubicacion"],
            },
            "negocio": {
                "nombre": p["nombre_negocio"],
                "rubro": p["rubro"],
                "ocupacion": p["ocupacion"],
                "antiguedad_anos": p["antiguedad"],
                "capacidad": p["capacidad"],
                "empleados": p["empleados"],
                "ingresos_mensuales": p["ingresos_mensuales"],
                "clientes_semanales": p["clientes"],
            },
            "contacto": {
                "telefono": p["telefono"],
                "dui": p["dui"],
                "nit": p["nit"],
            },
            "experiencia_estado": p["experiencia_estado"],
            "professional_persona": p["professional_persona"],
        })

    for p in proveedores:
        json_output["proveedores"].append({
            "id": p["id"],
            "nombre_completo": p["nombre_completo"],
            "demograficos": {
                "edad": p["edad"],
                "genero": p["genero"],
                "hijos": p["hijos"],
            },
            "ubicacion": {
                "departamento": p["departamento"],
                "municipio": p["municipio"],
                "direccion": p["ubicacion"],
            },
            "negocio": {
                "nombre": p["nombre_negocio"],
                "rubro": p["rubro"],
                "ocupacion": p["ocupacion"],
                "antiguedad_anos": p["antiguedad"],
                "capacidad": p["capacidad"],
                "empleados": p["empleados"],
                "ingresos_mensuales": p["ingresos_mensuales"],
            },
            "contacto": {
                "telefono": p["telefono"],
                "dui": p["dui"],
                "nit": p["nit"],
            },
            "professional_persona": p["professional_persona"],
        })

    json_path = os.path.join(output_dir, "personas_sinteticas.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_output, f, ensure_ascii=False, indent=2)
    print(f"  -> {json_path}")

    # ---- Summary ----
    print("\n--- RESUMEN ---")
    rubro_counts = {}
    for p in productores:
        rubro_counts[p["rubro"]] = rubro_counts.get(p["rubro"], 0) + 1
    print(f"Productores por rubro:")
    for rubro, count in sorted(rubro_counts.items()):
        print(f"  {rubro}: {count}")

    dept_counts = {}
    for p in productores:
        dept_counts[p["departamento"]] = dept_counts.get(p["departamento"], 0) + 1
    print(f"\nProductores por departamento:")
    for dept, count in sorted(dept_counts.items()):
        print(f"  {dept}: {count}")

    print(f"\nTotal: {len(productores)} productores + {len(proveedores)} proveedores "
          f"= {len(productores) + len(proveedores)} personas sinteticas generadas.")


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    generate_all()
