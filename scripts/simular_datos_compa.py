#!/usr/bin/env python3
"""
simular_datos_compa.py — Pipeline completo de generacion de datos demo para Compa.

Flujo:
  1. Cargar dataset nvidia/Nemotron-Personas-El-Salvador desde HuggingFace
     (con fallback sintetico si no esta disponible)
  2. Scoring de probabilidad de dueno de negocio sobre professional_persona
  3. Extraer nombres, inferir rubros del texto de la persona
  4. Generar data/productores_demo.csv y data/proveedores_demo.csv
  5. Generar oportunidades sinteticas al estilo COMPRASAL
  6. Insertar todo en Supabase

Uso:
  python scripts/simular_datos_compa.py                    # pipeline completo
  python scripts/simular_datos_compa.py --huggingface-only # solo carga HF
  python scripts/simular_datos_compa.py --csv-only         # solo genera CSVs
  python scripts/simular_datos_compa.py --supabase-only    # solo inserta en DB
  python scripts/simular_datos_compa.py --fallback          # fuerza fallback

Requiere:
  pip install datasets supabase pandas python-dotenv

Variables de entorno (.env):
  SUPABASE_URL      — https://xxxxx.supabase.co
  SUPABASE_KEY      — service_role key (para inserts)
  SUPABASE_TABLES   — (opcional) default: productores,oportunidades,proveedores

Autor: Compa Buildathon Team — 2026-07-04
"""

from __future__ import annotations

import csv
import json
import os
import random
import re
import sys
from collections import Counter
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

# ─── Constantes de ruta ───────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# ─── Configuracion ────────────────────────────────────────────────────────────
BUSINESS_SCORE_THRESHOLD = 20        # minimo para ser considerado dueno de negocio
NUM_PRODUCTORES = 15                 # cuantos productores generar
NUM_PROVEEDORES = 15                 # cuantos proveedores generar
NUM_OPORTUNIDADES = 25              # cuantas oportunidades COMPRASAL generar
SUPABASE_TABLES = os.getenv("SUPABASE_TABLES", "productores,oportunidades,proveedores").split(",")

# ─── 1. CAMPOS DEL DATASET NEMOTRON ──────────────────────────────────────────
# Documentacion completa de los 24 campos del dataset:
#   nvidia/Nemotron-Personas-El-Salvador
#
#   Config: 'default' | Split: 'train' | Streaming: soportado
#
#   Campo                          Tipo     Descripcion
#   ─────────────────────────────────────────────────────────────────────
#   uuid                           string   Identificador unico (UUID v4)
#   professional_persona           string   Texto narrativo en espanol sobre la vida
#                                           profesional (3-5 oraciones, estilo
#                                           "Nombre, de XX anios, ...")
#   sports_persona                 string   Perfil deportivo
#   arts_persona                   string   Perfil artistico/cultural
#   travel_persona                 string   Perfil de viajes
#   culinary_persona               string   Perfil culinario
#   family_persona                 string   Perfil familiar
#   persona                        string   Narrativa completa unificada
#   cultural_background            string   Trasfondo cultural
#   skills_and_expertise           string   Habilidades en texto narrativo
#   skills_and_expertise_list      string   Lista JSON de habilidades
#   hobbies_and_interests          string   Pasatiempos en texto
#   hobbies_and_interests_list     string   Lista JSON de pasatiempos
#   career_goals_and_ambitions     string   Metas profesionales (senial de negocio)
#   sex                            string   "Masculino" | "Femenino"
#   age                            int64    Edad en anios (18-100+)
#   languages_spoken               string   Idiomas (e.g. "espanol", "espanol e ingles")
#   marital_status                 string   "soltero"|"casado"|"union_libre"|...
#   household_type                 string   "nuclear"|"monoparental"|"extendida"|...
#   education_level                string   "ninguno"|"primaria"|"secundaria"|
#                                           "bachillerato"|"tecnico"|"universitario"
#   occupation                     string   Ocupacion CIUU estandar (e.g.
#                                           "Actividades de restaurantes y de
#                                           comida ambulante")
#   area                           string   "urbano" | "rural"
#   municipality                   string   1 de 44 municipios
#   department                     string   1 de 14 departamentos
#   country                        string   "El Salvador"

# ─── 2. ACCESO AL DATASET ─────────────────────────────────────────────────────
# Acceso: NO gated, NO requiere token. Carga directa con:
#
#     from datasets import load_dataset
#     ds = load_dataset("nvidia/Nemotron-Personas-El-Salvador",
#                       split="train", streaming=True)
#
# El dataset usa archivos Parquet (~3 shards de ~200MB c/u).
# streaming=True evita descargar todo; itera secuencialmente.
# Sin streaming, la descarga completa son ~600MB — factible en WiFi de
# conferencia si hay 5+ minutos.
#


# ═══════════════════════════════════════════════════════════════════════════════
#  SECCION A: CARGA DEL DATASET (HuggingFace + Fallback)
# ═══════════════════════════════════════════════════════════════════════════════

def load_dataset_huggingface() -> Optional[List[Dict[str, Any]]]:
    """
    Carga el dataset Nemotron desde HuggingFace con streaming.
    Retorna lista de diccionarios o None si falla.

    Acceso: el dataset NO es gated, no requiere token.
    Se usa streaming=True para evitar descargar todo (~600MB).

    Returns:
        List[Dict] con las primeras ~1000 filas puntuadas, o None si falla.
    """
    try:
        from datasets import load_dataset  # type: ignore
    except ImportError:
        print("[!] datasets no instalado. pip install datasets")
        return None

    try:
        print("[*] Cargando nvidia/Nemotron-Personas-El-Salvador (streaming)...")
        ds = load_dataset(
            "nvidia/Nemotron-Personas-El-Salvador",
            split="train",
            streaming=True,
        )
        print(f"[+] Dataset cargado. Features: {list(ds.features.keys())}")
        return ds
    except Exception as e:
        print(f"[!] Error cargando dataset HF: {e}")
        return None


def _normalize(text: str) -> str:
    """
    Normaliza texto eliminando acentos y diacriticos para matching robusto.
    "elaboración de carne" -> "elaboracion de carne"
    """
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ü': 'u', 'ñ': 'n',
        'Á': 'a', 'É': 'e', 'Í': 'i', 'Ó': 'o', 'Ú': 'u',
        'Ü': 'u', 'Ñ': 'n',
    }
    result = []
    for ch in text:
        result.append(replacements.get(ch, ch))
    return ''.join(result)


