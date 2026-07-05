#!/usr/bin/env python3
"""
generar_personas_fallback.py — Fallback persona generator for Compa hackathon.

PURPOSE: Generate realistic Salvadoran business personas WITHOUT accessing
HuggingFace datasets library. Used when nvidia/Nemotron-Personas-El-Salvador
is gated, too large to download, or conference WiFi is unreliable.

OUTPUT:
  - data/productores_demo.csv  (30 personas with business profiles)
  - data/proveedores_demo.csv  (20 supplier personas)
  - data/personas_sinteticas.json (full Nemotron-format persona texts)

USAGE:
  python scripts/generar_personas_fallback.py

DEPENDENCIES:
  Python 3.8+ (no external packages — uses random, json, csv only)

FIELD MAPPING (Nemotron-compatible):
  professional_persona  → Multi-sentence Spanish text describing persona
  departamento          → 1 of 14 real departamentos of El Salvador
  municipio             → 1 of 44 real municipios
  ocupacion             → Business-related occupation
  rubro_negocio         → Standardized business category
  _business_score       → Scored 0-100 by keyword frequency in persona text

AUTHOR: Compa Buildathon Team
DATE: 2026-07-04
"""

import random
import json
import csv
import os

# ─── Constants ───────────────────────────────────────────────────────────────

DEPARTAMENTOS_MUNICIPIOS = {
    "Ahuachapan": ["Ahuachapan", "Atiquizaya", "Tacuba", "San Francisco Menendez"],
    "Santa Ana": ["Santa Ana", "Metapan", "Chalchuapa", "Coatepeque", "Texistepeque"],
    "Sonsonate": ["Sonsonate", "Acajutla", "Izalco", "Armenia", "San Antonio del Monte"],
    "Chalatenango": ["Chalatenango", "La Palma", "Tejutla", "Nueva Concepcion", "Dulce Nombre de Maria"],
    "La Libertad": ["Santa Tecla", "Antiguo Cuscatlan", "Nuevo Cuscatlan", "San Juan Opico", "Quezaltepeque"],
    "San Salvador": ["San Salvador", "Soyapango", "Mejicanos", "Delgado", "Ilopango", "Cuscatancingo", "San Marcos", "Apopa"],
    "Cuscatlan": ["Cojutepeque", "Suchitoto", "San Pedro Perulapan"],
    "La Paz": ["Zacatecoluca", "San Pedro Nonualco", "Santiago Nonualco", "Olocuilta"],
    "Cabanas": ["Sensuntepeque", "Ilobasco", "Victoria"],
    "San Vicente": ["San Vicente", "San Sebastian", "San Cayetano Istepeque"],
    "Usulutan": ["Usulutan", "Jiquilisco", "Berlin", "Santiago de Maria", "Puerto El Triunfo"],
    "San Miguel": ["San Miguel", "Chinameca", "Moncagua", "Ciudad Barrios", "Chapeltique"],
    "Morazan": ["San Francisco Gotera", "Perquin", "Corinto", "Osicala", "Meanguera"],
    "La Union": ["La Union", "Pasaquina", "Puerto de La Union", "Santa Rosa de Lima", "Conchagua"]
}

RUBROS = [
    ("Alimentos y Bebidas", "Preparacion y venta de alimentos y bebidas preparadas"),
    ("Textiles y Uniformes", "Confeccion de prendas de vestir y uniformes"),
    ("Construccion y Mantenimiento", "Servicios de construccion y mantenimiento de edificios"),
    ("Suministros Agricolas", "Produccion y venta de productos agricolas"),
    ("Tecnologia y Servicios Digitales", "Desarrollo de software y servicios informaticos"),
    ("Servicios de Limpieza y Mantenimiento", "Servicios de limpieza general y especializada"),
    ("Transporte y Logistica", "Servicios de transporte de carga y pasajeros"),
    ("Calzado y Marroquinería", "Fabricacion y reparacion de calzado y articulos de cuero"),
    ("Mobiliario y Equipo", "Fabricacion de muebles y equipamiento"),
    ("Imprenta y Publicidad", "Servicios de impresion y publicidad"),
    ("Reciclaje y Gestion de Residuos", "Recoleccion y procesamiento de materiales reciclables"),
    ("Servicios Profesionales y Eventos", "Organizacion de eventos y servicios profesionales"),
]

