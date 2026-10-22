# #476263 Dynamic Moving Average Crossover Trend Following Strategy with Adaptive Risk Management -> `fmz_476263_sma5_12_cross_long`

- FMZ source id: 476263 (lineage).
- Source: https://www.fmz.com/strategy/476263 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-27 15:08:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C231). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; per-bar bracket described (pending) |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported; the bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 10] x `slow` [12, 30]: **4 trials**; the per-bar bracket pending.

## Ambiguities resolved

- Per-bar bracket (from the entry price, or the latest close in profit) kept pending (trailing_stop_pending). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
