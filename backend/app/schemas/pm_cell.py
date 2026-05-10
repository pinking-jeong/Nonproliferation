"""Physical Model cell + volume schema (loaded from YAML).

The PM YAML cells contain reference data that varies considerably across
volumes / elements (some elements use process-by-process structure, others
use category buckets). The schema is therefore intentionally permissive:
required identification fields are validated, while content fields accept
either lists or strength-keyed dicts.
"""
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# Reusable type alias: a list of values OR a strength-keyed dict.
KeywordList = list[str] | dict[str, list[str]]
VisualSignatures = dict[str, list[str]] | dict[str, Any]


class PMProcess(BaseModel):
    """A specific technological process within a PM cell.

    Fields are loosely typed because real PM YAMLs mix structural styles —
    e.g. ``rd_keywords`` may be either a flat list or a ``strong/medium/weak``
    bucket dict. We keep the model permissive (``extra='allow'``) so cells
    can carry domain-specific extensions without breaking the loader.
    """

    model_config = ConfigDict(extra="allow")

    id: str
    description: str | None = None
    references: list[str] = Field(default_factory=list)
    visual_signatures: VisualSignatures = Field(default_factory=dict)
    auxiliary_indicators: dict[str, Any] | list[Any] = Field(default_factory=list)
    materials_required: list[dict[str, Any]] = Field(default_factory=list)
    rd_keywords: KeywordList = Field(default_factory=list)
    end_products: list[str] = Field(default_factory=list)
    by_products: list[Any] = Field(default_factory=list)
    confidence_rules: dict[str, list[str]] = Field(default_factory=dict)


class PMCell(BaseModel):
    """A single PM cell (Volume × Element)."""

    model_config = ConfigDict(extra="allow")

    cell_id: str
    volume: int
    volume_name: str
    element: int
    element_name: str
    definitions: list[str] = Field(default_factory=list)
    processes: list[PMProcess] = Field(default_factory=list)


class PMVolume(BaseModel):
    """Convenience aggregation of cells under one volume."""

    model_config = ConfigDict(extra="allow")

    number: int
    name: str
    acquisition_path_position: str | None = None
    cells: list[PMCell] = Field(default_factory=list)
