"""IAEA Broader-Conclusion (BC) state catalog — realistic-negative class.

A "Broader Conclusion" is the IAEA's strongest positive evaluation:
all declared nuclear material is in peaceful activities and no
indications of undeclared activity. As of recent IAEA Annual
Safeguards Implementation Reports (SIR 2022-2024), about 70+ states
hold this status.

Each entry is documented with:
- ISO-3166 alpha-2 country code
- Year BC was first drawn (publicly reported)
- Whether the state has CSA + AP (always true for BC)
- Indicative facility scale (NPP count, research reactors)

These states constitute the **realistic negatives** for the GNN-light
classifier (vs. the synthetic indicator-stripped negatives used in
Phase 1). They have nuclear-relevant publication and trade signatures
but no covert-weapons-programme indicator.

Sources:
- IAEA SIR public excerpts (annual; specific states named in
  IAEA Director General Statements to the Board)
- IAEA Member States with Additional Protocols in Force
- Public NPT/AP/SQP database
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BCState:
    iso2: str
    name: str
    bc_first_drawn: int  # year
    npp_units: int        # operating nuclear power reactors
    research_reactors: int
    notes: str = ""


# Curated subset of IAEA-confirmed BC states. Not exhaustive (~30 of ~70+).
# Selected for diversity in fuel-cycle scale: from large fleets (FR, JP, KR)
# to research-only programmes (NO, AT, NZ).
BC_STATES: dict[str, BCState] = {
    # --- East Asia ---
    "JP": BCState(
        iso2="JP", name="Japan", bc_first_drawn=2003,
        npp_units=33, research_reactors=8,
        notes="Largest civilian Pu inventory globally; Rokkasho reprocessing under safeguards.",
    ),
    "KR": BCState(
        iso2="KR", name="Republic of Korea", bc_first_drawn=2008,
        npp_units=26, research_reactors=2,
        notes="HANARO research reactor + KAERI PRIDE pyroprocessing R&D.",
    ),
    # --- Europe ---
    "DE": BCState(
        iso2="DE", name="Germany", bc_first_drawn=2008,
        npp_units=0, research_reactors=4,
        notes="All commercial NPPs shut down 2023; KIT/Jülich research continues.",
    ),
    "FR": BCState(
        iso2="FR", name="France", bc_first_drawn=2009,
        npp_units=56, research_reactors=4,
        notes="EU member; Euratom safeguards layer; La Hague + MELOX civilian reprocessing/MOX.",
    ),
    "NL": BCState(
        iso2="NL", name="Netherlands", bc_first_drawn=2007,
        npp_units=1, research_reactors=2,
        notes="Urenco enrichment site (commercial, safeguarded).",
    ),
    "BE": BCState(
        iso2="BE", name="Belgium", bc_first_drawn=2007,
        npp_units=5, research_reactors=2,
        notes="SCK-CEN; BR2 research reactor (medical isotopes).",
    ),
    "IT": BCState(
        iso2="IT", name="Italy", bc_first_drawn=2007,
        npp_units=0, research_reactors=3,
        notes="No commercial NPPs since 1990; ENEA research.",
    ),
    "ES": BCState(
        iso2="ES", name="Spain", bc_first_drawn=2008,
        npp_units=7, research_reactors=2,
        notes="CSN regulator; civilian fleet phasing out.",
    ),
    "SE": BCState(
        iso2="SE", name="Sweden", bc_first_drawn=2007,
        npp_units=6, research_reactors=0,
        notes="SKB / Forsmark deep repository (KBS-3) leadership.",
    ),
    "FI": BCState(
        iso2="FI", name="Finland", bc_first_drawn=2007,
        npp_units=4, research_reactors=0,
        notes="Posiva / Onkalo first-of-kind operational deep repository (2024).",
    ),
    "NO": BCState(
        iso2="NO", name="Norway", bc_first_drawn=2007,
        npp_units=0, research_reactors=2,
        notes="JEEP-II + Halden BWR (decommissioning); historical Vemork D2O.",
    ),
    "DK": BCState(
        iso2="DK", name="Denmark", bc_first_drawn=2007,
        npp_units=0, research_reactors=0,
        notes="DR-1/2/3 reactors decommissioned; only LL waste / decommissioning.",
    ),
    "AT": BCState(
        iso2="AT", name="Austria", bc_first_drawn=2007,
        npp_units=0, research_reactors=1,
        notes="ATI Vienna TRIGA II research reactor; constitutional ban on fission power.",
    ),
    "CH": BCState(
        iso2="CH", name="Switzerland", bc_first_drawn=2008,
        npp_units=4, research_reactors=2,
        notes="Phasing out post-2034; ILL/PSI research.",
    ),
    "CZ": BCState(
        iso2="CZ", name="Czechia", bc_first_drawn=2008,
        npp_units=6, research_reactors=2,
        notes="Dukovany + Temelín VVER fleet; Rez research site.",
    ),
    "HU": BCState(
        iso2="HU", name="Hungary", bc_first_drawn=2008,
        npp_units=4, research_reactors=2,
        notes="Paks VVER; Paks-2 expansion under construction.",
    ),
    "PL": BCState(
        iso2="PL", name="Poland", bc_first_drawn=2008,
        npp_units=0, research_reactors=1,
        notes="Maria research reactor; commercial NPP planned.",
    ),
    "PT": BCState(
        iso2="PT", name="Portugal", bc_first_drawn=2007,
        npp_units=0, research_reactors=0,
        notes="No nuclear power; small medical/research isotope use only.",
    ),
    "GR": BCState(
        iso2="GR", name="Greece", bc_first_drawn=2008,
        npp_units=0, research_reactors=1,
        notes="Demokritos GRR-1 reactor.",
    ),
    "IE": BCState(
        iso2="IE", name="Ireland", bc_first_drawn=2007,
        npp_units=0, research_reactors=0,
        notes="No nuclear infrastructure; research-only.",
    ),
    # --- Americas ---
    "CA": BCState(
        iso2="CA", name="Canada", bc_first_drawn=2005,
        npp_units=19, research_reactors=8,
        notes="CANDU homeland; Cameco mining; Chalk River / NRU historical.",
    ),
    "MX": BCState(
        iso2="MX", name="Mexico", bc_first_drawn=2010,
        npp_units=2, research_reactors=2,
        notes="Laguna Verde BWR; ININ research.",
    ),
    "CL": BCState(
        iso2="CL", name="Chile", bc_first_drawn=2009,
        npp_units=0, research_reactors=2,
        notes="CCHEN La Reina + Lo Aguirre research reactors.",
    ),
    "PE": BCState(
        iso2="PE", name="Peru", bc_first_drawn=2010,
        npp_units=0, research_reactors=2,
        notes="IPEN RP-0/RP-10.",
    ),
    "UY": BCState(
        iso2="UY", name="Uruguay", bc_first_drawn=2008,
        npp_units=0, research_reactors=0,
        notes="Research/medical isotope use only.",
    ),
    # --- Oceania ---
    "AU": BCState(
        iso2="AU", name="Australia", bc_first_drawn=2005,
        npp_units=0, research_reactors=1,
        notes="ANSTO OPAL; significant uranium mining (Olympic Dam, Ranger).",
    ),
    "NZ": BCState(
        iso2="NZ", name="New Zealand", bc_first_drawn=2007,
        npp_units=0, research_reactors=0,
        notes="Nuclear-free zone; NPT-AP-BC.",
    ),
    # --- South Asia ---
    "BD": BCState(
        iso2="BD", name="Bangladesh", bc_first_drawn=2010,
        npp_units=0, research_reactors=1,
        notes="BAEC TRIGA Mark II; Rooppur NPP under construction.",
    ),
    "ID": BCState(
        iso2="ID", name="Indonesia", bc_first_drawn=2009,
        npp_units=0, research_reactors=3,
        notes="BATAN Bandung/Yogyakarta/Serpong research reactors.",
    ),
    # --- Africa & Middle East (peaceful) ---
    "ZA_post_1991": BCState(
        iso2="ZA", name="South Africa (post-1991)",
        bc_first_drawn=2010,
        npp_units=2, research_reactors=2,
        notes="Voluntary disarmament 1989-1991; SAFARI-1 research reactor "
              "+ Koeberg PWRs. Listed *separately* from the pre-1991 "
              "covert-programme retrofit case to keep the negative class clean.",
    ),
    "AR_post_1991": BCState(
        iso2="AR", name="Argentina (post-1991)",
        bc_first_drawn=2013,
        npp_units=3, research_reactors=5,
        notes="Atucha/Embalse fleet; INVAP research reactor exporter; "
              "ABACC bilateral safeguards continue alongside IAEA.",
    ),
    "BR_post_1991": BCState(
        iso2="BR", name="Brazil (post-1991)",
        bc_first_drawn=2024,
        npp_units=2, research_reactors=4,
        notes="Angra fleet; INB enrichment for civilian fuel; "
              "ABACC bilateral. BC reportedly first drawn 2024.",
    ),
}


def all_bc_states() -> list[BCState]:
    return list(BC_STATES.values())


def bc_summary() -> dict:
    states = all_bc_states()
    return {
        "n_states": len(states),
        "n_with_npp": sum(1 for s in states if s.npp_units > 0),
        "n_with_research_reactor": sum(1 for s in states if s.research_reactors > 0),
        "n_zero_facilities": sum(1 for s in states
                                  if s.npp_units == 0 and s.research_reactors == 0),
        "regions": "East Asia, Europe, Americas, Oceania, South Asia, Africa",
        "selection_note": (
            "Curated subset of the ~70+ IAEA Broader Conclusion states. "
            "Selected for diversity in fuel-cycle scale (zero to large)."
        ),
    }
