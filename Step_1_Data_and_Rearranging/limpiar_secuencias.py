"""Crea versiones limpias de los CSV combinados.

Conserva únicamente ``Sequence 1`` cuando la columna Sequence contiene
secuencias y conserva todas las filas ``Without Sequence``. En ambos casos
elimina la columna ``Sequence`` del archivo de salida.
"""

from __future__ import annotations

import csv
from pathlib import Path


SEQUENCE_COLUMN = "Sequence"
FILES = (
    "combined_BZN_DE_AT_LU.csv",
    "combined_BZN_DE_LU.csv",
)


def clean_file(input_path: Path) -> tuple[Path, int, int]:
    output_path = input_path.with_name(f"{input_path.stem}_Clean{input_path.suffix}")
    kept = 0
    discarded = 0

    with input_path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None or SEQUENCE_COLUMN not in reader.fieldnames:
            raise ValueError(f"No existe la columna {SEQUENCE_COLUMN!r} en {input_path.name}")

        output_fields = [field for field in reader.fieldnames if field != SEQUENCE_COLUMN]
        with output_path.open("w", encoding="utf-8-sig", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=output_fields)
            writer.writeheader()

            for row in reader:
                sequence = (row.get(SEQUENCE_COLUMN) or "").strip()
                if sequence not in ("Sequence 1", "Without Sequence"):
                    discarded += 1
                    continue

                writer.writerow({field: row.get(field, "") for field in output_fields})
                kept += 1

    return output_path, kept, discarded


def main() -> None:
    input_dir = Path(__file__).resolve().parent
    for filename in FILES:
        output_path, kept, discarded = clean_file(input_dir / filename)
        print(f"{output_path.name}: {kept:,} filas conservadas; {discarded:,} eliminadas")


if __name__ == "__main__":
    main()
