"""Indicator + ProcessHypothesis data models."""
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Strength(str, Enum):
    STRONG = "strong"
    MEDIUM = "medium"
    WEAK = "weak"
    UNCERTAIN = "uncertain"


class Modality(str, Enum):
    IMAGE = "image"
    TEXT = "text"
    TRADE = "trade"
    ENV_SIGNAL = "env_signal"
    EXPORT_CONTROL = "export_control"


class Indicator(BaseModel):
    """A single observation matched to a PM cell."""

    model_config = ConfigDict(use_enum_values=True)

    cell_id: str = Field(..., description="PM cell id e.g., V03_E01")
    process: str = Field(..., description="canonical process name")
    modality: Modality
    strength: Strength
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: dict[str, Any] = Field(default_factory=dict)
    source_uri: str | None = None
    timestamp: datetime | None = None
    extracted_by: str = Field(default="vlm", description="vlm | rule | hybrid")


class ProcessHypothesis(BaseModel):
    """Aggregated belief that a state is operating a given process."""

    process: str
    cells: list[str]
    posterior: float = Field(..., ge=0.0, le=1.0)
    contributing_indicators: list[Indicator]
    rationale: str | None = None