def score_business_owner(row: Dict[str, Any]) -> int:
    """
    Puntua la probabilidad de que una persona sea duena de negocio basado
    en el texto de professional_persona + persona + career_goals.

    Algoritmo: suma ponderada de coincidencias de keywords.

    Categorias de peso:
      - Alta (15pt): "negocio propio", "propietario", "dueno de",
                      "su propio puesto/tienda/taller/negocio",
                      "registro mercantil", "matricula de comercio",
                      "al frente de su"
      - Media (10pt): "cuenta propia", "formalizar", "microcredito",
                       "abrio su", "monto el negocio", "puso su propio",
                       "trabaja por su cuenta", "emprendimien"
      - Baja (5pt):  "independiente", "licencia", "clientes",
                      "proveedores", "socios", "ampliar el negocio"
      - Rubro (8pt):  "comedor", "pupuseria", "panaderia",
                       "tortilleria", "ferreteria", "abarrotes",
                       "puesto de mercado", "negocio familiar"

    Args:
        row: Una fila del dataset Nemotron.

    Returns:
        int: Puntaje 0-100+. Threshold recomendado: 20.
    """
    text_fields = [
        row.get("professional_persona", "") or "",
        row.get("persona", "") or "",
        row.get("career_goals_and_ambitions", "") or "",
    ]
    text = _normalize(" ".join(text_fields).lower())

    keywords = [
        # Alta — seniales directas de propiedad de negocio
        ("negocio propio", 15),
        ("propietario", 15),
        ("dueno de", 15),
        ("su propio negocio", 15),
        ("su propio puesto", 15),
        ("su propia tienda", 15),
        ("su propio taller", 15),
        ("su propio local", 15),
        ("registro mercantil", 15),
        ("matricula de comercio", 15),
        ("al frente de su", 15),
        # Media — seniales de emprendimiento o formalizacion
        ("emprendimien", 10),
        ("cuenta propia", 10),
        ("formalizar", 10),
        ("formalice", 8),
        ("abrio su", 10),
        ("monto el negocio", 10),
        ("puso su propio", 10),
        ("trabaja por su cuenta", 10),
        ("microcredito", 10),
        ("credito para negocio", 10),
        # Baja — seniales de actividad comercial
        ("independiente", 5),
        ("licencia", 5),
        ("atiende su", 8),
        ("vende sus productos", 8),
        ("vende en el mercado", 8),
        ("negocio familiar", 8),
        ("ampliar el negocio", 8),
        ("hacer crecer su negocio", 10),
        ("socios", 5),
        ("clientes", 4),
        ("proveedores", 6),
        # Rubro — tipo de negocio mencionado en el texto
        ("comedor", 8),
        ("pupuseria", 8),
        ("panaderia", 8),
        ("tortilleria", 8),
        ("ferreteria", 8),
        ("abarrotes", 8),
        ("tienda de ", 6),
        ("puesto de venta", 8),
        ("puesto de mercado", 8),
        ("taller de reparacion", 8),
        ("taller mecanico", 8),
        ("alquila", 4),
    ]

    score = 0
    for keyword, weight in keywords:
        if keyword in text:
            score += weight

    return score


def filter_business_owners(ds_iter, max_scan: int = 5000, threshold: int = 20) -> List[Dict]:
    """
    Escanea el dataset, puntua cada fila y retorna las que pasan el threshold,
    ordenadas por score descendente.

    Args:
        ds_iter: Iterable de filas del dataset (streaming).
        max_scan: Maximo de filas a escanear.
        threshold: Puntaje minimo.

    Returns:
        Lista de dicts con {row, score, business_signals}.
    """
    scored = []
    for i, row in enumerate(ds_iter):
        if i >= max_scan:
            break
        if i % 1000 == 0 and i > 0:
            print(f"   Escaneados {i} registros... encontrados {len(scored)} candidatos")

        score = score_business_owner(row)

        # Extraer las seniales que generaron el score (para analisis)
        if score >= threshold:
            rubro_hint = _infer_rubro_from_text(
                (row.get("professional_persona", "") or ""),
                row.get("occupation", "")
            )

            scored.append({
                "row": row,
                "score": score,
                "rubro_hint": rubro_hint,
            })

    # Ordenar por score descendente
    scored.sort(key=lambda x: x["score"], reverse=True)
    print(f"\n[+] Total candidatos con score>={threshold}: {len(scored)}")
    return scored


def _infer_rubro_from_text(text: str, occupation: str) -> str:
    """
    Infiere el rubro de negocio mas probable basado en el texto de la persona
    y su ocupacion CIUU.

    Usa un sistema de scoring de categorias contra keywords en el texto.
    """
    occ_lower = _normalize(occupation.lower())
    combined = _normalize(text.lower()) + " " + occ_lower

    categories = {
        "Alimentos y Bebidas": [
            "alimento", "comida", "restaurante", "cocina", "cocin",
            "panaderia", "pupuseria", "tortilleria", "comedor",
            "catering", "bebida", "gastronomia", "chef", "carnic",
            "elaboracion de productos", "conservacion de carne",
            "actividades de restaurantes", "comida ambulante",
        ],
        "Textiles y Uniformes": [
            "textil", "confeccion", "costura", "prendas de vestir",
            "uniforme", "modista", "sastre", "fabricacion de prendas",
            "bordado", "telar", "calzado", "ropa",
        ],
        "Construccion": [
            "construccion", "albanil", "maestro de obra", "edificio",
            "obra", "carpinteria", "electricista", "pintor",
            "construccion de edificios", "mantenimiento",
        ],
        "Servicios de Limpieza": [
            "limpieza", "fumigacion", "desinfeccion", "aseo",
            "lavado", "limpieza en seco",
        ],
        "Transporte y Logistica": [
            "transporte", "camion", "flete", "logistica",
            "carga", "pasajeros", "conductor", "transportista",
            "transporte de carga", "transporte urbano",
        ],
        "Tecnologia": [
            "tecnologia", "informatica", "software", "desarrollo",
            "sistemas", "computacion", "telecomunicacion",
            "centros de llamadas", "programador",
        ],
        "Agricola": [
            "agricola", "cultivo", "ganaderia", "cosecha",
            "cereales", "hortalizas", "semilla", "fertilizante",
            "cria de", "campo", "vivero", "apicultura",
        ],
        "Mobiliario y Equipo": [
            "mueble", "carpintero", "ebanista", "fabricacion de muebles",
            "tapicero", "soldador", "metalico",
        ],
        "Servicios Profesionales": [
            "contabilidad", "auditoria", "consultoria", "fiscal",
            "abogado", "juridico", "contador", "notario",
            "actividades juridicas", "servicios financieros",
        ],
        "Salud": [
            "medico", "odontologo", "hospital", "salud",
            "farmaceutico", "farmacia", "enfermeria",
            "atencion de la salud",
        ],
        "Belleza": [
            "peluqueria", "belleza", "barberia", "salon",
            "manicure", "cosmetologia",
        ],
        "Imprenta y Publicidad": [
            "imprenta", "impresion", "publicidad", "rotulacion",
            "grafico", "diseno grafico",
        ],
    }

    best_category = "Servicios Generales"
    best_score = 0

    for category, kws in categories.items():
        score = 0
        for kw in kws:
            if kw in combined:
                score += 1
        # Bonificar si la ocupacion CIUU contiene el nombre de la categoria
        for kw in category.lower().split():
            if kw in occ_lower:
                score += 2

        if score > best_score:
            best_score = score
            best_category = category

    return best_category


# ─── 3. EXTRACCION DE NOMBRES ──────────────────────────────────────────────────

# Lista de apellidos salvadorenos comunes para generar nombres completos
APELLIDOS_SALVADORENOS = [
    "Henriquez", "Rivera", "Melendez", "Campos", "Garcia", "Bonilla", "Portillo",
    "Quintanilla", "Lopez", "Mejia", "Hernandez", "Valencia", "Giron", "Alas",
    "Gonzalez", "Pineda", "Ayala", "Chinchilla", "Flores", "Aguilar", "Parada",
    "Benitez", "Contreras", "Guardado", "Machado", "Pena", "Castro", "Ramirez",
    "Martinez", "Diaz", "Alvarado", "Rivas", "Sorto", "Orellana", "Escobar",
    "Mendoza", "Velasco", "Castellanos", "Sibrian", "Cortez", "Serrano", "Rivas",
    "Reyes", "Torres", "Moreno", "Romero", "Alvarez", "Vasquez", "Herrera",
    "Medrano", "Navarro", "Marroquin", "Olmedo", "Carballo", "Zelaya",
]

