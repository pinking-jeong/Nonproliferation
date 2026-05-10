"""Load Physical Model YAML cells into Pydantic models."""
from pathlib import Path

import yaml

from ..schemas.pm_cell import PMCell


def load_cell(path: Path) -> PMCell:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return PMCell.model_validate(data)


def load_all_cells(schema_dir: Path) -> dict[str, PMCell]:
    """Load every *.yaml cell file under schema_dir."""
    cells: dict[str, PMCell] = {}
    for p in sorted(schema_dir.glob("**/*.yaml")):
        try:
            cell = load_cell(p)
            cells[cell.cell_id] = cell
        except Exception as e:  # noqa: BLE001 — surface schema errors at load time
            raise RuntimeError(f"Failed to load {p}: {e}") from e
    return cells
