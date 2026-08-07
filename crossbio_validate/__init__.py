"""crossbio-algo artifact validator (v0.2.1, P0-2).

Real implementation of the machine-checkable handoff: every stage's artifact.json
is validated against schemas/stage-schemas.json, and a chain of artifacts is
checked for parent-chain integrity, stage order, the fatal GATE, and the 5
cross-stage content rules (estimand continuity / failure_boundary->acceptance /
notation consistency / pseudocode->code / provenance).

Run:  python -m crossbio_validate validate-chain <dir>
      crossbio validate-chain <dir>            (if installed via pyproject.toml)
"""
from . import core  # noqa: F401

__version__ = "0.2.1"
