#!/usr/bin/env python3
"""Validate authoritative roadmap vs homepage projection, revision and accepted expansion state.

Usage:
    python scripts/roadmap_validate.py           # read-only CI check
    python scripts/roadmap_validate.py --sync    # update site-progress.json from roadmap and ledger

The Markdown milestone table is the project authority; site-progress.json is a
derived copy for the browser. Never silently update the Markdown from the JSON.
"""
from __future__ import annotations
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ROADMAP = ROOT / "DEVELOPMENT-ROADMAP.md"
STATUS = ROOT / "site-progress.json"
LEDGER = ROOT / "north-american-expression-ledger.json"
CONTROLLER = ROOT / "north-american-expansion-checkpoint.json"
SAGAMORE = ROOT / "sagamore-expression-ledger.json"
VALID_STATUS = {"accepted", "partial", "planned"}
ID_PATTERN = re.compile(r"^[a-z0-9-]{2,64}$")


def get_markdown():
    text = ROADMAP.read_text(encoding="utf-8")
    revision = re.search(r"^\*\*Roadmap revision:\*\* (R\d{3,})\s*$", text, re.M)
    updated = re.search(r"^\*\*Updated:\*\* (\d{4}-\d{2}-\d{2})\s*$", text, re.M)
    if not revision or not updated:
        raise ValueError("Roadmap must declare revision R### and ISO Updated date")
    section = re.search(r"^\| Gate ID \| Outcome \| Weight \| Status \| Evidence \|\s*$([\s\S]*?)(?=\n\n)", text, re.M)
    if not section:
        raise ValueError("Roadmap gate table missing")
    gates = []
    for line in section.group(1).splitlines():
        if not line.startswith("|") or re.match(r"\|[-|\s:]+\|", line):
            continue
        cols = [v.strip() for v in line.split("|")[1:-1]]
        if len(cols) != 5:
            raise ValueError("Malformed five-column gate line: " + line)
        key, label, weight, status, evidence = cols
        if not ID_PATTERN.fullmatch(key) or not label or not evidence:
            raise ValueError("Invalid gate ID/label/evidence: " + key)
        if status not in VALID_STATUS or not weight.isdecimal() or int(weight) < 1:
            raise ValueError("Invalid milestone status/weight: " + key)
        gates.append({"id": key, "label": label, "weight": int(weight),
                      "status": status, "evidence": evidence})
    if len(gates) < 10 or len({g["id"] for g in gates}) != len(gates):
        raise ValueError("Missing or duplicated long-term vision gates")
    if sum(g["weight"] for g in gates) != 100:
        raise ValueError("Total long-term roadmap weight must equal exactly 100")
    accepted = sum(g["weight"] for g in gates if g["status"] == "accepted")
    statement = re.search(
        r"\*\*Current baseline: (\d+)% accepted \((\d+)/(\d+) weighted points\)\.\*\*",
        text)
    if not statement or [int(v) for v in statement.groups()] != [accepted, accepted, 100]:
        raise ValueError("Update the roadmap's current accepted-progress sentence")
    return text, revision.group(1), updated.group(1), gates, accepted


