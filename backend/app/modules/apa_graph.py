"""Module E — Acquisition Path Analysis (APA) Graph.

A directed multigraph encoding nuclear-fuel-cycle processes, materials,
equipment, and end-products. Built either from the PM YAML schema (full
canonical graph) or constructed manually for tests.

Nodes
-----
- ``process``   — a fuel-cycle activity (e.g., ``gas_centrifuge``)
- ``material``  — a material requirement (e.g., ``maraging_steel``,
  ``UF6``, ``Pu``)
- ``equipment`` — especially-designed or dual-use item
- ``product``   — end product (LEU, HEU, Pu, U-233)
- ``state``     — country node (added when state-level evidence applies)
- ``indicator`` — observed signal (added per ProcessHypothesis)

Edges
-----
- ``REQUIRES``   — process → material/equipment (carries ``strength``)
- ``PRODUCES``   — process → product
- ``LEADS_TO``   — process → next process (uranium / plutonium chain)
- ``HAS_INDICATOR`` — state → indicator
- ``SUGGESTS``   — indicator → process (with strength + confidence)

Algorithms exposed
------------------
- ``acquisition_paths(target='Pu', state=None)``  — k-shortest paths
- ``risk_score(state)``  — weighted reachability score for the state
- ``populate_from_pm_schema(cells)``  — auto-build from loaded PM YAML

Edge weights are negative log strength so NetworkX shortest_path returns
the highest-strength route by default.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable

import networkx as nx

from ..schemas.indicator import Indicator, Strength
from ..schemas.pm_cell import PMCell

# Strength → likelihood ratio mirroring fusion_module._LR
_STRENGTH_LR: dict[str, float] = {
    Strength.STRONG.value: 8.0,
    Strength.MEDIUM.value: 2.5,
    Strength.WEAK.value: 1.3,
    Strength.UNCERTAIN.value: 1.0,
}

# Canonical fuel-cycle chains — used when PM schema lacks LEADS_TO links
URANIUM_CHAIN: list[tuple[str, str]] = [
    ("open_pit_mining", "milling_to_yellowcake"),
    ("underground_mining", "milling_to_yellowcake"),
    ("in_situ_leach_ISL", "milling_to_yellowcake"),
    ("by_product_recovery", "milling_to_yellowcake"),
    ("milling_to_yellowcake", "dry_route_to_UF6"),
    ("milling_to_yellowcake", "wet_route_to_UF6"),
    ("milling_to_yellowcake", "conversion_to_UO2"),
    ("dry_route_to_UF6", "gas_centrifuge"),
    ("dry_route_to_UF6", "gaseous_diffusion"),
    ("dry_route_to_UF6", "laser_AVLIS_MLIS_SILEX"),
    ("wet_route_to_UF6", "gas_centrifuge"),
    ("conversion_to_UO2", "lwr_fuel_fabrication"),
    ("conversion_to_UO2", "hwr_fuel_fabrication"),
]

PLUTONIUM_CHAIN: list[tuple[str, str]] = [
    ("lwr_fuel_fabrication", "light_water_reactor_LWR"),
    ("hwr_fuel_fabrication", "heavy_water_reactor_HWR"),
    ("gas_centrifuge", "lwr_fuel_fabrication"),  # LEU → fab
    ("light_water_reactor_LWR", "wet_storage_pool"),
    ("heavy_water_reactor_HWR", "wet_storage_pool"),
    ("graphite_moderated_reactor", "wet_storage_pool"),
    ("research_reactor", "wet_storage_pool"),
    ("fast_breeder_reactor", "wet_storage_pool"),
    ("wet_storage_pool", "PUREX_aqueous"),
    ("wet_storage_pool", "pyroprocessing_electrorefining"),
    ("dry_cask_storage", "PUREX_aqueous"),
]

# Process → product (PRODUCES edges)
PROCESS_PRODUCTS: dict[str, list[str]] = {
    "gas_centrifuge": ["LEU"],
    "gaseous_diffusion": ["LEU"],
    "laser_AVLIS_MLIS_SILEX": ["LEU"],
    "PUREX_aqueous": ["Pu"],
    "pyroprocessing_electrorefining": ["U-Pu-Zr_metallic"],
    "thorium_THOREX": ["U-233"],
}

# Process → required materials (lightweight defaults; PM YAML can override)
PROCESS_MATERIALS: dict[str, list[tuple[str, str]]] = {
    "gas_centrifuge": [
        ("maraging_steel", "strong"),
        ("carbon_fiber_T700", "medium"),
        ("UF6_natural", "strong"),
    ],
    "gaseous_diffusion": [
        ("nickel_barriers", "strong"),
        ("UF6_natural", "strong"),
    ],
    "PUREX_aqueous": [
        ("nitric_acid_high_purity", "strong"),
        ("TBP", "strong"),
        ("dodecane_diluent", "medium"),
        ("hydroxylamine_nitrate", "strong"),
    ],
    "heavy_water_reactor_HWR": [("D2O", "strong"), ("Zircaloy_4", "strong")],
    "graphite_moderated_reactor": [("nuclear_graphite", "strong")],
}


@dataclass(frozen=True)
class APAResult:
    """One acquisition path with weight and node sequence."""
    path: list[str]
    log_strength_sum: float
    target_product: str

    @property
    def aggregate_strength(self) -> float:
        return math.exp(self.log_strength_sum)


@dataclass
class APAGraph:
    """Directed multi-graph with helper methods."""
    G: nx.MultiDiGraph = field(default_factory=nx.MultiDiGraph)

    # ----------------------------- builders --------------------------------- #
    def add_process(self, pid: str, *, volume: int | None = None, name: str | None = None) -> None:
        self.G.add_node(pid, type="process", volume=volume, name=name or pid)

    def add_material(self, mid: str, *, hs_code: str | None = None) -> None:
        self.G.add_node(mid, type="material", hs_code=hs_code)

    def add_product(self, prod: str) -> None:
        self.G.add_node(prod, type="product")

    def add_state(self, state: str) -> None:
        self.G.add_node(state, type="state")

    def add_requires(self, process: str, material: str, strength: str = "medium") -> None:
        self.add_process(process)
        self.add_material(material)
        self.G.add_edge(process, material, relation="REQUIRES",
                        strength=strength, weight=self._weight(strength))

    def add_produces(self, process: str, product: str) -> None:
        self.add_process(process)
        self.add_product(product)
        self.G.add_edge(process, product, relation="PRODUCES",
                        strength="strong", weight=self._weight("strong"))

    def add_leads_to(self, src: str, dst: str, strength: str = "medium") -> None:
        self.add_process(src); self.add_process(dst)
        self.G.add_edge(src, dst, relation="LEADS_TO",
                        strength=strength, weight=self._weight(strength))

    def add_indicator(self, state: str, indicator: Indicator) -> None:
        self.add_state(state)
        ind_id = f"IND::{indicator.cell_id}::{indicator.modality}"
        self.G.add_node(ind_id, type="indicator", **indicator.model_dump())
        self.G.add_edge(state, ind_id, relation="HAS_INDICATOR")
        if indicator.process:
            self.add_process(indicator.process)
            sval = indicator.strength.value if hasattr(indicator.strength, "value") else indicator.strength
            self.G.add_edge(ind_id, indicator.process, relation="SUGGESTS",
                            strength=sval, weight=self._weight(sval))

    @staticmethod
    def _weight(strength: str) -> float:
        # NetworkX shortest path minimises weight; we want max strength →
        # weight = -log(LR). Strong (LR=8) → ~-2.08; weak (LR=1.3) → ~-0.26.
        return -math.log(_STRENGTH_LR.get(strength, 1.0))

    # --------------------------- bulk population ---------------------------- #
    def populate_canonical(self) -> None:
        """Add the canonical uranium and plutonium chain edges."""
        for src, dst in URANIUM_CHAIN + PLUTONIUM_CHAIN:
            self.add_leads_to(src, dst, strength="medium")
        for proc, products in PROCESS_PRODUCTS.items():
            for p in products:
                self.add_produces(proc, p)
        for proc, mats in PROCESS_MATERIALS.items():
            for mat, strength in mats:
                self.add_requires(proc, mat, strength)

    def populate_from_pm_schema(self, cells: dict[str, PMCell]) -> None:
        """Best-effort population from loaded PM cells.

        Looks at processes within E01 (EDE) and E04 (non-nuclear materials)
        cells to wire materials into the graph.
        """
        for cell in cells.values():
            for proc in cell.processes or []:
                self.add_process(proc.id, volume=cell.volume, name=proc.id)
                for mat in proc.materials_required or []:
                    name = mat.get("name") or mat.get("hs_code") or "unknown"
                    strength = mat.get("strength", "medium")
                    if not isinstance(strength, str):
                        strength = "medium"
                    self.add_requires(proc.id, name, strength)

    # ------------------------------ queries --------------------------------- #
    def acquisition_paths(
        self, target: str, *, k: int = 3, source: str | None = None
    ) -> list[APAResult]:
        """k highest-strength paths into ``target``.

        If ``source`` is None, return the k highest-strength paths from any
        leaf process. Excludes weaponization-related products by design (we
        only handle LEU / Pu / U-233 / U-Pu-Zr_metallic etc.).
        """
        if target not in self.G:
            return []

        # All nodes that could plausibly start a chain (nodes with no
        # in-edge of type LEADS_TO / PRODUCES). Materials and states do not
        # start chains; only processes do.
        candidate_sources: list[str]
        if source is not None:
            candidate_sources = [source]
        else:
            candidate_sources = [
                n for n, d in self.G.nodes(data=True)
                if d.get("type") == "process"
                and not any(
                    self.G[u][n][k0].get("relation") in {"LEADS_TO", "REQUIRES"}
                    for u in self.G.predecessors(n) for k0 in self.G[u][n]
                )
            ]

        # Build a simple DiGraph view restricted to LEADS_TO + PRODUCES edges
        # so paths are truly acquisition flows, not material lookups.
        flow = nx.DiGraph()
        for u, v, data in self.G.edges(data=True):
            if data.get("relation") in {"LEADS_TO", "PRODUCES"}:
                if flow.has_edge(u, v):
                    flow[u][v]["weight"] = min(flow[u][v]["weight"], data["weight"])
                else:
                    flow.add_edge(u, v, weight=data["weight"])

        results: list[APAResult] = []
        for src in candidate_sources:
            if src not in flow or target not in flow:
                continue
            try:
                gen = nx.shortest_simple_paths(flow, src, target, weight="weight")
                for i, path in enumerate(gen):
                    if i >= k:
                        break
                    wsum = sum(
                        flow[path[j]][path[j + 1]]["weight"]
                        for j in range(len(path) - 1)
                    )
                    results.append(
                        APAResult(
                            path=path,
                            log_strength_sum=-wsum,
                            target_product=target,
                        )
                    )
            except nx.NetworkXNoPath:
                continue
            except (nx.NodeNotFound, nx.NetworkXError):
                continue
        # Best (highest aggregate strength) first
        results.sort(key=lambda r: r.aggregate_strength, reverse=True)
        return results[:k]

    def state_evidence_processes(self, state: str) -> list[str]:
        """Processes for which ``state`` has at least one indicator."""
        if state not in self.G:
            return []
        out: list[str] = []
        for ind in self.G.successors(state):
            if self.G.nodes[ind].get("type") != "indicator":
                continue
            for proc in self.G.successors(ind):
                if self.G.nodes[proc].get("type") == "process":
                    out.append(proc)
        return sorted(set(out))

    def risk_score(self, state: str, target: str = "Pu") -> float:
        """Aggregate path-strength reachable from state evidence to target.

        Returns a number in [0, ∞). Larger = stronger circumstantial case.
        Caller is responsible for normalising or thresholding.
        """
        if state not in self.G or target not in self.G:
            return 0.0
        evid_procs = self.state_evidence_processes(state)
        if not evid_procs:
            return 0.0
        score = 0.0
        for proc in evid_procs:
            paths = self.acquisition_paths(target, k=1, source=proc)
            if paths:
                score += paths[0].aggregate_strength
        return score

    # ------------------------------ exports --------------------------------- #
    def to_cytoscape_json(self) -> dict:
        """Cytoscape.js elements format: {'nodes':[...], 'edges':[...]}.

        Each node is ``{'data': {'id', 'type', 'label', ...}}``; each
        edge is ``{'data': {'id', 'source', 'target', 'relation', ...}}``.
        """
        nodes = []
        for n, d in self.G.nodes(data=True):
            nodes.append({
                "data": {
                    "id": str(n),
                    "label": d.get("name") or str(n),
                    "type": d.get("type", "unknown"),
                    **{k: v for k, v in d.items() if k not in {"name", "type"}},
                }
            })
        edges = []
        for i, (u, v, d) in enumerate(self.G.edges(data=True)):
            edges.append({
                "data": {
                    "id": f"e{i}",
                    "source": str(u),
                    "target": str(v),
                    "relation": d.get("relation", "RELATED"),
                    "strength": d.get("strength"),
                    "weight": d.get("weight"),
                }
            })
        return {"nodes": nodes, "edges": edges}

    def to_graphml(self) -> str:
        """Serialise to GraphML XML string (re-readable by Gephi etc.).

        NetworkX ``write_graphml`` does not accept None attributes, so
        we fill in defaults before serialising.
        """
        import io
        H = nx.MultiDiGraph()
        for n, d in self.G.nodes(data=True):
            cleaned = {k: ("" if v is None else v) for k, v in d.items()
                       if isinstance(v, (str, int, float, bool))}
            H.add_node(str(n), **cleaned)
        for u, v, d in self.G.edges(data=True):
            cleaned = {k: ("" if val is None else val) for k, val in d.items()
                       if isinstance(val, (str, int, float, bool))}
            H.add_edge(str(u), str(v), **cleaned)
        buf = io.BytesIO()
        nx.write_graphml(H, buf)
        return buf.getvalue().decode("utf-8")

    # ------------------------------ utilities ------------------------------- #
    def stats(self) -> dict[str, int]:
        """Quick node/edge inventory for debugging."""
        type_counts: dict[str, int] = {}
        for _, d in self.G.nodes(data=True):
            type_counts[d.get("type", "unknown")] = type_counts.get(d.get("type", "unknown"), 0) + 1
        rel_counts: dict[str, int] = {}
        for _, _, d in self.G.edges(data=True):
            rel_counts[d.get("relation", "unknown")] = rel_counts.get(d.get("relation", "unknown"), 0) + 1
        return {
            "nodes_total": self.G.number_of_nodes(),
            "edges_total": self.G.number_of_edges(),
            **{f"node_{k}": v for k, v in type_counts.items()},
            **{f"edge_{k}": v for k, v in rel_counts.items()},
        }


def build_default_graph() -> APAGraph:
    """Convenience: a canonical graph populated with uranium + plutonium chains."""
    g = APAGraph()
    g.populate_canonical()
    return g