SEGUNDOS_NOMBRES = [
    "Alberto", "Antonio", "Armando", "Benjamin", "Daniel", "David",
    "Eduardo", "Enrique", "Ernesto", "Esteban", "Fabricio", "Fernando",
    "Francisco", "Gabriel", "Guillermo", "Ismael", "Javier", "Jose",
    "Julian", "Luis", "Manuel", "Marcelino", "Mario", "Mauricio",
    "Miguel", "Nelson", "Oscar", "Pablo", "Rafael", "Rene",
    "Ricardo", "Roberto", "Salvador", "Samuel", "Santiago", "Tomas",
    "Adriana", "Alejandra", "Beatriz", "Carmen", "Carolina", "Catalina",
    "Cristina", "Daniela", "Diana", "Elena", "Esperanza", "Esther",
    "Gabriela", "Gloria", "Isabel", "Katherine", "Lorena", "Luisa",
    "Marcela", "Margarita", "Marta", "Milagro", "Nathaly", "Patricia",
    "Rebeca", "Rosa", "Sandra", "Sofia", "Susana", "Veronica",
]


def extract_first_name(professional_persona: str) -> str:
    """
    Extrae el primer nombre del texto professional_persona.
    El patron tipico es: "Nombre, de XX anios, ..."

    Args:
        professional_persona: Texto narrativo de la persona.

    Returns:
        Primer nombre extraido o "Persona" si falla.
    """
    if not professional_persona:
        return "Persona"
    # El nombre es la primera palabra antes de la coma
    first_part = professional_persona.split(",")[0].strip()
    # A veces viene "Nombre Apellido" — tomar solo la primera palabra
    name = first_part.split()[0] if first_part.split() else "Persona"
    return name


def generate_full_name(first_name: str, sex: str = "Masculino") -> str:
    """
    Genera un nombre completo salvadoreno: primer nombre + apellido compuesto.

    Args:
        first_name: Primer nombre extraido del dataset.
        sex: "Masculino" o "Femenino" — para seleccionar segundo nombre.

    Returns:
        Nombre completo (e.g. "Maria Elena Henriquez").
    """
    apellido1 = random.choice(APELLIDOS_SALVADORENOS)
    apellido2 = random.choice(APELLIDOS_SALVADORENOS)
    # Los apellidos pueden ser el mismo (realista en ES)
    while apellido2 == apellido1 and len(APELLIDOS_SALVADORENOS) > 1:
        apellido2 = random.choice(APELLIDOS_SALVADORENOS)

    # 50% de probabilidad de incluir un segundo nombre
    if random.random() < 0.5:
        segundo = random.choice(SEGUNDOS_NOMBRES)
        # La primera letra del segundo nombre debe coincidir genero
        return f"{first_name} {segundo} {apellido1} {apellido2}"
    else:
        # 30% de usar "de" (comun en ES para mujeres casadas)
        if sex == "Femenino" and random.random() < 0.3:
            return f"{first_name} {apellido1} de {apellido2}"
        return f"{first_name} {apellido1} {apellido2}"


# ─── 4. GENERACION DE DATOS SINCRETICOS ───────────────────────────────────────

TELEFONO_PREFIJOS = ["+503"]

def generate_telefono() -> str:
    """Genera un numero de telefono salvadoreno realista: +503XXXXXXXX (8 digitos)"""
    return f"+503{random.randint(10000000, 99999999)}"


def generate_dui() -> str:
    """Genera un DUI valido: XXXXXXXX-X (8 digitos, guion, digito verificador)"""
    return f"{random.randint(1000000, 99999999):08d}-{random.randint(0, 9)}"


def generate_nit() -> str:
    """Genera un NIT valido: XXXX-XXXXXX-XXX-X"""
    return (f"{random.randint(1000, 9999)}-"
            f"{random.randint(100000, 999999)}-"
            f"{random.randint(100, 999)}-"
            f"{random.randint(0, 9)}")


# ─── 5. RUBRO INFERENCE ───────────────────────────────────────────────────────

def map_occupation_to_rubro(occupation: str) -> str:
    """
    Mapea una ocupacion CIUU del dataset Nemotron a un rubro estandarizado
    de COMPRASAL. Usa coincidencia de subcadenas contra la ocupacion.

    Mapeo completo de ocupaciones a rubros:

    Ocupacion CIUU (parcial)                              → Rubro COMPRASAL
    ─────────────────────────────────────────────────────────────────────
    Actividades de restaurantes / comida ambulante         → Alimentos y Bebidas
    Elaboracion de productos de panaderia                  → Alimentos y Bebidas
    Elaboracion y conservacion de carne                    → Alimentos y Bebidas
    Fabricacion de prendas de vestir                       → Textiles y Uniformes
    Venta al por menor de prendas de vestir                → Textiles y Uniformes
    Confeccion / textiles                                  → Textiles y Uniformes
    Construccion de edificios                              → Construccion
    Instalaciones electricas                               → Construccion
    Cultivo de cereales / hortalizas / frutas              → Suministros Agricolas
    Cria de ganado / aves                                  → Suministros Agricolas
    Transporte de carga / pasajeros                        → Transporte y Logistica
    Venta al por menor de alimentos / abarrotes            → Alimentos y Bebidas
    Venta al por menor en comercios no especializados      → Alimentos y Bebidas
    Mantenimiento y reparacion vehiculos                   → Transporte y Logistica
    Actividades de contabilidad / auditoria                → Servicios Profesionales
    Fabricacion de muebles                                 → Mobiliario y Equipo
    Peluqueria / tratamientos de belleza                   → Belleza
    Lavado y limpieza                                      → Servicios de Limpieza
    Actividades de centros de llamadas                     → Tecnologia
    Actividades de telecomunicaciones                      → Tecnologia
    Venta al por menor de productos farmaceuticos          → Salud
    Actividades de medicos y odontologos                   → Salud
    Fabricacion de productos metalicos                     → Construccion
    Otras actividades de comercio                          → Servicios Generales
    Otras actividades de manufactura                       → Servicios Generales
    """
    occ_lower = _normalize(occupation.lower())

    # Mapeo de patrones de ocupacion a rubros
    mapping = [
        # Alimentos
        (["restaurante", "comida ambulante", "elaboracion de", "panaderia",
          "conservacion de carne", "carniceria", "preparacion de alimentos",
          "bebida", "alimenticia", "matanza"], "Alimentos y Bebidas"),
        # Textiles
        (["confeccion", "prendas de vestir", "textil", "cuero", "calzado",
          "telar", "bordado", "costura", "fabricacion de prendas",
          "curtido", "marroquiner"], "Textiles y Uniformes"),
        # Construccion
        (["construccion", "albanileria", "electrici", "pintura",
          "carpinteria", "obra", "edificio", "instalaciones electricas",
          "productos metalicos para uso estructural",
          "fontaneria", "plomeria"], "Construccion"),
        # Agricola
        (["cultivo", "agricola", "ganaderia", "cria de", "cereales",
          "hortaliza", "semilla", "agropecuario", "caña de azucar",
          "avicola", "porcino", "apicultura", "vivero"], "Suministros Agricolas"),
        # Transporte
        (["transporte", "carga", "pasajero", "camion", "logistica",
          "flete", "mensajeria", "envio", "conductor"], "Transporte y Logistica"),
        # Limpieza
        (["limpieza", "fumigacion", "desinfeccion", "lavado",
          "aseo", "jardineria"], "Servicios de Limpieza"),
        # Salud
        (["medico", "odontologo", "hospital", "farmaceutico",
          "farmacia", "enfermeria", "salud humana", "optic"],
         "Servicios de Salud"),
        # Tecnologia
        (["centros de llamadas", "telecomunicacion", "informatica",
          "software", "desarrollo", "sistemas", "computacio",
          "programacion", "datos", "tecnologia"], "Tecnologia"),
        # Profesionales
        (["contabilidad", "auditoria", "consultoria", "fiscal",
          "juridico", "abogado", "notario", "contador",
          "actividades juridicas", "servicios financieros",
          "seguro", "inmobiliaria"], "Servicios Profesionales"),
        # Mobiliario
        (["mueble", "carpinteria de taller", "ebanisteria",
          "fabricacion de muebles", "colchones", "tapiceria",
          "equipo de oficina"], "Mobiliario y Equipo"),
        # Belleza
        (["peluqueria", "belleza", "barberia", "salon", "cosmetologia",
          "manicure", "pedicure", "tratamientos de belleza"], "Belleza"),
        # Imprenta
        (["imprenta", "impresion", "publicidad", "rotulacion",
          "grafico", "diseno grafico", "edicion"], "Imprenta y Publicidad"),
    ]

    for patterns, rubro in mapping:
        for pattern in patterns:
            if pattern in occ_lower:
                return rubro

    # Si no hay mapeo directo, verificar comercio generico
    if "comercio" in occ_lower or "venta" in occ_lower:
        return "Servicios Generales"

    return "Servicios Generales"


