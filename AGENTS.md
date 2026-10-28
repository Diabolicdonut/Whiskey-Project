# AGENTS.md — Old Oak Omnibus / Whiskey Project

> **Project authority:** [DEVELOPMENT-ROADMAP.md](DEVELOPMENT-ROADMAP.md). Read its full long-term vision, acceptance gates, sequencing and revision/change procedure before making any changes. It overrides this short entrypoint for project scope. Current code and accepted JSON controllers override historical prompts for implementation state.

## Recovery first — required for every worker

1. Inspect the live `main` HEAD and recent CI, **DEVELOPMENT-ROADMAP.md**, `site-progress.json`, `north-american-expansion-checkpoint.json`, `north-american-expression-ledger.json`, and relevant source/validation files.
2. Treat `final-validation-checkpoint.json`, `image-embedding-checkpoint.json`, the original **825** dossier hashes and original index projections as protected completed work. Do not revert newer accepted commits, replay checkpoints, rewrite unrelated dossiers, delete verified images or backdate research.
3. At roadmap R001 (2026-10-27), accepted North American checkpoint is **NA-036**, **1,043 dossiers**, **218 accepted expansion additions** and **7 pending**. Research and structured input for the seven are committed under `research/na-037-*.{md,json}` but NOT published. **This paragraph is a dated historical reference, not an alternative to the current controller.**
4. Resume from the controller's **next_action** and deterministic ledger order. Do not begin Sagamore or later families until the expansion controller has actually completed with validation and signoff.

## Current Sagamore discovery workstream (S001)

- Read `sagamore-expression-ledger.json` and `research/sagamore-2026-discovery.md` after NA-037 closure before adding Sagamore entries. Preserve all 15 preexisting Sagamore pages, differentiate label and batch identities, and do not count the 21 research candidates as published.
- First bounded target: 7-year BiB 2024, 8-year BiB 2026, and 9-year Reserve 2024; verify exact sources, independent tasting scope, time/currency/size of prices and calibrated scores. All changes must pass Chromium and original 825 preservation checks.
- The accepted project scope remains governed by `DEVELOPMENT-ROADMAP.md` R003, not the historical NA-036 line above. Keep the strict roadmap percentage at 41 until a whole gate is accepted.

## Implementation and editorial rules

- Make bounded, recoverable, small checkpoints; never promise an unverified bulk implementation. Use expected Git ref/parent SHA to avoid clobbering concurrent workers.
- Every new dossier requires exact identity and time/currency/bottle-size-aware price context; distinguish producer marketing from independent tasting and preserve reviewer disagreements. N/A is preferable to fabricated scores or images.
- Quality is 1–10 *within category*, 5 genuine average. Value is against reliable dated U.S. / NC ABC pricing where possible. Overall `sqrt(Quality * Value)`, N/A if a component is N/A.
- Dossiers must meet the complete article and serving/comparables/buy-band standards in DEVELOPMENT-ROADMAP.md. Do not add sibling photos or loose image assets to inflate coverage.
- Validate all relevant index/dossier regressions, links, current/old counts, image data and responsive Chromium at 390 / 768 / 1440. The original 825 must remain unchanged unless specifically authorized.

## Roadmap, revision, and homepage status — required with changes

- **The Markdown is authoritative.** If scope, priority, a gate, acceptance status or evidence changes, update DEVELOPMENT-ROADMAP.md, its revision R###, revision history, and the site manifest **in the same change**.
- Run `python scripts/roadmap_validate.py --sync` after editing the Markdown or expansion ledger, then `python scripts/roadmap_validate.py` to verify. The validator checks a 100-point denominator, byte-for-byte gate mirroring, editorial controller and ledger counts, and the homepage status loader.
- `site-progress.js` is already included on the homepage. It displays **Rev R###** plus **Roadmap N%** prominently; expand it for the editorial NA checkpoint, phase resolution, accepted gate list, and source roadmap.
- Completion counts only **accepted, evidence-backed gates**; partial/planned gates earn zero until accepted. The phase-specific candidate count (e.g. 231/238) is not the overall roadmap percentage.
- Keep dates, roadmap and dashboard consistent after every accepted change. CI runs the drift checker and preexisting structural/browser checks. Do not mark work complete before CI passes.
- Commit, report SHA, current accepted checkpoint, milestone/status effects, validation result and next_action.

Never make `site-progress.json` the sole place where roadmap status changes are recorded.
