"""GNN-light risk scorer — graph-feature engineering + sklearn classifier.

A true GNN (e.g., GCN / GraphSAGE) is overkill for the four-case Phase 1
ground-truth set. Instead, we compute a fixed feature vector per state
from its position in the APA graph and train a logistic regression /
gradient boosting model. This gives a learned, calibrated risk score
that can be retrained as more historical cases become available.

Features extracted per state:
  1. n_evidence      : number of indicator nodes
  2. n_processes     : distinct processes evidenced
  3. avg_strength    : mean SUGGESTS edge weight from indicators
  4. n_paths_to_Pu   : number of acquisition paths to Pu reachable
                      from the evidenced processes
  5. n_paths_to_LEU  : same to LEU
  6. n_paths_to_U233 : same to U-233
  7. best_path_strength_Pu : aggregate strength of best Pu path
  8. cells_breadth   : # distinct V?? volumes touched by indicators
  9. material_signal : count of REQUIRES edges reachable

Training: leave-one-out cross-validation across the 4 historical cases,
all of which are positives (programmes were eventually disclosed). To
avoid all-positive degenerate training we pair each positive with a
synthetic negative: the same state graph stripped of indicators.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..schemas.indicator import Indicator
from .apa_graph import APAGraph

FEATURE_NAMES = [
    "n_evidence",
    "n_processes",
    "avg_strength",
    "n_paths_to_Pu",
    "n_paths_to_LEU",
    "n_paths_to_U233",
    "best_path_strength_Pu_log",
    "cells_breadth",
    "material_signal",
]


def extract_features(graph: APAGraph, state: str) -> np.ndarray:
    """Compute the 9-dimensional feature vector for ``state``."""
    G = graph.G
    if state not in G:
        return np.zeros(len(FEATURE_NAMES))

    indicators = [n for n in G.successors(state)
                  if G.nodes[n].get("type") == "indicator"]
    n_evidence = len(indicators)

    # processes evidenced
    procs: set[str] = set()
    strengths: list[float] = []
    cells: set[str] = set()
    for ind in indicators:
        for proc in G.successors(ind):
            if G.nodes[proc].get("type") == "process":
                procs.add(proc)
            for k in G[ind][proc]:
                d = G[ind][proc][k]
                if d.get("relation") == "SUGGESTS":
                    # Convert weight (negative log LR) back to LR
                    w = d.get("weight", 0.0)
                    strengths.append(np.exp(-w))
        cell_id = G.nodes[ind].get("cell_id")
        if cell_id:
            # First two chars are V?? — keep as cell signature
            cells.add(cell_id[:3] if cell_id else "")

    avg_strength = float(np.mean(strengths)) if strengths else 0.0
    n_processes = len(procs)
    cells_breadth = len({c for c in cells if c.startswith("V")})

    # Path counts per target
    counts: dict[str, int] = {}
    best_log: dict[str, float] = {}
    for target in ("Pu", "LEU", "U-233"):
        c = 0
        best = 0.0
        for proc in procs:
            paths = graph.acquisition_paths(target, k=3, source=proc)
            c += len(paths)
            if paths:
                best = max(best, paths[0].log_strength_sum)
        counts[target] = c
        best_log[target] = best

    # Material breadth
    material_signal = 0
    for proc in procs:
        if proc in G:
            for nbr in G.successors(proc):
                if G.nodes[nbr].get("type") == "material":
                    material_signal += 1

    return np.array([
        n_evidence,
        n_processes,
        avg_strength,
        counts["Pu"],
        counts["LEU"],
        counts["U-233"],
        best_log["Pu"],
        cells_breadth,
        material_signal,
    ], dtype=float)


def train_evaluate_loo(
    graphs_with_indicators: list[tuple[APAGraph, str, list[Indicator]]],
    *,
    classifier: str = "logreg",
):
    """Leave-one-out cross-validation across historical cases.

    Each entry (graph, state, indicators) is one positive sample.
    We synthesise one negative per positive: identical graph but with
    indicators stripped (state-with-no-evidence), giving a 1:1 dataset.

    Parameters
    ----------
    graphs_with_indicators
        list of (graph, state_label, list_of_Indicator)
    classifier
        ``"logreg"`` (default) or ``"gbm"`` (gradient boosted trees).

    Returns dict with per-fold accuracy and aggregated metrics.
    """
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score
    from sklearn.preprocessing import StandardScaler

    X_pos: list[np.ndarray] = []
    X_neg: list[np.ndarray] = []
    labels: list[str] = []
    for graph, state, inds in graphs_with_indicators:
        for ind in inds:
            graph.add_indicator(state, ind)
        X_pos.append(extract_features(graph, state))
        labels.append(state)

        # Strip indicators for the negative twin
        neg_graph = APAGraph()
        for n, d in graph.G.nodes(data=True):
            if d.get("type") != "indicator":
                neg_graph.G.add_node(n, **d)
        for u, v, d in graph.G.edges(data=True):
            if d.get("relation") not in {"HAS_INDICATOR", "SUGGESTS"}:
                if u in neg_graph.G and v in neg_graph.G:
                    neg_graph.G.add_edge(u, v, **d)
        # Add the state node only (no indicators)
        neg_graph.add_state(state)
        X_neg.append(extract_features(neg_graph, state))

    X = np.vstack(X_pos + X_neg)
    y = np.array([1] * len(X_pos) + [0] * len(X_neg))

    n = len(X_pos)
    fold_results: list[dict] = []
    pred_proba_total = np.zeros(2 * n)
    for i in range(n):
        # Hold out positive i AND its negative twin (i + n)
        mask = np.ones(2 * n, dtype=bool)
        mask[i] = False
        mask[i + n] = False
        scaler = StandardScaler().fit(X[mask])
        X_train = scaler.transform(X[mask])
        X_test = scaler.transform(X[~mask])

        if classifier == "gbm":
            clf = GradientBoostingClassifier(n_estimators=50, max_depth=2,
                                             random_state=42)
        else:
            clf = LogisticRegression(max_iter=1000, random_state=42)
        clf.fit(X_train, y[mask])
        proba = clf.predict_proba(X_test)[:, 1]
        pred_proba_total[i] = proba[0]
        pred_proba_total[i + n] = proba[1]

        fold_results.append({
            "fold": i,
            "held_out_state": labels[i],
            "p_positive_pos": float(proba[0]),
            "p_positive_neg": float(proba[1]),
            "correct_pos": bool(proba[0] > 0.5),
            "correct_neg": bool(proba[1] <= 0.5),
        })

    y_pred = (pred_proba_total > 0.5).astype(int)
    return {
        "feature_names": FEATURE_NAMES,
        "n_positive": n,
        "n_negative": n,
        "fold_results": fold_results,
        "loo_accuracy": float(accuracy_score(y, y_pred)),
        "mean_p_pos": float(pred_proba_total[:n].mean()),
        "mean_p_neg": float(pred_proba_total[n:].mean()),
    }


@dataclass(frozen=True)
class RiskScoreResult:
    state: str
    p_program: float
    feature_vector: list[float]
    feature_names: list[str]


def score_state(graph: APAGraph, state: str, model) -> RiskScoreResult:
    """Apply a trained model to a state's graph features."""
    feats = extract_features(graph, state)
    if hasattr(model, "predict_proba"):
        p = float(model.predict_proba(feats.reshape(1, -1))[0, 1])
    else:
        p = float(model.predict(feats.reshape(1, -1))[0])
    return RiskScoreResult(
        state=state, p_program=p,
        feature_vector=feats.tolist(),
        feature_names=FEATURE_NAMES,
    )