def format_capacidad(rubro: str, persona_text: str) -> str:
    """
    Genera una descripcion de capacidad productiva basada en el rubro.
    """
    capacidades = {
        "Alimentos y Bebidas": lambda: f"{random.randint(50, 1500)} raciones/dia",
        "Textiles y Uniformes": lambda: f"{random.randint(20, 500)} prendas/semana",
        "Construccion": lambda: f"Capacidad de obra: {random.randint(1, 5)} proyectos simultaneos",
        "Suministros Agricolas": lambda: f"{random.randint(1, 50)} manzanas cultivadas",
        "Tecnologia": lambda: f"{random.randint(1, 10)} proyectos de desarrollo/mes",
        "Servicios de Limpieza": lambda: f"{random.randint(1, 10)} sedes atendidas/semana",
        "Transporte y Logistica": lambda: f"{random.randint(1, 5)} unidades de transporte",
        "Servicios Profesionales": lambda: f"{random.randint(5, 50)} clientes activos",
        "Mobiliario y Equipo": lambda: f"{random.randint(5, 100)} unidades/mes",
        "Imprenta y Publicidad": lambda: f"{random.randint(100, 5000)} impresiones/dia",
        "Servicios de Salud": lambda: f"{random.randint(5, 100)} pacientes/dia",
        "Belleza": lambda: f"{random.randint(5, 30)} clientes/dia",
        "Servicios Generales": lambda: f"{random.randint(1, 20)} contratos/mes",
    }
    gen = capacidades.get(rubro, lambda: f"{random.randint(1, 50)} unidades/mes")
    return gen()


# ═══════════════════════════════════════════════════════════════════════════════
#  SECCION B: GENERACION DE CSVs
# ═══════════════════════════════════════════════════════════════════════════════

def extract_candidates_from_hf(
    max_scan: int = 5000,
    threshold: int = BUSINESS_SCORE_THRESHOLD,
    num_productores: int = NUM_PRODUCTORES,
    num_proveedores: int = NUM_PROVEEDORES,
) -> Tuple[List[Dict], List[Dict]]:
    """
    Pipeline principal: carga HF dataset, filtra por score, extrae datos,
    retorna listas de productores y proveedores.

    Returns:
        (productores, proveedores) — cada uno como lista de dicts.
    """
    ds = load_dataset_huggingface()
    if ds is None:
        return [], []

    candidates = filter_business_owners(ds, max_scan=max_scan, threshold=threshold)
    if not candidates:
        print("[!] No se encontraron candidatos con el threshold actual.")
        return [], []

    # Separar productores (duenos de negocio con alta puntuacion)
    # de proveedores (tambien negocios, rubros complementarios)
    productores = []
    proveedores = []
    used_uuids = set()

    for cand in candidates:
        if len(productores) >= num_productores and len(proveedores) >= num_proveedores:
            break

        row = cand["row"]
        uuid_val = row.get("uuid", "")
        if uuid_val in used_uuids:
            continue
        used_uuids.add(uuid_val)

        first_name = extract_first_name(row.get("professional_persona", ""))
        full_name = generate_full_name(first_name, row.get("sex", "Masculino"))
        rubro = cand["rubro_hint"]
        capacidad = format_capacidad(rubro, row.get("professional_persona", ""))

        persona_dict = {
            "nombre": full_name,
            "primer_nombre": first_name,
            "rubro": rubro,
            "ubicacion": f"{row.get('municipality', '')}, {row.get('department', '')}",
            "departamento": row.get("department", ""),
            "municipio": row.get("municipality", ""),
            "capacidad": capacidad,
            "telefono": generate_telefono(),
            "dui": generate_dui(),
            "nit": generate_nit(),
            "edad": row.get("age", 30),
            "sexo": row.get("sex", "Masculino"),
            "educacion": row.get("education_level", ""),
            "ocupacion": row.get("occupation", ""),
            "area": row.get("area", "urbano"),
            "score": cand["score"],
            "fuente": "nemotron",
            "professional_persona": row.get("professional_persona", ""),
            "created_at": datetime.now().isoformat(),
        }

        if len(productores) < num_productores:
            productores.append(persona_dict)
        elif len(proveedores) < num_proveedores:
            proveedores.append(persona_dict)

    return productores, proveedores


