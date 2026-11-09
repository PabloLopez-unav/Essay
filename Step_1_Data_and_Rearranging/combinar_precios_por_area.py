"""Combina los CSV de precios eléctricos en dos archivos según el área.

Busca todos los CSV de entrada en la misma carpeta que este script y genera:

* combined_BZN_DE_AT_LU.csv
* combined_BZN_DE_LU.csv

Las filas se ordenan por el inicio de ``MTU (CET/CEST)``. La columna MTU se
conserva tal como aparece en los archivos originales y el programa muestra al
final el intervalo temporal encontrado para cada área.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path


AREA_DE_AT_LU = "BZN|DE-AT-LU"
AREA_DE_LU = "BZN|DE-LU"
MTU_COLUMN = "MTU (CET/CEST)"
OUTPUTS = {
    AREA_DE_AT_LU: "combined_BZN_DE_AT_LU.csv",
    AREA_DE_LU: "combined_BZN_DE_LU.csv",
}


def parse_mtu_start(value: str) -> datetime:
    """Devuelve el comienzo del intervalo MTU para poder ordenar las filas."""
    match = re.match(
        r"^\s*(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})"
        r"(?:\s+\([^)]+\))?\s+-\s+",
        value or "",
    )
    if match:
        return datetime.strptime(match.group(1), "%d/%m/%Y %H:%M:%S")
    else:
        raise ValueError(
            f"Formato MTU no reconocido: {value!r}. "
            "Se esperaba, por ejemplo, '05/01/2015 00:00:00 - "
            "05/01/2015 01:00:00'."
        ) from None


def combine_csvs(input_dir: Path) -> None:
    """Lee los CSV de input_dir y crea un archivo combinado por área."""
    grouped_rows: dict[str, list[tuple[datetime, dict[str, str]]]] = defaultdict(list)
    fieldnames: list[str] | None = None
    input_files = sorted(
        path
        for path in input_dir.glob("*.csv")
        if path.name not in OUTPUTS.values()
    )

    if not input_files:
        raise FileNotFoundError(f"No se encontraron CSV en {input_dir}")

    for csv_path in input_files:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ValueError(f"El archivo {csv_path.name} no tiene encabezado")

            if fieldnames is None:
                fieldnames = reader.fieldnames
            elif reader.fieldnames != fieldnames:
                raise ValueError(
                    f"Encabezado distinto en {csv_path.name}. "
                    "Todos los CSV deben tener las mismas columnas."
                )

            required = {"Area", MTU_COLUMN}
            missing = required - set(reader.fieldnames)
            if missing:
                raise ValueError(
                    f"Faltan las columnas {sorted(missing)} en {csv_path.name}"
                )

            for line_number, row in enumerate(reader, start=2):
                area = (row.get("Area") or "").strip()
                if area not in OUTPUTS:
                    raise ValueError(
                        f"Área desconocida en {csv_path.name}, línea {line_number}: "
                        f"{area!r}"
                    )
                mtu = row.get(MTU_COLUMN, "")
                grouped_rows[area].append((parse_mtu_start(mtu), row))

    assert fieldnames is not None

    for area, output_name in OUTPUTS.items():
        rows = sorted(grouped_rows[area], key=lambda item: item[0])
        output_path = input_dir / output_name
        with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(row for _, row in rows)

        if rows:
            first_mtu = rows[0][1][MTU_COLUMN]
            last_mtu = rows[-1][1][MTU_COLUMN]
            print(f"{area}: {len(rows):,} filas")
            print(f"  Desde: {first_mtu.split(' - ', 1)[0]}")
            print(f"  Hasta: {last_mtu.split(' - ', 1)[1]}")
            print(f"  Archivo: {output_path.name}")
        else:
            print(f"{area}: no se encontraron filas")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Combina los CSV de precios en dos archivos según Area."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Carpeta que contiene los CSV (por defecto, la carpeta del script).",
    )
    args = parser.parse_args()
    combine_csvs(args.input_dir.resolve())


if __name__ == "__main__":
    main()
