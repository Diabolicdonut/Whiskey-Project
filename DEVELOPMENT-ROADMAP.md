# Old Oak Omnibus — Authoritative Development Roadmap

**Roadmap revision:** R004
**Updated:** 2026-10-27  
**Project:** Old Oak Omnibus / Whiskey Project  
**Production site:** https://diabolicdonut.github.io/Whiskey-Project/  
**Repository:** https://github.com/Diabolicdonut/Whiskey-Project  
**Branch:** `main`

> **Authority:** This document is the governing project-wide vision, acceptance roadmap, and worker handoff contract. Every change to project scope, priority, definitions of done, or accepted development milestone **must be reflected in this file in the same commit as the implementation** (or before it, when planning). `site-progress.json` is the machine-readable projection of the table below; it does not supersede this document.

## 1. North-star vision and non-goals

Old Oak Omnibus is a long-lived, reader-first **whiskey encyclopedia and buying guide**. It should make an unfamiliar expression understandable, make its strengths/weaknesses and true price value comparable to similar whiskeys, and distinguish actual evidence from unsupported promotional claims. It combines historical and producer research, the technical realities of production, independent critic synthesis, serving guidance, comparative recommendations and a fast, approachable sortable catalogue. It is not an inventory site or a campaign to make the highest number of dossiers at any cost.

A whiskey **expression** is the basic unit: distinguish meaningful differences in proof, age, mash, finish, batch/era, cask or release identity. Do not duplicate the same canonical expression under variants of a spelling. Different years and barrels get distinct dossiers **when** verifiable distinctions justify it. Historical and hard-to-find releases can be catalogued, clearly dated and separated from currently buyable products.

The ideal long-term site supports Bourbon, Rye, Tennessee Whiskey (**kept separate from Bourbon**), Wheat whiskey, American single malt and other American whiskey, Canadian, Scotch (meaningfully separated by type), Irish, Japanese and further responsibly approved styles. Avoid implying that *all future releases on earth* are knowable or can be completed. New collections enter through **explicit, finite discovery ledgers** and updated planning weights at a reviewed roadmap revision.

## 2. Governing file hierarchy — inspect before editing

1. **This document** determines vision, sequencing, governance, required deliverables and roadmap acceptance definitions. `AGENTS.md` gives the compact entrypoint.
2. **Current branch files over historical chat recollections.** Read `main` HEAD, relevant accepted GitHub CI runs, this roadmap, and the current controllers before writing.
3. **Expansion authority:** `north-american-expansion-checkpoint.json` + `north-american-expression-ledger.json` are authoritative for North American implementation state, counts, immutable expression order and next action. Never advance a checkpoint based on this roadmap alone.
4. **Protected baseline:** `final-validation-checkpoint.json`, `image-embedding-checkpoint.json`, the original 825 dossier content hashes and baseline catalogue entries are preservation anchors. No unrelated edits or regeneration of baseline HTML.
5. **Published content/technical truth:** individual `*.html` articles, `whiskey-data.json`, `north-american-expansion-data.json`, `index.html`, the editorial/calibration audits and validation scripts must agree.
6. **Progress projection:** `site-progress.json` defines what the existing `site-progress.js` badge displays. Use `scripts/roadmap_validate.py` to detect inconsistency with this roadmap.

If any sources disagree, preserve accepted newer work, investigate, and **do not invent a successful validation or silently reset a ledger**.

## 3. Dossier contract (applies to every whiskey)

A canonical article must provide an expression-specific bottle image near the top **when exact-image bytes are authenticated** (otherwise a truthful missing-image note); descriptive overview; brand/historical context; producer/source and country; category; proof/ABV; mash bill with percentages only if supported; age and aging process; barrel finishes and release/era distinction; multiple independent critical perspectives when available; detailed synthesis including disagreement and confidence; strengths and weaknesses; at least two meaningful comparables; serving recommendations **neat, rocks, Old Fashioned and Manhattan** (and highball where suitable) with where it shines or is less suitable; a date-stamped assessed market price; five meaningful buy-price bands or five explicitly conditional bands where numbers cannot be defended; Quality/Value/Overall; sources and research date.

Never fabricate tasting, mash proportions, age, current availability, MSRP, rarity premium, retailer price, image authenticity or consensus. An article may honestly retain N/A when evidence is insufficient. Distinguish producer notes from independent reviews and historical reviews from current releases. Preserve source URLs and the scope of every named reviewer. Prefer self-contained embedded images; **do not add loose/external assets just to fill a gap**. Update dates only for actual new research, not a mechanical rebuild.