def fallback_generate_personas(
    num_productores: int = NUM_PRODUCTORES,
    num_proveedores: int = NUM_PROVEEDORES,
) -> Tuple[List[Dict], List[Dict]]:
    """
    Genera personas sinteticas cuando HuggingFace no esta disponible.

    Produce datos realististas usando templates y listas de nombres/ubicaciones
    salvadorenas. No requiere conexion a internet ni paquetes externos.

    Returns:
        (productores, proveedores) — listas de dicts.
    """
    # Datos geograficos
    DEPARTAMENTOS = [
        "Ahuachapan", "Santa Ana", "Sonsonate", "Chalatenango",
        "La Libertad", "San Salvador", "Cuscatlan", "La Paz",
        "Cabanas", "San Vicente", "Usulutan", "San Miguel",
        "Morazan", "La Union",
    ]
    MUNICIPIOS_POR_DEPTO = {
        "Ahuachapan": ["Ahuachapan Centro", "Ahuachapan Norte", "Ahuachapan Sur"],
        "Santa Ana": ["Santa Ana Centro", "Santa Ana Este", "Santa Ana Oeste"],
        "Sonsonate": ["Sonsonate Centro", "Sonsonate Norte", "Sonsonate Sur"],
        "Chalatenango": ["Chalatenango Centro", "Chalatenango Norte", "Chalatenango Sur"],
        "La Libertad": ["La Libertad Centro", "La Libertad Costa", "La Libertad Norte"],
        "San Salvador": ["San Salvador Centro", "San Salvador Norte", "San Salvador Sur", "San Salvador Este", "San Salvador Oeste"],
        "Cuscatlan": ["Cuscatlan Centro", "Cuscatlan Sur"],
        "La Paz": ["La Paz Centro", "La Paz Este", "La Paz Oeste"],
        "Cabanas": ["Cabanas Centro", "Cabanas Sur"],
        "San Vicente": ["San Vicente Centro", "San Vicente Sur"],
        "Usulutan": ["Usulutan Centro", "Usulutan Este", "Usulutan Norte"],
        "San Miguel": ["San Miguel Centro", "San Miguel Sur", "San Miguel Norte"],
        "Morazan": ["Morazan Centro", "Morazan Norte", "Morazan Sur"],
        "La Union": ["La Union Centro", "La Union Norte", "La Union Sur"],
    }

    RUBROS_CON_OCUPACIONES = {
        "Alimentos y Bebidas": [
            "dueno de un comedor", "propietario de una panaderia",
            "emprendedora de pupuseria", "dueno de restaurante familiar",
            "propietario de tortilleria", "dueña de negocio de catering",
        ],
        "Textiles y Uniformes": [
            "dueno de taller de costura", "propietario de sastreria",
            "emprendedora de confeccion textil", "dueña de taller de uniformes",
        ],
        "Construccion": [
            "maestro de obra independiente", "propietario de ferreteria",
            "dueno de taller de carpinteria", "contratista de construccion",
        ],
        "Suministros Agricolas": [
            "agricultor independiente", "propietario de finca",
            "dueno de vivero", "emprendedor agricola",
        ],
        "Servicios de Limpieza": [
            "dueno de negocio de limpieza", "propietario de servicio de fumigacion",
            "emprendedora de limpieza general",
        ],
        "Transporte y Logistica": [
            "propietario de camion de carga", "dueno de servicio de transporte",
            "emprendedor de logistica local",
        ],
        "Tecnologia": [
            "desarrollador independiente", "dueno de negocio de servicios informaticos",
            "emprendedor de tecnologia",
        ],
        "Mobiliario y Equipo": [
            "dueno de taller de muebles", "propietario de carpinteria",
            "emprendedora de ebanisteria",
        ],
        "Servicios Profesionales": [
            "contador independiente", "dueno de bufete contable",
            "propietario de consultoria fiscal",
        ],
        "Belleza": [
            "duena de salon de belleza", "propietaria de barberia",
            "emprendedora de cosmetologia",
        ],
        "Imprenta y Publicidad": [
            "dueno de imprenta local", "propietario de negocio de rotulacion",
            "emprendedor de diseno grafico",
        ],
    }

    NOMBRES_M = ["Jose", "Carlos", "Pedro", "Francisco", "Roberto", "Jorge",
                  "Manuel", "Miguel", "Luis", "Juan", "David", "Oscar", "Rene",
                  "Wilfredo", "Carlos", "Mauricio", "Rafael"]
    NOMBRES_F = ["Maria", "Ana", "Rosa", "Lidia", "Margarita", "Marta",
                  "Gabriela", "Sandra", "Veronica", "Diana", "Claudia",
                  "Sofia", "Andrea", "Elena", "Beatriz"]

    # --- Generar productores ---
    productores = []
    used_names = set()

    for i in range(num_productores):
        rubro = random.choice(list(RUBROS_CON_OCUPACIONES.keys()))
        ocupacion_texto = random.choice(RUBROS_CON_OCUPACIONES[rubro])
        sex = random.choice(["Masculino", "Femenino"])
        nombres = NOMBRES_M if sex == "Masculino" else NOMBRES_F
        first_name = random.choice(nombres)

        # Evitar duplicados exactos de nombre
        full_name = generate_full_name(first_name, sex)
        while full_name in used_names:
            full_name = generate_full_name(first_name, sex)
        used_names.add(full_name)

        depto = random.choice(DEPARTAMENTOS)
        muns = MUNICIPIOS_POR_DEPTO.get(depto, [depto])
        mun = random.choice(muns)
        edad = random.randint(22, 70)

        # Generar texto professional_persona sintetico
        persona_text = _generate_fallback_persona_text(
            first_name, edad, sex, rubro, ocupacion_texto, depto, mun
        )

        capacidad = format_capacidad(rubro, persona_text)

        productores.append({
            "nombre": full_name,
            "primer_nombre": first_name,
            "rubro": rubro,
            "ubicacion": f"{mun}, {depto}",
            "departamento": depto,
            "municipio": mun,
            "capacidad": capacidad,
            "telefono": generate_telefono(),
            "dui": generate_dui(),
            "nit": generate_nit(),
            "edad": edad,
            "sexo": sex,
            "educacion": random.choice(["primaria", "secundaria", "bachillerato", "tecnico", "universitario"]),
            "ocupacion": ocupacion_texto,
            "area": random.choice(["urbano", "rural"]),
            "score": random.randint(25, 95),
            "fuente": "fallback_sintetico",
            "professional_persona": persona_text,
            "created_at": datetime.now().isoformat(),
        })

    # --- Generar proveedores ---
    proveedores = []
    rubros_usados = [p["rubro"] for p in productores]
    for i in range(num_proveedores):
        # Preferir rubros que no esten en productores para diversidad
        rubros_disponibles = list(RUBROS_CON_OCUPACIONES.keys())
        rubro = random.choice(rubros_disponibles)
        ocupacion_texto = random.choice(RUBROS_CON_OCUPACIONES[rubro])
        sex = random.choice(["Masculino", "Femenino"])
        nombres = NOMBRES_M if sex == "Masculino" else NOMBRES_F
        first_name = random.choice(nombres)

        full_name = generate_full_name(first_name, sex)
        while full_name in used_names:
            full_name = generate_full_name(first_name, sex)
        used_names.add(full_name)

        depto = random.choice(DEPARTAMENTOS)
        muns = MUNICIPIOS_POR_DEPTO.get(depto, [depto])
        mun = random.choice(muns)
        edad = random.randint(22, 70)

        persona_text = _generate_fallback_persona_text(
            first_name, edad, sex, rubro, ocupacion_texto, depto, mun
        )

        proveedores.append({
            "nombre": full_name,
            "primer_nombre": first_name,
            "rubro": rubro,
            "ubicacion": f"{mun}, {depto}",
            "departamento": depto,
            "municipio": mun,
            "telefono": generate_telefono(),
            "dui": generate_dui(),
            "nit": generate_nit(),
            "edad": edad,
            "sexo": sex,
            "ocupacion": ocupacion_texto,
            "area": random.choice(["urbano", "rural"]),
            "score": random.randint(20, 90),
            "fuente": "fallback_sintetico",
            "professional_persona": persona_text,
            "created_at": datetime.now().isoformat(),
        })

    return productores, proveedores


