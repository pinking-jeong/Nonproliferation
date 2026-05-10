"""Tests for the Module E APA graph."""
from backend.app.modules.apa_graph import APAGraph, build_default_graph
from backend.app.schemas.indicator import Indicator, Modality, Strength


def test_default_graph_populates_uranium_and_plutonium_chains():
    g = build_default_graph()
    s = g.stats()
    assert s["nodes_total"] >= 20
    # Uranium-side products
    assert "LEU" in g.G
    # Plutonium-side products
    assert "Pu" in g.G
    # Canonical chain link
    assert g.G.has_edge("dry_route_to_UF6", "gas_centrifuge")
    assert g.G.has_edge("PUREX_aqueous", "Pu")


def test_acquisition_paths_to_pu_returns_known_route():
    g = build_default_graph()
    paths = g.acquisition_paths("Pu", k=3)
    assert paths, "expected at least one path to Pu"
    # The natural route from uranium feed should pass through a reactor
    top = paths[0].path
    assert "PUREX_aqueous" in top, f"expected PUREX in path, got {top}"


def test_acquisition_paths_to_LEU():
    g = build_default_graph()
    paths = g.acquisition_paths("LEU", k=3)
    assert paths
    # All LEU paths must terminate via an enrichment process
    enrichment_terminal = {"gas_centrifuge", "gaseous_diffusion", "laser_AVLIS_MLIS_SILEX"}
    for p in paths:
        assert any(node in enrichment_terminal for node in p.path)


def test_state_evidence_indicator_propagates():
    g = build_default_graph()
    ind = Indicator(
        cell_id="V03_E01", process="gas_centrifuge",
        modality=Modality.IMAGE, strength=Strength.STRONG, confidence=0.9,
    )
    g.add_indicator("StateX", ind)
    assert "gas_centrifuge" in g.state_evidence_processes("StateX")


def test_risk_score_increases_with_evidence():
    g = build_default_graph()
    base = g.risk_score("UnknownState", target="Pu")
    assert base == 0.0

    ind = Indicator(
        cell_id="V05_E01", process="heavy_water_reactor_HWR",
        modality=Modality.IMAGE, strength=Strength.STRONG, confidence=0.9,
    )
    g.add_indicator("ConcernState", ind)
    score = g.risk_score("ConcernState", target="Pu")
    assert score > 0


def test_unknown_target_returns_empty():
    g = build_default_graph()
    assert g.acquisition_paths("not_a_real_product", k=3) == []


def test_populate_from_pm_schema_runs(tmp_path):
    """PMCell-driven population should not crash on the full schema."""
    from pathlib import Path
    from backend.app.modules.pm_loader import load_all_cells

    schema_dir = Path(__file__).resolve().parents[1] / "pm_schema"
    if not schema_dir.exists():
        return  # skip when run from a worktree without the schema
    cells = load_all_cells(schema_dir)
    g = APAGraph()
    g.populate_from_pm_schema(cells)
    s = g.stats()
    assert s["nodes_total"] > 0
    assert s.get("edge_REQUIRES", 0) > 0


def test_aggregate_strength_is_positive():
    g = build_default_graph()
    paths = g.acquisition_paths("LEU", k=1)
    assert paths
    assert paths[0].aggregate_strength > 0
