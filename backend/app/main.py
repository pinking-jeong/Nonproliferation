"""FastAPI entry point — minimal MVP routes."""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import get_settings
from .modules.apa_graph import APAGraph, build_default_graph
from .modules.document_module import DocumentMiningModule
from .modules.fusion_module import fuse
from .modules.image_module import ImageUnderstandingModule
from .modules.pm_loader import load_all_cells
from .modules.validator import (
    HISTORICAL_CASES,
    run_all,
    run_case,
    synthetic_collector,
)
from .schemas.indicator import Indicator, ProcessHypothesis

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ospm")

app = FastAPI(title="OS-PM API", version="0.1.0")
_settings = get_settings()


@app.on_event("startup")
def _load_pm():
    try:
        app.state.cells = load_all_cells(_settings.pm_schema_dir)
        log.info("Loaded %d PM cells", len(app.state.cells))
    except Exception as e:  # noqa: BLE001
        log.warning("PM schema not loaded: %s", e)
        app.state.cells = {}

    # Build canonical APA graph from chains + PM materials.
    try:
        graph = build_default_graph()
        if app.state.cells:
            graph.populate_from_pm_schema(app.state.cells)
        app.state.apa = graph
        log.info("APA graph: %s", graph.stats())
    except Exception as e:  # noqa: BLE001
        log.warning("APA graph not built: %s", e)
        app.state.apa = APAGraph()


@app.get("/health")
def health():
    return {"status": "ok", "cells_loaded": len(getattr(app.state, "cells", {}))}


@app.get("/pm/cells")
def list_cells():
    return {cid: c.element_name for cid, c in getattr(app.state, "cells", {}).items()}


class ImageAnalyzeRequest(BaseModel):
    image_path: str
    geo_context: dict | None = None


@app.post("/analyze/image", response_model=list[Indicator])
def analyze_image(req: ImageAnalyzeRequest):
    p = Path(req.image_path)
    if not p.exists():
        raise HTTPException(404, f"image not found: {req.image_path}")
    mod = ImageUnderstandingModule()
    raw = mod.coarse_detect(p, req.geo_context)
    if raw.get("facility_type") in (None, "uncertain", "none"):
        return []
    # one-shot demo: skip the RAG retrieval for the MVP
    elements = mod.extract_elements(p, candidate_cells=[], geo_ctx=req.geo_context)
    return mod.to_indicators(elements, source_uri=str(p))


class LiteratureRequest(BaseModel):
    country_code: str = Field(..., examples=["IR"])
    year_start: int = Field(..., examples=[2018])
    year_end: int = Field(..., examples=[2024])
    max_papers: int = 20


@app.post("/analyze/literature", response_model=list[Indicator])
def analyze_literature(req: LiteratureRequest):
    mod = DocumentMiningModule()
    out: list[Indicator] = []
    for i, work in enumerate(mod.search_openalex(req.country_code, (req.year_start, req.year_end))):
        if i >= req.max_papers:
            break
        ind = mod.classify_paper(work)
        if ind:
            out.append(ind)
    return out


class FuseRequest(BaseModel):
    indicators: list[Indicator]
    prior: float = 0.05


@app.post("/fuse", response_model=list[ProcessHypothesis])
def fuse_endpoint(req: FuseRequest):
    return fuse(req.indicators, prior=req.prior)


# --------------------------------------------------------------------------- #
#  Module E — APA Graph endpoints
# --------------------------------------------------------------------------- #


@app.get("/apa/stats")
def apa_stats():
    g: APAGraph = getattr(app.state, "apa", None) or APAGraph()
    return g.stats()


@app.get("/apa/export/cytoscape")
def apa_export_cytoscape():
    """Cytoscape.js elements JSON for in-browser visualisation."""
    g: APAGraph = getattr(app.state, "apa", None) or APAGraph()
    return g.to_cytoscape_json()


@app.get("/apa/export/graphml")
def apa_export_graphml():
    """GraphML XML for Gephi / yEd offline visualisation."""
    from fastapi.responses import Response
    g: APAGraph = getattr(app.state, "apa", None) or APAGraph()
    return Response(content=g.to_graphml(), media_type="application/xml")


class APAPathRequest(BaseModel):
    target: str = Field(..., examples=["Pu", "LEU", "U-233"])
    k: int = Field(default=3, ge=1, le=20)
    source: str | None = None


@app.post("/apa/paths")
def apa_paths(req: APAPathRequest):
    g: APAGraph = getattr(app.state, "apa", None) or APAGraph()
    paths = g.acquisition_paths(req.target, k=req.k, source=req.source)
    return [
        {
            "path": r.path,
            "log_strength_sum": round(r.log_strength_sum, 4),
            "aggregate_strength": round(r.aggregate_strength, 4),
            "target_product": r.target_product,
        }
        for r in paths
    ]


class APARiskRequest(BaseModel):
    state: str
    target: str = "Pu"
    indicators: list[Indicator] = Field(default_factory=list)


@app.post("/apa/risk")
def apa_risk(req: APARiskRequest):
    g: APAGraph = getattr(app.state, "apa", None) or APAGraph()
    for ind in req.indicators:
        g.add_indicator(req.state, ind)
    return {
        "state": req.state,
        "target": req.target,
        "evidence_processes": g.state_evidence_processes(req.state),
        "risk_score": round(g.risk_score(req.state, target=req.target), 4),
    }


# --------------------------------------------------------------------------- #
#  Module F — Validation endpoints
# --------------------------------------------------------------------------- #


@app.get("/validate/cases")
def list_cases():
    return {
        name: {
            "state": c.state,
            "cut_off": c.cut_off.isoformat(),
            "expected_top_process": c.expected_top_process,
            "expected_pm_cells": list(c.expected_pm_cells),
            "minimum_lead_time_years": list(c.minimum_lead_time_years),
            "disclosure_event": c.public_disclosure_event,
            "notes": c.notes,
        }
        for name, c in HISTORICAL_CASES.items()
    }


class ValidateRequest(BaseModel):
    """Run a validation case with caller-supplied indicators (synthetic)."""
    case_name: str
    indicators: list[Indicator]
    prior: float = 0.05


@app.post("/validate/run")
def validate_run(req: ValidateRequest):
    if req.case_name not in HISTORICAL_CASES:
        raise HTTPException(404, f"unknown case: {req.case_name}")
    case = HISTORICAL_CASES[req.case_name]
    coll = synthetic_collector({req.case_name: req.indicators})
    return run_case(case, coll, prior=req.prior).to_dict()


class ValidateAllRequest(BaseModel):
    indicators_per_case: dict[str, list[Indicator]] = Field(default_factory=dict)
    prior: float = 0.05


@app.post("/validate/run_all")
def validate_run_all(req: ValidateAllRequest):
    coll = synthetic_collector(req.indicators_per_case)
    results, metrics = run_all(coll, prior=req.prior)
    return {
        "results": [r.to_dict() for r in results],
        "metrics": metrics.to_dict(),
    }