def _generate_fallback_persona_text(
    first_name: str, edad: int, sex: str, rubro: str,
    ocupacion_texto: str, depto: str, mun: str
) -> str:
    """Genera texto de professional_persona sintetico al estilo Nemotron."""
    years_exp = max(1, edad - 18 - random.randint(0, 5))

    articulo = "a" if sex == "Femenino" else "o"
    posesivo = "su" if sex == "Femenino" else "su"

    # Frases de negocio segun categoria
    biz_phrases = {
        "Alimentos y Bebidas": [
            f"prepara {random.choice(['pupusas', 'almuerzos', 'pan fresco', 'tortillas'])} "
            f"todos los dias para {random.choice(['los vecinos', 'los trabajadores de la zona', 'su comunidad', 'los mercados locales'])}",
            f"compro {random.choice(['una plancha industrial', 'un horno nuevo', 'una cocina industrial'])} "
            f"para aumentar su produccion",
        ],
        "Textiles y Uniformes": [
            f"fabrica {random.choice(['uniformes escolares', 'ropa casual', 'prendas bordadas', 'delantales'])} "
            f"por encargo para {random.choice(['colegios', 'empresas', 'particulares'])}",
            f"tiene {random.randint(2, 8)} maquinas de coser y {random.randint(1, 3)} empleados",
        ],
        "Construccion": [
            f"ha construido {random.choice(['casas', 'bodegas', ' locales comerciales'])} "
            f"en {random.choice(['la zona', 'el municipio', 'varios cantones'])}",
            f"trabaja con {random.randint(2, 10)} albaniles y {random.randint(1, 3)} ayudantes",
        ],
    }

    # Oracion base (estilo Nemotron)
    text = (f"{first_name}, de {edad} anios, lleva "
            f"{years_exp} anios trabajando como {ocupacion_texto} en {mun}, {depto}. ")

    # Agregar detalle de negocio
    if random.random() < 0.7 and rubro in biz_phrases:
        text += random.choice(biz_phrases[rubro]) + ". "

    # Agregar senial de formalizacion o crecimiento
    growth_phrases = [
        f"{first_name} formalizo su negocio hace {random.randint(1, 5)} anios "
        f"y ahora factura entre ${random.randint(500, 3000)} y ${random.randint(3000, 15000)} mensuales.",
        f"Con {random.randint(1, 8)} empleados, {first_name} atiende "
        f"{random.choice(['a sus clientes', 'pedidos', 'contratos'])} "
        f"con dedicacion y busca crecer.",
    ]
    text += random.choice(growth_phrases)

    return text