def main(sync=False):
    errors = []
    roadmap, revision, updated, gates, accepted = get_markdown()
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    checkpoint = json.loads(CONTROLLER.read_text(encoding="utf-8"))
    counts = ledger["counts"]
    total = counts["candidates"]
    resolved = sum(counts[k] for k in ("accepted", "excluded", "baseline_preserved"))
    if resolved + counts["pending"] != total:
        errors.append("Ledger disposition counts do not sum to all candidates")
    if checkpoint["dossier_count"] != checkpoint["original_dossier_count"] + len(checkpoint["added_dossiers"]):
        errors.append("Checkpoint dossier count disagrees with accepted additions")
    if len(checkpoint["added_dossiers"]) != counts["accepted"]:
        errors.append("Published expansion addition count disagrees with accepted ledger")
    if checkpoint["status"] != "complete" and any(g["id"] == "na-expansion" and g["status"] == "accepted" for g in gates):
        errors.append("North American gate marked accepted before controller completion")

    # This exact phrase is deliberately required to make workers update the
    # authoritative roadmap whenever a new checkpoint or ledger disposition lands.
    summary = re.search(r"\*\*Stage A[^\n]*?NA-(\d+), ([\d,]+) dossiers\*\*", roadmap)
    if not summary:
        # Current roadmap Stage A is prose, not a bold status banner.
        summary = re.search(r"Stage A[^\n]*?NA-(\d+), ([\d,]+) dossiers", roadmap)
    if not summary:
        errors.append("Roadmap Stage A must state current NA checkpoint and dossier count")
    elif (int(summary.group(1)) != checkpoint["checkpoint"] or
          int(summary.group(2).replace(",", "")) != checkpoint["dossier_count"]):
        errors.append("Roadmap Stage A is stale relative to current expansion checkpoint")
    disposition = re.search(r"\((\d+) of (\d+) decisions\)", roadmap)
    if not disposition or (int(disposition.group(1)), int(disposition.group(2))) != (resolved, total):
        errors.append("Roadmap Stage A is stale relative to ledger disposition count")

    # Switch the visible secondary counter when NA-037 closes, but continue
    # validating the immutable North American controller above.
    phase_source = "north-american-expression-ledger.json"
    phase_done, phase_total = resolved, total
    if checkpoint["status"] == "complete" and SAGAMORE.is_file():
        sc = json.loads(SAGAMORE.read_text(encoding="utf-8"))["counts"]
        phase_source = "sagamore-expression-ledger.json"
        phase_done = sc["existing_published"] + sc.get("accepted_published", 0) + sc["excluded_pending_liquid_distinction"]
        phase_total = sc["total"]
        if phase_done + sc["pending_research"] != phase_total:
            errors.append("Sagamore disposition counts do not reconcile")

    if sync:
        status["asOf"] = updated
        status["revision"] = revision
        status["progress"]["completed"] = phase_done
        status["progress"]["total"] = phase_total
        status["roadmap"]["document"] = "DEVELOPMENT-ROADMAP.md"
        status["roadmap"]["gates"] = gates
        STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        status = json.loads(STATUS.read_text(encoding="utf-8"))

    if status.get("revision") != revision:
        errors.append("site-progress.json roadmap revision differs from Markdown")
    if status.get("asOf") != updated:
        errors.append("site-progress.json review date differs from Markdown")
    if status.get("roadmap", {}).get("document") != "DEVELOPMENT-ROADMAP.md":
        errors.append("Site status does not link to authoritative roadmap")
    if status.get("roadmap", {}).get("gates") != gates:
        errors.append("Site milestone definitions differ from authoritative roadmap table")
    if status.get("progress", {}).get("completed") != phase_done:
        errors.append("Displayed active-phase completed count differs from source ledger")
    if status.get("progress", {}).get("total") != phase_total:
        errors.append("Displayed active-phase total differs from source ledger")
    if status.get("progress", {}).get("source", {}).get("file") != phase_source:
        errors.append("Displayed active-phase source differs from current workflow")
    if not (ROOT / "AGENTS.md").is_file():
        errors.append("AI-worker recovery instruction AGENTS.md missing")
    if '<script defer src="./site-progress.js"' not in (ROOT / "index.html").read_text(encoding="utf-8"):
        errors.append("Homepage missing project-wide progress widget loader")
    if not (ROOT / "site-progress.js").is_file():
        errors.append("Homepage status widget JS missing")

    result = {"schema": "old-oak-roadmap-check-v1", "revision": revision,
              "accepted_points": accepted, "total_points": 100,
              "project_percent": accepted, "gate_count": len(gates),
              "editorial_checkpoint": checkpoint["checkpoint"],
              "published_dossiers": checkpoint["dossier_count"],
              "north_american_resolved": resolved, "north_american_total": total,
              "active_phase": phase_source, "phase_resolved": phase_done, "phase_total": phase_total,
              "status": "passed" if not errors else "failed", "errors": errors}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main(sync="--sync" in sys.argv))
