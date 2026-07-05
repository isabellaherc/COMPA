"""Export local demo data from supabase-schema.sql.

The SQL file is the source of truth for Phase 2. This script regenerates
local fallback/data artifacts so JSON and CSV no longer drift from the seed SQL.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "supabase-schema.sql"
DATA_DIR = ROOT / "data"


def strip_sql_comments(sql: str) -> str:
    lines: list[str] = []
    for line in sql.splitlines():
        in_quote = False
        out = []
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == "'":
                out.append(ch)
                if i + 1 < len(line) and line[i + 1] == "'":
                    out.append("'")
                    i += 2
                    continue
                in_quote = not in_quote
                i += 1
                continue
            if not in_quote and ch == "-" and i + 1 < len(line) and line[i + 1] == "-":
                break
            out.append(ch)
            i += 1
        lines.append("".join(out))
    return "\n".join(lines)


def extract_insert(sql: str, table: str) -> tuple[list[str], str]:
    pattern = re.compile(
        rf"INSERT\s+INTO\s+{re.escape(table)}\s*\((.*?)\)\s*VALUES\s*(.*?);",
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(sql)
    if not match:
        raise ValueError(f"INSERT for {table} not found")
    columns = [c.strip() for c in match.group(1).split(",")]
    return columns, match.group(2).strip()


def parse_values(values_sql: str) -> list[list[Any]]:
    rows: list[list[Any]] = []
    row: list[Any] | None = None
    token: list[str] = []
    in_quote = False
    i = 0

    def flush_token() -> None:
        assert row is not None
        raw = "".join(token).strip()
        token.clear()
        row.append(parse_value(raw))

    while i < len(values_sql):
        ch = values_sql[i]
        if in_quote:
            if ch == "'":
                if i + 1 < len(values_sql) and values_sql[i + 1] == "'":
                    token.append("'")
                    i += 2
                    continue
                in_quote = False
                i += 1
                continue
            token.append(ch)
            i += 1
            continue

        if ch == "'":
            in_quote = True
            i += 1
            continue
        if ch == "(":
            row = []
            token = []
            i += 1
            continue
        if ch == "," and row is not None:
            flush_token()
            i += 1
            continue
        if ch == ")" and row is not None:
            flush_token()
            rows.append(row)
            row = None
            token = []
            i += 1
            continue
        if row is not None:
            token.append(ch)
        i += 1

    return rows


def parse_value(raw: str) -> Any:
    if raw == "" or raw.upper() == "NULL":
        return None
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    if re.fullmatch(r"-?\d+\.\d+", raw):
        return float(raw)
    return raw


def load_table(sql: str, table: str) -> list[dict[str, Any]]:
    columns, values_sql = extract_insert(sql, table)
    rows = parse_values(values_sql)
    return [dict(zip(columns, row)) for row in rows]


def with_ids(prefix: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    width = max(3, len(str(len(rows))))
    return [{"id": f"{prefix}-{idx:0{width}d}", **row} for idx, row in enumerate(rows, start=1)]


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({key: row.get(key, "") for key in fieldnames} for row in rows)


def tipo_largo(tipo: str | None) -> str | None:
    mapping = {
        "LP": "Licitacion Publica",
        "LG": "Libre Gestion",
        "CD": "Contratacion Directa",
        "CP": "Comparacion de Precios",
        "AFA": "Alianza/Figura Especial",
        "CV": "Convenio",
    }
    return mapping.get(tipo or "", tipo)


def main() -> None:
    sql = strip_sql_comments(SCHEMA.read_text(encoding="utf-8-sig"))
    productores = with_ids("prod", load_table(sql, "productores"))
    oportunidades = with_ids("opp", load_table(sql, "oportunidades"))
    proveedores = with_ids("prov", load_table(sql, "proveedores"))

    for opp in oportunidades:
        opp["monto"] = float(opp["monto"])
        opp["tipo_contratacion_label"] = tipo_largo(opp.get("tipo_contratacion"))

    rubros = sorted(
        set(row["rubro"] for row in productores)
        | set(row["rubro_requerido"] for row in oportunidades)
        | set(row["rubro"] for row in proveedores)
    )
    cobertura = {
        "rubros_cerrados": rubros,
        "conteos": {
            "productores": Counter(row["rubro"] for row in productores),
            "oportunidades": Counter(row["rubro_requerido"] for row in oportunidades),
            "proveedores": Counter(row["rubro"] for row in proveedores),
        },
        "sin_oportunidades": sorted(
            set(row["rubro"] for row in productores) - set(row["rubro_requerido"] for row in oportunidades)
        ),
        "sin_proveedores": sorted(
            set(row["rubro_requerido"] for row in oportunidades) - set(row["rubro"] for row in proveedores)
        ),
        "generated_from": "supabase-schema.sql",
        "generated_at": date.today().isoformat(),
    }

    write_json(DATA_DIR / "productores.json", {"_meta": {"source": "supabase-schema.sql"}, "productores": productores})
    write_json(DATA_DIR / "proveedores.json", {"_meta": {"source": "supabase-schema.sql"}, "proveedores": proveedores})
    write_json(DATA_DIR / "oportunidades.json", oportunidades)
    write_json(DATA_DIR / "rubros-cerrados.json", cobertura)

    fallback = {
        "_meta": {
            "name": "Compa Fallback Data",
            "version": "2.0",
            "source_of_truth": "supabase-schema.sql",
            "last_updated": date.today().isoformat(),
            "purpose": "Fallback local derivado del SQL para evitar drift entre Supabase, JSON y CSV.",
            "note": "IDs prod/opp/prov son locales para fallback. En Supabase usar UUID reales.",
        },
        "productores": productores,
        "oportunidades": oportunidades,
        "proveedores": proveedores,
        "rubros_cerrados": rubros,
        "decisiones_fallback": {
            "preguntas": [
                {
                    "pregunta": "Ya calculo cuanto le cuesta producir cada almuerzo con los precios actuales de los ingredientes?",
                    "intencion": "Evaluacion de costos reales",
                    "palabras_clave": ["costo", "producir", "almuerzo", "ingredientes"],
                },
                {
                    "pregunta": "Tiene flujo de caja para aguantar 60 a 90 dias antes del pago del Estado?",
                    "intencion": "Evaluacion de liquidez y ciclo de pago estatal",
                    "palabras_clave": ["flujo", "pago", "esperar", "plazo"],
                },
                {
                    "pregunta": "Que plan B tiene si gana y no puede cumplir con la cantidad completa?",
                    "intencion": "Evaluacion de capacidad operativa y riesgo de incumplimiento",
                    "palabras_clave": ["capacidad", "cumplir", "plan", "riesgo"],
                },
            ],
            "_fallback": True,
            "_fallback_reason": "OpenAI/Codex API unavailable; serving hardcoded fallback questions",
        },
    }
    write_json(DATA_DIR / "fallback.json", fallback)

    write_csv(
        DATA_DIR / "seed-oportunidades.csv",
        oportunidades,
        ["id", "titulo", "institucion", "monto", "fecha_cierre", "rubro_requerido", "unspsc_code", "url_fuente", "tipo_contratacion", "tipo_contratacion_label"],
    )
    write_csv(
        DATA_DIR / "seed-productores.csv",
        productores,
        ["id", "nombre", "rubro", "ubicacion", "capacidad", "telefono", "dui", "nit"],
    )

    print(f"Exported {len(productores)} productores, {len(oportunidades)} oportunidades, {len(proveedores)} proveedores")
    print(f"Rubros sin oportunidades: {cobertura['sin_oportunidades']}")
    print(f"Rubros sin proveedores: {cobertura['sin_proveedores']}")


if __name__ == "__main__":
    main()