"""Tests for APA graph export formats."""
import xml.etree.ElementTree as ET

from backend.app.modules.apa_graph import build_default_graph


def test_cytoscape_export_has_nodes_and_edges():
    g = build_default_graph()
    out = g.to_cytoscape_json()
    assert "nodes" in out and "edges" in out
    assert len(out["nodes"]) > 0
    assert len(out["edges"]) > 0
    # Spot-check shape
    n0 = out["nodes"][0]
    assert "data" in n0 and "id" in n0["data"]
    e0 = out["edges"][0]
    assert "data" in e0 and "source" in e0["data"] and "target" in e0["data"]


def test_cytoscape_export_includes_known_nodes():
    g = build_default_graph()
    out = g.to_cytoscape_json()
    ids = {n["data"]["id"] for n in out["nodes"]}
    assert "Pu" in ids
    assert "LEU" in ids
    assert "gas_centrifuge" in ids
    assert "PUREX_aqueous" in ids


def test_graphml_export_is_valid_xml():
    g = build_default_graph()
    s = g.to_graphml()
    # Should parse as XML
    root = ET.fromstring(s)
    # GraphML namespace
    assert "graphml" in root.tag.lower()


def test_graphml_export_includes_edges():
    g = build_default_graph()
    s = g.to_graphml()
    # Quick sanity: graphML contains edge elements
    assert "<edge" in s.lower()
    assert "<node" in s.lower()