## 4. Scoring and value contract

**Quality (1–10)** is intrinsically **category-relative** and excludes price: 1 catastrophic/drain-pour; 2 poor; 3 bad/flawed; 4 below average; **5 genuine category average**; 6 good; 7 very good; 8 excellent; 9 exceptional/elite; 10 reference-class. Use category-specific, defensible low/high anchors and a representative 5. Bourbon vs bourbon, rye vs rye, Canadian styles separately, etc. Do not use American Bourbon benchmarks to score Canadian single malt or Scotch. Where anchors are sparse, use explicitly labeled parent-category or provisional universal-rubric assessment: Integration 25%, Flavor 20%, Finish 15%, Cleanliness 15%, Texture 10%, Maturity 10%, Distinctiveness 5%. Identify uncertainty rather than forcing extreme anchors.

**Value (1–10)** compares Quality to **typical North Carolina ABC** purchase price where applicable, including pragmatic buying alternatives, value thresholds and diminishing returns. Keep time, currency, bottle size, proof, current-versus-historical availability and alternate-U.S.-offer basis attached to each quoted price. Never silently substitute CAD for USD, a 375 mL price for 750 mL, a collector asking price for regular retail, or a launch MSRP for a current price. **Overall = √(Quality × Value)**; show one decimal while sorting on full precision. Overall remains N/A if either component is unsupported. Resist luxury-price halo effects and explain what higher age, unusual maturation, finishing or proof actually contributes.

## 5. Reader experience and platform vision

The landing page is a compact, alphabetically browsable and fully sortable horizontal list of **Whiskey (linked), Type, Proof, typical NC ABC Cost, Mash Bill, Age, Quality, Value and Overall**. Families and other categorical filters must be complete, uniquely labeled and alphabetized by displayed label (**All first**). Keep Tennessee Whiskey distinct. Use defensible mash shorthand (C corn, R rye, W wheat, MB malted barley, etc.), honest N/A sorting and transparent historical/alternate-price labels.

Maintain search including aliases, filters with URL state and browser back navigation, accessible tables and forms, keyboard support, fast loading, coherent mobile layout (390px), tablet (768px), and desktop (1440px). The **revision and full-roadmap percentage** should be evident at a glance from the existing site progress badge, with expanded milestone detail and a direct link back here. This must remain a static GitHub Pages site requiring no account or external services for essential reading.

## 6. Approved long-term milestones — 100 weighted points

Status meanings: **accepted** = explicitly validated full gate criteria; **partial** = ongoing/partially delivered and earns **zero** accepted points; **planned** = not started and earns zero. The percentage is the sum of weights of **accepted** gates divided by the total weight of **100**. It is **not** the number of published bottles divided by an arbitrary target and does not treat partial implementation as done. The weights are fixed planning decisions until a documented revision is approved.

| Gate ID | Outcome | Weight | Status | Evidence |
|---|---|---:|---|---|
| foundation | Preserve accepted 825-dossier baseline and authoritative recovery records | 8 | accepted | final-validation-checkpoint.json; north-american-expansion-checkpoint.json |
| initial-corpus | Establish the initial researched 825-expression dossier corpus | 10 | accepted | final-validation-checkpoint.json; audit.md |
| image-audit | Finish the initial 825-image inspection and verified embedding pass | 5 | accepted | image-embedding-checkpoint.json |
| catalogue-core | Deliver searchable, compact, nine-column sortable catalogue and score model | 7 | accepted | index.html; whiskey-data.json; scripts/north_american_validate.py |
| na-expansion | Close all 238 Widow Jane/Canadian expression decisions and publish validated dossiers | 11 | accepted | north-american-expansion-checkpoint.json; north-american-expression-ledger.json; research/na-037-authored.json |
| sagamore | Complete separately researched Sagamore Spirit expression family | 8 | partial | sagamore-expression-ledger.json; research/sagamore-2026-discovery.md |
| priority-families | Close approved North American family gaps (Weller, Kings, Jeptha Creed, Canadian Club and others) | 5 | planned | family-catalog-v6.7.md; future family ledgers |
| world-families | Expand major international and underserved whiskey styles in approved finite batches | 5 | planned | future approved discovery ledgers |
| quality-calibration | Recalibrate all dossiers with category-specific 1–10 anchors and reviewer-supported evidence | 9 | partial | calibration-hierarchy-v6.2.md; score-audit.json; north-american-calibration.md |
| price-value | Maintain trustworthy NC ABC-oriented pricing, Value, and five evidence-based buy bands | 8 | partial | value-review-audit.json; north-american-expansion-data.json |
| dossier-standard | Enforce complete canonical articles, serving comparisons and traceable reviewer synthesis | 7 | partial | incomplete-dossier-review-v5.1.md; scripts/north_american_validate.py |
| media-provenance | Complete expression-exact bottle imagery and public source/link provenance checks | 6 | partial | image-embedding-checkpoint.json; north-american-expression-ledger.json |
| ux-accessibility | Finish family/alphabetical filter normalization, responsive design and accessibility | 5 | partial | index.html; scripts/north_american_runtime.cjs |
| release-qa | Apply full-repository static, browser and preservation acceptance on every release | 4 | partial | scripts/north_american_validate.py; .github/workflows/completion-validation.yml |
| project-governance | Maintain single source-of-truth roadmap, revision and forward maintenance workflow | 2 | partial | DEVELOPMENT-ROADMAP.md; site-progress.json; scripts/roadmap_validate.py |