PRIMEROS_NOMBRES_F = [
    "Maria", "Ana", "Rosa", "Lidia", "Margarita", "Marta", "Katherine",
    "Gabriela", "Sandra", "Veronica", "Diana", "Claudia", "Sofia", "Andrea"
]
PRIMEROS_NOMBRES_M = [
    "Jose", "Carlos", "Pedro", "Francisco", "Roberto", "Jorge", "Wilfredo",
    "Rene", "Manuel", "Miguel", "Luis", "Juan", "David", "Oscar"
]
APELLIDOS = [
    "Henriquez", "Rivera", "Melendez", "Campos", "Garcia", "Bonilla", "Portillo",
    "Quintanilla", "Lopez", "Mejia", "Hernandez", "Valencia", "Giron", "Alas",
    "Gonzalez", "Pineda", "Ayala", "Chinchilla", "Flores", "Aguilar", "Parada",
    "Benitez", "Contreras", "Guardado", "Machado", "Pena", "Castro", "Ramirez",
    "Martinez", "Diaz", "Alvarado", "Rivas", "Sorto", "Orellana", "Escobar"
]

OCUPACIONES = {
    "Alimentos y Bebidas": ["Cocinera", "Panadero", "Chef", "Pastelero", "Carnicero", "Empacador de alimentos"],
    "Textiles y Uniformes": ["Sastre", "Modista", "Bordador", "Confeccionista", "Disenador textil"],
    "Construccion y Mantenimiento": ["Maestro de obra", "Albanil", "Electricista", "Pintor", "Carpintero"],
    "Suministros Agricolas": ["Agricultor", "Ganadero", "Horticultor", "Viverista", "Apicultor"],
    "Tecnologia y Servicios Digitales": ["Desarrollador", "Disenador grafico", "Ingeniero de sistemas", "Community manager"],
    "Servicios de Limpieza y Mantenimiento": ["Supervisor de limpieza", "Servicios generales", "Desinfectador"],
    "Transporte y Logistica": ["Conductor", "Transportista", "Operador logistico"],
    "Calzado y Marroquinería": ["Zapatero", "Talabartero", "Disenador de calzado"],
    "Mobiliario y Equipo": ["Carpintero", "Ebanista", "Tapicero", "Soldador"],
    "Imprenta y Publicidad": ["Digitalizador", "Impresor", "Rotulista", "Disenador grafico"],
    "Reciclaje y Gestion de Residuos": ["Reciclador", "Gestor de residuos", "Clasificador"],
    "Servicios Profesionales y Eventos": ["Organizador de eventos", "Relacionista publico", "Coordinador logistico"],
}

def generate_dui():
    """Generate a realistic DUI (Documento Unico de Identidad) number."""
    return f"{random.randint(1000000, 9999999)}-{random.randint(0, 9)}"

def generate_nit():
    """Generate a realistic NIT (Numero de Identificacion Tributaria) number."""
    return f"{random.randint(1000, 9999)}-{random.randint(100000, 999999)}-{random.randint(100, 999)}-{random.randint(0, 9)}"

def generate_phone():
    """Generate a realistic Salvadoran mobile phone number."""
    return f"+503{random.randint(60000000, 79999999)}"

def generate_persona_text(genero, nombre, edad, departamento, municipio, rubro, ocupacion, mismo="misma", is_business_owner=True):
    """
    Generate a professional_persona text in Salvadoran Spanish,
    matching the Nemotron dataset format.

    The text includes business signals that the Python filter script
    uses to score business_owner_likelihood: "negocio propio", "dueno de",
    "emprendimiento", "licencia", "matricula", "formalice", "RUPES", etc.
    """
    el = "ella" if genero == "Femenino" else "el"
    genero_label = "mujer" if genero == "Femenino" else "hombre"
    su = "su"

    if genero == "Femenino":
        related_verb = "originaria de"
    else:
        related_verb = "originario de"

    business_terms = [
        f"Tiene un negocio propio de {rubro.lower()}",
        f"Es dueno de su propio emprendimiento en {rubro.lower()}",
        f"Tiene su negocio formalizado con licencia municipal y matricula de comercio",
        f"Ha formalizado su negocio, paga impuestos y tiene matricula de comercio activa",
        f"Su emprendimiento es su principal fuente de ingresos y ya esta registrado en RUPES",
    ]

    state_experience_templates = [
        f"Nunca ha vendido al Estado pero le interesa participar en licitaciones publicas.",
        f"Ha participado en licitaciones del Estado y ha ganado contratos en el pasado.",
        f"Tiene experiencia vendiendo a instituciones publicas como MAG y MINEDUCYT.",
        f"Esta inscrito en RUPES y busca activamente oportunidades de contratacion publica.",
        f"No tiene experiencia en licitaciones pero tiene la capacidad y las ganas de intentarlo.",
    ]

    capacity_templates = [
        f"Su capacidad actual es de producir para {random.randint(50, 2000)} unidades al mes.",
        f"Atiende a {random.randint(10, 200)} clientes semanales en su local.",
        f"Cuenta con {random.randint(2, 8)} empleados trabajando con {el}.",
        f"Su negocio genera ingresos mensuales de aproximadamente ${random.randint(800, 15000)}.",
        f"Invierte constantemente en mejorar {su} maquinaria y equipo de trabajo.",
    ]

    paragraphs = []
    # Sentence 1: Name, age, origin
    paragraphs.append(
        f"{nombre} es {una_para_genero(genero)} {genero_label} de {edad} anos, {related_verb} "
        f"{municipio}, {departamento}."
    )

    # Sentence 2: Occupation and business
    negocio_type = random.choice([
        f"Es {ocupacion} y tiene un negocio propio de {rubro.lower()}",
        f"Trabaja como {ocupacion} y ha construido un emprendimiento en {rubro.lower()}",
        f"Se dedica a {'la' if genero == 'Femenino' else 'el'} {ocupacion.lower()} con su propio taller/negocio",
    ])
    paragraphs.append(f"{negocio_type} que {el} {mismo} fundo hace {random.randint(2, 25)} anos.")

    # Sentence 3: Business detail
    business_detail = random.choice(business_terms)
    paragraphs.append(f"{business_detail}.")

    # Sentence 4: Capacity / employees
    paragraphs.append(random.choice(capacity_templates))

    # Sentence 5: State experience
    paragraphs.append(random.choice(state_experience_templates))

    # Sentence 6: Aspiration
    aspirations = [
        f"Su sueno es crecer {su} negocio y poder generar mas empleos en {su} comunidad.",
        f"Quiere aprender mas sobre contrataciones publicas para acceder a oportunidades mas grandes.",
        f"Le gustaria asociarse con otros productores locales para competir en licitaciones mas grandes.",
        f"Su meta es tener una marca reconocida a nivel nacional en los proximos {random.randint(2, 5)} anos.",
        f"Busca financiamiento para expandir {su} operacion y comprar equipo mas eficiente.",
    ]
    paragraphs.append(random.choice(aspirations))

    return " ".join(paragraphs)

