# #437548 AlexIncs Bar v12 Breakout Accumulation Strategy Based on Meaningful Bar Filtering -> `fmz_437548_alexinc_meaningful_bars`

- FMZ source id: 437548 (lineage).
- Source: https://www.fmz.com/strategy/437548 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-03 16:30:16). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C102). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Body ratios and counts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The lot, capital % and martingale stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`body_mult` [3.0, 2.0] x `meanful_div` [3.0, 2.0]: **4 trials**; the /5 and /2 body tests and the 6-bar average fixed.

## Ambiguities resolved

- Always-true open test as written; average price = the fill; call-order fills. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
