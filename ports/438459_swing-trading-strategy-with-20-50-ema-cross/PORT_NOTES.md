# #438459 Swing Trading Strategy with 20 50 EMA Cross -> `fmz_438459_ema20_50_cross_short_one_bar`

- FMZ source id: 438459 (lineage).
- Source: https://www.fmz.com/strategy/438459 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-12 11:22:33). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C110). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the short's immediate exit as a signal |
| 2 | PASS | EMA crossings; per-bar long bracket described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [50, 100]: **4 trials**; the long's per-bar bracket pending.

## Ambiguities resolved

- Shorts closed after one bar (wrong-side bracket); long per-bar bracket pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