def una_para_genero(genero):
    return "una" if genero == "Femenino" else "un"

def calcular_business_score(texto):
    """
    Score a professional_persona text for business ownership likelihood.
    Matches the scoring algorithm in simular_datos_compa.py.

    Keywords grouped by weight:
      HIGH (10pts): negocio propio, dueno de, su negocio, emprendimiento
      MEDIUM (5pts): licencia, matricula, formalice, RUPES, factura, proveedor
      LOW (2pts): clientes, taller, local, ventas, mercado, empleados
    """
    texto_lower = texto.lower()
    score = 0

    high_keywords = ["negocio propio", "dueno de", "su negocio", "emprendimiento", "propietario de"]
    medium_keywords = ["licencia", "matricula", "formalice", "rupES", "factura", "proveedor",
                       "formalizado", "registro", "comercio"]
    low_keywords = ["clientes", "taller", "local", "ventas", "mercado", "empleados",
                    "produccion", "capacidad", "ingresos", "invierte"]

    for kw in high_keywords:
        if kw in texto_lower:
            score += 10
    for kw in medium_keywords:
        if kw in texto_lower:
            score += 5
    for kw in low_keywords:
        if kw in texto_lower:
            score += 2

    return min(score, 100)

def generate_personas(count=30):
    """Generate `count` realistic Salvadoran business personas."""
    personas = []
    used_names = set()

    for i in range(count):
        genero = random.choice(["Femenino", "Masculino"])
        nombres_list = PRIMEROS_NOMBRES_F if genero == "Femenino" else PRIMEROS_NOMBRES_M

        # Generate unique name
        while True:
            nombre = f"{random.choice(nombres_list)} {random.choice(APELLIDOS)}"
            apellido2 = random.choice([a for a in APELLIDOS if a != nombre.split()[-1]])
            nombre_completo = f"{nombre} {apellido2}"
            if nombre_completo not in used_names:
                used_names.add(nombre_completo)
                break

        departamento = random.choice(list(DEPARTAMENTOS_MUNICIPIOS.keys()))
        municipio = random.choice(DEPARTAMENTOS_MUNICIPIOS[departamento])

        rubro_obj = random.choice(RUBROS)
        rubro = rubro_obj[0]
        rubro_desc = rubro_obj[1]

        ocupacion = random.choice(OCUPACIONES[rubro])
        mismo = "misma" if genero == "Femenino" else "mismo"

        edad = random.randint(22, 65)

        telefono = generate_phone()
        dui = generate_dui()
        nit = generate_nit()
        capacidad = random.randint(50, 5000)
        empleados = random.randint(1, 20)
        ingreso_mensual = random.randint(800, 15000)

        persona_text = generate_persona_text(
            genero=genero,
            nombre=nombre_completo,
            edad=edad,
            departamento=departamento,
            municipio=municipio,
            rubro=rubro,
            ocupacion=ocupacion,
            mismo=mismo,
            is_business_owner=True,
        )

        business_score = calcular_business_score(persona_text)

        persona = {
            "persona_id": f"pers-{i+1:03d}",
            "name": nombre_completo,
            "age": edad,
            "genero": genero,
            "departamento": departamento,
            "municipio": municipio,
            "ocupacion": ocupacion,
            "rubro_negocio": rubro,
            "rubro_descripcion": rubro_desc,
            "telefono": telefono,
            "dui": dui,
            "nit": nit,
            "capacidad_unidades": capacidad,
            "empleados": empleados,
            "ingreso_mensual_estimado": ingreso_mensual,
            "professional_persona": persona_text,
            "_business_score": business_score,
        }
        personas.append(persona)

    return personas