**Current baseline: 41% accepted (41/100 weighted points).** This intentionally replaces the earlier **44%** shorter delivery-plan metric because the denominator now covers the *broader known long-term vision*. A drop in displayed percentage here is **scope rebasing, not loss of accepted work**. The initial 30 points are earned by the 825-dossier accepted baseline, initial image verification, and functioning comparison catalogue. Numeric progress beyond these gates requires documented acceptance; claiming the broader project is “nearly done” based on 231/238 expansion decisions would be misleading.

### Detailed stage sequence and acceptance checkpoints

**Stage A — Preserve and finish current commitments.** Original 825 dossiers remain immutable. As of 2026-10-27, **NA-037, 1,050 dossiers** = 825 baseline + 28 Widow Jane + 197 Canadian; ledger **225 accepted, 11 excluded, 2 baseline-preserved, 0 pending** (238 of 238 decisions). The final seven Canadian dossiers are published and were tested with zero failures using full structural checking and focused Chromium at 390/768/1440. North American Expansion is complete; categorical filters have been alphabetized with All first. Do not replay accepted checkpoints 001–037. Advance to approved Sagamore research as Stage B.

**Stage B — Extend expression coverage deliberately.** **Sagamore S001 discovery accepted 2026-10-27:** 15 existing dossiers preserved, 21 distinct or conditional expression candidates recorded for independent evidence review, three presentation/non-whiskey exclusions/holds. Source-linked finite ledger: `sagamore-expression-ledger.json`; audit: `research/sagamore-2026-discovery.md`. Start with the separately sourced 2024 7-year BiB, 2026 8-year BiB and 2024 9-year rye, publishing only after verified full dossier, index, source/score, pricing and Chromium acceptance. This is a *partial* Sagamore milestone; no new dossiers are accepted by discovery alone. Move to Sagamore Spirit as the next named family, then prioritize requested gaps (Weller, Kings, Jeptha Creed, Canadian Club and other substantive Canadian/North American families) and approved international styles. Publish in bounded 5–10-dossier recoverable batches (or smaller when risk demands), with own discovery ledger/acceptance evidence. Research flagship and notable variants first; distinguish true expressions from bottle-size/packaging variations. Reprioritize only through a roadmap revision rather than opportunistic count maximization.

**Stage C — Audit quality, value and article depth across *all* published dossiers.** Establish well-supported worst, midpoint and best anchors *per* like-for-like style; review scores across the original and expansion cohorts; audit discrepancies such as same-family spelling duplicates, provisional/unsupported scores, major price/value outliers and inconsistent bottle sizes. Complete reviewer synthesis, five price bands, where-to-use serving guidance, technically honest recipes and contextual comparables without rewriting validated prose gratuitously.

**Stage D — Media, accessibility, source trust and maintainability.** Improve only authenticated bottle images, remove genuinely unused redundant assets without disturbing accepted embeddings, check source link health and editorial provenance, normalize family controls, improve site responsiveness/performance/keyboard access and strengthen CI. Maintain an explicit cadence for dated NC ABC/alternate price and source refresh, and for investigating user-reported errors. A broad, permanently unfinished catalogue remains a healthy living product *after* the agreed finite roadmap reaches acceptance.

### Quantitative milestones vs vision progress

