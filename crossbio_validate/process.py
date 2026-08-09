"""Process Assurance Layer (v0.3.1) — state-machine-enforced workflow.

The run-manifest tracks which stages have been COMPLETED / SKIPPED / are BLOCKED, preventing an
agent from silently bypassing required steps (the CCC process-audit finding: agent loaded skills
but skipped search / brainstorm / artifact / audit).

Commands (exposed via cli.py):
  crossbio init-run <dir> --mode standard --tier T2   create a run-manifest
  crossbio next <dir>                                  → ALLOWED_STAGE (gate)
  crossbio complete-stage <dir> <stage> [--artifact-id ..] [--evidence-manifest ..]
  crossbio skip-stage <dir> <stage> --reason <code> --justification <text>
  crossbio finalize <dir>                              → READY_FOR_USER or PROVISIONAL_NONCOMPLIANT
"""
from __future__ import annotations

import json
import os
from typing import Optional

# Per-mode predecessor DAGs. Each stage lists predecessors that must be COMPLETED or SKIPPED.
STAGE_DAGS = {
    "quick": {
        "data_audit":        {"required": True,  "predecessors": []},
        "evidence_search":   {"required": True,  "predecessors": ["data_audit"]},
        "brainstorm":        {"required": False, "predecessors": ["evidence_search"]},
        "algorithm_design":  {"required": True,  "predecessors": ["data_audit"]},
        "specification":     {"required": False, "predecessors": ["algorithm_design"]},
        "adversarial_audit": {"required": False, "predecessors": ["algorithm_design"]},
    },
    "standard": {
        "data_audit":        {"required": True,  "predecessors": []},
        "evidence_search":   {"required": True,  "predecessors": ["data_audit"]},
        "brainstorm":        {"required": False, "predecessors": ["evidence_search"]},
        "viability":         {"required": True,  "predecessors": ["evidence_search"]},
        "algorithm_design":  {"required": True,  "predecessors": ["viability"]},
        "specification":     {"required": True,  "predecessors": ["algorithm_design"]},
        "adversarial_audit": {"required": True,  "predecessors": ["specification"]},
    },
    "publication": {
        "data_audit":        {"required": True,  "predecessors": []},
        "evidence_search":   {"required": True,  "predecessors": ["data_audit"]},
        "brainstorm":        {"required": True,  "predecessors": ["evidence_search"]},
        "viability":         {"required": True,  "predecessors": ["brainstorm"]},
        "adversarial_audit": {"required": True,  "predecessors": ["viability"]},
        "algorithm_design":  {"required": True,  "predecessors": ["adversarial_audit"]},
        "specification":     {"required": True,  "predecessors": ["algorithm_design"]},
        "benchmark":         {"required": True,  "predecessors": ["specification"]},
        "roadmap":           {"required": True,  "predecessors": ["benchmark"]},
    },
}

VALID_SKIP_REASONS = {
    "USER_DEFINED_SINGLE_DIRECTION",
    "INSUFFICIENT_DATA",
    "NOT_APPLICABLE",
    "TIME_CONSTRAINT",
    "SKIPPED_BY_USER",
}


class RunManifest:
    """A run-manifest.json tracking the process state of a research task."""

    def __init__(self, path: str, data: dict):
        self.path = path
        self.data = data

    # ---- construction ----
    @classmethod
    def create(cls, run_dir: str, mode: str = "standard", target_tier: str = "T2") -> "RunManifest":
        dag = STAGE_DAGS.get(mode, STAGE_DAGS["standard"])
        stages = {}
        for stage, config in dag.items():
            stages[stage] = {
                "required": config["required"],
                "status": "pending",
                "artifact_id": None,
                "skip_reason_code": None,
                "skip_justification": None,
                "evidence_manifest": None,
            }
        data = {
            "run_id": os.path.basename(os.path.abspath(run_dir.rstrip("/"))),
            "mode": mode,
            "target_tier": target_tier,
            "stages": stages,
        }
        os.makedirs(run_dir, exist_ok=True)
        path = os.path.join(run_dir, "run-manifest.json")
        m = cls(path, data)
        m.save()
        return m

    @classmethod
    def load(cls, run_dir: str) -> "RunManifest":
        path = os.path.join(run_dir, "run-manifest.json")
        if not os.path.isfile(path):
            raise FileNotFoundError(f"no run-manifest.json in {run_dir}")
        with open(path) as f:
            return cls(path, json.load(f))

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)

    # ---- queries ----
    def _dag(self):
        return STAGE_DAGS.get(self.data["mode"], STAGE_DAGS["standard"])

    def stage_status(self, stage: str) -> str:
        return self.data["stages"].get(stage, {}).get("status", "pending")

    def predecessors_done(self, stage: str) -> bool:
        preds = self._dag().get(stage, {}).get("predecessors", [])
        return all(self.stage_status(p) in ("completed", "skipped") for p in preds)

    def allowed_stage(self) -> Optional[str]:
        """The first stage that is pending AND its predecessors are done."""
        for stage in self._dag():
            if self.stage_status(stage) == "pending" and self.predecessors_done(stage):
                return stage
        return None

    # ---- transitions ----
    def complete_stage(self, stage: str, artifact_id: str = None, evidence_manifest: str = None):
        if stage not in self.data["stages"]:
            raise ValueError(f"unknown stage '{stage}' for mode '{self.data['mode']}'")
        if not self.predecessors_done(stage):
            preds = self._dag()[stage]["predecessors"]
            blocked = [p for p in preds if self.stage_status(p) not in ("completed", "skipped")]
            raise ValueError(f"stage '{stage}' BLOCKED — predecessors not done: {blocked}")
        self.data["stages"][stage]["status"] = "completed"
        if artifact_id:
            self.data["stages"][stage]["artifact_id"] = artifact_id
        if evidence_manifest:
            self.data["stages"][stage]["evidence_manifest"] = evidence_manifest
        self.save()

    def skip_stage(self, stage: str, reason_code: str, justification: str):
        if stage not in self.data["stages"]:
            raise ValueError(f"unknown stage '{stage}' for mode '{self.data['mode']}'")
        if reason_code not in VALID_SKIP_REASONS:
            raise ValueError(f"invalid reason_code '{reason_code}'; valid: {sorted(VALID_SKIP_REASONS)}")
        self.data["stages"][stage]["status"] = "skipped"
        self.data["stages"][stage]["skip_reason_code"] = reason_code
        self.data["stages"][stage]["skip_justification"] = justification
        self.save()

    # ---- finalization ----
    def finalize(self):
        """Check process compliance. Returns (status_string, missing_list, warnings_list)."""
        missing = []
        warnings = []
        for stage, config in self._dag().items():
            st = self.data["stages"].get(stage, {})
            status = st.get("status", "pending")
            required = config["required"]
            if required and status not in ("completed", "skipped"):
                missing.append(f"{stage} (required, status={status})")
            if status == "skipped" and required:
                if not st.get("skip_reason_code"):
                    missing.append(f"{stage} (required, skipped without reason_code)")
                else:
                    warnings.append(f"{stage} skipped (required) — reason: {st['skip_reason_code']}")
            if status == "completed" and required and not st.get("artifact_id"):
                missing.append(f"{stage} (completed but no artifact_id)")
            # evidence_search must have evidence_manifest
            if stage == "evidence_search" and status == "completed" and not st.get("evidence_manifest"):
                missing.append(f"{stage} (completed but no evidence_manifest — did you actually search?)")

        status = "READY_FOR_USER" if not missing else "PROVISIONAL_NONCOMPLIANT"
        return status, missing, warnings