def persona_to_productor_row(p):
    """Convert a persona dict to a productor CSV-compatible dict."""
    return {
        "id": f"prod-{p['persona_id'].split('-')[1]}",
        "nombre": p["name"],
        "rubro": p["rubro_negocio"],
        "ubicacion": f"{p['municipio']}, {p['departamento']}",
        "capacidad": f"{p['capacidad_unidades']} unidades/mes",
        "telefono": p["telefono"],
        "dui": p["dui"],
        "nit": p["nit"],
        "experiencia_estado": "Ninguna" if random.random() > 0.6 else "Experiencia previa",
        "ingreso_mensual": p["ingreso_mensual_estimado"],
        "nombre_negocio": f"Negocio de {p['name'].split()[0]}",
        "antiguedad_anos": max(1, p["age"] - random.randint(18, 35)),
        "empleados": p["empleados"],
    }

def persona_to_proveedor_row(p):
    """Convert a persona dict to a proveedor CSV-compatible dict."""
    return {
        "id": f"prov-{p['persona_id'].split('-')[1]}",
        "nombre": p["name"],
        "rubro": p["rubro_negocio"],
        "ubicacion": f"{p['municipio']}, {p['departamento']}",
        "capacidad": f"{p['capacidad_unidades']} unidades/mes",
        "telefono": p["telefono"],
        "personalidad": random.choice(["agresivo", "conservador", "estrategico"]),
    }

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    print("Generando 30 personas sinteticas...")
    personas = generate_personas(count=30)

    # Save full JSON with Nemotron-format personas
    json_path = os.path.join(data_dir, "personas_sinteticas.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "_meta": {
                "source": "generar_personas_fallback.py",
                "format": "Nemotron-compatible synthetic personas",
                "count": len(personas),
                "generated": "2026-07-04",
                "hackathon": "Compa Buildathon",
                "note": "Fallback dataset when nvidia/Nemotron-Personas-El-Salvador is inaccessible",
            },
            "personas": personas,
        }, f, ensure_ascii=False, indent=2)
    print(f"  -> {json_path} ({len(personas)} personas)")

    # Generate productores CSV (first 10 by default)
    productores = [persona_to_productor_row(p) for p in personas[:10]]
    csv_prod_path = os.path.join(data_dir, "productores_demo.csv")
    prod_fields = ["id", "nombre", "rubro", "ubicacion", "capacidad", "telefono",
                   "dui", "nit", "experiencia_estado", "ingreso_mensual",
                   "nombre_negocio", "antiguedad_anos", "empleados"]
    with open(csv_prod_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=prod_fields)
        writer.writeheader()
        writer.writerows(productores)
    print(f"  -> {csv_prod_path} ({len(productores)} productores)")

    # Generate proveedores CSV (remaining 20 or first 20)
    proveedores_raw = personas[10:30] if len(personas) >= 20 else personas[:20]
    proveedores = [persona_to_proveedor_row(p) for p in proveedores_raw]
    csv_prov_path = os.path.join(data_dir, "proveedores_demo.csv")
    prov_fields = ["id", "nombre", "rubro", "ubicacion", "capacidad", "telefono", "personalidad"]
    with open(csv_prov_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=prov_fields)
        writer.writeheader()
        writer.writerows(proveedores)
    print(f"  -> {csv_prov_path} ({len(proveedores)} proveedores)")

    print("\nBusiness score distribution:")
    scores = [p["_business_score"] for p in personas]
    print(f"  Min: {min(scores)}, Max: {max(scores)}, Avg: {sum(scores)/len(scores):.0f}")
    print(f"  High (70+): {len([s for s in scores if s >= 70])}")
    print(f"  Medium (40-69): {len([s for s in scores if 40 <= s < 70])}")
    print(f"  Low (<40): {len([s for s in scores if s < 40])}")

    print("\nDone. Files ready for Supabase seeding or n8n Code node consumption.")

if __name__ == "__main__":
    main()
