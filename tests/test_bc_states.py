"""Sanity tests for the BC-state catalog."""
from backend.app.modules.bc_states import BC_STATES, all_bc_states, bc_summary


def test_bc_states_loaded():
    assert len(BC_STATES) >= 25
    for k, s in BC_STATES.items():
        assert isinstance(s.iso2, str) and len(s.iso2) == 2
        # Japan was first BC state in 2003; AP entered into force from 2003+.
        assert s.bc_first_drawn >= 2003
        assert s.npp_units >= 0
        assert s.research_reactors >= 0


def test_at_least_one_state_each_category():
    states = all_bc_states()
    assert any(s.npp_units >= 10 for s in states), "expected at least one large fleet"
    assert any(s.npp_units == 0 and s.research_reactors > 0 for s in states), \
        "expected at least one research-only state"
    assert any(s.npp_units == 0 and s.research_reactors == 0 for s in states), \
        "expected at least one zero-facility state (BC just on AP/CSA)"


def test_summary_consistent():
    out = bc_summary()
    assert out["n_states"] == len(BC_STATES)
    assert out["n_with_npp"] + out["n_zero_facilities"] <= out["n_states"]