def generate_productores_csv(productores: List[Dict], output_path: Path) -> None:
    """
    Escribe productores_demo.csv.

    Columnas compatibles con el schema de Supabase:
        id, nombre, rubro, ubicacion, capacidad, telefono, dui, nit,
        edad, sexo, educacion, ocupacion, area, score, fuente, created_at
    """
    fieldnames = [
        "nombre", "rubro", "ubicacion", "departamento", "municipio",
        "capacidad", "telefono", "dui", "nit", "edad", "sexo", "educacion",
        "ocupacion", "area", "score", "fuente", "professional_persona", "created_at",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for prod in productores:
            writer.writerow(prod)

    print(f"[+] {output_path.name}: {len(productores)} filas escritas")


def generate_proveedores_csv(proveedores: List[Dict], output_path: Path) -> None:
    """
    Escribe proveedores_demo.csv.
    """
    fieldnames = [
        "nombre", "rubro", "ubicacion", "departamento", "municipio",
        "telefono", "dui", "nit", "edad", "sexo", "ocupacion",
        "area", "score", "fuente", "professional_persona", "created_at",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for prov in proveedores:
            writer.writerow(prov)

    print(f"[+] {output_path.name}: {len(proveedores)} filas escritas")


# ═══════════════════════════════════════════════════════════════════════════════
#  SECCION C: GENERACION DE OPORTUNIDADES COMPRASAL
# ═══════════════════════════════════════════════════════════════════════════════

def generate_oportunidades_dataset(
    n: int = NUM_OPORTUNIDADES,
    output_csv: Optional[Path] = None,
    output_json: Optional[Path] = None,
) -> List[Dict]:
    """
    Genera oportunidades sinteticas COMPRASAL usando el generador existente.

    Si el modulo generador_oportunidades esta disponible, lo usa.
    Si no, implementa una version simplificada aqui mismo.

    Returns:
        Lista de dicts con campos: id, titulo, institucion, monto,
        fecha_cierre, rubro_requerido, unspsc_code, url_fuente,
        tipo_contratacion, descripcion
    """
    try:
        # Intentar importar el generador existente
        sys.path.insert(0, str(SCRIPT_DIR))
        from generador_oportunidades import generate_oportunidades as gen_ops  # type: ignore
        oportunidades = gen_ops(n)
        print(f"[+] Oportunidades generadas via generador_oportunidades.py ({len(oportunidades)} filas)")
    except ImportError:
        print("[!] generador_oportunidades.py no disponible. Usando generador embebido.")
        oportunidades = _embed_generate_oportunidades(n)
    except Exception as e:
        print(f"[!] Error con generador_oportunidades: {e}. Usando generador embebido.")
        oportunidades = _embed_generate_oportunidades(n)

    # Escribir CSV
    if output_csv:
        fieldnames = [
            "id", "titulo", "institucion", "monto", "fecha_cierre",
            "rubro_requerido", "unspsc_code", "url_fuente",
            "tipo_contratacion", "descripcion",
        ]
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for opp in oportunidades:
                writer.writerow(opp)
        print(f"[+] {output_csv.name}: {len(oportunidades)} filas escritas")

    # Escribir JSON
    if output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(oportunidades, f, ensure_ascii=False, indent=2)
        print(f"[+] {output_json.name}: {len(oportunidades)} oportunidades")

    return oportunidades


def _embed_generate_oportunidades(n: int = 25) -> List[Dict]:
    """
    Generador simplificado de oportunidades COMPRASAL embebido.
    Usado solo si generador_oportunidades.py no esta disponible.
    """
    INSTITUCIONES = [
        ("MINSAL", "Ministerio de Salud"),
        ("MINEDUCYT", "Ministerio de Educacion"),
        ("MOPT", "Ministerio de Obras Publicas"),
        ("MAG", "Ministerio de Agricultura"),
        ("ISSS", "Instituto Salvadoreno del Seguro Social"),
        ("ANDA", "Administracion Nacional de Acueductos"),
        ("FISDL", "Fondo de Inversion Social"),
        ("AMSS", "Alcaldia de San Salvador"),
        ("MINSAL", "Ministerio de Salud"),
        ("PNC", "Policia Nacional Civil"),
    ]

    RUBROS = [
        ("Alimentos y Bebidas", "50000000"),
        ("Textiles y Uniformes", "53000000"),
        ("Construccion", "72000000"),
        ("Servicios de Limpieza", "76100000"),
        ("Transporte y Logistica", "78000000"),
        ("Tecnologia", "43230000"),
        ("Suministros Agricolas", "24000000"),
        ("Mobiliario y Equipo", "56000000"),
        ("Servicios Profesionales", "80100000"),
        ("Servicios de Salud", "51000000"),
        ("Imprenta y Publicidad", "82120000"),
        ("Belleza", "51000000"),
    ]

    TITULOS = [
        "Servicio de {rubro} en {ubicacion} - {inst}",
        "Adquisicion de {insumos} para {inst} - Lote {lote}",
        "Contratacion de Servicios de {rubro} para {inst}",
        "Suministro de {insumos} para el Programa de {inst}",
        "Servicio de {rubro} a Nivel Nacional para {inst}",
    ]

    UBICACIONES = [
        "San Salvador", "Santa Ana", "San Miguel", "Sonsonate",
        "La Libertad", "Usulutan", "Ahuachapan", "Zacatecoluca",
        "Cojutepeque", "San Vicente", "La Union", "Chalatenango",
        "San Francisco Gotera", "Sensuntepeque",
    ]

    RUBRO_INSUMOS = {
        "Alimentos y Bebidas": "Alimentos No Perecederos",
        "Textiles y Uniformes": "Uniformes y Prendas de Vestir",
        "Construccion": "Materiales de Construccion",
        "Servicios de Limpieza": "Insumos de Limpieza y Fumigacion",
        "Transporte y Logistica": "Servicios de Transporte",
        "Tecnologia": "Equipo Informatico y Software",
        "Suministros Agricolas": "Insumos Agricolas y Semillas",
        "Mobiliario y Equipo": "Mobiliario de Oficina",
        "Servicios Profesionales": "Servicios de Consultoria",
        "Servicios de Salud": "Medicamentos e Insumos Medicos",
        "Imprenta y Publicidad": "Material Publicitario",
        "Belleza": "Insumos de Belleza",
    }

    base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    oportunidades = []

    for i in range(n):
        rubro, unspsc = random.choice(RUBROS)
        inst_siglas, inst_nombre = random.choice(INSTITUCIONES)
        ubicacion = random.choice(UBICACIONES)
        lote = random.randint(1, 15)

        titulo_template = random.choice(TITULOS)
        titulo = titulo_template.format(
            rubro=rubro,
            ubicacion=ubicacion,
            inst=inst_siglas,
            insumos=RUBRO_INSUMOS.get(rubro, "Bienes y Servicios"),
            lote=lote,
        )

        monto = round(random.uniform(1000, 250000), 2)
        fecha_cierre = (base_date + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
        tipo = random.choice(["Licitacion Publica", "Libre Gestion", "Contratacion Directa"])
        exp = f"{inst_siglas}-{random.randint(1, 99):02d}-{random.randint(1000, 9999)}-2026"

        oportunidades.append({
            "id": f"opp-{i+1:03d}",
            "titulo": titulo,
            "institucion": f"{inst_siglas} - {inst_nombre}",
            "monto": monto,
            "fecha_cierre": fecha_cierre,
            "rubro_requerido": rubro,
            "unspsc_code": unspsc,
            "url_fuente": f"https://www.comprasal.gob.sv/Oportunidades/DetalleOportunidad.aspx?exp={exp}",
            "tipo_contratacion": tipo,
            "descripcion": (
                f"La presente contratacion tiene por objeto la adquisicion de "
                f"{RUBRO_INSUMOS.get(rubro, 'bienes y servicios').lower()} "
                f"para las dependencias de {inst_nombre} en {ubicacion}, "
                f"por un monto estimado de ${monto:,.2f}. "
                f"Los interesados deben presentar su oferta en sobre sellado "
                f"en la UACI de la institucion."
            ),
        })

    return oportunidades


# ═══════════════════════════════════════════════════════════════════════════════
#  SECCION D: SUPABASE INSERT
# ═══════════════════════════════════════════════════════════════════════════════

def insert_into_supabase(
    productores: List[Dict],
    proveedores: List[Dict],
    oportunidades: List[Dict],
) -> Dict[str, int]:
    """
    Inserta los datos generados en Supabase usando supabase-py.

    Variables de entorno requeridas:
        SUPABASE_URL — URL del proyecto (e.g. https://xxxxx.supabase.co)
        SUPABASE_KEY — service_role key (permite inserts sin RLS)

    Mapea los campos del CSV a las columnas reales de la DB:
      Tabla            Columnas DB                       Columnas CSV que mapean
      ─────────────────────────────────────────────────────────────────────────
      productores      nombre, rubro, ubicacion,          mismas + capacidad,
                       capacidad, telefono, dui, nit      telefono, dui, nit
      proveedores      nombre, rubro, ubicacion,          mismas + telefono, dui,
                       telefono, dui, nit, persona_text,  nit, professional_persona
                       rubros_suministra                  (rubros_suministra ausente)
      oportunidades    titulo, institucion, monto,        mismas
                       fecha_cierre, rubro_requerido,
                       unspsc_code, url_fuente,
                       tipo_contratacion

    Returns:
        Dict con conteos de filas insertadas por tabla.
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("[!] SUPABASE_URL y SUPABASE_KEY no configuradas en .env")
        print("[*] Saltando insercion en Supabase. Los CSVs ya estan generados.")
        return {"status": "skipped", "reason": "missing_credentials"}

    try:
        from supabase import create_client  # type: ignore
    except ImportError:
        print("[!] supabase-py no instalado. pip install supabase")
        return {"status": "skipped", "reason": "missing_package"}

    print(f"\n[*] Conectando a Supabase: {supabase_url}")
    client = create_client(supabase_url, supabase_key)

    # Columnas permitidas por tabla (para filtrar campos extra del CSV)
    SCHEMA_COLUMNS = {
        "productores": {"nombre", "rubro", "ubicacion", "capacidad",
                        "telefono", "dui", "nit"},
        "proveedores": {"nombre", "rubro", "ubicacion", "telefono",
                        "dui", "nit", "persona_text", "rubros_suministra"},
        "oportunidades": {"titulo", "institucion", "monto", "fecha_cierre",
                          "rubro_requerido", "unspsc_code", "url_fuente",
                          "tipo_contratacion"},
    }

    # Mapeo de nombres de campo CSV a columna DB
    FIELD_MAP = {
        "proveedores": {"professional_persona": "persona_text"},
    }

    counts = {}
    tables = {
        "productores": productores,
        "proveedores": proveedores,
        "oportunidades": oportunidades,
    }

    for table_name in SUPABASE_TABLES:
        data = tables.get(table_name, [])
        if not data:
            print(f"[!] Tabla '{table_name}' no tiene datos para insertar.")
            continue

        allowed = SCHEMA_COLUMNS.get(table_name, set())
        field_map = FIELD_MAP.get(table_name, {})

        # Limpiar datos: solo columnas que existen en la DB
        cleaned_data = []
        for record in data:
            cleaned = {}
            for csv_key, db_key in field_map.items():
                if csv_key in record:
                    cleaned[db_key] = record[csv_key]
            for col in allowed:
                if col in record:
                    cleaned[col] = record[col]
            if cleaned:
                cleaned_data.append(cleaned)

        if not cleaned_data:
            print(f"[!] Tabla '{table_name}': sin datos validos despues de filtrar.")
            continue

        try:
            response = client.table(table_name).insert(cleaned_data).execute()
            inserted = len(response.data) if response.data else 0
            counts[table_name] = inserted
            print(f"[+] {table_name}: {inserted} filas insertadas")
        except Exception as e:
            print(f"[!] Error insertando en '{table_name}': {e}")
            counts[table_name] = 0

    return counts


# ═══════════════════════════════════════════════════════════════════════════════
#  SECCION E: ORQUESTACION PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def run_pipeline(
    use_fallback: bool = False,
    csv_only: bool = False,
    supabase_only: bool = False,
    huggingface_only: bool = False,
) -> None:
    """
    Ejecuta el pipeline completo de generacion de datos.

    Args:
        use_fallback: Forzar uso del generador sintetico (sin HF).
        csv_only: Solo generar CSVs, no insertar en Supabase.
        supabase_only: Solo insertar CSVs existentes en Supabase.
        huggingface_only: Solo mostrar informacion del dataset HF.
    """
    print("=" * 60)
    print("  simular_datos_compa.py — Pipeline de Datos para Compa")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    productores: List[Dict] = []
    proveedores: List[Dict] = []
    oportunidades: List[Dict] = []

    # ── Modo: solo HuggingFace info ──
    if huggingface_only:
        ds = load_dataset_huggingface()
        if ds:
            features = list(ds.features.keys()) if hasattr(ds, 'features') else []
            print(f"\n[*] Features ({len(features)}):")
            for fname, ftype in ds.features.items():
                print(f"    {fname}: {ftype}")
            # Sample
            for i, row in enumerate(ds):
                if i >= 3:
                    break
                score = score_business_owner(row)
                name = extract_first_name(row.get("professional_persona", ""))
                rubro = map_occupation_to_rubro(row.get("occupation", ""))
                print(f"\n  [{i}] {name} | score={score} | rubro={rubro}")
                print(f"      Occ: {row.get('occupation', '')[:80]}")
                print(f"      Dept: {row.get('department', '')} / Mun: {row.get('municipality', '')}")
        return

    # ── Modo: solo Supabase (cargar CSVs existentes) ──
    if supabase_only:
        print("[*] Modo supabase-only: cargando CSVs existentes...")
        productores_csv = DATA_DIR / "productores_demo.csv"
        proveedores_csv = DATA_DIR / "proveedores_demo.csv"
        oportunidades_csv = DATA_DIR / "oportunidades.csv"

        if productores_csv.exists():
            import pandas as pd  # type: ignore
            productores = pd.read_csv(productores_csv).to_dict("records")
            print(f"[+] Cargados {len(productores)} productores")
        if proveedores_csv.exists():
            import pandas as pd
            proveedores = pd.read_csv(proveedores_csv).to_dict("records")
            print(f"[+] Cargados {len(proveedores)} proveedores")
        if oportunidades_csv.exists():
            import pandas as pd
            oportunidades = pd.read_csv(oportunidades_csv).to_dict("records")
            print(f"[+] Cargadas {len(oportunidades)} oportunidades")

        if not any([productores, proveedores, oportunidades]):
            print("[!] No se encontraron CSVs. Ejecute sin --supabase-only primero.")
            return

        counts = insert_into_supabase(productores, proveedores, oportunidades)
        print(f"\n[*] Resultado: {counts}")
        return

    # ── Modo: generacion de datos ──
    if not use_fallback:
        print("[*] Fase 1: Cargando dataset Nemotron desde HuggingFace...")
        productores, proveedores = extract_candidates_from_hf(
            num_productores=NUM_PRODUCTORES,
            num_proveedores=NUM_PROVEEDORES,
        )
        if not productores:
            print("[!] Dataset HF no disponible o sin candidatos. Usando fallback sintetico.")
            productores, proveedores = fallback_generate_personas(
                num_productores=NUM_PRODUCTORES,
                num_proveedores=NUM_PROVEEDORES,
            )
    else:
        print("[*] Fase 1: Usando generador sintetico (fallback)...")
        productores, proveedores = fallback_generate_personas(
            num_productores=NUM_PRODUCTORES,
            num_proveedores=NUM_PROVEEDORES,
        )

    # ── Fase 2: Escribir CSVs ──
    print("\n[*] Fase 2: Escribiendo CSVs...")

    # Escribir productores
    prod_csv = DATA_DIR / "productores_demo.csv"
    generate_productores_csv(productores, prod_csv)

    # Escribir proveedores
    prov_csv = DATA_DIR / "proveedores_demo.csv"
    generate_proveedores_csv(proveedores, prov_csv)

    # ── Fase 3: Generar oportunidades ──
    print("\n[*] Fase 3: Generando oportunidades COMPRASAL...")
    oportunidades = generate_oportunidades_dataset(
        n=NUM_OPORTUNIDADES,
        output_csv=DATA_DIR / "oportunidades.csv",
        output_json=DATA_DIR / "oportunidades.json",
    )

    # ── Fase 4: Resumen ──
    print("\n" + "=" * 60)
    print("  RESUMEN DE DATOS GENERADOS")
    print("=" * 60)
    print(f"  Productores:     {len(productores)}")
    print(f"  Proveedores:     {len(proveedores)}")
    print(f"  Oportunidades:   {len(oportunidades)}")

    # Distribucion de rubros
    rubro_counts = Counter(p["rubro"] for p in productores)
    print(f"\n  Rubros (productores): {dict(rubro_counts)}")

    print(f"\n  Archivos generados en {DATA_DIR}/:")
    print(f"    - productores_demo.csv")
    print(f"    - proveedores_demo.csv")
    print(f"    - oportunidades.csv")
    print(f"    - oportunidades.json")

    # ── Fase 5: Supabase (si no es csv-only) ──
    if not csv_only:
        print("\n[*] Fase 5: Insertando en Supabase...")
        counts = insert_into_supabase(productores, proveedores, oportunidades)
        print(f"\n[*] Resultado Supabase: {counts}")
    else:
        print("\n[*] Modo csv-only: Supabase saltado.")
        print("[*] Para insertar despues: python scripts/simular_datos_compa.py --supabase-only")

    print("\n[+] Pipeline completado.")


# ═══════════════════════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="simular_datos_compa.py — Pipeline de datos demo para Compa",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python scripts/simular_datos_compa.py
  python scripts/simular_datos_compa.py --fallback
  python scripts/simular_datos_compa.py --csv-only
  python scripts/simular_datos_compa.py --supabase-only
  python scripts/simular_datos_compa.py --huggingface-only
  python scripts/simular_datos_compa.py --productores 30 --proveedores 20
        """,
    )
    parser.add_argument("--fallback", action="store_true",
                        help="Forzar uso del generador sintetico sin HuggingFace")
    parser.add_argument("--csv-only", action="store_true",
                        help="Solo generar CSVs, sin insertar en Supabase")
    parser.add_argument("--supabase-only", action="store_true",
                        help="Solo insertar CSVs existentes en Supabase")
    parser.add_argument("--huggingface-only", action="store_true",
                        help="Solo inspeccionar el dataset de HuggingFace")
    parser.add_argument("--productores", type=int, default=NUM_PRODUCTORES,
                        help=f"Numero de productores a generar (default: {NUM_PRODUCTORES})")
    parser.add_argument("--proveedores", type=int, default=NUM_PROVEEDORES,
                        help=f"Numero de proveedores a generar (default: {NUM_PROVEEDORES})")
    parser.add_argument("--oportunidades", type=int, default=NUM_OPORTUNIDADES,
                        help=f"Numero de oportunidades a generar (default: {NUM_OPORTUNIDADES})")

    args = parser.parse_args()

    # Actualizar constantes desde argumentos
    NUM_PRODUCTORES = args.productores
    NUM_PROVEEDORES = args.proveedores
    NUM_OPORTUNIDADES = args.oportunidades

    run_pipeline(
        use_fallback=args.fallback,
        csv_only=args.csv_only,
        supabase_only=args.supabase_only,
        huggingface_only=args.huggingface_only,
    )
