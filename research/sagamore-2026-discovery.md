# Sagamore Spirit — discovery and baseline-preservation audit

**Checked:** 2026-10-27, accepted NA-037 and roadmap R002. **Output:** `sagamore-expression-ledger.json`, a finite, machine-readable discovery slate.

## Findings

- There are **15 already published Sagamore dossiers**, all preserved by exact filenames in the ledger; the historical family-catalog-v6.7.md listed 15, though the new ledger is sourced from current repo `main` rather than historical summary counts.
- Current and historical official Sagamore listings disclose many further rye and specialty variants. The ledger tracks **21 distinct or potentially distinct expression candidates** as `pending_research`, with edition/batch identity safeguards.
- **Three exclusions/holds**: Ravens Purple Rising and Darkness Falls memorabilia/packaging require a proven liquid distinction before adding a redundant dossier; Sagamore Spirit Amaro is not whiskey. This does not claim either Ravens edition is proven identical; both are excluded *pending evidence of liquid difference*.
- Some existing articles are narrow batch-specific records (Batch 2R Small Batch, Batch 9A Double Oak) and **must not be silently treated as current general-expression reviews**. The High Rye Bourbon 2025 and 2026 articles must remain distinct until a supported batch comparison identifies whether any is a duplicate.
- Producer specifications never become independent reviewer ratings. Every new article must carry transparent dated NC/alternative USD 750 mL price provenance, or Value = N/A. Do not infer undisclosed high/low rye mash proportions.

## Recommended first release — three explicitly separate identities

1. **Sagamore Bottled-in-Bond 7-Year (2024):** 100 proof, fall 2017 distillation; historical distillery listing $59 / bottle and independent Bourbon Lens + Drinkhacker tastings. Differentiate from the existing 5-year review and the separately documented 6-year 2023 bottling.
2. **Sagamore Bottled-in-Bond 8-Year (September 2026):** 100 proof, spring 2018 distillation, 100% Maryland distilled, age 8. Breaking Bourbon published an exact-expression review and a 2026 $60/750mL reference; label this *MSRP/reviewer price*, not verified NC ABC. The review sample was producer-provided, so retain that disclosure.
3. **Sagamore 9-Year Straight Rye (2024 Batch 1A):** 112.6 proof, nine years, independent tasting from The Whiskey Reviewer plus related collector notes; separate from the **already published 10-Year Rye**. Avoid implying a 2024 dated tasting is current 2026 stock.

These three are **discovered only**; this checkpoint does not publish the articles, assign scores, claim all price listings current, or increment the 1,050 total. Target follow-up: publish in a bounded release with 825 baseline and all NA dossiers immutably preserved, extend index search/filter/projection and expansion metadata, full `--full` static and 390/768/1440 Chromium checks, then explicit ledger/roadmap acceptance.

## Official discovery and independent review source leads

- Official Sagamore current and past releases: https://sagamorespirit.com/spirits/
- Sagamore 8-year Bottled-in-Bond official: https://sagamorespirit.com/spirits/sagamore-bottled-in-bond-straight-rye-whiskey/
- Sagamore 7-year 2024 store SKU: https://shop.sagamorespirit.com/products/sagamore-2024-bottled-in-bond-straight-rye-whiskey
- Sagamore 9-year official: https://sagamorespirit.com/spirits/sagamore-9-year-old-rye-whiskey/
- Sagamore 2025 Manhattan official: https://sagamorespirit.com/spirits/manhattan-finish/
- Sagamore America 250 official: https://sagamorespirit.com/spirits/america-250-straight-rye-whiskey/
- Breaking Bourbon 8-year BiB review 2026: https://www.breakingbourbon.com/review/sagamore-bottled-in-bond-8-year-old-straight-rye-2026
- Bourbon Lens 7-year BiB tasting: https://bourbonlens.com/7-year-bottled-in-bond-rye-whiskey/
- Drinkhacker 7-year BiB independent tasting: https://www.drinkhacker.com/2025/10/28/review-sagamore-rye-bottled-in-bond-7-years-old/
- Whiskey Reviewer 9-year Batch 1A tasting: https://whiskeyreviewer.com/2025/04/sagamore-9-year-old-rye-reserve-series-review-batch-1a/
- Breaking Bourbon 2025 cask strength: https://www.breakingbourbon.com/review/sagamore-rye-cask-strength
- 2024 Manhattan relaunch press: https://www.prweb.com/releases/sagamore-spirit-launches-second-release-of-manhattan-finish-rye-whiskey-302098547.html

## Recovered preexisting filenames — do not regenerate

- `sagamore-10-year-rye.html`
- `sagamore-bottled-in-bond-5-year-reviewed-2023.html`
- `sagamore-calvados-finish-2020.html`
- `sagamore-cask-strength-7-year-batch-1a.html`
- `sagamore-cognac-finish-2026-catalogue.html`
- `sagamore-high-rye-bourbon-2026.html`
- `sagamore-high-rye-bourbon.html`
- `sagamore-manhattan-finish-2020.html`
- `sagamore-port-finish-2023.html`
- `sagamore-pot-still-rye-malt-catalogue.html`
- `sagamore-rye-cask-strength.html`
- `sagamore-rye-double-oak-batch-9a.html`
- `sagamore-rye-small-batch-batch-2r.html`
- `sagamore-sherry-finish-reviewed-2023.html`
- `sagamore-tequila-finish-2021.html`

## Rules for later workers

Read `DEVELOPMENT-ROADMAP.md`, `AGENTS.md`, `sagamore-expression-ledger.json` and live `main` before researching or changing Sagamore. Respect prior accepted checkpoint NA-037. Add later candidates only as reviewed finite scope changes. Never import the North American 238-candidate ledger into this new phase, never claim a pending candidate is a published dossier, and never change Quality/Value/Overall scores without independent matched evidence.
