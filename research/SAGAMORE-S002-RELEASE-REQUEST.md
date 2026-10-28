# Sagamore S002 — publication request

**Date:** 2026-10-27  
**Starting authority:** DEVELOPMENT-ROADMAP.md R004, Sagamore discovery S001, 15 existing preserved Sagamore dossiers / 21 pending / 3 exclusion-holds, published catalogue 1,050, North American checkpoint NA-037 complete.

**Precisely authorized additions:**

- Sagamore Bottled-in-Bond 7 Year (2024), `sagamore-bib-7-year-2024.html`.
- Sagamore Bottled-in-Bond 8 Year (2026), `sagamore-bib-8-year-2026.html`.
- Sagamore Reserve 9 Year Straight Rye Batch 1A (2024), `sagamore-rye-9-year-2024.html`.

**Source data:** `research/sagamore-s002-authored.json`, researched/reviewed exact releases with provisional category-relative Quality, dated alternate US pricing, explicit NC pricing qualifications, five buy-price bands, serving modes and matched independent review scopes.

**Fail-closed contract:** `.github/workflows/sagamore-s002-publish.yml` checks exact preflight and no prior S002 acceptance, builds the three files in the isolated runner, runs `scripts/north_american_validate.py --full` across 1,053 dossiers and `scripts/north_american_runtime.cjs --focused` across 687 responsive views, then verifies metadata, family decisions and roadmap R005 consistency before committing as a single fast-forward update.

Never regenerate any of the protected 825 baseline dossiers, the accepted 225 NA-037 expansion dossier files, or the 15 already-published Sagamore dossiers. Do not claim success before GitHub Actions and follow-on publishing validation pass.