A field-specific metric such as `231/238` means **North American candidate disposition**, *not* total-project progress. Likewise `1,043 dossiers` is a content count, not 1,043 ÷ a speculative worldwide total. The homepage badge must display **the roadmap weighted percentage prominently** and surface the narrower expansion count only in details.

## 7. Required AI-worker procedure (every session)

1. **Recover first:** inspect current `main` SHA, this roadmap, `site-progress.json`, the relevant ledgers/checkpoints, prior accepted CI and latest accepted edits. Never trust a remembered older checkpoint.
2. **Declare bounded scope:** state which gate(s), source documents, authorizations and small checkpoint are involved. Do not make unrequested cross-family changes.
3. **Do research before scoring:** authenticate exact expression, date, producer provenance, primary specifications, independent tasting and size/currency-specific price; distinguish hard evidence from editorial interpretation.
4. **Implement in small, atomic, restart-safe units:** keep old accepted files byte-preserved except intentional justified changes. Use expected Git SHA/lease to avoid overwriting concurrent workers; do not reuse rolled-back or rejected patches.
5. **Validate before accepting:** run existing structural checks, original 825 hash/index preservation, link/image/data consistency, scoring math, all named UI controls and Chromium at 390/768/1440. Inspect CI results and record limitations. A passing input schema alone does **not** accept new dossiers.
6. **Update roadmap and status in the same accepted change:** adjust gate status only when its definition of done is met, add new finite gates/rebalance weights explicitly when scope changes, record dated evidence and change log, update `site-progress.json` revision and gate mirror, run `python scripts/roadmap_validate.py`. Update relevant expression ledger/controller separately according to its stricter rules.
7. **Report grounded results:** state old/new commit and checkpoint, validated counts, accepted vs pending, any blockers, next `next_action`, and exact CI status. Never say “finished” for a created-but-unvalidated file or promise asynchronous continuation.

A new AI worker must not rewrite prior accepted articles, inflate completion by converting partial work to accepted without evidence, or silently edit only `site-progress.json` while leaving this document stale.

**S001 active-phase display:** After NA-037 completion, the secondary homepage metric tracks **Sagamore 18/39 discovery dispositions** (15 existing published expressions and 3 excluded/held, with 21 pending exact-release research). It is not the number of new articles completed or a substitute for the **41/100** accepted full-vision points.

## 8. Revision, governance and completion rules

The project-wide **roadmap revision** uses `R001`, `R002`, etc., independently of technical implementation commit SHA and the North American **NA-036** editorial checkpoint. Every material change to roadmap vision, weights, statuses, milestone priorities, acceptance evidence or an accepted milestone **increments the R-number**, updates the heading above and `site-progress.json.revision`, and adds a dated change-log entry. Cosmetic spelling-only corrections may retain the revision. The homepage badge shows this **roadmap/project revision**; the expansion checkpoint remains separately identified in expanded detail.

Do not count partial gate weight toward accepted completion, and do not change weights casually to boost percent. When a new requirement materially expands scope, give it a discrete weighted gate or adjust explicitly at a revision and explain denominator rebasing. A point total other than 100 or mismatch between this table and `site-progress.json` is a CI failure. A completed overall roadmap requires every approved gate accepted with evidence; it does **not** imply every possible whiskey release in the future has been researched.

## 9. Revision history

- **2026-10-27 — R004:** Show Sagamore's 18/39 discovery dispositions as the homepage's active secondary counter instead of completed North American 238/238. Preserve overall **41%** accepted points, 1,050 published dossiers and NA-037; validate active ledger parity.
- **2026-10-27 — R003:** Started Sagamore Spirit S001 with a source-linked, finite ledger: 15 protected existing dossiers, 21 edition-gated research candidates and 3 exclusions/holds. Marked Sagamore gate partial without claiming publication; overall strict accepted weight remains **41%**. Added discovery validation to CI; next S002 is three individual evidence-led dossiers.
- **2026-10-27 — R002:** Accepted and validated NA-037: seven remaining Canadian dossiers; total 1,050, 238/238 decisions, all original 825 preserved. Normalized catalogue filters alphabetically. North American gate accepted (+11 weighted points); overall **41%**. Next authorized family: Sagamore.
- **2026-10-27 — R001:** Expanded the existing 11-gate/44% coverage sketch into a holistic, 15-gate, 100-point roadmap covering platform, world-category coverage, source/price accuracy, complete dossier and calibration standards, maintenance and AI-worker procedures. Rebased accepted percentage to **30%** without changing accepted dossiers, scoring or expansion checkpoint. Wired the site-visible revision and roadmap to this governing document.
